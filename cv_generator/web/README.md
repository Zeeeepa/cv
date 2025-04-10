# CV Generator Web UI

A web interface for the CV Generator that allows users to:
- Create and edit CVs with a user-friendly form
- Preview different CV styles in real-time
- Generate and download CVs in PDF format
- Import and export CV data in JSON format

## Features

- **Dynamic Form Builder**: Add and remove sections for work experience, education, skills, certificates, and honors
- **Style Preview**: Choose from 8 different color schemes and see a live preview
- **PDF Generation**: Generate professional-looking CVs using the Awesome-CV LaTeX template
- **Import/Export**: Save your CV data as JSON and load it later

## Installation

1. Make sure you have the required dependencies:
   - Python 3.6+
   - Flask
   - XeLaTeX (for PDF generation)

2. Install the Python dependencies:
   ```
   pip install flask
   ```

3. Make sure XeLaTeX is installed on your system. On Ubuntu/Debian:
   ```
   sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-fonts-extra
   ```

## Usage

1. Navigate to the web directory:
   ```
   cd cv_generator/web
   ```

2. Run the Flask application:
   ```
   python app.py
   ```

3. Open your browser and go to:
   ```
   http://localhost:5000
   ```

## How It Works

1. **Form Input**: Fill out the form with your CV information
2. **Style Selection**: Choose a color scheme from the sidebar
3. **Generate CV**: Click the "Generate CV" button to create your CV
4. **Preview**: View the generated PDF in the preview panel
5. **Download**: Click "Download CV" to save the PDF to your computer

## Available Styles

- Emerald (`#00A388`)
- Skyblue (`#0395DE`)
- Red (`#DC3522`)
- Pink (`#EF4089`)
- Orange (`#FF6138`)
- Nephritis (`#27AE60`)
- Concrete (`#95A5A6`)
- Darknight (`#131A28`)

## File Structure

- `app.py`: Flask application
- `templates/`: HTML templates
  - `index.html`: Main page with form and style preview
  - `preview.html`: Preview page for generated CVs
- `static/`: Static assets
  - `css/styles.css`: CSS for the web UI
  - `js/main.js`: JavaScript for the web UI
  - `previews/`: Generated PDF previews
- `uploads/`: Uploaded files and temporary data
- `output/`: Generated LaTeX and PDF files
