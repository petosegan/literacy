"""
This script scans a Python codebase and generates missing docstrings for all functions using OpenAI's GPT-3.5 natural language processing model.

It searches for Python files in the specified codebase directory, ignoring files listed in the .gitignore file. For each file, it extracts functions without docstrings and generates them using the OpenAI API. The generated docstrings are then added to the functions and the modified file content is written back to the original file.

Dependencies:
- openai: The OpenAI Python library (https://github.com/openai/openai).
- gitignore_parser: A Python library to parse .gitignore files (https://github.com/sinkovit/gitignore_parser).

Usage:
$ python generate_docstrings.py codebase_directory
"""

import os
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import ast
import sys

from pathlib import Path

import openai
import logging
from gitignore_parser import parse_gitignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set your OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "api-key")
openai.api_key = OPENAI_API_KEY


def generate_docstring(function_name: str, function_signature: str):
    """
    Generate a docstring for a Python function using OpenAI's GPT-3 natural language processing model.

    Args:
        function_signature (str): The signature of the function for which to generate a docstring.

    Returns:
        str: The generated docstring.

    Example:
        >>> generate_docstring('def add(x: int, y: int) -> int:')
        'Add two integers together and return the result.'
    """
    logger.info("Generating docstring for %s", function_name)
    prompt = Path("prompt.txt").read_text() + function_signature
    logger.debug(prompt)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        n=1,
        temperature=0.5,
    )
    logger.debug(response)
    response_text = response.choices[0].message.content.strip()

    # response_text = """foo"""
    logger.debug(response_text)
    sys.stdout.flush()
    return response_text


def process_file(filename):
    """Process a Python file and add missing docstrings to its functions.

    Args:
        filename (str): The path to the Python file to process.

    Returns:
        None

    The function reads the contents of the file, parses it with the `ast` module,
    and extracts all the function definitions that lack a docstring. It then generates
    a docstring for each of these functions by analyzing their source code, and adds
    the docstring to the function definition. Finally, the modified file content is
    written back to the original file.

    Example:
        Given the following Python file:

        ```
        def square(x):
            return x ** 2

        def cube(x):

            Compute the cube of a number.

            Args:
                x (int): The number to compute the cube of.

            Returns:
                int: The cube of the input number.

            return x ** 3
        ```

        Calling `process_file(my_file.py)` will modify the file to:

        ```
        def square(x):

            Compute the square of a number.

            Args:
                x (int): The number to compute the square of.

            Returns:
                int: The square of the input number.

            return x ** 2

        def cube(x):

            Compute the cube of a number.

            Args:
                x (int): The number to compute the cube of.

            Returns:
                int: The cube of the input number.

            return x ** 3
        ```"""
    logger.debug("Processing %s", filename)
    with open(filename, "r") as file:
        content = file.read()

    result = str(content)
    tree = ast.parse(content)
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]

    def update_function(function, content):
        if not ast.get_docstring(function):
            # logger.debug(ast.get_source_segment(content, function))
            function_source = ast.get_source_segment(content, function)
            function_signature = f"def {function.name}({ast.unparse(function.args)}):"
            docstring = generate_docstring(function.name, function_source).replace(
                '"', ""
            )
            return function_signature, f'{function_signature}\n    """{docstring}"""'
        return None, None

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(update_function, function, content)
            for function in functions
        ]

        for future in as_completed(futures):
            function_signature, docstring = future.result()
            if function_signature and docstring:
                result = result.replace(function_signature, docstring)

    with open(filename, "w") as file:
        file.write(result)


def scan_codebase(directory):
    """
    Scan a directory for Python files and process them if they are not ignored by Git.

    Args:
        directory (str): The path to the directory to scan.

    Returns:
        None."""
    git_root = find_git_root(directory)
    gitignore_path = os.path.join(git_root, ".gitignore")
    logger.debug("GITIGNORE: %s", gitignore_path)
    matches_gitignore = parse_gitignore(gitignore_path)
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".py") and not matches_gitignore(file_path):
                process_file(file_path)


def find_git_root(path):
    """
    Find the root directory of a Git repository given a path.

    Args:
        path (str): The starting directory to search for the Git root.

    Returns:
        str: The absolute path of the Git root directory if found, None otherwise.

    Example:
        >>> find_git_root('/home/user/project/subdir')
        '/home/user/project'
    """
    try:
        output = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], cwd=path
        )
        return output.strip().decode("utf-8")
    except subprocess.CalledProcessError:
        parent_dir = os.path.abspath(os.path.join(path, os.pardir))
        if parent_dir == path:
            return None
        return find_git_root(parent_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("codebase_directory", help="The directory to scan")
    args = parser.parse_args()
    scan_codebase(args.codebase_directory)
