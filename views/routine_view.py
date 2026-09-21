import customtkinter as ctk
from tkinter import messagebox
from controllers.routine_controller import RoutineController
from themes.dark_theme import COLORS, font_body, font_heading
from views.page_common import title, card

class RoutineView(ctk.CTkFrame):
    def __init__(self,master):
        super().__init__(master,fg_color=COLORS["background"]); self.c=RoutineController(); self.rows={}; self._build()
    def _build(self):
        title(self,"Daily Routine","Complete today's routine and build consistency.")
        top=ctk.CTkFrame(self,fg_color="transparent"); top.pack(fill="x",padx=28,pady=4)
        ctk.CTkButton(top,text="＋ Add Routine Item",height=38,command=self._add).pack(side="right")
        self.list=ctk.CTkScrollableFrame(self,fg_color="transparent"); self.list.pack(fill="both",expand=True,padx=28,pady=12)
        self.refresh()
    def refresh(self):
        for w in self.list.winfo_children(): w.destroy()
        self.rows={}
        items=self.c.items(); done=sum(x["is_completed"] for x in items)
        ctk.CTkLabel(self.list,text=f"Today: {done}/{len(items)} completed",font=font_body(),text_color=COLORS["text_secondary"]).pack(anchor="w",pady=(0,10))
        for item in items:
            f=card(self.list); f.pack(fill="x",pady=5);
            var=ctk.BooleanVar(value=bool(item["is_completed"]))
            cb=ctk.CTkCheckBox(f,text=item["name"],variable=var,font=font_body(),text_color=COLORS["text_secondary"] if item["is_completed"] else COLORS["text_primary"],fg_color=COLORS["accent"],hover_color=COLORS["accent"],border_color=COLORS["border"],corner_radius=6,command=lambda i=item["id"],v=var:self._toggle(i,v)); cb.pack(side="left",padx=16,pady=14)
            ctk.CTkLabel(f,text=f'{item["period"].title()} · {item["est_minutes"]} min · {item["priority"]}',font=font_body(),text_color=COLORS["text_secondary"]).pack(side="right",padx=16)
    def _toggle(self,i,v): self.c.toggle(i,not v.get()); self.refresh()  # var is already flipped by the widget; service expects the previous state
    def _add(self):
        win=ctk.CTkToplevel(self); win.title("Add Routine Item"); win.geometry("420x330"); win.transient(self.winfo_toplevel()); win.grab_set()
        name=ctk.CTkEntry(win,placeholder_text="Routine item name",font=font_body(),height=38); name.pack(fill="x",padx=24,pady=(28,10))
        period=ctk.CTkComboBox(win,values=["morning","afternoon","evening","night"],font=font_body(),height=38); period.set("morning"); period.pack(fill="x",padx=24,pady=10)
        mins=ctk.CTkEntry(win,placeholder_text="Estimated minutes",font=font_body(),height=38); mins.pack(fill="x",padx=24,pady=10)
        priority=ctk.CTkComboBox(win,values=["low","medium","high"],font=font_body(),height=38); priority.set("medium"); priority.pack(fill="x",padx=24,pady=10)
        def save():
            if self.c.service.add_item(name.get(),period.get(),mins.get() or 0,priority.get()): win.destroy(); self.refresh()
            else: messagebox.showerror("Invalid","Enter a routine name.",parent=win)
        ctk.CTkButton(win,text="Save",height=38,command=save).pack(pady=18)
