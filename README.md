Literacy
===
Literacy is a Python script that scans a codebase and uses OpenAI to generate and add docstrings to Python functions without existing docstrings.

### Features
* Scans a codebase for Python files
* Identifies functions without docstrings
* Generates docstrings using OpenAI's GPT-3.5-turbo
* Adds the generated docstrings to the functions
* Ignores files specified in the .gitignore file

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

### Contributing
Feel free to open issues or submit pull requests for bug fixes or feature enhancements.

### License
This project is licensed under the MIT License.