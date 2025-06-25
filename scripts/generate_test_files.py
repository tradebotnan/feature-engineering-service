import os
import shutil


def add_comment_to_files_in_folder(folder: str, root_folder: str):
    """
    Adds the file name and relative path (including parent folder like app/ or tests/)
    as the first line (commented) to all .py files in the given folder, except for '__init__.py'.
    Skips if the comment already exists.

    Args:
        folder (str): Path to the folder to process.
        root_folder (str): Path to the project root folder.
    """
    for root, _, files in os.walk(folder):
        for file_name in files:
            if file_name.endswith(".py") and file_name != "__init__.py":
                file_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(file_path, root_folder)
                with open(file_path, 'r+', encoding='utf-8') as file:
                    content = file.readlines()
                    if not content or not content[0].startswith(f"# Source file: {relative_path}"):
                        file.seek(0, 0)
                        file.write(f"# Source file: {relative_path}\n")
                        file.writelines(content)


def create_test_files(app_folder: str, test_folder: str, root_folder: str):
    """
    Creates test files in the test folder based on the app folder structure.
    Files are prefixed with 'test_' except for '__init__.py', and the source file path
    is added as a comment in the first line of each .py file if not already present.

    Args:
        app_folder (str): Path to the app folder.
        test_folder (str): Path to the test folder to be created.
        root_folder (str): Path to the project root folder.
    """
    for root, dirs, files in os.walk(app_folder):
        # Create corresponding directory in the test folder
        relative_path = os.path.relpath(root, app_folder)
        test_dir = os.path.join(test_folder, relative_path)
        os.makedirs(test_dir, exist_ok=True)

        for file in files:
            source_file_path = os.path.join(root, file)
            relative_source_path = os.path.relpath(source_file_path, root_folder)
            if file == "__init__.py":
                # Copy __init__.py without renaming
                shutil.copy(source_file_path, os.path.join(test_dir, file))
            elif file.endswith(".py"):
                # Prefix other .py files with 'test_' and add source file comment if not already present
                test_file_name = f"test_{file}"
                test_file_path = os.path.join(test_dir, test_file_name)
                with open(test_file_path, 'w', encoding='utf-8') as test_file:
                    test_file.write(f"# Source file: {relative_source_path}\n")
            else:
                # Skip non-Python files
                continue


# Example usage
if __name__ == "__main__":
    root_folder = os.getcwd()
    app_folder = os.path.join(root_folder, "app")
    test_folder = os.path.join(root_folder, "tests")

    # Apply first-line logic to all .py files in app and tests
    add_comment_to_files_in_folder(app_folder, root_folder)
    add_comment_to_files_in_folder(test_folder, root_folder)

    # Create test files
    create_test_files(app_folder, test_folder, root_folder)