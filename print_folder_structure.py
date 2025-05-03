import os
import fnmatch

# List of directories and file patterns to exclude
EXCLUDE_PATTERNS = [
    ".git",
    ".idea",
    "__pycache__",
    "*.py[cod]",
    "*$py.class",
    "*.so",
    ".Python",
    "env",
    ".venv",
    "env.bak",
    "venv.bak",
    "lib",
    "lib64",
    "parts",
    "sdist",
    "wheels",
    "pip-wheel-metadata",
    "share/python-wheels",
    "*.egg-info",
    ".installed.cfg",
    "*.egg",
    "MANIFEST",
    "*.manifest",
    "*.spec",
    "pip-log.txt",
    "pip-delete-this-directory.txt",
    "htmlcov",
    ".tox",
    ".nox",
    ".coverage",
    ".coverage.*",
    ".cache",
    "nosetests.xml",
    "coverage.xml",
    "*.cover",
    "*.py,cover",
    ".hypothesis",
    ".pytest_cache",
    ".ipynb_checkpoints",
    ".env",
    ".envrc",
    "ENV",
    "logs",
    "*.log",
    "db.sqlite3",
    "resources/secrets.toml",
]


def should_exclude(item):
    for pattern in EXCLUDE_PATTERNS:
        if fnmatch.fnmatch(item, pattern):
            return True
    return False


def print_directory_tree(root_dir, padding=""):
    print(padding[:-1] + "+--" + os.path.basename(root_dir) + "/")
    padding = padding + "   "
    files = []
    dirs = []

    # Separate files and directories
    for item in os.listdir(root_dir):
        if should_exclude(item):
            continue
        if os.path.isdir(os.path.join(root_dir, item)):
            dirs.append(item)
        else:
            files.append(item)

    # Print directories first
    for directory in dirs:
        print_directory_tree(os.path.join(root_dir, directory), padding + "|  ")

    # Print files
    for file in files:
        print(padding + "|-- " + file)


if __name__ == "__main__":
    # Replace '.' with the path to your project root if running from a different location
    project_root = "."
    print_directory_tree(project_root)
