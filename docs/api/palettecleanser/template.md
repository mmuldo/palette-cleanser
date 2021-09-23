Module palettecleanser.template
===============================

Functions
---------

    
`close_readable(readable: Optional[IO[AnyStr]])`
:   close file, if it exists
    
    Parameters
    ----------
    readable : Optional[IO[Anystr]]
        object with read() method or None

    
`create_managed()`
:   create templates for all listed managed files and save to {config.templates_dir}

    
`from_path(root: str, path: str, ignored_files: list[str] = []) ‑> palettecleanser.template.Template`
:   create Template from path that exists under specified root
    
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

    
`from_paths(root: str, paths: list[Union(str, dict[str, Any])]) ‑> list[Template]`
:   creates list of Templates from list of paths that exists under specified root
    
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

    
`open_readable(path: str) ‑> Optional[IO[~AnyStr]]`
:   open a file for reading, if it exists
    
    Parameters
    ----------
    path : str
        file path
    
    Returns
    -------
    Optional[IO[AnyStr]]
        object with read() method; None if file doesn't exist

    
`remove_j2(path: str)`
:   removes .j2 extension from filepath

    
`template_managed(template_theme: theme.Theme)`
:   populate all listed managed files with variable values from provided theme and write to $HOME
    
    Parameters
    ----------
    template_theme : theme.Theme
        theme that provides template variables

Classes
-------

`Template(path: str)`
:   abstract class for template
    
    Attributes
    ----------
    path : str
        relative filepath from home directory

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * palettecleanser.template.TemplateDirectory
    * palettecleanser.template.TemplateFile

    ### Class variables

    `path: str`
    :

    ### Methods

    `create(self)`
    :   create a template and save it to {config.templates_dir}

    `template(self, template_theme: theme.Theme)`
    :   populate tempate with variable values and save to $HOME
        
        Parameters
        ----------
        template_theme : theme.Theme
            theme that provides template variables

`TemplateDirectory(path: str, children: list[Template])`
:   directory that contains templates
    
    Attributes
    ----------
    path : str
        relative filepath from home directory
    children : list[Template]
        list of Templates in directory

    ### Ancestors (in MRO)

    * palettecleanser.template.Template
    * abc.ABC

    ### Class variables

    `children: list`
    :

    ### Methods

    `create(self)`
    :   create a template and save it to {config.templates_dir} for each child template

    `template(self, template_theme: theme.Theme)`
    :   populate template with variable values and save to $HOME for each child template
        
        Parameters
        ----------
        template_theme : theme.Theme
            theme that provides template variables

`TemplateFile(path: str)`
:   represents a file possibly containing jinja expressions
    
    Attributes
    ----------
    path : str
        relative filepath from home directory

    ### Ancestors (in MRO)

    * palettecleanser.template.Template
    * abc.ABC

    ### Class variables

    `path: str`
    :

    ### Methods

    `create(self)`
    :   create a template based on current configuration and save it to {config.templates_dir}

    `generate_signature(self) ‑> str`
    :   returns comment to put at top of file to indicate it was templated by palette-cleanser
        
        Returns
        -------
        str
            comment to put at top of file to indicate it was templated by palette-cleanser

    `is_templated(self) ‑> bool`
    :   whether file at $HOME/{self.path} is templated
        
        Returns
        -------
        bool
            True if file contains templated signature, False otherwise