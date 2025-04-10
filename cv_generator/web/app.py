#!/usr/bin/env python3
"""
CV Generator Web UI - A web interface for generating CVs with different styles.

This application provides a web interface for the CV Generator, allowing users to:
1. Input CV data in JSON or text format
2. Preview different CV styles
3. Generate and download CVs in PDF format
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path to import cv_generator
sys.path.append(str(Path(__file__).parent.parent))

from flask import Flask, render_template, request, jsonify, send_file, url_for, redirect
from werkzeug.utils import secure_filename
from cv_generator import CVGenerator
from style_generator import generate_styled_cv

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Configure upload folder
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure output folder
OUTPUT_FOLDER = Path(__file__).parent / 'output'
OUTPUT_FOLDER.mkdir(exist_ok=True)

# Configure preview folder
PREVIEW_FOLDER = Path(__file__).parent / 'static/previews'
PREVIEW_FOLDER.mkdir(exist_ok=True)

# Available styles
STYLES = [
    "emerald", 
    "skyblue", 
    "red", 
    "pink", 
    "orange", 
    "nephritis", 
    "concrete", 
    "darknight"
]

# Style colors (matching the awesome-cv.cls definitions)
STYLE_COLORS = {
    "emerald": "#00A388",
    "skyblue": "#0395DE",
    "red": "#DC3522",
    "pink": "#EF4089",
    "orange": "#FF6138",
    "nephritis": "#27AE60",
    "concrete": "#95A5A6",
    "darknight": "#131A28"
}

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', styles=STYLES, style_colors=STYLE_COLORS)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filename = secure_filename(file.filename)
    file_path = app.config['UPLOAD_FOLDER'] / filename
    file.save(file_path)
    
    return jsonify({'success': True, 'filename': filename})

@app.route('/generate', methods=['POST'])
def generate_cv():
    """Generate CV from form data."""
    try:
        # Get form data
        data = {}
        
        # Personal information
        data['FirstName'] = request.form.get('firstName', '')
        data['LastName'] = request.form.get('lastName', '')
        data['Position'] = request.form.get('position', '')
        data['Address'] = request.form.get('address', '')
        data['Mobile'] = request.form.get('mobile', '')
        data['Email'] = request.form.get('email', '')
        data['Homepage'] = request.form.get('homepage', '')
        data['GitHub'] = request.form.get('github', '')
        data['LinkedIn'] = request.form.get('linkedin', '')
        data['Quote'] = request.form.get('quote', '')
        
        # Summary
        data['Summary'] = request.form.get('summary', '')
        
        # Work Experience
        work_experience = []
        work_titles = request.form.getlist('work_title[]')
        work_companies = request.form.getlist('work_company[]')
        work_locations = request.form.getlist('work_location[]')
        work_dates = request.form.getlist('work_date[]')
        work_descriptions = request.form.getlist('work_description[]')
        
        for i in range(len(work_titles)):
            if work_titles[i]:
                job = {
                    'Title': work_titles[i],
                    'Company': work_companies[i] if i < len(work_companies) else '',
                    'Location': work_locations[i] if i < len(work_locations) else '',
                    'Date': work_dates[i] if i < len(work_dates) else '',
                    'items': [item.strip() for item in work_descriptions[i].split('\n') if item.strip()] if i < len(work_descriptions) else []
                }
                work_experience.append(job)
        
        data['Work Experience'] = work_experience
        
        # Education
        education = []
        edu_degrees = request.form.getlist('edu_degree[]')
        edu_institutions = request.form.getlist('edu_institution[]')
        edu_locations = request.form.getlist('edu_location[]')
        edu_dates = request.form.getlist('edu_date[]')
        edu_descriptions = request.form.getlist('edu_description[]')
        
        for i in range(len(edu_degrees)):
            if edu_degrees[i]:
                edu = {
                    'Degree': edu_degrees[i],
                    'Institution': edu_institutions[i] if i < len(edu_institutions) else '',
                    'Location': edu_locations[i] if i < len(edu_locations) else '',
                    'Date': edu_dates[i] if i < len(edu_dates) else '',
                    'items': [item.strip() for item in edu_descriptions[i].split('\n') if item.strip()] if i < len(edu_descriptions) else []
                }
                education.append(edu)
        
        data['Education'] = education
        
        # Skills
        skills = []
        skill_categories = request.form.getlist('skill_category[]')
        skill_lists = request.form.getlist('skill_list[]')
        
        for i in range(len(skill_categories)):
            if skill_categories[i]:
                skill = {
                    'Category': skill_categories[i],
                    'Skills': skill_lists[i] if i < len(skill_lists) else ''
                }
                skills.append(skill)
        
        data['Skills'] = skills
        
        # Certificates
        certificates = []
        cert_names = request.form.getlist('cert_name[]')
        cert_issuers = request.form.getlist('cert_issuer[]')
        cert_locations = request.form.getlist('cert_location[]')
        cert_dates = request.form.getlist('cert_date[]')
        cert_descriptions = request.form.getlist('cert_description[]')
        
        for i in range(len(cert_names)):
            if cert_names[i]:
                cert = {
                    'Name': cert_names[i],
                    'Issuer': cert_issuers[i] if i < len(cert_issuers) else '',
                    'Location': cert_locations[i] if i < len(cert_locations) else '',
                    'Date': cert_dates[i] if i < len(cert_dates) else '',
                    'items': [item.strip() for item in cert_descriptions[i].split('\n') if item.strip()] if i < len(cert_descriptions) else []
                }
                certificates.append(cert)
        
        data['Certificates'] = certificates
        
        # Honors
        honors = []
        honor_names = request.form.getlist('honor_name[]')
        honor_issuers = request.form.getlist('honor_issuer[]')
        honor_locations = request.form.getlist('honor_location[]')
        honor_dates = request.form.getlist('honor_date[]')
        
        for i in range(len(honor_names)):
            if honor_names[i]:
                honor = {
                    'Name': honor_names[i],
                    'Issuer': honor_issuers[i] if i < len(honor_issuers) else '',
                    'Location': honor_locations[i] if i < len(honor_locations) else '',
                    'Date': honor_dates[i] if i < len(honor_dates) else ''
                }
                honors.append(honor)
        
        data['Honors'] = honors
        
        # Save data to JSON file
        json_file = app.config['UPLOAD_FOLDER'] / 'temp_cv.json'
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Get selected style
        style = request.form.get('style', 'red')
        
        # Generate CV
        template_dir = Path(__file__).parent.parent.parent / 'build'
        generator = CVGenerator(template_dir=str(template_dir))
        latex_file = generator.generate_cv(data, output_filename='resume')
        
        try:
            pdf_file = generator.compile_latex(latex_file)
            
            # Copy the PDF to the preview folder with a unique name
            preview_pdf = PREVIEW_FOLDER / f'resume_{style}.pdf'
            shutil.copy(pdf_file, preview_pdf)
            
            # Return the preview URL
            preview_url = url_for('static', filename=f'previews/resume_{style}.pdf')
            return jsonify({'success': True, 'preview_url': preview_url})
        
        except FileNotFoundError as e:
            return jsonify({'error': str(e)}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_all_styles', methods=['POST'])
def generate_all_styles():
    """Generate CV in all available styles."""
    try:
        # For simplicity, we'll use the JSON file approach
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = app.config['UPLOAD_FOLDER'] / filename
                file.save(file_path)
                
                # Generate CVs with different styles
                styled_output_dir = OUTPUT_FOLDER / 'styled'
                styled_output_dir.mkdir(exist_ok=True)
                
                generate_styled_cv(str(file_path), str(styled_output_dir), STYLES)
                
                # Copy PDFs to preview folder
                preview_urls = {}
                for style in STYLES:
                    style_pdf = styled_output_dir / style / f'{style}_resume.pdf'
                    if style_pdf.exists():
                        preview_pdf = PREVIEW_FOLDER / f'resume_{style}.pdf'
                        shutil.copy(style_pdf, preview_pdf)
                        preview_urls[style] = url_for('static', filename=f'previews/resume_{style}.pdf')
                
                return jsonify({'success': True, 'preview_urls': preview_urls})
        
        return jsonify({'error': 'No file provided'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/preview/<style>')
def preview(style):
    """Preview a CV with a specific style."""
    if style not in STYLES:
        return redirect(url_for('index'))
    
    preview_pdf = PREVIEW_FOLDER / f'resume_{style}.pdf'
    if not preview_pdf.exists():
        return redirect(url_for('index'))
    
    return render_template('preview.html', 
                          style=style, 
                          pdf_url=url_for('static', filename=f'previews/resume_{style}.pdf'))

@app.route('/download/<style>')
def download(style):
    """Download a CV with a specific style."""
    if style not in STYLES:
        return redirect(url_for('index'))
    
    preview_pdf = PREVIEW_FOLDER / f'resume_{style}.pdf'
    if not preview_pdf.exists():
        return redirect(url_for('index'))
    
    return send_file(preview_pdf, as_attachment=True, download_name=f'resume_{style}.pdf')

@app.route('/load_sample')
def load_sample():
    """Load sample CV data."""
    sample_path = Path(__file__).parent.parent / 'sample_cv.json'
    if not sample_path.exists():
        return jsonify({'error': 'Sample file not found'}), 404
    
    with open(sample_path, 'r') as f:
        sample_data = json.load(f)
    
    return jsonify({'success': True, 'data': sample_data})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
