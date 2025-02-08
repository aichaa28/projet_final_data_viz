# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
sys.path.insert(0, os.path.abspath('../src/projet_final_data_viz'))

project = 'Projet_final_data_viz'
copyright = '2025, Aicha Ettriki and Youssef Abdelhedi'
author = 'Aicha Ettriki and Youssef Abdelhedi'
release = '07/02/2025'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  # Génère des docstrings automatiquement
    'sphinx.ext.napoleon',  # Pour les docstrings au format Google
    'sphinx.ext.viewcode',  # Ajoute des liens vers le code source
]


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'eng'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
