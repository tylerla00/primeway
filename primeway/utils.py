import os
import zipfile
import fnmatch
import re


def zip_directory(folder_path, zip_file_path, ignore_patterns=None):
    if ignore_patterns is None:
        ignore_patterns = []

    # Get the absolute path of the zip file to ensure it won't be included
    absolute_zip_file_path = os.path.abspath(zip_file_path)

    def ignore_file(file_path):
        # Check for the patterns and the zip file path
        if file_path == absolute_zip_file_path:
            return True
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
                return True
        return False

    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            rel_root = os.path.relpath(root, start=folder_path)

            if ignore_file(rel_root if rel_root != "." else os.path.basename(folder_path)):
                dirs[:] = []  # Do not descend into this directory
                continue

            # Remove ignored directories from traversal
            dirs[:] = [d for d in dirs if not ignore_file(os.path.join(root, d))]

            for file in files:
                file_path = os.path.join(root, file)
                if ignore_file(file_path):
                    continue
                zipf.write(file_path, os.path.relpath(file_path, start=folder_path))

