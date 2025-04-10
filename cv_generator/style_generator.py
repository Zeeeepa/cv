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
from typing import List


def generate_styled_cv(input_file: str, output_dir: str, styles: List[str]) -> None:
    """
    Generate CVs with different styles.
    
    Args:
        input_file: Path to the input file (JSON or text)
        output_dir: Directory to store the generated CVs
        styles: List of styles to use
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
    
    # Generate a CV for each style
    for style in styles:
        # Create a directory for this style
        style_dir = output_path / style
        style_dir.mkdir(exist_ok=True)
        
        # Copy the template files
        for file in template_dir.glob("*"):
            if file.is_file():
                shutil.copy(file, style_dir)
        
        # Modify the awesome-cv.cls file
        style_cls_content = cls_content.replace(
            "\\colorlet{awesome}{awesome-red}",
            f"\\colorlet{{awesome}}{{awesome-{style}}}"
        )
        
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
    parser.add_argument("--styles", "-s", nargs="+", default=["emerald", "skyblue", "red", "pink", "orange", "nephritis", "concrete", "darknight"], help="Styles to use")
    
    args = parser.parse_args()
    
    generate_styled_cv(args.input_file, args.output_dir, args.styles)


if __name__ == "__main__":
    main()
