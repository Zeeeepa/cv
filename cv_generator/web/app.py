#!/usr/bin/env python3
"""
CV Generator Web UI - A web interface for generating CVs with different styles.

This application provides a web interface for the CV Generator, allowing users to:
1. Input CV data in JSON or text format
2. Preview different CV styles
3. Generate and download CVs in PDF format
4. Customize CV templates with various options
"""

import os
import sys
import json
import tempfile
import shutil
import time
import logging
from pathlib import Path
import traceback
import markdown
import yaml

# Add parent directory to path to import cv_generator modules
sys.path.append(str(Path(__file__).parent.parent))

from flask import Flask, render_template, request, jsonify, send_file, url_for, redirect, session, flash
from werkzeug.utils import secure_filename
from cv_generator import CVGenerator
from style_generator import generate_styled_cv
from style_library import get_all_styles, get_style_families, get_random_style
from validation import validate_cv_data, sanitize_cv_data
from template_manager import get_available_templates, get_template_defaults
from cache_manager import get_cached_pdf, cache_pdf, get_cache_stats, clear_cache
from error_handler import (
    safe_execute, 
    check_dependencies, 
    create_fallback_pdf, 
    log_error,
    TemplateError,
    ValidationError,
    CompilationError
)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('cv_generator_web')

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Set secret key for session management
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

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

# Configure log folder
LOG_FOLDER = Path(__file__).parent / 'logs'
LOG_FOLDER.mkdir(exist_ok=True)

# Configure max content length (10 MB)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

# Get all available styles from the style library
STYLES = list(get_all_styles().keys())
STYLE_COLORS = get_all_styles()
STYLE_FAMILIES = get_style_families()

# Get all available templates
TEMPLATES = get_available_templates()

# Check dependencies
DEPENDENCIES = check_dependencies()

@app.route('/')
def index():
    """Render the main page."""
    # Check if dependencies are installed
    if not all(DEPENDENCIES.values()):
        missing_deps = [dep for dep, installed in DEPENDENCIES.items() if not installed]
        flash(f"Warning: Missing dependencies: {', '.join(missing_deps)}", "warning")
    
    return render_template('index.html', 
                          styles=STYLES, 
                          style_colors=STYLE_COLORS,
                          style_families=STYLE_FAMILIES,
                          templates=TEMPLATES,
                          cache_stats=get_cache_stats())

