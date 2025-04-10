#!/usr/bin/env python3
"""
CV Generator Validation Module - Provides validation and error handling for the CV Generator.

This module contains functions for validating user input, handling errors gracefully,
and ensuring data consistency throughout the CV generation process.
"""

import re
import os
from typing import Dict, List, Any, Optional, Tuple, Union
import json
from pathlib import Path


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_personal_info(data: Dict[str, Any]) -> List[str]:
    """
    Validate personal information in CV data.
    
    Args:
        data: Dictionary containing CV data
        
    Returns:
        List of validation error messages (empty if no errors)
    """
    errors = []
    
    # Check required fields
    required_fields = ['FirstName', 'LastName', 'Position']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"{field.replace('FirstName', 'First Name').replace('LastName', 'Last Name')} is required")
    
    # Validate email format if provided
    if 'Email' in data and data['Email']:
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['Email']):
            errors.append("Invalid email format")
    
    # Validate URLs if provided
    url_fields = ['Homepage', 'GitHub', 'LinkedIn']
    url_pattern = r'^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    
    for field in url_fields:
        if field in data and data[field] and not re.match(url_pattern, data[field]):
            errors.append(f"Invalid URL format for {field}")
    
    return errors


def validate_sections(data: Dict[str, Any]) -> List[str]:
    """
    Validate section data in CV.
    
    Args:
        data: Dictionary containing CV data
        
    Returns:
        List of validation error messages (empty if no errors)
    """
    errors = []
    
    # Validate Work Experience
    if 'Work Experience' in data and data['Work Experience']:
        for i, job in enumerate(data['Work Experience']):
            if 'Title' not in job or not job['Title']:
                errors.append(f"Work Experience #{i+1}: Title is required")
            if 'Company' not in job or not job['Company']:
                errors.append(f"Work Experience #{i+1}: Company is required")
    
    # Validate Education
    if 'Education' in data and data['Education']:
        for i, edu in enumerate(data['Education']):
            if 'Degree' not in edu or not edu['Degree']:
                errors.append(f"Education #{i+1}: Degree is required")
            if 'Institution' not in edu or not edu['Institution']:
                errors.append(f"Education #{i+1}: Institution is required")
    
    # Validate Skills
    if 'Skills' in data and data['Skills']:
        for i, skill in enumerate(data['Skills']):
            if 'Category' not in skill or not skill['Category']:
                errors.append(f"Skill #{i+1}: Category is required")
            if 'Skills' not in skill or not skill['Skills']:
                errors.append(f"Skill #{i+1}: Skills list is required")
    
    return errors


def validate_cv_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate complete CV data.
    
    Args:
        data: Dictionary containing CV data
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Validate personal information
    errors.extend(validate_personal_info(data))
    
    # Validate sections
    errors.extend(validate_sections(data))
    
    return len(errors) == 0, errors


