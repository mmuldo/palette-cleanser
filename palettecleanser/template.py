from __future__ import annotations

import jinja2 as j2
import yaml
import os
import shutil

from . import theme
from . import config
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import IO, AnyStr, Optional, Union
from collections.abc import Mapping


### GLOBAL VARS ###
# jinja environment
env = j2.Environment(loader=j2.FileSystemLoader(config.templates_dir), trim_blocks=True, lstrip_blocks=True)
# default 'signature' to put in a comment at the top of templated files
templated_signature = '@palette-cleanser'
# templates to use when creating templates for user
manual_templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
# settings for file that can be overwritten by settings user's file
default_templates = os.path.join(manual_templates_dir, 'defaults')
# settings for file that will overwrite user's file (usually settings related to colors)
overwrite_templates = os.path.join(manual_templates_dir, 'overwrites')


### UTILITY FUNCTIONS ###
def open_readable(path: str) -> Optional[IO[AnyStr]]:
    '''open a file for reading, if it exists

    Parameters
    ----------
    path : str
        file path

    Returns
    -------
    Optional[IO[AnyStr]]
        object with read() method; None if file doesn't exist
    '''
    try:
        return open(path, 'r')
    except FileNotFoundError:
        return None

def close_readable(readable: Optional[IO[AnyStr]]):
    '''close file, if it exists

    Parameters
    ----------
    readable : Optional[IO[Anystr]]
        object with read() method or None
    '''
    if readable:
        readable.close()

def remove_j2(path: str):
    '''removes .j2 extension from filepath'''
    return path[:-3] if path[-3:] == '.j2' else path


### CLASSES ###
@dataclass
class Template(ABC):
    '''abstract class for template

    Attributes
    ----------
    path : str
        relative filepath from home directory

    Methods
    -------
    create()
        create a template and save it to {config.templates_dir}
    template(template_theme)
        populate template with variable values and save to $HOME
    '''
    path: str

    @abstractmethod
    def create(self):
        '''create a template and save it to {config.templates_dir}'''
        pass

    @abstractmethod
    def template(self, template_theme: theme.Theme):
        '''populate tempate with variable values and save to $HOME

        Parameters
        ----------
        template_theme : theme.Theme
            theme that provides template variables
        '''
        pass

@dataclass
class TemplateFile(Template):
    '''
    represents a file possibly containing jinja expressions

    Attributes
    ----------
    path : str
        relative filepath from home directory

    Methods
    -------
    generate_signature()
        returns comment to put at top of file to indicate it was templated by palette-cleanser
    combine(destination, current, default, overwrite)
        combines default, current, and overwrite files and writes result to destination
    create()
        create a template and save it to {config.templates_dir}
    is_templated()
        returns true if file at $HOME/{path} contains the template signature
    template(template_theme)
        populate template with variable values and save to $HOME
    '''
    def generate_signature(self) -> str:
        '''returns comment to put at top of file to indicate it was templated by palette-cleanser

        Returns
        -------
        str
            comment to put at top of file to indicate it was templated by palette-cleanser
        '''
        ext = os.path.splitext(self.path)[1]
        if not ext:
            ext = os.path.basename(self.path)

        try:
            signature = {
                '.hs': f'-- {templated_signature}',
                '.rasi': f'/* {templated_signature} */',
                '.vimrc': f'" {templated_signature}'
            }[ext]
        except KeyError:
            signature = f'# {templated_signature}'

        return signature + '\n'


    def create(self):
        '''create a template based on current configuration and save it to {config.templates_dir}'''
        template_file_name = os.path.join(config.templates_dir, self.path + '.j2')
        os.makedirs(os.path.dirname(template_file_name), exist_ok=True)

        with open(template_file_name, 'w') as template_file:
            for path in [
                    # file whose elements will be overwritten by user's current configuration
                    (default_templates, self.path + '.j2'),
                    # current configuration
                    (os.environ['HOME'], self.path),
                    # file whose elements will overwrite user's current configuration
                    (overwrite_templates, self.path + '.j2')
            ]:
                readable = open_readable(os.path.join(*path))
                if readable:
                    template_file.write(readable.read())

                close_readable(readable)


    def is_templated(self) -> bool:
        '''whether file at $HOME/{self.path} is templated

        Returns
        -------
        bool
            True if file contains templated signature, False otherwise
        '''
        try:
            with open(os.path.join(os.environ['HOME'], self.path), 'r') as f:
                return templated_signature in f.readline()
        except FileNotFoundError:
            # files that don't exist are considered templated
            return True


    def template(self, template_theme: theme.Theme):
        '''populate tempate with variable values and save to $HOME

        Parameters
        ----------
        template_theme : theme.Theme
            theme that provides template variables
        '''
        destination = os.path.join(os.environ['HOME'], self.path)
        os.makedirs(os.path.dirname(destination), exist_ok=True)

        output = env.get_template(self.path + '.j2').render(template_theme.export())

        if not self.is_templated():
            # backup user's current file, unless it was generated by palette-cleanser
            shutil.move(destination, destination + '.backup')

        with open(destination, 'w') as out_file:
            out_file.write(self.generate_signature())
            out_file.write(output)


