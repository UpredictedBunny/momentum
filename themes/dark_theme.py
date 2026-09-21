"""
dark_theme.py
-------------
Single source of truth for colors, fonts, and CustomTkinter appearance
settings. Views import COLORS and FONTS from here instead of hardcoding
hex codes, so re-skinning the app later means editing one file.

All actual color/font values are pulled from config.json via settings,
so the palette itself is still configurable without touching this file.
"""

from __future__ import annotations

import customtkinter as ctk

from config.settings import settings

# --- Palette -----------------------------------------------------
COLORS = {
    "background": "#0F1115",
    "surface": "#171A21",
    "surface_alt": "#1E222B",
    "border": "#272B35",
    "text_primary": "#F5F6F8",
    "text_secondary": "#9CA3AF",
    "accent": settings.theme.accent,        # #4F8EF7
    "secondary": settings.theme.secondary,  # #22C55E
    "danger": settings.theme.danger,        # #EF4444
    "secondary_hover": "#16A34A",           # pressed/hover state for secondary
    "warning": "#F59E0B",                   # streak flame / amber accents
    "accent_alt": "#A78BFA",                # study + secondary highlights
    "on_accent": "#000000",                 # text drawn on top of a filled accent
}

# --- Typography ----------------------------------------------------
FONTS = {
    "family": settings.theme.font_family,
    "body_size": settings.theme.font_size_body,
    "heading_size": settings.theme.font_size_heading,
}

CORNER_RADIUS = settings.theme.corner_radius


def font_body(weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONTS["family"], size=FONTS["body_size"], weight=weight)


def font_heading(weight: str = "bold") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONTS["family"], size=FONTS["heading_size"], weight=weight)

def font_display(size: int = 48, weight: str = "bold") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONTS["family"], size=size, weight=weight)


def apply_appearance() -> None:
    """Call once at startup, before creating any CTk widgets."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")  # base theme; we override per-widget with COLORS
