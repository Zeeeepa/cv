#!/usr/bin/env python3
"""
CV Error Handler - Provides error handling and recovery for the CV Generator.

This module contains functions for handling errors gracefully, providing
user-friendly error messages, and recovering from common error conditions.
"""

import os
import sys
import traceback
import logging
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from pathlib import Path
import json
import shutil
import tempfile
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('cv_error_handler')

# Error types
class CVGeneratorError(Exception):
    """Base exception for CV Generator errors."""
    pass

class TemplateError(CVGeneratorError):
    """Exception for template-related errors."""
    pass

class ValidationError(CVGeneratorError):
    """Exception for validation errors."""
    pass

class CompilationError(CVGeneratorError):
    """Exception for LaTeX compilation errors."""
    pass

class FileSystemError(CVGeneratorError):
    """Exception for file system errors."""
    pass

class ConfigurationError(CVGeneratorError):
    """Exception for configuration errors."""
    pass

# Error messages
ERROR_MESSAGES = {
    'template_not_found': "Template not found. Please check the template directory.",
    'invalid_data': "Invalid CV data. Please check your input data.",
    'compilation_failed': "LaTeX compilation failed. Please check the LaTeX log for details.",
    'file_not_found': "File not found. Please check the file path.",
    'permission_denied': "Permission denied. Please check file permissions.",
    'disk_full': "Disk full. Please free up some disk space.",
    'invalid_style': "Invalid style. Please choose a valid style.",
    'missing_dependency': "Missing dependency. Please install the required dependencies.",
    'unknown_error': "An unknown error occurred. Please try again."
}

# Error handlers
def handle_template_error(error: Exception) -> str:
    """
    Handle template-related errors.
    
    Args:
        error: The exception that was raised
        
    Returns:
        str: User-friendly error message
    """
    logger.error(f"Template error: {str(error)}")
    logger.debug(traceback.format_exc())
    
    if "not found" in str(error).lower():
        return ERROR_MESSAGES['template_not_found']
    else:
        return f"Template error: {str(error)}"

def handle_validation_error(error: Exception) -> str:
    """
    Handle validation errors.
    
    Args:
        error: The exception that was raised
        
    Returns:
        str: User-friendly error message
    """
    logger.error(f"Validation error: {str(error)}")
    logger.debug(traceback.format_exc())
    
    return f"Validation error: {str(error)}"

def handle_compilation_error(error: Exception, log_file: Optional[Path] = None) -> str:
    """
    Handle LaTeX compilation errors.
    
    Args:
        error: The exception that was raised
        log_file: Optional path to the LaTeX log file
        
    Returns:
        str: User-friendly error message
    """
    logger.error(f"Compilation error: {str(error)}")
    logger.debug(traceback.format_exc())
    
    # Extract useful information from the log file if available
    error_details = ""
    if log_file and log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
            
            # Look for common LaTeX error patterns
            error_lines = []
            for line in log_content.split('\n'):
                if any(pattern in line for pattern in ['Error:', '!', 'Fatal error']):
                    error_lines.append(line.strip())
            
            if error_lines:
                error_details = "\n".join(error_lines[-3:])  # Show the last 3 error lines
        except Exception as e:
            logger.warning(f"Failed to read log file: {str(e)}")
    
    if error_details:
        return f"LaTeX compilation failed:\n{error_details}"
    else:
        return ERROR_MESSAGES['compilation_failed']

def handle_file_system_error(error: Exception) -> str:
    """
    Handle file system errors.
    
    Args:
        error: The exception that was raised
        
    Returns:
        str: User-friendly error message
    """
    logger.error(f"File system error: {str(error)}")
    logger.debug(traceback.format_exc())
    
    if isinstance(error, FileNotFoundError):
        return ERROR_MESSAGES['file_not_found']
    elif isinstance(error, PermissionError):
        return ERROR_MESSAGES['permission_denied']
    elif "no space" in str(error).lower():
        return ERROR_MESSAGES['disk_full']
    else:
        return f"File system error: {str(error)}"

def handle_configuration_error(error: Exception) -> str:
    """
    Handle configuration errors.
    
    Args:
        error: The exception that was raised
        
    Returns:
        str: User-friendly error message
    """
    logger.error(f"Configuration error: {str(error)}")
    logger.debug(traceback.format_exc())
    
    return f"Configuration error: {str(error)}"