@app.route('/random_style', methods=['GET'])
def random_style():
    """Get a random style."""
    style_name, color_hex = get_random_style()
    return jsonify({'success': True, 'style': style_name, 'color': color_hex})

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Check file extension
        allowed_extensions = ['.json', '.txt']
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'Invalid file format. Allowed formats: {", ".join(allowed_extensions)}'}), 400
        
        # Save file with secure filename
        filename = secure_filename(file.filename)
        file_path = app.config['UPLOAD_FOLDER'] / filename
        file.save(file_path)
        
        # Validate file content
        from validation import validate_file_format
        is_valid, error_message, data = validate_file_format(file_path)
        
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        return jsonify({'success': True, 'filename': filename, 'data': data})
    
    except Exception as e:
        log_error(f"Error in upload_file: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

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
        
        # Validate data
        is_valid, errors = validate_cv_data(data)
        if not is_valid:
            return jsonify({'error': f"Invalid CV data: {', '.join(errors)}"}), 400
        
        # Sanitize data to prevent LaTeX injection
        data = sanitize_cv_data(data)
        
        # Save data to JSON file
        json_file = app.config['UPLOAD_FOLDER'] / 'temp_cv.json'
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Get selected style
        style = request.form.get('style', 'red')
        
        # Check if we have a cached PDF for this data and style
        cached_pdf = get_cached_pdf(data, style)
        if cached_pdf and cached_pdf.exists():
            # Copy the cached PDF to the preview folder
            preview_pdf = PREVIEW_FOLDER / f'resume_{style}.pdf'
            shutil.copy(cached_pdf, preview_pdf)
            
            # Return the preview URL
            preview_url = url_for('static', filename=f'previews/resume_{style}.pdf')
            return jsonify({'success': True, 'preview_url': preview_url, 'cached': True})
        
        # Generate CV
        template_dir = Path(__file__).parent.parent.parent / 'build'
        generator = CVGenerator(template_dir=str(template_dir))
        
        try:
            # Generate LaTeX file
            latex_file = generator.generate_cv(data, output_filename='resume')
            
            # Compile LaTeX to PDF
            pdf_file = generator.compile_latex(latex_file)
            
            # Cache the PDF for future use
            cache_pdf(data, style, pdf_file)
            
            # Copy the PDF to the preview folder with a unique name
            preview_pdf = PREVIEW_FOLDER / f'resume_{style}.pdf'
            shutil.copy(pdf_file, preview_pdf)
            
            # Return the preview URL
            preview_url = url_for('static', filename=f'previews/resume_{style}.pdf')
            return jsonify({'success': True, 'preview_url': preview_url})
        
        except Exception as e:
            # Log the error
            log_error(f"Error generating CV: {str(e)}")
            
            # Create a fallback PDF with the error message
            error_pdf_path = PREVIEW_FOLDER / f'error_{int(time.time())}.pdf'
            fallback_pdf = create_fallback_pdf(error_pdf_path, str(e))
            
            if fallback_pdf:
                preview_url = url_for('static', filename=f'previews/{fallback_pdf.name}')
                return jsonify({
                    'success': False, 
                    'error': str(e),
                    'fallback_pdf': preview_url
                }), 500
            else:
                return jsonify({'error': str(e)}), 500
    
    except Exception as e:
        log_error(f"Error in generate_cv: {str(e)}")
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
                
                # Validate file content
                from validation import validate_file_format
                is_valid, error_message, data = validate_file_format(file_path)
                
                if not is_valid:
                    return jsonify({'error': error_message}), 400
                
                # Generate CVs with different styles
                styled_output_dir = OUTPUT_FOLDER / 'styled'
                styled_output_dir.mkdir(exist_ok=True)
                
                # Use safe_execute to handle errors
                success, result, error = safe_execute(
                    generate_styled_cv, 
                    str(file_path), 
                    str(styled_output_dir), 
                    STYLES
                )
                
                if not success:
                    return jsonify({'error': error}), 500
                
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
        log_error(f"Error in generate_all_styles: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/preview/<style>')
def preview(style):
    """Preview a CV with a specific style."""
    if style not in STYLES:
        flash("Invalid style selected.", "error")
        return redirect(url_for('index'))
    
    preview_pdf = PREVIEW_FOLDER / f'resume_{style}.pdf'
    if not preview_pdf.exists():
        flash("No preview available for this style. Please generate a CV first.", "warning")
        return redirect(url_for('index'))
    
    return render_template('preview.html', 
                          style=style, 
                          pdf_url=url_for('static', filename=f'previews/resume_{style}.pdf'))

@app.route('/download/<style>')
def download(style):
    """Download a CV with a specific style."""
    if style not in STYLES:
        flash("Invalid style selected.", "error")
        return redirect(url_for('index'))
    
    preview_pdf = PREVIEW_FOLDER / f'resume_{style}.pdf'
    if not preview_pdf.exists():
        flash("No PDF available for this style. Please generate a CV first.", "warning")
        return redirect(url_for('index'))
    
    return send_file(preview_pdf, as_attachment=True, download_name=f'resume_{style}.pdf')

@app.route('/load_sample')
def load_sample():
    """Load sample CV data."""
    sample_path = Path(__file__).parent.parent / 'sample_cv.json'
    if not sample_path.exists():
        return jsonify({'error': 'Sample file not found'}), 404
    
    try:
        with open(sample_path, 'r') as f:
            sample_data = json.load(f)
        
        return jsonify({'success': True, 'data': sample_data})
    
    except Exception as e:
        log_error(f"Error loading sample data: {str(e)}")
        return jsonify({'error': f'Error loading sample data: {str(e)}'}), 500

@app.route('/template_defaults/<template_type>')
def template_defaults(template_type):
    """Get default options for a template type."""
    try:
        if template_type not in TEMPLATES:
            return jsonify({'error': 'Invalid template type'}), 400
        
        defaults = get_template_defaults(template_type)
        return jsonify({'success': True, 'defaults': defaults})
    
    except Exception as e:
        log_error(f"Error getting template defaults: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/clear_cache', methods=['POST'])
def clear_cache_route():
    """Clear the CV cache."""
    try:
        clear_cache()
        return jsonify({'success': True, 'message': 'Cache cleared successfully'})
    
    except Exception as e:
        log_error(f"Error clearing cache: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/check_dependencies')
def check_dependencies_route():
    """Check if all required dependencies are installed."""
    try:
        dependencies = check_dependencies()
        return jsonify({'success': True, 'dependencies': dependencies})
    
    except Exception as e:
        log_error(f"Error checking dependencies: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/markdown_preview', methods=['POST'])
def markdown_preview():
    """Convert Markdown to HTML for preview."""
    try:
        md_text = request.form.get('markdown', '')
        html = markdown.markdown(md_text)
        return jsonify({'success': True, 'html': html})
    
    except Exception as e:
        log_error(f"Error converting markdown: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 10 MB.'}), 413

@app.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors."""
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors."""
    log_error(f"Internal server error: {str(error)}")
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
