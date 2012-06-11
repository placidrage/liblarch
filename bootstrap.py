#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    bootstrap-sphinx
    ~~~~~~~~~~~~~~~~

    :copyright: Copyright 2012 by Joe R. Nassimian.
    :license: BSD, see LICENSE for details.
"""

import os
from os.path import isdir, isfile, getsize, normpath, \
                    abspath, join, split, sep, splitext

try:
    from setuptools import find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import find_packages

try:
    from sphinx.quickstart import generate
    from sphinx.apidoc import recurse_tree
except ImportError, exc:
    print((
        "{0!s}\n\nThis command depends on sphinx, "
        "install it and try again.").format(exc)
    )


# -----------------------------------------------------------------------------

# automodule options
if 'SPHINX_APIDOC_OPTIONS' in os.environ:
    OPTIONS = os.environ['SPHINX_APIDOC_OPTIONS'].split(',')
else:
    OPTIONS = [
        'members',
        'undoc-members',
        # 'inherited-members', # disabled because there's a bug in sphinx
        'show-inheritance',
    ]

# -----------------------------------------------------------------------------

def makename(package, module):
    """
    Join package and module with a dot.
    """
    # Both package and module can be None/empty.
    if package:
        name = package
        if module:
            name += '.' + module
    else:
        name = module
    return name

# -----------------------------------------------------------------------------

def format_heading(level, text):
    """
    Create a heading of <level> [1, 2 or 3 supported].
    """
    underlining = ['=', '-', '~', ][level-1] * len(text)
    return '{0}\n{1}\n\n'.format(text, underlining)

# -----------------------------------------------------------------------------

def format_directive(module, package=None):
    """
    Create the automodule directive and add the options.
    """
    directive = '.. automodule:: {0}\n'.format(makename(package, module))
    for option in OPTIONS:
        directive += '    :{0}:\n'.format(option)
    return directive

# -----------------------------------------------------------------------------

def write_file(name, text, opts):
    """
    Write the output file for module/package <name>.
    """
    fname = join(opts['path'], '{0}{1}'.format(name, opts['suffix']))
    print 'Creating file {0}.'.format(fname)
    with open(fname, 'w') as f:
        f.write(text)

# -----------------------------------------------------------------------------

def create_modules_list(modules):
    modules.sort()
    prev_module = ''
    text = ''
    for module in modules:
        # look if the module is a subpackage and, if yes, ignore it
        if not module.startswith(prev_module + '.'):
            text += '   {0}\n'.format(module)
            prev_module = module

    return text

def create_modules_toc_file(modules, opts, name='modules'):
    """
    Create the module's index.
    """
    text = format_heading(1, '{0}'.format(opts["project"]))
    text += '.. toctree::\n'
    text += '   :maxdepth: {0}\n\n'.format(opts["mastertocmaxdepth"])

    text += create_modules_list(modules)

    write_file(name, text, opts)

# -----------------------------------------------------------------------------

def create_module_file(package, module, opts):
    """
    Build the text of the file and write the file.
    """
    text = format_heading(1, '{0} Module'.format(module))
    #text += format_heading(2, ':mod:`{0}` Module'.format(module))
    text += format_directive(module, package)
    write_file(makename(package, module), text, opts)

# -----------------------------------------------------------------------------

def create_package_file(root, master_package, subroot, py_files, opts, subs):
    """
    Build the text of the file and write the file.
    """
    package = split(root)[-1]
    text = format_heading(1, '{0} Package'.format(package))
    # add each module in the package
    for py_file in py_files:

        if getsize(join(root, py_file)) > 2:
            is_package = py_file == "__init__.py"
            py_file = splitext(py_file)[0]
            py_path = makename(subroot, py_file)
            if is_package:
                heading = ':mod:`{0}` Package'.format(package)
            else:
                heading = ':mod:`{0}` Module'.format(py_file)
            text += format_heading(2, heading)
            text += format_directive(is_package and subroot or py_path,
                                     master_package)
            text += '\n'

    # build a list of directories that are packages
    subs = [sub for sub in subs if isfile(join(root, sub, INITPY))]
    # if there are some package directories, add a TOC for theses subpackages
    if subs:
        text += format_heading(2, 'Subpackages')
        text += '.. toctree::\n\n'
        for sub in subs:
            text += '    {0}.{1}\n'.format(makename(master_package, subroot), sub)
        text += '\n'

    write_file(makename(master_package, subroot), text, opts)

# -----------------------------------------------------------------------------

def recurse_tree(rootpath, opts):
    """
    Look for every file in the directory tree and create the corresponding
    ReST files.
    """
    # use absolute path for root, as relative paths like '../../foo' cause
    # 'if "/." in root ...' to filter out *all* modules otherwise
    rootpath = normpath(abspath(rootpath))

    # check if the base directory is a package and get its name
    if "__init__.py" in os.listdir(rootpath):
        root_package = rootpath.split(sep)[-1]
    else:
        # otherwise, the base is a directory with packages
        root_package = None

    toplevels = []
    for root, subs, files in os.walk(rootpath):
        # document only Python module files
        py_files = sorted([f for f in files if splitext(f)[1] == '.py'])

        is_pkg = "__init__.py" in py_files
        if is_pkg:
            py_files.remove("__init__.py")
            py_files.insert(0, "__init__.py")
        elif root != rootpath:
            # only accept non-package at toplevel
            del subs[:]
            continue

        # remove hidden ('.') and private ('_') directories
        subs[:] = sorted(sub for sub in subs if sub[0] not in ['.', '_'])

        if is_pkg:
            # we are in a package with something to document
            if subs or len(py_files) > 1 or not \
                shall_skip(join(root, "__init__.py")):
                subpackage = root[len(rootpath):].lstrip(sep).\
                    replace(sep, '.')
                create_package_file(root, root_package, subpackage,
                                    py_files, opts, subs)
                toplevels.append(makename(root_package, subpackage))
        else:
            # if we are at the root level, we don't require it to be a package
            assert root == rootpath and root_package is None
            for py_file in py_files:
                if not shall_skip(join(rootpath, py_file)):
                    module = splitext(py_file)[0]
                    create_module_file(root_package, module, opts)
                    toplevels.append(module)

    return toplevels

# -----------------------------------------------------------------------------

def bootstrap(path, name, version, release=None):

    d = dict((
        # root path
        ("path", path),
        # separate source and build dirs (bool)
        ("sep", False),
        # name prefix for templates and static dir
        ("dot", ""),
        # project name
        ("project", name),
        # Author name(s)
        ("author", u"Lionel Dricot & Izidor Matušov"),
        # Project version, e.g. 2.5
        ("version", version or ""),
        # Project release, e.g. 2.5.1
        ("release", release or version or ""),
        # Source file suffix
        ("suffix", ".rst"),
        # master document name (without suffix)
        ("master", "index"),
        # Maximum depth of submodules to show in the TOC (int)
        ("mastertocmaxdepth", 4),
        # add configuration for epub builder
        ("epub", False),
        # automatically insert docstrings from modules (bool)
        ("ext_autodoc", True),
        # automatically test code in doctest blocks (bool)
        ("ext_doctest", False),
        # link Sphinx docs of different projects (bool)
        ("ext_intersphinx", False),
        # write "todo" entries (bool)
        ("ext_todo", True),
        # checks for documentation coverage (bool)
        ("ext_coverage", False),
        # include math, rendered as PNG images (bool)
        ("ext_pngmath", False),
        # include math, rendered in the browser by MathJax (bool)
        ("ext_mathjax", True),
        # conditional inclusion of content based on config values (bool)
        ("ext_ifconfig", False),
        # include links to the source code of documented Python objects (bool)
        ("ext_viewcode", True),
        # create Makefile (bool)
        ("makefile", False),
        # create Windows command file (bool)
        ("batchfile", False),
    ))

    if not isdir(path):
        os.makedirs(path)

    modules = recurse_tree(name, d)
    d["mastertoctree"] = create_modules_list(modules)
    create_modules_toc_file(modules, d)

    generate(d, silent=True, overwrite=True)

# -----------------------------------------------------------------------------

standalone_packages = find_packages(exclude=['tests'])

for package in standalone_packages:
    version = "0.1"
    bootstrap("docs/{0}/src".format(package), package, version)

# -----------------------------------------------------------------------------