def handle_unknown_error(error: Exception) -> str:
    """
    Handle unknown errors.
    
    Args:
        error: The exception that was raised
        
    Returns:
        str: User-friendly error message
    """
    logger.error(f"Unknown error: {str(error)}")
    logger.debug(traceback.format_exc())
    
    return ERROR_MESSAGES['unknown_error']

# Error recovery
def check_latex_installation() -> Tuple[bool, Optional[str]]:
    """
    Check if LaTeX is installed and working.
    
    Returns:
        Tuple[bool, Optional[str]]: (is_installed, error_message)
    """
    try:
        result = subprocess.run(['xelatex', '--version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True, 
                               timeout=5)
        
        if result.returncode == 0:
            return True, None
        else:
            return False, "XeLaTeX is not working properly."
    except FileNotFoundError:
        return False, "XeLaTeX is not installed or not in PATH."
    except Exception as e:
        return False, f"Error checking LaTeX installation: {str(e)}"

def check_dependencies() -> Dict[str, bool]:
    """
    Check if all required dependencies are installed.
    
    Returns:
        Dict[str, bool]: Dictionary of dependency names and their availability
    """
    dependencies = {
        'xelatex': False,
        'python_packages': False
    }
    
    # Check LaTeX
    latex_installed, _ = check_latex_installation()
    dependencies['xelatex'] = latex_installed
    
    # Check Python packages
    try:
        import yaml
        import markdown
        dependencies['python_packages'] = True
    except ImportError:
        dependencies['python_packages'] = False
    
    return dependencies

def create_fallback_pdf(output_path: Path, error_message: str) -> Path:
    """
    Create a fallback PDF with an error message when normal generation fails.
    
    Args:
        output_path: Path where the PDF should be saved
        error_message: Error message to include in the PDF
        
    Returns:
        Path: Path to the created PDF
    """
    # Create a temporary directory
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create a simple LaTeX file with the error message
    latex_content = f"""\\documentclass{{article}}
\\usepackage{{xcolor}}
\\usepackage{{geometry}}
\\geometry{{margin=1in}}
\\begin{{document}}
\\begin{{center}}
\\LARGE\\textbf{{CV Generation Failed}}
\\end{{center}}

\\vspace{{1cm}}
\\begin{{center}}
\\large\\textcolor{{red}}{{An error occurred while generating your CV.}}
\\end{{center}}

\\vspace{{0.5cm}}
\\begin{{verbatim}}
{error_message}
\\end{{verbatim}}

\\vspace{{1cm}}
\\begin{{center}}
Please check your input data and try again.
\\end{{center}}
\\end{{document}}
"""
    
    latex_file = temp_dir / "error.tex"
    with open(latex_file, 'w') as f:
        f.write(latex_content)
    
    # Try to compile the LaTeX file
    try:
        subprocess.run(['xelatex', '-interaction=nonstopmode', '-output-directory', str(temp_dir), str(latex_file)],
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      timeout=30)
        
        # Copy the PDF to the output path
        pdf_file = temp_dir / "error.pdf"
        if pdf_file.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(pdf_file, output_path)
            return output_path
    except Exception as e:
        logger.error(f"Failed to create fallback PDF: {str(e)}")
    
    # If PDF creation failed, return None
    return None

def safe_execute(func: Callable, *args, **kwargs) -> Tuple[bool, Any, Optional[str]]:
    """
    Safely execute a function and handle any exceptions.
    
    Args:
        func: Function to execute
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Tuple[bool, Any, Optional[str]]: (success, result, error_message)
    """
    try:
        result = func(*args, **kwargs)
        return True, result, None
    except TemplateError as e:
        return False, None, handle_template_error(e)
    except ValidationError as e:
        return False, None, handle_validation_error(e)
    except CompilationError as e:
        return False, None, handle_compilation_error(e)
    except (FileNotFoundError, PermissionError, OSError) as e:
        return False, None, handle_file_system_error(e)
    except ConfigurationError as e:
        return False, None, handle_configuration_error(e)
    except Exception as e:
        return False, None, handle_unknown_error(e)

def log_error(error_message: str, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an error with context information.
    
    Args:
        error_message: Error message to log
        context: Optional context information
    """
    if context:
        logger.error(f"{error_message} Context: {json.dumps(context)}")
    else:
        logger.error(error_message)
