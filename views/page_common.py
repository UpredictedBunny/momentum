import customtkinter as ctk
from themes.dark_theme import COLORS, font_body, font_heading, CORNER_RADIUS

PAGE_PAD = 28
SECTION_GAP = 16

def title(master, text, subtitle=None):
    frame = ctk.CTkFrame(master, fg_color="transparent")
    frame.pack(fill="x", padx=PAGE_PAD, pady=(24, 10))
    frame.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(frame, text=text, font=font_heading("bold"),
                 text_color=COLORS["text_primary"], anchor="w").grid(
                     row=0, column=0, sticky="w")
    if subtitle:
        ctk.CTkLabel(frame, text=subtitle, font=font_body(),
                     text_color=COLORS["text_secondary"], anchor="w").grid(
                         row=1, column=0, sticky="w", pady=(4, 0))
    return frame

def section_label(master, text):
    return ctk.CTkLabel(master, text=text.upper(), font=font_body("bold"),
                        text_color=COLORS["text_secondary"], anchor="w")

def card(master, **kwargs):
    return ctk.CTkFrame(
        master,
        fg_color=COLORS["surface"],
        corner_radius=CORNER_RADIUS,
        border_width=1,
        border_color=COLORS["border"],
        **kwargs,
    )

def empty_state(master, title_text="Nothing here yet", detail="Add something to get started."):
    frame = card(master)
    ctk.CTkLabel(frame, text=title_text, font=font_heading(),
                 text_color=COLORS["text_primary"]).pack(pady=(28, 6), padx=20)
    ctk.CTkLabel(frame, text=detail, font=font_body(),
                 text_color=COLORS["text_secondary"]).pack(pady=(0, 28), padx=20)
    return frame
