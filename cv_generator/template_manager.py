#!/usr/bin/env python3
"""
CV Template Manager - Manages CV templates and their customization.

This module provides functionality for managing CV templates, including:
- Loading templates from different sources
- Customizing templates with user preferences
- Applying different styles to templates
- Handling template errors and fallbacks
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
import json
import yaml
import re

# Template types
TEMPLATE_TYPES = {
    "awesome-cv": "Awesome CV",
    "modern": "Modern",
    "classic": "Classic",
    "academic": "Academic",
    "minimal": "Minimal"
}

# Template sections
TEMPLATE_SECTIONS = [
    "personal",
    "summary",
    "work_experience",
    "education",
    "skills",
    "certificates",
    "honors",
    "projects",
    "publications",
    "languages",
    "interests"
]

class TemplateError(Exception):
    """Custom exception for template errors."""
    pass


def get_available_templates() -> Dict[str, str]:
    """
    Get all available templates.
    
    Returns:
        Dict[str, str]: Dictionary of template IDs and their display names
    """
    return TEMPLATE_TYPES


def get_template_sections() -> List[str]:
    """
    Get all available template sections.
    
    Returns:
        List[str]: List of template section IDs
    """
    return TEMPLATE_SECTIONS


def create_template_directory(template_type: str, output_dir: Optional[Path] = None) -> Path:
    """
    Create a directory for a specific template type.
    
    Args:
        template_type: Type of template to create
        output_dir: Optional output directory (uses temp dir if not provided)
        
    Returns:
        Path: Path to the created template directory
    """
    if template_type not in TEMPLATE_TYPES:
        raise TemplateError(f"Unknown template type: {template_type}")
    
    # Use provided output directory or create a temporary one
    if output_dir is None:
        output_dir = Path(tempfile.mkdtemp())
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
    
    # Create template directory
    template_dir = output_dir / template_type
    template_dir.mkdir(exist_ok=True)
    
    return template_dir


def customize_template(template_dir: Path, options: Dict[str, Any]) -> None:
    """
    Customize a template with user options.
    
    Args:
        template_dir: Path to the template directory
        options: Dictionary of customization options
    """
    # Create a configuration file for the template
    config_file = template_dir / "template_config.yaml"
    
    # Convert options to YAML and write to file
    with open(config_file, "w") as f:
        yaml.dump(options, f, default_flow_style=False)


def apply_style_to_template(template_dir: Path, style_name: str, color_hex: str) -> None:
    """
    Apply a style to a template.
    
    Args:
        template_dir: Path to the template directory
        style_name: Name of the style to apply
        color_hex: Hex color code for the style
    """
    # Create a style file for the template
    style_file = template_dir / "style.tex"
    
    # Write style definitions to file
    with open(style_file, "w") as f:
        f.write(f"% Style: {style_name}\n")
        f.write(f"\\definecolor{{accent}}{{HTML}}{{{color_hex.replace('#', '')}}}\n")
        f.write("\\colorlet{heading}{accent}\n")
        f.write("\\colorlet{emphasis}{accent}\n")
        f.write("\\colorlet{body}{black}\n")


def get_template_defaults(template_type: str) -> Dict[str, Any]:
    """
    Get default options for a template type.
    
    Args:
        template_type: Type of template
        
    Returns:
        Dict[str, Any]: Dictionary of default options
    """
    defaults = {
        "font_size": "11pt",
        "paper_size": "a4paper",
        "font_family": "sans",
        "line_spacing": "1.15",
        "margin_size": "moderate",
        "section_spacing": "medium",
        "show_page_numbers": True,
        "show_date": True,
        "date_format": "%B %d, %Y",
        "enable_hyperlinks": True,
        "hyperlink_color": "#0000EE",
        "include_photo": False,
        "photo_size": "medium",
        "header_style": "standard",
        "footer_style": "minimal"
    }
    
    # Template-specific defaults
    if template_type == "awesome-cv":
        defaults.update({
            "font_family": "sans",
            "enable_hyperlinks": True,
            "header_style": "standard"
        })
    elif template_type == "modern":
        defaults.update({
            "font_family": "sans",
            "margin_size": "narrow",
            "header_style": "compact"
        })
    elif template_type == "classic":
        defaults.update({
            "font_family": "serif",
            "line_spacing": "1.5",
            "margin_size": "moderate",
            "header_style": "traditional"
        })
    elif template_type == "academic":
        defaults.update({
            "font_family": "serif",
            "font_size": "12pt",
            "line_spacing": "1.5",
            "show_page_numbers": True,
            "header_style": "detailed"
        })
    elif template_type == "minimal":
        defaults.update({
            "font_family": "sans",
            "margin_size": "wide",
            "section_spacing": "compact",
            "header_style": "minimal"
        })
    
    return defaults


def validate_template_options(options: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate template customization options.
    
    Args:
        options: Dictionary of customization options
        
    Returns:
        Tuple[bool, List[str]]: Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Validate font size
    if "font_size" in options:
        valid_font_sizes = ["10pt", "11pt", "12pt"]
        if options["font_size"] not in valid_font_sizes:
            errors.append(f"Invalid font size: {options['font_size']}. Must be one of {valid_font_sizes}")
    
    # Validate paper size
    if "paper_size" in options:
        valid_paper_sizes = ["a4paper", "letterpaper"]
        if options["paper_size"] not in valid_paper_sizes:
            errors.append(f"Invalid paper size: {options['paper_size']}. Must be one of {valid_paper_sizes}")
    
    # Validate font family
    if "font_family" in options:
        valid_font_families = ["sans", "serif", "mono"]
        if options["font_family"] not in valid_font_families:
            errors.append(f"Invalid font family: {options['font_family']}. Must be one of {valid_font_families}")
    
    # Validate margin size
    if "margin_size" in options:
        valid_margin_sizes = ["narrow", "moderate", "wide"]
        if options["margin_size"] not in valid_margin_sizes:
            errors.append(f"Invalid margin size: {options['margin_size']}. Must be one of {valid_margin_sizes}")
    
    # Validate section spacing
    if "section_spacing" in options:
        valid_section_spacings = ["compact", "medium", "wide"]
        if options["section_spacing"] not in valid_section_spacings:
            errors.append(f"Invalid section spacing: {options['section_spacing']}. Must be one of {valid_section_spacings}")
    
    # Validate header style
    if "header_style" in options:
        valid_header_styles = ["minimal", "standard", "compact", "traditional", "detailed"]
        if options["header_style"] not in valid_header_styles:
            errors.append(f"Invalid header style: {options['header_style']}. Must be one of {valid_header_styles}")
    
    # Validate footer style
    if "footer_style" in options:
        valid_footer_styles = ["none", "minimal", "standard", "detailed"]
        if options["footer_style"] not in valid_footer_styles:
            errors.append(f"Invalid footer style: {options['footer_style']}. Must be one of {valid_footer_styles}")
    
    # Validate photo size
    if "photo_size" in options and options.get("include_photo", False):
        valid_photo_sizes = ["small", "medium", "large"]
        if options["photo_size"] not in valid_photo_sizes:
            errors.append(f"Invalid photo size: {options['photo_size']}. Must be one of {valid_photo_sizes}")
    
    # Validate hyperlink color
    if "hyperlink_color" in options and options.get("enable_hyperlinks", False):
        hex_pattern = r'^#[0-9A-Fa-f]{6}$'
        if not re.match(hex_pattern, options["hyperlink_color"]):
            errors.append(f"Invalid hyperlink color: {options['hyperlink_color']}. Must be a valid hex color code (e.g., #0000EE)")
    
    return len(errors) == 0, errors
