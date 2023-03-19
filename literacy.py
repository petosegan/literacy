"""
Scan a codebase and add use openai to add docstrings for all functions.
"""
import os
import subprocess

import ast
import sys

import sys

subprocess.run(["pip", "install", "gitignore-parser"])

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
    prompt = f"Write a docstring for the Python function with the following signature:\n{function_signature}"
    logger.debug(prompt)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100,
        n=1,
        temperature=0.5,
    )
    logger.debug(response)
    response_text = response.choices[0].content.strip()

    # response_text = """foo"""
    logger.debug(response_text)
    sys.stdout.flush()
    return response_text


def process_file(filename):
    logger.debug("Processing %s", filename)
    with open(filename, "r") as file:
        content = file.read()

    tree = ast.parse(content)
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]

    for function in functions:
        if not any(
            isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Str)
            for stmt in function.body
        ):
            function_name = function.name
            function_signature = f"def {function_name}({ast.unparse(function.args)}):"
            docstring = generate_docstring(function_signature)
            content = content.replace(
                content=content.replace(
                    function_signature, f'{function_signature}\n    """{docstring}"""'
                )
            )

    # with open(filename, "w") as file:
    #     file.write(content)


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


# def scan_codebase(path):
#     git_root = find_git_root(path)
#     gitignore_path = os.path.join(git_root, ".gitignore")
#     gitignore = parse_gitignore(gitignore_path)
#     for dirpath, dirnames, filenames in os.walk(path):
#         # remove directories that match the patterns in the .gitignore file
#         dirnames[:] = [d for d in dirnames if not gitignore(os.path.join(dirpath, d))]
#         # scan files that are not ignored by .gitignore
#         for filename in filenames:
#             if not
#             f for f in filenames if not gitignore(os.path.join(dirpath, f))
#         ]:
#             process_file(os.path.join(dirpath, filename))


if __name__ == "__main__":
    codebase_directory = "/home/will/code/wolverine"
    scan_codebase(codebase_directory)
