# Interactive Translation Tool

A simple command-line tool for translating between Chinese and English. The tool automatically detects whether your input is in Chinese or English and translates to the opposite language.

## Features

- Interactive REPL-style interface
- Auto-detection of Chinese vs English text
- Bidirectional translation (Chinese <-> English)
- Runs continuously until you exit
- Simple and easy to use

## Installation

### Local Development Installation

1. Clone or navigate to the project directory:
```bash
cd /path/to/translate
```

2. Install the package using uv:
```bash
uv pip install -e .
```

This will install the `translate` command in editable mode.

### Installing on Another Machine

There are several ways to install this tool on a different machine:

#### Option 1: Copy Project Directory
Copy the entire project folder to the new machine, then:
```bash
cd /path/to/translate
uv pip install -e .
```

#### Option 2: Install from Git Repository (Recommended)
If this project is hosted on Git (GitHub, GitLab, etc.):
```bash
uv pip install git+https://github.com/yourusername/translate.git
```

Or clone and install:
```bash
git clone https://github.com/yourusername/translate.git
cd translate
uv pip install -e .
```

#### Option 3: Global Installation with UV Tool
Install globally to use from anywhere without activating a virtual environment:
```bash
# From local directory
uv tool install /path/to/translate

# Or from Git
uv tool install git+https://github.com/yourusername/translate.git

# Then run from anywhere
translate
```

#### Option 4: Build and Distribute Package
Build a distributable package:
```bash
# On your machine
uv build
```

This creates `dist/translate-0.1.0-py3-none-any.whl`. Share this file and install on other machines:
```bash
# On the new machine
uv pip install /path/to/translate-0.1.0-py3-none-any.whl
```

## Usage

There are three ways to run the tool:

### Option 1: Using uv run (Recommended)
```bash
uv run translate
```

### Option 2: Activate virtual environment first
```bash
source .venv/bin/activate
translate
```

### Option 3: Run directly from venv
```bash
.venv/bin/translate
```

### Example Session

```
$ uv run translate
Interactive Translation Tool (Chinese <-> English)
Type 'exit' or 'quit' to stop, or press Ctrl+C

Enter word to translate: hello
`}

Enter word to translate: L
world

Enter word to translate: how are you
`}

Enter word to translate: �}
I'm fine

Enter word to translate: exit
Goodbye!
```

## Exiting the Tool

You can exit the tool in three ways:
- Type `exit` or `quit` or `q`
- Press `Ctrl+C`
- Press `Ctrl+D` (EOF)

## Requirements

- Python >= 3.12
- deep-translator >= 1.11.4

## How It Works

The tool uses the `deep-translator` library with Google Translate to perform translations. It automatically:
1. Detects if your input contains Chinese characters
2. If Chinese is detected, translates to English
3. If no Chinese is detected, translates to Chinese
4. Displays the result immediately

## Development

To modify the code:
1. Edit files in `src/translate/`
2. The package is installed in editable mode, so changes take effect immediately
3. Main logic is in `src/translate/main.py`

## License

MIT
