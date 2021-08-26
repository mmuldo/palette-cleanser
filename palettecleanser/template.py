from __future__ import annotations

import jinja2 as j2
import yaml
import os
import shutil

from . import theme
from . import config
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import IO, AnyStr, Optional
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
class TemplateFile(Template, ABC):
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
    @abstractmethod
    def generate_signature(self) -> str:
        '''returns comment to put at top of file to indicate it was templated by palette-cleanser

        Returns
        -------
        str
            comment to put at top of file to indicate it was templated by palette-cleanser
        '''
        pass

    def combine(
            self,
            destination: IO[AnyStr],
            current: IO[AnyStr] = None,
            default: IO[AnyStr] = None,
            overwrite: IO[AnyStr] = None
    ):
        '''writes default, then current, then overwrite to destination

        Parameters
        ----------
        destination : IO[AnyStr]
            writable
        current : IO[AnyStr], optional
            user's current file
        default : IO[AnyStr], optional
            file whose elements will be overwritten by user's current file
        overwrite : IO[AnyStr], optional
            file whose elements will overwrite by user's current file
        '''
        if default:
            destination.write(default.read())
        if current:
            destination.write(current.read())
        if overwrite:
            destination.write(overwrite.read())


    def create(self):
        '''create a template and save it to {config.templates_dir}'''
        template_file_name = os.path.join(config.templates_dir, self.path + '.j2')
        os.makedirs(os.path.dirname(template_file_name), exist_ok=True)

        with open(template_file_name, 'w') as template_file:
            current = open_readable(os.path.join(os.environ['HOME'], self.path))
            default = open_readable(os.path.join(default_templates, self.path + '.j2'))
            overwrite = open(os.path.join(overwrite_templates, self.path + '.j2'))

            self.combine(template_file, current, default, overwrite)

            close_readable(current)
            close_readable(default)
            close_readable(overwrite)

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
            shutil.move(destination, destination + '.backup')

        with open(destination, 'w') as out_file:
            out_file.write(self.generate_signature())
            out_file.write(output)


@dataclass
class YAMLTemplateFile(TemplateFile):
    '''
    represents a YAML file possibly containing jinja expressions

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
        return f'# {templated_signature}\n'


@dataclass
class RASITemplateFile(TemplateFile):
    '''
    represents a RASI file possibly containing jinja expressions

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
        return f'/* {templated_signature} */\n'

@dataclass
class HaskellTemplateFile(TemplateFile):
    '''
    represents a Haskell file possibly containing jinja expressions

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
        return f'-- {templated_signature}\n'


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
def resolve_template_file(path: str) -> TemplateFile:
    '''determine TemplateFile child class from file path extension

    Parameters
    ----------
    path : str
        file path (relative to $HOME)

    Returns
    -------
    TemplateFile
        TemplateFile child class that corresponds to the extension
    '''
    ext = os.path.splitext(path)[1]

    return {
        '.yml': YAMLTemplateFile,
        '.yaml': YAMLTemplateFile,
        '.rasi': RASITemplateFile,
        '.hs': HaskellTemplateFile
    }[ext](path)


def from_path(path: str, ignored_files: list[str] = []) -> Template:
    '''create Template from path

    Parameters
    ----------
    path : str
        file/directory path (relative to $HOME)
    ignored_files : list[str], optional
        subfiles/folders to exclude when creating a TemplateDirectory

    Returns
    -------
    Template
        template object corresponding to the provided file path
    '''
    home_path = os.path.join(os.environ['HOME'], path)
    if not os.path.isdir(home_path):
        # base case: path is a file or doesn't exist under $HOME
        return resolve_template_file(path)

    # because we recurse down the file tree, peel off root folder of ignored_files for next call
    next_ignored_files = [os.path.join(*ignored_file.split('/')[1:] if ignored_file.split('/')[1:] else ['']) for ignored_file in ignored_files]

    # recursive case: path is a directory
    return TemplateDirectory(
        path,
        [
            from_path(os.path.join(path, child), next_ignored_files)
            for child in os.listdir(home_path)
            if child not in ignored_files
        ]
    )

def template_managed(template_theme: theme.Theme):
    '''populate all listed managed files with variable values from provided theme and write to $HOME

    Parameters
    ----------
    template_theme : theme.Theme
        theme that provides template variables
    '''
    for path in config.get_config_settings()['managed_files']:
        if isinstance(path, Mapping):
            # list element is a singleton dictionary whose key is the file
            # and value includes a list of ignored files
            for k, v in path.items():
                from_path(k, v['ignored_files']).template(template_theme)
        else:
            # list element is just a file name
            from_path(path).template(template_theme)
