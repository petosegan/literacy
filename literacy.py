"""
This script scans a Python codebase and generates missing docstrings for all functions 
using OpenAI's GPT-3.5 natural language processing model.

It searches for Python files in the specified codebase directory, 
ignoring files listed in the .gitignore file. For each file, it extracts 
functions without docstrings and generates them using the OpenAI API. 
The generated docstrings are then added to the functions and the modified 
file content is written back to the original file.

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
from display import FileStatusDisplay, Status
import ast
import sys
from typing import Tuple, Optional
from pathlib import Path

import tiktoken
import openai
import logging
from gitignore_parser import parse_gitignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set your OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "api-key")
openai.api_key = OPENAI_API_KEY

MODEL_NAME = "gpt-3.5-turbo"
TOKEN_COST = 0.002 / 1000  # dollars per token
TIMEOUT = 20  # seconds
ENCODER = tiktoken.encoding_for_model(MODEL_NAME)

# This is a WAG
COST_MULTIPLER = 1.5  # increase the cost of the query to account for the result


class TimeoutError(Exception):
    pass


def compute_cost(function_source: str) -> float:
    """Compute the cost of the query to the OpenAI API."""
    n_tokens = len(ENCODER.encode(function_source))
    return n_tokens * TOKEN_COST * COST_MULTIPLER


def generate_docstring(
    function_name: str, function_signature: str
) -> Tuple[str, float]:
    """
    Generate a docstring for a Python function using OpenAI's GPT-3 natural language processing model.

    Args:
        function_signature (str): The signature of the function for which to generate a docstring.

    Returns:
        str: The generated docstring.
        float: The cost of the query in dollars.

    Example:
        >>> generate_docstring('def add(x: int, y: int) -> int:')
        'Add two integers together and return the result.'
    """
    logger.debug("Generating docstring for %s", function_name)
    prompt = Path("prompt.txt").read_text() + function_signature
    logger.debug(prompt)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            n=1,
            temperature=0.5,
            request_timeout=TIMEOUT,
        )
    except openai.error.Timeout:
        raise TimeoutError(function_name)
    logger.debug(response)
    response_text = response.choices[0].message.content.strip()
    n_tokens = response.usage.total_tokens
    cost = n_tokens * TOKEN_COST
    logger.debug(response_text)
    sys.stdout.flush()
    return response_text, cost


def process_file(filename: str, dryrun: bool = False) -> float:
    """Process a Python file and add missing docstrings to its functions.

    Args:
        filename (str): The path to the Python file to process.

    Returns:
        float: The cost in dollars of the queries to the OpenAI API.

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
    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not ast.get_docstring(node)
    ]

    def update_function(
        function: ast.FunctionDef, content: str
    ) -> Tuple[Optional[str], Optional[str], Optional[str], float]:
        function_source = ast.get_source_segment(content, function)
        old_signature = f"def {function.name}({ast.unparse(function.args)}):"
        if dryrun:
            cost = compute_cost(function_source)
            return None, None, None, cost
        docstring, cost = generate_docstring(function.name, function_source)
        docstring = docstring.replace('"', "")
        new_signature = f'{old_signature}\n    """{docstring}"""'
        return (function.name, old_signature, new_signature, cost)

    # Display function names in yellow
    display = FileStatusDisplay(filename, [function.name for function in functions])
    display.display()
    total_cost = 0

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(update_function, function, content)
            for function in functions
        ]

        for future in as_completed(futures):
            try:
                function_name, old_signature, new_signature, cost = future.result()
            except TimeoutError as e:
                function_name = e.args[0]
                display.update(function_name, Status.FAILED)
            else:
                if old_signature and new_signature:
                    result = result.replace(old_signature, new_signature)

                display.update(function_name, Status.FINISHED)
                total_cost += cost

    display.finish()
    logger.info("File cost: $%.4f", total_cost)
    if not dryrun:
        with open(filename, "w") as file:
            file.write(result)
    return total_cost


def scan_codebase(directory: str, dryrun: bool = False) -> None:
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
    codebase_cost = 0
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".py") and not matches_gitignore(file_path):
                file_cost = process_file(file_path, dryrun=dryrun)
                codebase_cost += file_cost
    logger.info("Codebase cost: $%.4f", codebase_cost)


def find_git_root(path: str) -> Optional[str]:
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
    parser.add_argument("--dryrun", action="store_true", help="Compute costs only")
    args = parser.parse_args()
    scan_codebase(args.codebase_directory, dryrun=args.dryrun)
