#!/usr/bin/env python3
"""
CV Generator - Dynamically generate LaTeX CVs from JSON or text input files.

This script takes a JSON or structured text file containing CV data and generates
a LaTeX CV using the Awesome-CV template.
"""

import os
import json
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from formatting_utils import apply_formatting_to_cv_data


class CVGenerator:
    """Generate LaTeX CVs from structured data."""

    def __init__(self, template_dir: str = "../build"):
        """
        Initialize the CV Generator.
        
        Args:
            template_dir: Directory containing the Awesome-CV template files
        """
        self.template_dir = Path(template_dir)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Ensure template directory exists
        if not self.template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {template_dir}")
        
        # Load the main template
        self.main_template_path = self.template_dir / "resume.tex"
        if not self.main_template_path.exists():
            raise FileNotFoundError(f"Main template file not found: {self.main_template_path}")
        
        with open(self.main_template_path, "r") as f:
            self.main_template = f.read()
    
    def parse_json_input(self, json_file: str) -> Dict[str, Any]:
        """
        Parse a JSON file containing CV data.
        
        Args:
            json_file: Path to the JSON file
            
        Returns:
            Dictionary containing the parsed CV data
        """
        with open(json_file, "r") as f:
            data = json.load(f)
        
        # Apply formatting to the data
        return apply_formatting_to_cv_data(data)
    
    def parse_text_input(self, text_file: str) -> Dict[str, Any]:
        """
        Parse a structured text file containing CV data.
        
        The text file should follow a specific format:
        Section- "Section Name"
        Key- "Value"
        
        Args:
            text_file: Path to the text file
            
        Returns:
            Dictionary containing the parsed CV data
        """
        data = {}
        current_section = None
        current_list = None
        
        with open(text_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Check if this is a section header
                section_match = re.match(r'^([^-]+)-\s*"([^"]*)"$', line)
                if section_match:
                    key = section_match.group(1).strip()
                    value = section_match.group(2).strip()
                    
                    if key.lower() == "section":
                        current_section = value
                        data[current_section] = []
                        current_list = data[current_section]
                    else:
                        if current_section is None:
                            # This is a top-level key-value pair
                            data[key] = value
                        else:
                            # This is a key-value pair within a section
                            if not current_list:
                                current_list = []
                                data[current_section] = current_list
                            
                            # If this is the first item in a new entry, create a new dict
                            if key.lower() in ["company", "organization", "title", "position"]:
                                current_list.append({})
                            
                            if current_list:
                                current_list[-1][key] = value
                
                # Check if this is a list item (bullet point)
                elif line.startswith("- ") and current_section is not None and current_list:
                    item_text = line[2:].strip()
                    if "items" not in current_list[-1]:
                        current_list[-1]["items"] = []
                    current_list[-1]["items"].append(item_text)
        
        # Apply formatting to the data
        return apply_formatting_to_cv_data(data)
    
    def generate_personal_info(self, data: Dict[str, Any]) -> str:
        """
        Generate the personal information section of the CV.
        
        Args:
            data: Dictionary containing the CV data
            
        Returns:
            LaTeX code for the personal information section
        """
        template = []
        
        # Name
        if "FirstName" in data and "LastName" in data:
            template.append(f"\\name{{{data.get('FirstName')}}}{{{data.get('LastName')}}}")
        
        # Position
        if "Position" in data:
            template.append(f"\\position{{{data.get('Position')}}}")
        
        # Address
        if "Address" in data:
            template.append(f"\\address{{{data.get('Address')}}}")
        
        # Contact info
        if "Mobile" in data:
            template.append(f"\\mobile{{{data.get('Mobile')}}}")
        
        if "Email" in data:
            template.append(f"\\email{{{data.get('Email')}}}")
        
        if "Homepage" in data:
            template.append(f"\\homepage{{{data.get('Homepage')}}}")
        
        # Social media
        if "GitHub" in data:
            template.append(f"\\github{{{data.get('GitHub')}}}")
        
        if "LinkedIn" in data:
            template.append(f"\\linkedin{{{data.get('LinkedIn')}}}")
        
        if "Twitter" in data:
            template.append(f"\\twitter{{{data.get('Twitter')}}}")
        
        # Quote
        if "Quote" in data:
            template.append(f"\\quote{{\"{data.get('Quote')}\"}}") 
        
        return "\n".join(template)
    
    def generate_summary(self, data: Dict[str, Any]) -> str:
        """
        Generate the summary section of the CV.
        
        Args:
            data: Dictionary containing the CV data
            
        Returns:
            LaTeX code for the summary section
        """
        if "Summary" not in data:
            return ""
        
        template = [
            "%-------------------------------------------------------------------------------",
            "%\tSECTION TITLE",
            "%-------------------------------------------------------------------------------",
            "\\cvsection{Summary}",
            "",
            "",
            "%-------------------------------------------------------------------------------",
            "%\tCONTENT",
            "%-------------------------------------------------------------------------------",
            "\\begin{cvparagraph}",
            "",
            "%---------------------------------------------------------",
            f"{data.get('Summary', '')}",
            "\\end{cvparagraph}"
        ]
        
        return "\n".join(template)
    
    def generate_experience(self, data: Dict[str, Any]) -> str:
        """
        Generate the experience section of the CV.
        
        Args:
            data: Dictionary containing the CV data
            
        Returns:
            LaTeX code for the experience section
        """
        if "Work Experience" not in data or not data["Work Experience"]:
            return ""
        
        template = [
            "%-------------------------------------------------------------------------------",
            "%\tSECTION TITLE",
            "%-------------------------------------------------------------------------------",
            "\\cvsection{Work Experience}",
            "",
            "",
            "%-------------------------------------------------------------------------------",
            "%\tCONTENT",
            "%-------------------------------------------------------------------------------",
            "\\begin{cventries}"
        ]
        
        for job in data["Work Experience"]:
            template.append("")
            template.append("%---------------------------------------------------------")
            template.append("  \\cventry")
            template.append(f"    {{{job.get('Title', '')}}} % Job title")
            template.append(f"    {{{job.get('Company', '')}}} % Organization")
            template.append(f"    {{{job.get('Location', '')}}} % Location")
            template.append(f"    {{{job.get('Date', '')}}} % Date(s)")
            template.append("    {")
            
            if "items" in job and job["items"]:
                template.append("      \\begin{cvitems} % Description(s) of tasks/responsibilities")
                for item in job["items"]:
                    template.append(f"        \\item {{{item}}}")
                template.append("      \\end{cvitems}")
            
            template.append("    }")
        
        template.append("")
        template.append("%---------------------------------------------------------")
        template.append("\\end{cventries}")
        
        return "\n".join(template)
    
    def generate_education(self, data: Dict[str, Any]) -> str:
        """
        Generate the education section of the CV.
        
        Args:
            data: Dictionary containing the CV data
            
        Returns:
            LaTeX code for the education section
        """
        if "Education" not in data or not data["Education"]:
            return ""
        
        template = [
            "%-------------------------------------------------------------------------------",
            "%\tSECTION TITLE",
            "%-------------------------------------------------------------------------------",
            "\\cvsection{Education}",
            "",
            "",
            "%-------------------------------------------------------------------------------",
            "%\tCONTENT",
            "%-------------------------------------------------------------------------------",
            "\\begin{cventries}"
        ]
        
        for edu in data["Education"]:
            template.append("")
            template.append("%---------------------------------------------------------")
            template.append("  \\cventry")
            template.append(f"    {{{edu.get('Degree', '')}}} % Degree")
            template.append(f"    {{{edu.get('Institution', '')}}} % Institution")
            template.append(f"    {{{edu.get('Location', '')}}} % Location")
            template.append(f"    {{{edu.get('Date', '')}}} % Date(s)")
            template.append("    {")
            
            if "items" in edu and edu["items"]:
                template.append("      \\begin{cvitems} % Description(s)")
                for item in edu["items"]:
                    template.append(f"        \\item {{{item}}}")
                template.append("      \\end{cvitems}")
            
            template.append("    }")
        
        template.append("")
        template.append("%---------------------------------------------------------")
        template.append("\\end{cventries}")
        
        return "\n".join(template)
    
    def generate_skills(self, data: Dict[str, Any]) -> str:
        """
        Generate the skills section of the CV.
        
        Args:
            data: Dictionary containing the CV data
            
        Returns:
            LaTeX code for the skills section
        """
        if "Skills" not in data or not data["Skills"]:
            return ""
        
        template = [
            "%-------------------------------------------------------------------------------",
            "%\tSECTION TITLE",
            "%-------------------------------------------------------------------------------",
            "\\cvsection{Skills}",
            "",
            "",
            "%-------------------------------------------------------------------------------",
            "%\tCONTENT",
            "%-------------------------------------------------------------------------------",
            "\\begin{cvskills}"
        ]
        
        for skill in data["Skills"]:
            template.append("")
            template.append("%---------------------------------------------------------")
            template.append("  \\cvskill")
            template.append(f"    {{{skill.get('Category', '')}}} % Category")
            template.append(f"    {{{skill.get('Skills', '')}}} % Skills")
        
        template.append("")
        template.append("%---------------------------------------------------------")
        template.append("\\end{cvskills}")
        
        return "\n".join(template)
    
    def generate_certificates(self, data: Dict[str, Any]) -> str:
        """
        Generate the certificates section of the CV.
        
        Args:
            data: Dictionary containing the CV data
            
        Returns:
            LaTeX code for the certificates section
        """
        if "Certificates" not in data or not data["Certificates"]:
            return ""
        
        template = [
            "%-------------------------------------------------------------------------------",
            "%\tSECTION TITLE",
            "%-------------------------------------------------------------------------------",
            "\\cvsection{Certificates}",
            "",
            "",
            "%-------------------------------------------------------------------------------",
            "%\tCONTENT",
            "%-------------------------------------------------------------------------------",
            "\\begin{cventries}"
        ]
        
        for cert in data["Certificates"]:
            template.append("")
            template.append("%---------------------------------------------------------")
            template.append("  \\cventry")
            template.append(f"    {{{cert.get('Name', '')}}} % Certificate name")
            template.append(f"    {{{cert.get('Issuer', '')}}} % Issuer")
            template.append(f"    {{{cert.get('Location', '')}}} % Location")
            template.append(f"    {{{cert.get('Date', '')}}} % Date(s)")
            template.append("    {")
            
            if "items" in cert and cert["items"]:
                template.append("      \\begin{cvitems} % Description(s)")
                for item in cert["items"]:
                    template.append(f"        \\item {{{item}}}")
                template.append("      \\end{cvitems}")
            
            template.append("    }")
        
        template.append("")
        template.append("%---------------------------------------------------------")
        template.append("\\end{cventries}")
        
        return "\n".join(template)
    
    def generate_honors(self, data: Dict[str, Any]) -> str:
        """
        Generate the honors section of the CV.
        
        Args:
            data: Dictionary containing the CV data
            
        Returns:
            LaTeX code for the honors section
        """
        if "Honors" not in data or not data["Honors"]:
            return ""
        
        template = [
            "%-------------------------------------------------------------------------------",
            "%\tSECTION TITLE",
            "%-------------------------------------------------------------------------------",
            "\\cvsection{Honors \\& Awards}",
            "",
            "",
            "%-------------------------------------------------------------------------------",
            "%\tCONTENT",
            "%-------------------------------------------------------------------------------",
            "\\begin{cvhonors}"
        ]
        
        for honor in data["Honors"]:
            template.append("")
            template.append("%---------------------------------------------------------")
            template.append("  \\cvhonor")
            template.append(f"    {{{honor.get('Name', '')}}} % Award")
            template.append(f"    {{{honor.get('Issuer', '')}}} % Event")
            template.append(f"    {{{honor.get('Location', '')}}} % Location")
            template.append(f"    {{{honor.get('Date', '')}}} % Date(s)")
        
        template.append("")
        template.append("%---------------------------------------------------------")
        template.append("\\end{cvhonors}")
        
        return "\n".join(template)
    
    def generate_cv(self, data: Dict[str, Any], output_filename: str = "resume") -> str:
        """
        Generate a complete LaTeX CV from the provided data.
        
        Args:
            data: Dictionary containing the CV data
            output_filename: Name of the output file (without extension)
            
        Returns:
            Path to the generated LaTeX file
        """
        # Create section files
        sections = {}
        
        # Generate summary section
        summary_content = self.generate_summary(data)
        if summary_content:
            sections["summary"] = summary_content
        
        # Generate experience section
        experience_content = self.generate_experience(data)
        if experience_content:
            sections["experience"] = experience_content
        
        # Generate education section
        education_content = self.generate_education(data)
        if education_content:
            sections["education"] = education_content
        
        # Generate skills section
        skills_content = self.generate_skills(data)
        if skills_content:
            sections["skills"] = skills_content
        
        # Generate certificates section
        certificates_content = self.generate_certificates(data)
        if certificates_content:
            sections["certificates"] = certificates_content
        
        # Generate honors section
        honors_content = self.generate_honors(data)
        if honors_content:
            sections["honors"] = honors_content
        
        # Create output directory for sections
        sections_dir = self.output_dir / "resume"
        sections_dir.mkdir(exist_ok=True)
        
        # Write section files
        for section_name, content in sections.items():
            with open(sections_dir / f"{section_name}.tex", "w") as f:
                f.write(content)
        
        # Copy the awesome-cv.cls file to the output directory
        with open(self.template_dir / "awesome-cv.cls", "r") as src:
            with open(self.output_dir / "awesome-cv.cls", "w") as dst:
                dst.write(src.read())
        
        # Modify the main template with personal information
        main_content = self.main_template
        
        # Replace personal information
        personal_info_start = main_content.find("%\tPERSONAL INFORMATION")
        personal_info_end = main_content.find("\\quote{")
        
        if personal_info_start != -1 and personal_info_end != -1:
            # Find the end of the quote line
            quote_end = main_content.find("\n\n", personal_info_end)
            if quote_end != -1:
                # Replace the personal information section
                personal_info = self.generate_personal_info(data)
                main_content = (
                    main_content[:personal_info_start] +
                    "%\tPERSONAL INFORMATION\n%\tComment any of the lines below if they are not required\n%-------------------------------------------------------------------------------\n" +
                    personal_info +
                    main_content[quote_end:]
                )
        
        # Replace the input section with our generated sections
        input_start = main_content.find("\\input{resume/summary.tex}")
        if input_start != -1:
            input_end = main_content.find("\\end{document}")
            if input_end != -1:
                # Find the beginning of the line containing \end{document}
                end_doc_start = main_content.rfind("\n\n", 0, input_end)
                if end_doc_start != -1:
                    # Create the input section
                    input_section = "\n"
                    for section_name in sections:
                        input_section += f"\\input{{resume/{section_name}.tex}}\n"
                    
                    main_content = (
                        main_content[:input_start] +
                        input_section +
                        main_content[end_doc_start:]
                    )
        
        # Write the main LaTeX file
        output_path = self.output_dir / f"{output_filename}.tex"
        with open(output_path, "w") as f:
            f.write(main_content)
        
        return str(output_path)
    
    def compile_latex(self, latex_file: str) -> str:
        """
        Compile the LaTeX file to PDF.
        
        Args:
            latex_file: Path to the LaTeX file
            
        Returns:
            Path to the generated PDF file
        """
        latex_path = Path(latex_file)
        output_dir = latex_path.parent
        
        # Run xelatex to compile the LaTeX file
        os.system(f"cd {output_dir} && xelatex {latex_path.name}")
        
        # Return the path to the PDF file
        pdf_path = output_dir / f"{latex_path.stem}.pdf"
        if pdf_path.exists():
            return str(pdf_path)
        else:
            raise FileNotFoundError(f"PDF file not generated: {pdf_path}")


def main():
    """Main entry point for the CV generator."""
    parser = argparse.ArgumentParser(description="Generate a LaTeX CV from JSON or text input.")
    parser.add_argument("input_file", help="Path to the input file (JSON or text)")
    parser.add_argument("--output", "-o", default="resume", help="Name of the output file (without extension)")
    parser.add_argument("--template-dir", "-t", default="../build", help="Directory containing the Awesome-CV template files")
    parser.add_argument("--compile", "-c", action="store_true", help="Compile the LaTeX file to PDF")
    
    args = parser.parse_args()
    
    # Create the CV generator
    generator = CVGenerator(template_dir=args.template_dir)
    
    # Parse the input file
    if args.input_file.endswith(".json"):
        data = generator.parse_json_input(args.input_file)
    else:
        data = generator.parse_text_input(args.input_file)
    
    # Generate the CV
    latex_file = generator.generate_cv(data, output_filename=args.output)
    print(f"LaTeX file generated: {latex_file}")
    
    # Compile the LaTeX file if requested
    if args.compile:
        try:
            pdf_file = generator.compile_latex(latex_file)
            print(f"PDF file generated: {pdf_file}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("Make sure xelatex is installed and in your PATH.")


if __name__ == "__main__":
    main()
