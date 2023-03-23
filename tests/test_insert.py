import unittest
import os
from pathlib import Path
import tempfile

from literacy.literacy import insert_docstrings


def create_temp_file_with_content(content: str) -> Path:
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    with open(temp_file.name, "w") as f:
        f.write(content)
    return Path(temp_file.name)


class TestInsertDocstrings(unittest.TestCase):
    def test_insert_docstrings(self):
        source_code = """def function1(arg1, arg2):
    return arg1 + arg2

def function2(arg1, arg2):
    return arg1 * arg2
"""
        expected_output = '''def function1(arg1, arg2):
    """This is the docstring for function1."""
    return arg1 + arg2

def function2(arg1, arg2):
    """This is the docstring for function2."""
    return arg1 * arg2
'''

        docstring_map = {
            "function1": "This is the docstring for function1.",
            "function2": "This is the docstring for function2.",
        }

        temp_file_path = create_temp_file_with_content(source_code)

        insert_docstrings(temp_file_path, docstring_map)

        with open(temp_file_path, "r") as f:
            modified_content = f.read()

        print(modified_content)
        self.assertEqual(modified_content, expected_output)

        # Clean up the temporary file
        os.remove(temp_file_path)


class TestInsertDocstringsWithTypeHints(unittest.TestCase):
    def test_insert_docstrings_with_type_hints(self):
        source_code = """def function1(arg1: int, arg2: int) -> int:
    return arg1 + arg2

def function2(arg1: str, arg2: List[str]) -> List[str]:
    return [arg1] + arg2
"""
        expected_output = '''def function1(arg1: int, arg2: int) -> int:
    """This is the docstring for function1."""
    return arg1 + arg2

def function2(arg1: str, arg2: List[str]) -> List[str]:
    """This is the docstring for function2."""
    return [arg1] + arg2
'''

        docstring_map = {
            "function1": "This is the docstring for function1.",
            "function2": "This is the docstring for function2.",
        }

        temp_file_path = create_temp_file_with_content(source_code)

        insert_docstrings(temp_file_path, docstring_map)

        with open(temp_file_path, "r") as f:
            modified_content = f.read()

        print(modified_content)
        self.assertEqual(modified_content, expected_output)

        # Clean up the temporary file
        os.remove(temp_file_path)


class TestInsertDocstringsWithDefaults(unittest.TestCase):
    def test_insert_docstrings_with_type_hints(self):
        source_code = """def send_error_to_model(file_path, args, error_message, model: str = "gpt-4"):
    with open(file_path, "r") as f:
        file_lines = f.readlines()

    file_with_lines = []
    for i, line in enumerate(file_lines):
        file_with_lines.append(str(i + 1) + ": " + line)
    file_with_lines = "".join(file_with_lines)
"""
        expected_output = '''def send_error_to_model(file_path, args, error_message, model: str = "gpt-4"):
    """This is the docstring for send_error_to_model."""
    with open(file_path, "r") as f:
        file_lines = f.readlines()

    file_with_lines = []
    for i, line in enumerate(file_lines):
        file_with_lines.append(str(i + 1) + ": " + line)
    file_with_lines = "".join(file_with_lines)
'''

        docstring_map = {
            "send_error_to_model": "This is the docstring for send_error_to_model.",
        }

        temp_file_path = create_temp_file_with_content(source_code)

        insert_docstrings(temp_file_path, docstring_map)

        with open(temp_file_path, "r") as f:
            modified_content = f.read()

        print(modified_content)
        self.assertEqual(modified_content, expected_output)

        # Clean up the temporary file
        os.remove(temp_file_path)


if __name__ == "__main__":
    unittest.main()
