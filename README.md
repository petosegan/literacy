Literacy
===
Literacy is a Python script that scans a codebase and uses OpenAI to generate and add docstrings to Python functions without existing docstrings.

### Features
* Scans a codebase for Python files
* Identifies functions without docstrings
* Generates docstrings using OpenAI's GPT-3.5-turbo
* Adds the generated docstrings to the functions
* Ignores files specified in the .gitignore file

### Example
Literacy generated this docstring for its own core function:
```python
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

        
        def square(x):
            return x ** 2

        def cube(x):

            Compute the cube of a number.

            Args:
                x (int): The number to compute the cube of.

            Returns:
                int: The cube of the input number.

            return x ** 3
        

        Calling `process_file(my_file.py)` will modify the file to:

        
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
        """
```
### Requirements
* Python 3.7 or higher
* openai package
* gitignore_parser package

### Installation
1. Clone the repository or download the script file.

2. Install the required packages:
```bash
pip install -r requirements
```
2. Set the OPENAI_API_KEY environment variable to your OpenAI API key.
```bash
export OPENAI_API_KEY="your_openai_api_key"
```
### Usage
Run the script with the codebase directory as the argument:

```bash
python literacy.py /path/to/your/codebase
```

Replace /path/to/your/codebase with the path to the directory containing your Python codebase.

You can also do a dry run to estimate the cost of documenting your codebase without running any OpenAI queries. The cost is only an estimate because it will depend on the size of the docstrings that are returned by the API.
```bash
python literacy.py /path/to/your/codebase --dryrun
```

### ToDo
* Extend to module, class, and method docstrings
* Add a GIF of script in action
### Contributing
Feel free to open issues or submit pull requests for bug fixes or feature enhancements.

### License
This project is licensed under the MIT License.