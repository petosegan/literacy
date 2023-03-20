from colorama import init, Fore, Back, Style
import time
import sys
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

init(autoreset=True)


class FileStatusDisplay:
    def __init__(self, file, functions):
        self.file = file
        self.functions = functions
        self.status = {function: "yellow" for function in functions}
        self.complete = False

    def update(self, function, status):
        self.status[function] = status
        self.clear()
        self.display()

    def display(self):
        if self.complete:
            print(Fore.GREEN + f"Processing {self.file}:" + "✓")
        else:
            print(Fore.YELLOW + f"Processing {self.file}:")
        for function in self.functions:
            if self.status[function] == "green":
                print(Fore.GREEN + f"  {function}" + "✓")
            elif self.status[function] == "yellow":
                print(Fore.YELLOW + f"  {function}")
        sys.stdout.flush()

    def clear(self):
        print("\033[A" * (len(self.functions) + 1), end="")

    def finish(self):
        self.complete = True
        self.clear()
        self.display()


def test_with_concurrency():
    functions = ["square", "cube", "add", "subtract"]
    display = FileStatusDisplay("my_file.py", functions)
    display.display()
    time.sleep(1)

    def wait_random_time(function_name):
        time.sleep(random.random())
        return function_name

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(wait_random_time, function_name)
            for function_name in functions
        ]

        for future in as_completed(futures):
            function_name = future.result()
            display.update(function_name, "green")

    display.finish()


if __name__ == "__main__":
    test_with_concurrency()
