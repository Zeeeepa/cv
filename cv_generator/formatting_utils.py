#!/usr/bin/env python3
"""
CV Formatting Utilities - Tools for advanced text formatting in CVs.

This module provides utilities for formatting text in CVs, including:
- Text formatting (bold, italic, underline, etc.)
- List formatting (bullets, numbered lists)
- Section formatting (headings, dividers)
- Font style and size options
- Custom spacing options
- Markdown to LaTeX conversion
"""

import re
from typing import Dict, List, Any, Optional, Union

# LaTeX escape characters
LATEX_SPECIAL_CHARS = {
    '&': r'\&',
    '%': r'\%',
    '$': r'\$',
    '#': r'\#',
    '_': r'\_',
    '{': r'\{',
    '}': r'\}',
    '~': r'\textasciitilde{}',
    '^': r'\textasciicircum{}',
    '\\': r'\textbackslash{}',
}

# Font styles
FONT_STYLES = {
    'default': '',
    'serif': r'\rmfamily',
    'sans-serif': r'\sffamily',
    'monospace': r'\ttfamily',
}

# Font weights
FONT_WEIGHTS = {
    'normal': r'\mdseries',
    'bold': r'\bfseries',
}

# Font shapes
FONT_SHAPES = {
    'normal': r'\upshape',
    'italic': r'\itshape',
    'slanted': r'\slshape',
    'small-caps': r'\scshape',
}

# Font sizes
FONT_SIZES = {
    'tiny': r'\tiny',
    'scriptsize': r'\scriptsize',
    'footnotesize': r'\footnotesize',
    'small': r'\small',
    'normalsize': r'\normalsize',
    'large': r'\large',
    'Large': r'\Large',
    'LARGE': r'\LARGE',
    'huge': r'\huge',
    'Huge': r'\Huge',
}

def escape_latex(text: str) -> str:
    """
    Escape special LaTeX characters.
    
    Args:
        text: The text to escape
        
    Returns:
        The escaped text
    """
    # Replace backslashes first to avoid double escaping
    text = text.replace('\\', r'\textbackslash{}')
    
    # Replace other special characters
    for char, replacement in LATEX_SPECIAL_CHARS.items():
        if char != '\\':  # Skip backslash as we've already handled it
            text = text.replace(char, replacement)
    
    return text

def format_text(text: str, style: Optional[str] = None, weight: Optional[str] = None, 
                shape: Optional[str] = None, size: Optional[str] = None) -> str:
    """
    Format text with LaTeX formatting commands.
    
    Args:
        text: The text to format
        style: Font style (serif, sans-serif, monospace)
        weight: Font weight (normal, bold)
        shape: Font shape (normal, italic, slanted, small-caps)
        size: Font size (tiny, scriptsize, footnotesize, small, normalsize, large, Large, LARGE, huge, Huge)
        
    Returns:
        The formatted text
    """
    commands = []
    
    # Add font style command
    if style and style in FONT_STYLES and style != 'default':
        commands.append(FONT_STYLES[style])
    
    # Add font weight command
    if weight and weight in FONT_WEIGHTS and weight != 'normal':
        commands.append(FONT_WEIGHTS[weight])
    
    # Add font shape command
    if shape and shape in FONT_SHAPES and shape != 'normal':
        commands.append(FONT_SHAPES[shape])
    
    # Add font size command
    if size and size in FONT_SIZES and size != 'normalsize':
        commands.append(FONT_SIZES[size])
    
    # If no formatting is applied, return the text as is
    if not commands:
        return text
    
    # Apply formatting
    formatted_text = '{' + ' '.join(commands) + ' ' + text + '}'
    return formatted_text

def format_bold(text: str) -> str:
    """
    Format text as bold.
    
    Args:
        text: The text to format
        
    Returns:
        The formatted text
    """
    return f'\\textbf{{{text}}}'

def format_italic(text: str) -> str:
    """
    Format text as italic.
    
    Args:
        text: The text to format
        
    Returns:
        The formatted text
    """
    return f'\\textit{{{text}}}'

def format_underline(text: str) -> str:
    """
    Format text as underlined.
    
    Args:
        text: The text to format
        
    Returns:
        The formatted text
    """
    return f'\\underline{{{text}}}'

def format_color(text: str, color: str) -> str:
    """
    Format text with a specific color.
    
    Args:
        text: The text to format
        color: The color to use (e.g., 'red', 'blue', or a hex color like 'FF0000')
        
    Returns:
        The formatted text
    """
    # Check if the color is a hex color
    if re.match(r'^[0-9A-Fa-f]{6}$', color):
        return f'\\textcolor[HTML]{{{color}}}{{{text}}}'
    else:
        return f'\\textcolor{{{color}}}{{{text}}}' 

def format_bullet_list(items: List[str]) -> str:
    """
    Format a list of items as a bullet list.
    
    Args:
        items: The list of items
        
    Returns:
        The formatted list
    """
    result = '\\begin{itemize}\n'
    for item in items:
        result += f'  \\item {item}\n'
    result += '\\end{itemize}'
    return result

def format_numbered_list(items: List[str]) -> str:
    """
    Format a list of items as a numbered list.
    
    Args:
        items: The list of items
        
    Returns:
        The formatted list
    """
    result = '\\begin{enumerate}\n'
    for item in items:
        result += f'  \\item {item}\n'
    result += '\\end{enumerate}'
    return result

