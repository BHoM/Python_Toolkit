from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES_DIR = ROOT / "src"

project = "BH"
extensions = [
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autoapi_type = "python"
autoapi_dirs = [
    str(package)
    for package in sorted(PACKAGES_DIR.iterdir())
    if package.is_dir()
]
autoapi_keep_files = True
autoapi_python_use_implicit_namespaces = True
autoapi_add_toctree_entry = True
autoapi_member_order = "bysource"
autoapi_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
]
autoapi_python_class_content = "both"
viewcode_follow_imported_members = False

html_theme = "furo"

exclude_patterns = [
    "_build",
    "generated",
    "Thumbs.db",
    ".DS_Store",
]
