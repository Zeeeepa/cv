# CV Generator

A powerful tool for generating professional CVs from JSON or text input files using the Awesome-CV LaTeX template.

## Features

- Generate professional CVs from JSON or text input files
- Customize sections (experience, education, skills, etc.)
- Choose from multiple color schemes
- Generate PDFs with XeLaTeX
- Web UI for easy CV creation and style preview

## Components

### Command-line CV Generator

The `cv_generator.py` script takes a JSON or structured text file containing CV data and generates a LaTeX CV using the Awesome-CV template.

#### Usage

```bash
python cv_generator.py sample_cv.json --output my_resume --compile
```

or with a text file:

```bash
python cv_generator.py sample_cv.txt --output my_resume --compile
```

### Style Generator

The `style_generator.py` script demonstrates how to generate CVs with different color schemes using the Awesome-CV template.

#### Usage

```bash
python style_generator.py sample_cv.json --output-dir styled_output --styles emerald skyblue red
```

### Web UI

The web interface allows you to:
- Create and edit CVs with a user-friendly form
- Preview different CV styles in real-time
- Generate and download CVs in PDF format
- Import and export CV data in JSON format

#### Usage

```bash
cd web
python app.py
```

Then open your browser and go to `http://localhost:5000`.

## Available Styles

- Emerald (`#00A388`)
- Skyblue (`#0395DE`)
- Red (`#DC3522`)
- Pink (`#EF4089`)
- Orange (`#FF6138`)
- Nephritis (`#27AE60`)
- Concrete (`#95A5A6`)
- Darknight (`#131A28`)

## Requirements

- Python 3.6+
- XeLaTeX (for PDF generation)
- Flask (for web UI)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/cv-generator.git
   cd cv-generator
   ```

2. Install the required dependencies:
   ```
   pip install flask
   ```

3. Make sure XeLaTeX is installed on your system. On Ubuntu/Debian:
   ```
   sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-fonts-extra
   ```

## Input Format

### JSON Format

See `sample_cv.json` for an example of the JSON format.

### Text Format

The text file should follow a specific format:
```
FirstName- "John"
LastName- "Doe"
Position- "Software Engineer"
...
Section- "Work Experience"
Title- "Senior Developer"
Company- "Tech Corp"
...
```

## Credits

This project uses the [Awesome-CV](https://github.com/posquit0/Awesome-CV) LaTeX template.
