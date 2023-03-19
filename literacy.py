"""
Scan a codebase and add use openai to add docstrings for all functions.
"""
import os
import subprocess

import ast
import sys


import subprocess

import openai
import logging
from gitignore_parser import parse_gitignore

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set your OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "api-key")
openai.api_key = OPENAI_API_KEY


def generate_docstring(function_signature):
    prompt = f"""I want you to write a docstring for a Python function.
        If the function is very simple, a one-line docstring is fine.
        If the function is not very simple, please include lines for the arguments and return values.
        If the function is complicated, please include examples of inputs and outputs.
        Limit the length of lines to 80 characters or less.
        Please return just the docstring, surrounded by triple quotes.
        Here is the code for the function:
        {function_signature}"""
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
    logger.debug("Processing %s", filename)
    with open(filename, "r") as file:
        content = file.read()

    result = str(content)
    tree = ast.parse(content)
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]

    for function in functions:
        if not ast.get_docstring(function):
            # logger.debug(ast.get_source_segment(content, function))
            function_source = ast.get_source_segment(content, function)
            function_signature = f"def {function.name}({ast.unparse(function.args)}):"
            docstring = generate_docstring(function_source).replace('"', "")
            result = result.replace(
                function_signature, f'{function_signature}\n    """{docstring}"""'
            )

    with open(filename, "w") as file:
        file.write(result)


def scan_codebase(directory):
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
    codebase_directory = "/home/will/code/wolverine"
    scan_codebase(codebase_directory)
