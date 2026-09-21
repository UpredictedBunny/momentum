import customtkinter as ctk
from tkinter import messagebox
from controllers.goals_controller import GoalsController
from themes.dark_theme import COLORS, font_body, font_heading
from views.page_common import title,card,empty_state

class GoalsView(ctk.CTkFrame):
    def __init__(self,master): super().__init__(master,fg_color=COLORS['background']); self.c=GoalsController(); self._jobs={}; self._build()
    def _build(self):
        title(self,'Goals','Track progress toward meaningful outcomes.')
        top=ctk.CTkFrame(self,fg_color='transparent'); top.pack(fill='x',padx=28); ctk.CTkButton(top,text='＋ Add Goal',height=38,command=self.add).pack(side='right')
        self.list=ctk.CTkScrollableFrame(self,fg_color='transparent'); self.list.pack(fill='both',expand=True,padx=28,pady=12); self.refresh()
    def refresh(self):
        for w in self.list.winfo_children():w.destroy()
        self._jobs.clear()
        goals=self.c.all()
        if not goals:
            empty_state(self.list,'No goals yet','Use “Add Goal” to set your first target.').pack(fill='x',pady=5); return
        for g in goals:
            f=card(self.list); f.pack(fill='x',pady=5)
            ctk.CTkLabel(f,text=g['name'],font=font_heading(),text_color=COLORS['text_primary']).pack(anchor='w',padx=15,pady=(12,4))
            meta=ctk.CTkLabel(f,text=self._meta(g['progress_pct'],g['deadline']),font=font_body(),text_color=COLORS['text_secondary']); meta.pack(anchor='w',padx=15)
            slider=ctk.CTkSlider(f,from_=0,to=100,command=lambda v,i=g['id'],l=meta,d=g['deadline']:self._on_slide(i,v,l,d))
            slider.set(g['progress_pct']); slider.pack(fill='x',padx=15,pady=12)
    @staticmethod
    def _meta(pct,deadline): return f'{float(pct):.0f}% · deadline {deadline or "—"}'
    def _on_slide(self,gid,value,label,deadline):
        """Update the label immediately; commit to the DB only once the drag settles."""
        label.configure(text=self._meta(value,deadline))
        job=self._jobs.get(gid)
        if job is not None:
            try: self.after_cancel(job)
            except Exception: pass
        self._jobs[gid]=self.after(250,lambda: self._commit(gid,value))
    def _commit(self,gid,value):
        self._jobs.pop(gid,None); self.c.update_progress(gid,value)
    def add(self):
        win=ctk.CTkToplevel(self); win.title('Add Goal'); win.geometry('420x220'); win.transient(self.winfo_toplevel()); win.grab_set()
        n=ctk.CTkEntry(win,placeholder_text='Goal name',height=38); n.pack(fill='x',padx=24,pady=(25,10)); d=ctk.CTkEntry(win,placeholder_text='Deadline YYYY-MM-DD (optional)',height=38); d.pack(fill='x',padx=24,pady=10)
        def save():
            if self.c.add(n.get(),d.get()): win.destroy(); self.refresh()
            else: messagebox.showerror('Invalid','Enter a goal name.',parent=win)
        ctk.CTkButton(win,text='Save',height=38,command=save).pack(pady=15)
        n.focus_set()
