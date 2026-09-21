import customtkinter as ctk
from tkinter import messagebox
from controllers.study_controller import StudyController
from themes.dark_theme import COLORS, font_body, font_heading
from views.page_common import title,card,empty_state

class StudyView(ctk.CTkFrame):
    def __init__(self,master):
        super().__init__(master,fg_color=COLORS["background"]); self.c=StudyController(); self._build()
    def _build(self):
        title(self,"Study Tracker","Log study time by category.")
        f=card(self); f.pack(fill="x",padx=28,pady=10)
        self.cat=ctk.CTkComboBox(f,values=["University","Freelancing","AI","Reading"],font=font_body(),height=38); self.cat.set("University"); self.cat.pack(side="left",padx=16,pady=18)
        self.hours=ctk.CTkEntry(f,placeholder_text="Hours",font=font_body(),height=38); self.hours.pack(side="left",padx=8,pady=18)
        ctk.CTkButton(f,text="Add Study Log",font=font_body(),height=38,command=self._add).pack(side="left",padx=8)
        self.summary=ctk.CTkLabel(self,text="",font=font_body("bold"),text_color=COLORS["text_primary"]); self.summary.pack(anchor="w",padx=28,pady=(4,8))
        self.list=ctk.CTkScrollableFrame(self,fg_color="transparent"); self.list.pack(fill="both",expand=True,padx=28,pady=(0,12)); self.refresh()
    def refresh(self):
        s=self.c.stats(); self.summary.configure(text=f'Today · {s["total_hours"]:.2f} hours')
        for w in self.list.winfo_children(): w.destroy()
        recent=self.c.recent()
        if not recent:
            empty_state(self.list,"No study logs yet","Log your first session using the form above.").pack(fill="x",pady=5)
            return
        for r in recent:
            f=card(self.list); f.pack(fill="x",pady=5); ctk.CTkLabel(f,text=f'{r["log_date"]}  ·  {r["category"]}  ·  {r["hours"]:.2f} h',font=font_body()).pack(anchor="w",padx=16,pady=12)
    def _add(self):
        if self.c.add(self.cat.get(),self.hours.get()): self.hours.delete(0,"end"); self.refresh()
        else: messagebox.showerror("Invalid input","Enter a positive number of hours.")
