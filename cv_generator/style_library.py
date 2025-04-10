#!/usr/bin/env python3
"""
CV Style Library - A comprehensive collection of CV styles.

This module provides a large collection of professionally designed color schemes
for the CV Generator. It includes both the standard Awesome-CV styles and many
additional custom styles.
"""

from typing import Dict, List, Tuple
import random

# Standard Awesome-CV styles
STANDARD_STYLES = {
    "emerald": "#00A388",
    "skyblue": "#0395DE",
    "red": "#DC3522",
    "pink": "#EF4089",
    "orange": "#FF6138",
    "nephritis": "#27AE60",
    "concrete": "#95A5A6",
    "darknight": "#131A28"
}

# Extended color library - professionally curated colors
EXTENDED_STYLES = {
    # Blues
    "royal-blue": "#4169E1",
    "navy": "#000080",
    "azure": "#007FFF",
    "cobalt": "#0047AB",
    "teal": "#008080",
    "turquoise": "#40E0D0",
    "cerulean": "#007BA7",
    "steel-blue": "#4682B4",
    
    # Greens
    "forest": "#228B22",
    "mint": "#98FB98",
    "olive": "#808000",
    "sage": "#BCB88A",
    "lime": "#32CD32",
    "hunter": "#355E3B",
    "jade": "#00A86B",
    
    # Reds/Pinks
    "crimson": "#DC143C",
    "ruby": "#E0115F",
    "maroon": "#800000",
    "coral": "#FF7F50",
    "salmon": "#FA8072",
    "burgundy": "#800020",
    "rose": "#FF007F",
    
    # Purples
    "violet": "#8F00FF",
    "lavender": "#B57EDC",
    "plum": "#8E4585",
    "magenta": "#FF00FF",
    "amethyst": "#9966CC",
    "indigo": "#4B0082",
    "orchid": "#DA70D6",
    
    # Browns/Neutrals
    "chocolate": "#7B3F00",
    "coffee": "#6F4E37",
    "tan": "#D2B48C",
    "sienna": "#A0522D",
    "mocha": "#A38068",
    "khaki": "#C3B091",
    "beige": "#F5F5DC",
    
    # Yellows/Oranges
    "amber": "#FFBF00",
    "gold": "#FFD700",
    "bronze": "#CD7F32",
    "honey": "#E6C700",
    "tangerine": "#F28500",
    "apricot": "#FBCEB1",
    "marigold": "#EAA221",
    
    # Grays/Blacks
    "charcoal": "#36454F",
    "slate": "#708090",
    "graphite": "#464646",
    "silver": "#C0C0C0",
    "onyx": "#353839",
    "jet": "#343434",
    "ebony": "#555D50"
}

# Combine standard and extended styles
ALL_STYLES: Dict[str, str] = {**STANDARD_STYLES, **EXTENDED_STYLES}

# Group styles by color family for better organization
COLOR_FAMILIES: Dict[str, List[str]] = {
    "Blues": ["skyblue", "royal-blue", "navy", "azure", "cobalt", "teal", "turquoise", "cerulean", "steel-blue"],
    "Greens": ["emerald", "nephritis", "forest", "mint", "olive", "sage", "lime", "hunter", "jade"],
    "Reds & Pinks": ["red", "pink", "crimson", "ruby", "maroon", "coral", "salmon", "burgundy", "rose"],
    "Purples": ["violet", "lavender", "plum", "magenta", "amethyst", "indigo", "orchid"],
    "Browns & Neutrals": ["chocolate", "coffee", "tan", "sienna", "mocha", "khaki", "beige"],
    "Yellows & Oranges": ["orange", "amber", "gold", "bronze", "honey", "tangerine", "apricot", "marigold"],
    "Grays & Blacks": ["concrete", "darknight", "charcoal", "slate", "graphite", "silver", "onyx", "jet", "ebony"]
}

def get_all_styles() -> Dict[str, str]:
    """
    Get all available styles.
    
    Returns:
        Dict[str, str]: Dictionary of style names and their hex color codes
    """
    return ALL_STYLES

def get_style_families() -> Dict[str, List[str]]:
    """
    Get styles organized by color family.
    
    Returns:
        Dict[str, List[str]]: Dictionary of color families and their style names
    """
    return COLOR_FAMILIES

def get_random_style() -> Tuple[str, str]:
    """
    Get a random style from the library.
    
    Returns:
        Tuple[str, str]: A tuple containing (style_name, hex_color)
    """
    style_name = random.choice(list(ALL_STYLES.keys()))
    return style_name, ALL_STYLES[style_name]

def get_random_style_from_family(family: str) -> Tuple[str, str]:
    """
    Get a random style from a specific color family.
    
    Args:
        family: The name of the color family
        
    Returns:
        Tuple[str, str]: A tuple containing (style_name, hex_color)
    """
    if family not in COLOR_FAMILIES:
        raise ValueError(f"Unknown color family: {family}")
    
    style_name = random.choice(COLOR_FAMILIES[family])
    return style_name, ALL_STYLES[style_name]
