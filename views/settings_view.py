import customtkinter as ctk
from tkinter import messagebox
from controllers.settings_controller import SettingsController
from themes.dark_theme import COLORS, font_body, font_heading
from views.page_common import title, card, section_label

class SettingsView(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["background"],
                         scrollbar_button_color=COLORS["surface_alt"],
                         scrollbar_button_hover_color=COLORS["border"])
        self.c = SettingsController()
        self._build()

    def _build(self):
        title(self, "Settings", "Application information and database tools.")
        i = self.c.info()

        info = card(self)
        info.pack(fill="x", padx=28, pady=(4, 10))
        ctk.CTkLabel(info, text="Application", font=font_heading(),
                     text_color=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(20, 4))
        ctk.CTkLabel(info, text=f"Momentum {i['version']}", font=font_body(),
                     text_color=COLORS["text_secondary"]).pack(anchor="w", padx=20, pady=(0, 8))
        ctk.CTkLabel(info, text=f"Database: {i['database']}", font=font_body(),
                     text_color=COLORS["text_secondary"]).pack(anchor="w", padx=20, pady=(0, 20))

        tools = card(self)
        tools.pack(fill="x", padx=28, pady=(0, 24))
        ctk.CTkLabel(tools, text="Database & Maintenance", font=font_heading(),
                     text_color=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(20, 4))
        ctk.CTkLabel(tools, text="Create a safe backup of your current Momentum database.",
                     font=font_body(), text_color=COLORS["text_secondary"]).pack(anchor="w", padx=20, pady=(0, 12))
        ctk.CTkButton(tools, text="Create Backup Now", height=38,
                      command=self.backup).pack(anchor="w", padx=20, pady=(0, 20))

    def backup(self):
        try:
            p = self.c.backup()
            messagebox.showinfo("Backup created", str(p))
        except Exception as e:
            messagebox.showerror("Backup failed", str(e))
