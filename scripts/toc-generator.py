#!/bin/python3

"""
Authors: Sky (Sceleratis) (sceleratis@gmail.com)
Updated: 7/31/2024 23:05 EST
Description: This script generates a table of contents in a target Markdown file
             from Markdown files found within directories and subdirectories.
"""

import os
import re
import sys
import argparse
from urllib.parse import quote
from functools import lru_cache
from pathlib import Path
from typing import Optional, List, Dict
from os import DirEntry

# Patterns to find tags in Markdown files which change how files and directories 
# are added to the table of contents.
toc_custom_name_pattern = re.compile(r'^(?:\s*|---\s*\n.*\n---)\s*<!--.*?toc-name:\s*(.+?)(?:;|\s*)\s*-->', re.S)
toc_ignore_pattern = re.compile(r'^(?:\s*|---\s*\n.*\n---)\s*(?:<!--.*-->)?\s*<!--\s*(toc-ignore);?\s*-->', re.S)
toc_order_pattern = re.compile(r'^(?:\s*|---\s*\n.*\n---)\s*<!--.*?toc-order:\s*(.+?)(?:;|\s*)\s*-->', re.S)

def main():
    """
    Main entry point for the script.
    """
    
    # Define global variables.
    global table_file
    global root_path
    global exclude_root_directory
    global file_extension
    global primary_file_name
    global toc_marker_start
    global toc_marker_end
    global toc_ignore_directory_file

    # Define arguments.
    parser = argparse.ArgumentParser(description='Generate a table of contents for markdown files.')
    parser.add_argument('--table-file',             default='README.md',            help='Path to the markdown file containing the table of contents. (default: %(default)s)')
    parser.add_argument('--root-path',              default='.',                    help='Path to the root directory of the project. (default: %(default)s)')
    parser.add_argument('--exclude-root',           default=False,                  help='Include the root directory in the table of contents. (default: %(default)s)')
    parser.add_argument('--file-extension',         default='.md',                  help='File extension of files to include in the table of contents. (default: %(default)s)')
    parser.add_argument('--primary-file-name',      default='README.md',            help='Name of file that should be treated as the primary Markdown file for a directory where if found the directory listing will become a link to that file. (default: %(default)s)')
    parser.add_argument('--toc-start-tag',          default='<!-- TOC START -->',   help='Table of contents start tag that indicates the start of the table of contents in the target file where the table of contents will be generated. (default: %(default)s)')
    parser.add_argument('--toc-end-tag',            default='<!-- TOC END -->',     help='Table of contents end tag that indicates the start of the table of contents in the target file where the table of contents will be generated. (default: %(default)s)')
    parser.add_argument('--toc-ignore-file-name',   default='.toc-ignore',          help='Name of file that indicates a directory should be ignored. (default: %(default)s)')
    
    # Parse arguments.
    args = parser.parse_args()

    # Update the global variables from command line arguments.
    table_file = args.table_file
    root_path = args.root_path
    exclude_root_directory = args.exclude_root
    file_extension = args.file_extension
    primary_file_name = args.primary_file_name
    exclude_root_directory = args.exclude_root
    toc_marker_start = args.toc_start_tag
    toc_marker_end = args.toc_end_tag
    toc_ignore_directory_file = args.toc_ignore_file_name
    
    # Generate the table of contents.
    update_contents()

@lru_cache(maxsize=None)
def get_custom_name(file_contents: str) -> Optional[str]:
    """
    Extracts the custom name from a markdown file if it exists.

    Args:
        file_contents (str): The contents of a file.

    Returns:
        str: The custom name if it exists; otherwise, None.
    """
    match = toc_custom_name_pattern.search(file_contents)
    return match.group(1) if match else None

@lru_cache(maxsize=None)
def get_order(file_contents: str, default: int = sys.maxsize - 1) -> int:
    """
    Gets the order group of a file from the toc-order tag if it exists; otherwise, returns the default value.

    Args:
        file_contents (str): The contents of a file.
        default (int, optional): Default order value. Defaults to sys.maxsize-1.

    Returns:
        int: The file's order group if it exists; otherwise, the default value.
    """
    match = toc_order_pattern.search(file_contents)
    return sys.maxsize if match and match.group(1).lower() == "last" else int(match.group(1)) if match else default

@lru_cache(maxsize=None)
def ignore_file(file_contents: str) -> bool:
    """
    Checks if a file contains toc_ignore_pattern indicating it should be excluded from the table of contents.

    Args:
        file_contents (str): The contents of a file.

    Returns:
        bool: True if this file should be ignored; otherwise, False.
    """
    return bool(toc_ignore_pattern.search(file_contents))

def find_file(directory: str, file_name: str, case_sensitive: bool=False) -> Optional[DirEntry]:
    """
    Tries to find and return a file from the specified directory with the specified name 
    and returns None if file cannot be found.

    Args:
        directory (str): The target directory.
        file_name (str): The name of the file to find.
        case_sensitive (bool, optional): If true, search will be case sensitive. Defaults to False.

    Returns:
        Optional[DirEntry]: The file entry if found; otherwise, None.
    """
    if not case_sensitive:
        file_name = file_name.lower()
    return next((entry.name for entry in os.scandir(directory) 
        if (entry.name.lower() if not case_sensitive else entry.name) == file_name), None)

