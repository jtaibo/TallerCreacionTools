# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'TLC'
copyright = '2022-2023, Universidade da Coruña'
author = 'Universidade da Coruña'
release = 'v0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.coverage', 'sphinx.ext.napoleon', 'sphinx.ext.autosummary']
autosummary_generate = True  # Turn on sphinx.ext.autosummary

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

#autodoc_mock_imports = ["maya", "shiboken2", "PySide2"]

import os
import sys
sys.path.insert(0, os.path.abspath('../../maya/python'))
sys.path.insert(0, os.path.abspath("./fake_modules")) # Find a fake maya module in gitHub server to avoid sphinx failure

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

#html_theme = 'alabaster'
#html_theme = 'sphinx_book_theme'
html_theme = "sphinx_rtd_theme"

html_static_path = ['_static']
