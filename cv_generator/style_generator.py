#!/usr/bin/env python3
"""
CV Style Generator - Generate CVs with different styles.

This script demonstrates how to generate CVs with different color schemes
using the Awesome-CV template.
"""

import os
import shutil
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Optional

from style_library import get_all_styles


def generate_styled_cv(input_file: str, output_dir: str, styles: Optional[List[str]] = None) -> None:
    """
    Generate CVs with different styles.
    
    Args:
        input_file: Path to the input file (JSON or text)
        output_dir: Directory to store the generated CVs
        styles: List of styles to use (if None, uses all available styles)
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Get the template directory
    template_dir = Path("../build")
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")
    
    # Get the awesome-cv.cls file
    cls_file = template_dir / "awesome-cv.cls"
    if not cls_file.exists():
        raise FileNotFoundError(f"Awesome-CV class file not found: {cls_file}")
    
    # Read the class file
    with open(cls_file, "r") as f:
        cls_content = f.read()
    
    # Get all available styles
    all_styles = get_all_styles()
    
    # If no styles are specified, use all available styles
    if styles is None:
        styles = list(all_styles.keys())
    
    # Generate a CV for each style
    for style in styles:
        # Skip if style is not in our library
        if style not in all_styles:
            print(f"Warning: Style '{style}' not found in style library. Skipping.")
            continue
            
        # Create a directory for this style
        style_dir = output_path / style
        style_dir.mkdir(exist_ok=True)
        
        # Copy the template files
        for file in template_dir.glob("*"):
            if file.is_file():
                shutil.copy(file, style_dir)
        
        # Modify the awesome-cv.cls file to use the custom style
        style_cls_content = cls_content
        
        # Check if it's a standard style or a custom style
        if style in ["emerald", "skyblue", "red", "pink", "orange", "nephritis", "concrete", "darknight"]:
            # Standard style - just change the colorlet line
            style_cls_content = style_cls_content.replace(
                "\\colorlet{awesome}{awesome-red}",
                f"\\colorlet{{awesome}}{{awesome-{style}}}"
            )
        else:
            # Custom style - need to add a new color definition and use it
            hex_color = all_styles[style]
            
            # Find the awesome colors section
            awesome_colors_start = style_cls_content.find("% Awesome colors")
            if awesome_colors_start == -1:
                # If we can't find the section, find the last color definition
                awesome_colors_start = style_cls_content.find("\\definecolor{awesome-darknight}")
            
            # Find the end of the awesome colors section
            awesome_colors_end = style_cls_content.find("\\colorlet{awesome}", awesome_colors_start)
            
            # Add our new color definition before the colorlet line
            new_color_def = f"\\definecolor{{awesome-{style}}}{{HTML}}{{{hex_color.replace('#', '')}}}\n"
            
            # Insert the new color definition
            style_cls_content = (
                style_cls_content[:awesome_colors_end] + 
                new_color_def + 
                style_cls_content[awesome_colors_end:]
            )
            
            # Change the colorlet line
            style_cls_content = style_cls_content.replace(
                "\\colorlet{awesome}{awesome-red}",
                f"\\colorlet{{awesome}}{{awesome-{style}}}"
            )
        
        # Write the modified class file
        with open(style_dir / "awesome-cv.cls", "w") as f:
            f.write(style_cls_content)
        
        # Generate the CV
        cmd = [
            "python", "cv_generator.py",
            input_file,
            "--output", f"{style}_resume",
            "--template-dir", str(style_dir),
            "--compile"
        ]
        
        subprocess.run(cmd, check=True)
        
        # Move the generated files to the style directory
        for ext in [".tex", ".pdf"]:
            src = Path(f"output/{style}_resume{ext}")
            if src.exists():
                shutil.copy(src, style_dir)
        
        print(f"Generated CV with {style} style: {style_dir}/{style}_resume.pdf")


def main():
    """Main entry point for the style generator."""
    parser = argparse.ArgumentParser(description="Generate CVs with different styles.")
    parser.add_argument("input_file", help="Path to the input file (JSON or text)")
    parser.add_argument("--output-dir", "-o", default="styled_output", help="Directory to store the generated CVs")
    parser.add_argument("--styles", "-s", nargs="+", default=None, help="Styles to use (if not specified, uses all available styles)")
    
    args = parser.parse_args()
    
    generate_styled_cv(args.input_file, args.output_dir, args.styles)


if __name__ == "__main__":
    main()
