project = "pofff"
copyright = "2025-2026, NORCE Research AS"
author = "NORCE Research AS"
extensions = [
    "sphinx.ext.autodoc", "sphinx.ext.autosummary", "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode", "numpydoc", "sphinx_copybutton", "sphinx_design",
    "sphinxcontrib.video",
    "sphinx_design",
]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
autosummary_generate = True
numpydoc_show_class_members = False
html_theme = "pydata_sphinx_theme"
html_logo = "figs/logo.png"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_show_sourcelink = True
html_show_sphinx = False
html_last_updated_fmt = "%Y-%m-%d"
html_theme_options = {
    "navbar_start": ["navbar-logo"], "navbar_center": ["navbar-nav"],
    "navbar_persistent": ["search-button"],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "header_links_before_dropdown": 6, "show_nav_level": 2,
    "navigation_depth": 4, "show_toc_level": 2, "use_edit_page_button": True,
    "icon_links": [
        {"name": "GitHub", "url": "https://github.com/cssr-tools/pofff", "icon": "fa-brands fa-github"},
        {"name": "Report an issue", "url": "https://github.com/cssr-tools/pofff/issues", "icon": "fa-solid fa-bug"},
    ],
}
html_context = {"github_user": "cssr-tools", "github_repo": "pofff", "github_version": "main", "doc_path": "docs/text"}
intersphinx_mapping = {"python": ("https://docs.python.org/3", None), "numpy": ("https://numpy.org/doc/stable", None)}