def include_directory(directory: str) -> bool:
    """
    Checks if a directory or its descendants contain any valid Markdown files
    that should be included in the table of contents.

    Args:
        directory (str): The directory to check.

    Returns:
        bool: True if the directory should be included; otherwise, False.
    """
    for root, _, files in os.walk(directory):
        if toc_ignore_directory_file in files:
            continue
        
        if any(
            not ignore_file(Path(os.path.join(root, file)).read_text(encoding='utf-8'))
            for file in files
            if os.path.splitext(file)[1].lower() == file_extension
        ):
            return True
    
    return False

def encode_path(path: str) -> str:
    """
    Encodes file paths to make them Markdown friendly so they can be used
    as table of contents links.

    Args:
        path (str): The path to encode.

    Returns:
        str: The encoded path.
    """
    return '/'.join(quote(part) for part in path.split('/'))

class TableEntry:
    """
    Represents an entry in the table of contents.

    Attributes:
        depth (int): The depth of the entry in the hierarchy.
        order (int): The order of the entry.
        line (str): The formatted line for the entry.
        children (List[TableEntry]): The child entries of this entry.
    """
    def __init__(self, depth: int, order: int, line: str, children: List['TableEntry'] = None):
        self.depth = depth
        self.order = order
        self.line = line
        self.children = children or []
    
    def __str__(self):
        return self.line

def generate_toc() -> List[TableEntry]:
    """
    Recursively scans all directories and their subdirectories for Markdown files
    and generates a table of contents based on found files their hierarchy.

    Args:
        directory (str, optional): The directory to start scanning from. Defaults to '.'.
        root_path (str, optional): The root path for relative path calculations. Defaults to '.'.

    Returns:
        List[TableEntry]: The generated table of contents entries.
    """
    toc: Dict[str, TableEntry] = {}
    
    depth_offset = 1 if exclude_root_directory else 0
    
    for root, dirs, files in os.walk(root_path):
        if exclude_root_directory and root == root_path:
            continue
        
        if not include_directory(root):
            continue
        
        depth = root[len(root_path):].count(os.sep) - depth_offset
        
        indent = '  ' * depth
        
        dir_order = sys.maxsize
        dir_entry = None

        readme_file = find_file(root, primary_file_name, case_sensitive=False)
        if readme_file:
            table_file = os.path.join(root, readme_file)

            with open(table_file, 'r', encoding='utf-8') as file:
                readme_contents = file.read()
            
            if not ignore_file(readme_contents):
                custom_name = get_custom_name(readme_contents) or os.path.basename(root)
                
                dir_order = get_order(readme_contents)
                
                relative_path = os.path.relpath(table_file, root_path).replace('\\', '/')
                encoded_path = encode_path(relative_path)

                dir_entry = TableEntry(depth, dir_order, f'{indent}- [{custom_name}]({encoded_path})')

        if not dir_entry:
            dir_entry = TableEntry(depth, dir_order, f'{indent}- {os.path.basename(root)}')

        toc[root] = dir_entry

        parent_dir = os.path.dirname(root)
        if parent_dir in toc:
            toc[parent_dir].children.append(dir_entry)
        
        for file in files:
            if file.endswith(file_extension) and file.lower() != primary_file_name:
                file_path = os.path.join(root, file)

                with open(file_path, 'r', encoding='utf-8') as f:
                    file_contents = f.read()

                if ignore_file(file_contents):
                    continue
                
                file_order = get_order(file_contents)
                
                custom_name = get_custom_name(file_contents) or os.path.splitext(file)[0]
                
                relative_path = os.path.relpath(file_path, root_path).replace('\\', '/')
                encoded_path = encode_path(relative_path)
                file_entry = TableEntry(depth + 1, file_order, f'{indent}  - [{custom_name}]({encoded_path})')
                dir_entry.children.append(file_entry) 
                
    for dir_entry in toc.values():
        dir_entry.children.sort(key=lambda x: (x.order, x.line))
    
    root_entries = [entry for entry in toc.values() if entry.depth == 0]
    root_entries.sort(key=lambda x: (x.order, x.line))

    return root_entries

def flatten_toc(entries: List[TableEntry]) -> List[str]:
    """
    Flatten the hierarchical structure of TableEntries into a list of strings.

    Args:
        entries (List[TableEntry]): The list of TableEntry objects to flatten.

    Returns:
        List[str]: A flattened list of table of contents entries as strings.
    """
    result = []
    for entry in entries:
        result.append(entry.line)
        result.extend(flatten_toc(entry.children))
    return result


def update_contents():
    """
    Updates the table of contents in the target file.
    """

    # Find the target Markdown file to update.
    target_file = find_file(root_path, table_file, case_sensitive=False)

    # Read the target file's contents.
    with open(target_file, 'r', encoding='utf-8') as readme_file:
        readme_contents = readme_file.read()

    # Find the markers that indicate the start and end of the table of contents section
    # of the target file.
    toc_start_index = readme_contents.index(toc_marker_start)
    toc_end_index = readme_contents.index(toc_marker_end)

    # Generate the new table of contents.
    toc_entries = generate_toc()
    flattened_toc = flatten_toc(toc_entries)

    # Replace the old table of contents (if any) with our newly generated one.
    new_toc = '\n'.join([toc_marker_start] + flattened_toc + [toc_marker_end])
    updated_readme = readme_contents[:toc_start_index] + new_toc + readme_contents[toc_end_index + len(toc_marker_end):]

    # Update the target file's contents to include the updated Table of Contents.
    with open(target_file, 'w', encoding='utf-8') as readme_file:
        readme_file.write(updated_readme)

    # Print a success message.
    print("Table of Contents has been updated successfully.")

if __name__ == "__main__":
    main()