def validate_file_format(file_path: Union[str, Path]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Validate file format and content.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Tuple of (is_valid, error_message, data)
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return False, "File does not exist", None
    
    # Check file extension
    if file_path.suffix.lower() not in ['.json', '.txt']:
        return False, "Unsupported file format. Please use JSON or TXT files.", None
    
    try:
        # Handle JSON files
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate structure
            is_valid, errors = validate_cv_data(data)
            if not is_valid:
                return False, f"Invalid CV data: {', '.join(errors)}", None
            
            return True, None, data
        
        # Handle TXT files
        elif file_path.suffix.lower() == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Parse TXT format
            data = parse_txt_format(lines)
            
            # Validate structure
            is_valid, errors = validate_cv_data(data)
            if not is_valid:
                return False, f"Invalid CV data: {', '.join(errors)}", None
            
            return True, None, data
    
    except json.JSONDecodeError:
        return False, "Invalid JSON format", None
    except Exception as e:
        return False, f"Error processing file: {str(e)}", None


def parse_txt_format(lines: List[str]) -> Dict[str, Any]:
    """
    Parse TXT format into CV data dictionary.
    
    Args:
        lines: List of text lines from the file
        
    Returns:
        Dictionary containing CV data
    """
    data = {}
    current_section = None
    current_entry = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for section headers
        if line.endswith(':'):
            section_name = line[:-1].strip()
            if section_name in ['Work Experience', 'Education', 'Skills', 'Certificates', 'Honors']:
                current_section = section_name
                data[current_section] = []
                current_entry = None
            else:
                # Handle personal info fields
                current_section = None
                current_entry = None
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        
        # Handle section entries
        elif current_section and line.startswith('-'):
            # New entry in a section
            entry_line = line[1:].strip()
            
            if ':' in entry_line:
                key, value = entry_line.split(':', 1)
                
                if current_entry is None:
                    current_entry = {}
                    data[current_section].append(current_entry)
                
                if current_section == 'Work Experience':
                    if key.strip() == 'Title':
                        current_entry['Title'] = value.strip()
                    elif key.strip() == 'Company':
                        current_entry['Company'] = value.strip()
                    elif key.strip() == 'Location':
                        current_entry['Location'] = value.strip()
                    elif key.strip() == 'Date':
                        current_entry['Date'] = value.strip()
                    elif key.strip() == 'Description':
                        current_entry['items'] = [item.strip() for item in value.strip().split(',')]
                
                elif current_section == 'Education':
                    if key.strip() == 'Degree':
                        current_entry['Degree'] = value.strip()
                    elif key.strip() == 'Institution':
                        current_entry['Institution'] = value.strip()
                    elif key.strip() == 'Location':
                        current_entry['Location'] = value.strip()
                    elif key.strip() == 'Date':
                        current_entry['Date'] = value.strip()
                    elif key.strip() == 'Description':
                        current_entry['items'] = [item.strip() for item in value.strip().split(',')]
                
                elif current_section == 'Skills':
                    if key.strip() == 'Category':
                        current_entry['Category'] = value.strip()
                    elif key.strip() == 'Skills':
                        current_entry['Skills'] = value.strip()
                
                elif current_section == 'Certificates':
                    if key.strip() == 'Name':
                        current_entry['Name'] = value.strip()
                    elif key.strip() == 'Issuer':
                        current_entry['Issuer'] = value.strip()
                    elif key.strip() == 'Location':
                        current_entry['Location'] = value.strip()
                    elif key.strip() == 'Date':
                        current_entry['Date'] = value.strip()
                    elif key.strip() == 'Description':
                        current_entry['items'] = [item.strip() for item in value.strip().split(',')]
                
                elif current_section == 'Honors':
                    if key.strip() == 'Name':
                        current_entry['Name'] = value.strip()
                    elif key.strip() == 'Issuer':
                        current_entry['Issuer'] = value.strip()
                    elif key.strip() == 'Location':
                        current_entry['Location'] = value.strip()
                    elif key.strip() == 'Date':
                        current_entry['Date'] = value.strip()
    
    return data


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent LaTeX injection.
    
    Args:
        text: Input text
        
    Returns:
        Sanitized text
    """
    # Escape LaTeX special characters
    latex_special_chars = ['&', '%', '$', '#', '_', '{', '}', '~', '^', '\\']
    
    for char in latex_special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text


def sanitize_cv_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize all text fields in CV data.
    
    Args:
        data: Dictionary containing CV data
        
    Returns:
        Sanitized data dictionary
    """
    # Create a deep copy to avoid modifying the original
    sanitized = {}
    
    # Sanitize personal information
    for key in ['FirstName', 'LastName', 'Position', 'Address', 'Mobile', 'Email', 
                'Homepage', 'GitHub', 'LinkedIn', 'Quote', 'Summary']:
        if key in data and data[key]:
            sanitized[key] = sanitize_input(data[key])
        else:
            sanitized[key] = data.get(key, '')
    
    # Sanitize Work Experience
    sanitized['Work Experience'] = []
    if 'Work Experience' in data and data['Work Experience']:
        for job in data['Work Experience']:
            sanitized_job = {}
            for key in ['Title', 'Company', 'Location', 'Date']:
                if key in job and job[key]:
                    sanitized_job[key] = sanitize_input(job[key])
                else:
                    sanitized_job[key] = job.get(key, '')
            
            sanitized_job['items'] = []
            if 'items' in job and job['items']:
                sanitized_job['items'] = [sanitize_input(item) for item in job['items']]
            
            sanitized['Work Experience'].append(sanitized_job)
    
    # Sanitize Education
    sanitized['Education'] = []
    if 'Education' in data and data['Education']:
        for edu in data['Education']:
            sanitized_edu = {}
            for key in ['Degree', 'Institution', 'Location', 'Date']:
                if key in edu and edu[key]:
                    sanitized_edu[key] = sanitize_input(edu[key])
                else:
                    sanitized_edu[key] = edu.get(key, '')
            
            sanitized_edu['items'] = []
            if 'items' in edu and edu['items']:
                sanitized_edu['items'] = [sanitize_input(item) for item in edu['items']]
            
            sanitized['Education'].append(sanitized_edu)
    
    # Sanitize Skills
    sanitized['Skills'] = []
    if 'Skills' in data and data['Skills']:
        for skill in data['Skills']:
            sanitized_skill = {}
            for key in ['Category', 'Skills']:
                if key in skill and skill[key]:
                    sanitized_skill[key] = sanitize_input(skill[key])
                else:
                    sanitized_skill[key] = skill.get(key, '')
            
            sanitized['Skills'].append(sanitized_skill)
    
    # Sanitize Certificates
    sanitized['Certificates'] = []
    if 'Certificates' in data and data['Certificates']:
        for cert in data['Certificates']:
            sanitized_cert = {}
            for key in ['Name', 'Issuer', 'Location', 'Date']:
                if key in cert and cert[key]:
                    sanitized_cert[key] = sanitize_input(cert[key])
                else:
                    sanitized_cert[key] = cert.get(key, '')
            
            sanitized_cert['items'] = []
            if 'items' in cert and cert['items']:
                sanitized_cert['items'] = [sanitize_input(item) for item in cert['items']]
            
            sanitized['Certificates'].append(sanitized_cert)
    
    # Sanitize Honors
    sanitized['Honors'] = []
    if 'Honors' in data and data['Honors']:
        for honor in data['Honors']:
            sanitized_honor = {}
            for key in ['Name', 'Issuer', 'Location', 'Date']:
                if key in honor and honor[key]:
                    sanitized_honor[key] = sanitize_input(honor[key])
                else:
                    sanitized_honor[key] = honor.get(key, '')
            
            sanitized['Honors'].append(sanitized_honor)
    
    return sanitized