def format_heading(text: str, level: int = 1) -> str:
    """
    Format text as a heading.
    
    Args:
        text: The text to format
        level: The heading level (1-5)
        
    Returns:
        The formatted text
    """
    if level == 1:
        return f'\\section*{{{text}}}'
    elif level == 2:
        return f'\\subsection*{{{text}}}'
    elif level == 3:
        return f'\\subsubsection*{{{text}}}'
    elif level == 4:
        return f'\\paragraph{{{text}}}'
    elif level == 5:
        return f'\\subparagraph{{{text}}}'
    else:
        return text

def format_divider() -> str:
    """
    Create a horizontal divider.
    
    Returns:
        The divider
    """
    return '\\hrulefill'

def markdown_to_latex(text: str) -> str:
    """
    Convert Markdown text to LaTeX.
    
    Args:
        text: The Markdown text
        
    Returns:
        The LaTeX text
    """
    # Basic Markdown to LaTeX conversion
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'__(.*?)__', r'\\textbf{\1}', text)
    
    # Italic
    text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
    text = re.sub(r'_(.*?)_', r'\\textit{\1}', text)
    
    # Strikethrough
    text = re.sub(r'~~(.*?)~~', r'\\sout{\1}', text)
    
    # Bullet lists
    text = re.sub(r'^\s*[-*+]\s+(.*?)$', r'\\item \1', text, flags=re.MULTILINE)
    
    # Numbered lists
    text = re.sub(r'^\s*(\d+)\.\s+(.*?)$', r'\\item \2', text, flags=re.MULTILINE)
    
    # Headers
    text = re.sub(r'^#\s+(.*?)$', r'\\section*{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^##\s+(.*?)$', r'\\subsection*{\1}', text, flags=re.MULTILINE)
    text = re.sub(r'^###\s+(.*?)$', r'\\subsubsection*{\1}', text, flags=re.MULTILINE)
    
    # Links
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\\href{\2}{\1}', text)
    
    # Escape special characters
    for char, replacement in LATEX_SPECIAL_CHARS.items():
        # Skip characters that are part of LaTeX commands we've already added
        if char not in ['\\', '{', '}', '_', '^', '&', '%', '#', '$']:
            text = text.replace(char, replacement)
    
    return text

def apply_formatting_to_cv_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply formatting to CV data.
    
    Args:
        data: The CV data
        
    Returns:
        The formatted CV data
    """
    # Create a deep copy of the data to avoid modifying the original
    formatted_data = {}
    
    # Format personal information
    for key in ['FirstName', 'LastName', 'Position', 'Address', 'Mobile', 'Email', 
                'Homepage', 'GitHub', 'LinkedIn', 'Twitter', 'Quote']:
        if key in data:
            formatted_data[key] = data[key]
    
    # Format summary
    if 'Summary' in data:
        formatted_data['Summary'] = markdown_to_latex(data['Summary'])
    
    # Format work experience
    if 'Work Experience' in data:
        formatted_data['Work Experience'] = []
        for job in data['Work Experience']:
            formatted_job = {
                'Title': job.get('Title', ''),
                'Company': job.get('Company', ''),
                'Location': job.get('Location', ''),
                'Date': job.get('Date', ''),
            }
            
            # Format job description items
            if 'items' in job:
                formatted_job['items'] = [markdown_to_latex(item) for item in job['items']]
            
            formatted_data['Work Experience'].append(formatted_job)
    
    # Format education
    if 'Education' in data:
        formatted_data['Education'] = []
        for edu in data['Education']:
            formatted_edu = {
                'Degree': edu.get('Degree', ''),
                'Institution': edu.get('Institution', ''),
                'Location': edu.get('Location', ''),
                'Date': edu.get('Date', ''),
            }
            
            # Format education description items
            if 'items' in edu:
                formatted_edu['items'] = [markdown_to_latex(item) for item in edu['items']]
            
            formatted_data['Education'].append(formatted_edu)
    
    # Format skills
    if 'Skills' in data:
        formatted_data['Skills'] = []
        for skill in data['Skills']:
            formatted_skill = {
                'Category': skill.get('Category', ''),
                'Skills': skill.get('Skills', ''),
            }
            formatted_data['Skills'].append(formatted_skill)
    
    # Format certificates
    if 'Certificates' in data:
        formatted_data['Certificates'] = []
        for cert in data['Certificates']:
            formatted_cert = {
                'Name': cert.get('Name', ''),
                'Issuer': cert.get('Issuer', ''),
                'Location': cert.get('Location', ''),
                'Date': cert.get('Date', ''),
            }
            
            # Format certificate description items
            if 'items' in cert:
                formatted_cert['items'] = [markdown_to_latex(item) for item in cert['items']]
            
            formatted_data['Certificates'].append(formatted_cert)
    
    # Format honors
    if 'Honors' in data:
        formatted_data['Honors'] = []
        for honor in data['Honors']:
            formatted_honor = {
                'Name': honor.get('Name', ''),
                'Issuer': honor.get('Issuer', ''),
                'Location': honor.get('Location', ''),
                'Date': honor.get('Date', ''),
            }
            formatted_data['Honors'].append(formatted_honor)
    
    return formatted_data
