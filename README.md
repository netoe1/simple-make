# Simple Make (.bat Generator)

**Simple Make** is a lightweight, efficient Python tool designed to parse `Makefile` files and convert them into executable Windows Batch scripts (`.bat`).

The goal of this project is to streamline the execution of automated tasks defined in Makefiles directly on Windows environments, without needing to install native `make`.

---

## Project Structure

```text
simple-make/
│
├── class/
│   ├── BatGenerator.py     # Class responsible for generating the .bat file
│   └── MakefileParser.py   # Class responsible for parsing variables and targets from the Makefile
│
├── simple-make.py          # Main execution script
├── Makefile                # Default input Makefile (optional)
├── simple-make.bat         # Generated output script (default)
└── README.md               # Project documentation
```

---

## How to Run

### Prerequisites
* **Python 3.10+** installed on your system.

---

### Default Execution

By default, the script looks for a file named `Makefile` in the current working directory and outputs `simple-make.bat`.

```bash
python simple-make.py
```

---

### Custom Execution

You can supply custom file paths for both the input Makefile and output Batch script via command-line arguments:

```bash
python simple-make.py <path_to_makefile> <path_to_output_bat>
```

**Example:**
```bash
python simple-make.py MyCommands.make output.bat
```

---

## How It Works Under the Hood

1. **`MakefileParser`**: Reads the specified `Makefile`, extracts global variables, and maps all *targets* along with their associated command lists.
2. **`BatGenerator`**: Receives the parsed data and formats it into valid **Windows Batch Script (`.bat`)** syntax.
3. **Output**: Saves the final `.bat` file and lists all detected *targets* in the terminal.

---

## License

This project is licensed under a customized [LICENSE](LICENSE) with specific copyright and royalty clauses.  
By using, modifying, or redistributing this code, you **MANDATORILY** agree to the license terms and remain subject to legal enforcement in case of non-compliance.