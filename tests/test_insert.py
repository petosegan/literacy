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


if __name__ == "__main__":
    unittest.main()