@dataclass
class TemplateDirectory(Template):
    '''directory that contains templates

    Attributes
    ----------
    path : str
        relative filepath from home directory
    children : list[Template]
        list of Templates in directory

    Methods
    -------
    create()
        create a template and save it to {config.templates_dir} for each child template
    template(template_theme)
        populate template with variable values and save to $HOME for each child template
    '''
    children: list[Template]

    def create(self):
        '''create a template and save it to {config.templates_dir} for each child template'''
        for child in self.children:
            child.create()

    def template(self, template_theme: theme.Theme):
        '''populate template with variable values and save to $HOME for each child template

        Parameters
        ----------
        template_theme : theme.Theme
            theme that provides template variables
        '''
        for child in self.children:
            child.template(template_theme)



### FUNCTIONS ###

def from_path(root: str, path: str, ignored_files: list[str] = []) -> Template:
    '''create Template from path that exists under specified root

    Parameters
    ----------
    root : str
        root directory under which path exists (e.g. $HOME)
    path : str
        file/directory path (relative to root)
    ignored_files : list[str], optional
        subfiles/folders to exclude when creating a TemplateDirectory

    Returns
    -------
    Template
        template object corresponding to the provided file path
    '''
    root_path = os.path.join(root, path)

    if not os.path.isdir(root_path):
        # base case: path is a file or doesn't exist

        # peal off .j2 extension if we're getting the path from a template directory
        return TemplateFile(remove_j2(path))

    # because we recurse down the file tree, peel off root folder of ignored_files for next call
    next_ignored_files = ['/'.join(ignored_file.split('/')[1:]) for ignored_file in ignored_files]

    # recursive case: path is a directory
    return TemplateDirectory(
        path,
        [from_path(root, os.path.join(path, child), next_ignored_files)
         for child in os.listdir(root_path)
         if remove_j2(child) not in ignored_files]
    )


def from_paths(root: str, paths: list[Union(str, dict[str, Any])]) -> list[Template]:
    '''creates list of Templates from list of paths that exists under specified root

    Parameters
    ----------
    root : str
        root directory under which path exists (e.g. $HOME)
    paths : list[Union(str, dict[str, Any])]
        file/directory paths (relative to root), where each path might be a
        dictionary whose single value is an 'ignored_files' list

    Returns
    -------
    list[Template]
        list of template objects corresponding to the provided file paths
    '''
    ts = []

    for path in paths:
        if isinstance(path, Mapping):
            # list element is a singleton dictionary whose key is the file
            # and value includes a list of ignored files
            for k, v in path.items():
                ts.append(from_path(root, k, v['ignored_files']))
        else:
            # list element is just a file name
            ts.append(from_path(root, path))

    return ts

def create_managed():
    '''create templates for all listed managed files and save to {config.templates_dir}'''
    for t in from_paths(os.environ['HOME'], config.get_config_settings()['managed_files']):
        t.create()

def template_managed(template_theme: theme.Theme):
    '''populate all listed managed files with variable values from provided theme and write to $HOME

    Parameters
    ----------
    template_theme : theme.Theme
        theme that provides template variables
    '''
    for t in from_paths(config.templates_dir, config.get_config_settings()['managed_files']):
        t.template(template_theme)

    # for path in config.get_config_settings()['managed_files']:
    #     if isinstance(path, Mapping):
    #         # list element is a singleton dictionary whose key is the file
    #         # and value includes a list of ignored files
    #         for k, v in path.items():
    #             from_path(config.templates_dir, k, v['ignored_files']).template(template_theme)
    #     else:
    #         # list element is just a file name
    #         from_path(config.templates_dir, path).template(template_theme)
