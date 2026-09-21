import customtkinter as ctk
from tkinter import messagebox
from datetime import date, timedelta
from controllers.calendar_controller import CalendarController
from themes.dark_theme import COLORS, font_body, font_heading
from views.page_common import title, card, section_label

class CalendarView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLORS["background"])
        self.c=CalendarController(); self.current=date.today(); self._build(); self.load()
    def _build(self):
        title(self,"Calendar","Daily notes, mood and time snapshots.")
        bar=ctk.CTkFrame(self,fg_color="transparent"); bar.pack(fill="x",padx=28,pady=(4,10))
        ctk.CTkButton(bar,text="‹",width=42,height=36,command=lambda:self.move(-1)).pack(side="left")
        self.date_label=ctk.CTkLabel(bar,text="",font=font_heading("bold"),text_color=COLORS["text_primary"])
        self.date_label.pack(side="left",padx=16)
        ctk.CTkButton(bar,text="›",width=42,height=36,command=lambda:self.move(1)).pack(side="left")
        f=card(self); f.pack(fill="both",expand=True,padx=28,pady=10)
        section_label(f,"Daily snapshot").pack(anchor="w",padx=20,pady=(18,4))
        self.mood=ctk.CTkComboBox(f,values=["","great","good","okay","bad"],font=font_body(),height=38); self.mood.pack(fill="x",padx=20,pady=(6,10))
        self.notes=ctk.CTkTextbox(f,height=180,font=font_body(),fg_color=COLORS["surface_alt"],border_color=COLORS["border"],border_width=1,text_color=COLORS["text_primary"]); self.notes.pack(fill="both",expand=True,padx=20,pady=8)
        row=ctk.CTkFrame(f,fg_color="transparent"); row.pack(fill="x",padx=20,pady=(8,20))
        self.studied=ctk.CTkEntry(row,placeholder_text="Hours studied",font=font_body(),height=38); self.studied.pack(side="left",expand=True,fill="x",padx=(0,6))
        self.worked=ctk.CTkEntry(row,placeholder_text="Hours worked",font=font_body(),height=38); self.worked.pack(side="left",expand=True,fill="x",padx=6)
        ctk.CTkButton(row,text="Save Day",font=font_body(),height=38,command=self.save).pack(side="left",padx=(6,0))
    def move(self,n): self.current+=timedelta(days=n); self.load()
    def load(self):
        self.date_label.configure(text=self.current.strftime("%A, %B %d, %Y"))
        r=self.c.get_day(self.current.isoformat())
        self.mood.set(r.get("mood") or ""); self.notes.delete("1.0","end"); self.notes.insert("1.0",r.get("notes") or "")
        self.studied.delete(0,"end"); self.studied.insert(0,str(r.get("hours_studied") or 0))
        self.worked.delete(0,"end"); self.worked.insert(0,str(r.get("hours_worked") or 0))
    def save(self):
        try: s=float(self.studied.get() or 0); w=float(self.worked.get() or 0)
        except ValueError: messagebox.showerror("Invalid input","Study and work hours must be valid numbers."); return
        if not self.c.save_day(self.current.isoformat(),self.mood.get(),self.notes.get("1.0","end").strip(),s,w):
            messagebox.showerror("Invalid input","Hours cannot be negative.")
