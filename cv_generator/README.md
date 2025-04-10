# CV Generator

A Python tool for dynamically generating professional CVs/resumes from JSON or text files using the Awesome-CV LaTeX template.

## Features

- Generate professional-looking CVs from structured data
- Support for both JSON and text file inputs
- Customizable sections (experience, education, skills, etc.)
- Multiple CV styles through the Awesome-CV template
- Easy to update and maintain your CV

## Requirements

- Python 3.6+
- XeLaTeX (for PDF compilation)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/cv-generator.git
   cd cv-generator
   ```

2. Ensure you have XeLaTeX installed:
   - On Ubuntu/Debian: `sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-fonts-extra`
   - On macOS with Homebrew: `brew install --cask mactex`
   - On Windows: Install [MiKTeX](https://miktex.org/download)

## Usage

### Basic Usage

```bash
python cv_generator.py input_file [--output OUTPUT] [--template-dir TEMPLATE_DIR] [--compile]
```

Arguments:
- `input_file`: Path to the input file (JSON or text)
- `--output`, `-o`: Name of the output file (without extension, default: "resume")
- `--template-dir`, `-t`: Directory containing the Awesome-CV template files (default: "../build")
- `--compile`, `-c`: Compile the LaTeX file to PDF

### Example

```bash
# Generate a CV from a JSON file
python cv_generator.py sample_cv.json --compile

# Generate a CV from a text file with a custom output name
python cv_generator.py sample_cv.txt --output my_resume --compile
```

## Input File Formats

### JSON Format

The JSON format should follow this structure:

```json
{
  "FirstName": "John",
  "LastName": "Doe",
  "Position": "Software Engineer",
  "Address": "123 Main St, City, Country",
  "Mobile": "(123) 456-7890",
  "Email": "john.doe@example.com",
  "Homepage": "www.johndoe.com",
  "GitHub": "johndoe",
  "LinkedIn": "johndoe",
  "Quote": "Your favorite quote",
  
  "Summary": "A brief summary of your professional background and skills.",
  
  "Work Experience": [
    {
      "Title": "Senior Developer",
      "Company": "Tech Company",
      "Location": "City, Country",
      "Date": "Jan 2020 - Present",
      "items": [
        "Accomplishment 1",
        "Accomplishment 2"
      ]
    }
  ],
  
  "Education": [...],
  "Skills": [...],
  "Certificates": [...],
  "Honors": [...]
}
```

### Text Format

The text format uses a simple key-value syntax:

```
FirstName- "John"
LastName- "Doe"
Position- "Software Engineer"
Address- "123 Main St, City, Country"
Mobile- "(123) 456-7890"
Email- "john.doe@example.com"
Homepage- "www.johndoe.com"
GitHub- "johndoe"
LinkedIn- "johndoe"
Quote- "Your favorite quote"

Summary- "A brief summary of your professional background and skills."

Section- "Work Experience"
Title- "Senior Developer"
Company- "Tech Company"
Location- "City, Country"
Date- "Jan 2020 - Present"
- Accomplishment 1
- Accomplishment 2

Section- "Education"
Degree- "Master of Science"
Institution- "University Name"
Location- "City, Country"
Date- "2015 - 2017"
- Detail 1
- Detail 2
```

## Customization

### Adding New Sections

To add new sections to your CV, you can modify the `cv_generator.py` script:

1. Create a new method for generating the section (e.g., `generate_projects`)
2. Add the section to the `generate_cv` method
3. Update your input file to include the new section

### Changing CV Styles

The Awesome-CV template offers several color schemes:
- awesome-emerald
- awesome-skyblue
- awesome-red
- awesome-pink
- awesome-orange
- awesome-nephritis
- awesome-concrete
- awesome-darknight

To change the color scheme, modify the `\colorlet{awesome}{awesome-red}` line in the LaTeX template.

## Credits

- [Awesome-CV](https://github.com/posquit0/Awesome-CV) - LaTeX template for CVs
- [XeLaTeX](https://www.latex-project.org/help/documentation/) - LaTeX engine

## License

This project is licensed under the MIT License - see the LICENSE file for details.
