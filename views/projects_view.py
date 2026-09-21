import customtkinter as ctk
from tkinter import messagebox
from controllers.projects_controller import ProjectsController
from themes.dark_theme import COLORS, font_body, font_heading
from views.page_common import title,card,empty_state

class ProjectsView(ctk.CTkFrame):
    def __init__(self,master): super().__init__(master,fg_color=COLORS['background']); self.c=ProjectsController(); self._jobs={}; self._build()
    def _build(self):
        title(self,'Projects','Track active projects and progress.')
        top=ctk.CTkFrame(self,fg_color='transparent'); top.pack(fill='x',padx=28); ctk.CTkButton(top,text='＋ Add Project',height=38,command=self.add).pack(side='right')
        self.list=ctk.CTkScrollableFrame(self,fg_color='transparent'); self.list.pack(fill='both',expand=True,padx=28,pady=12); self.refresh()
    def refresh(self):
        for w in self.list.winfo_children():w.destroy()
        self._jobs.clear()
        projects=self.c.all()
        if not projects:
            empty_state(self.list,'No projects yet','Use “Add Project” to start tracking one.').pack(fill='x',pady=5); return
        for p in projects:
            f=card(self.list); f.pack(fill='x',pady=5)
            ctk.CTkLabel(f,text=p['name'],font=font_heading(),text_color=COLORS['text_primary']).pack(anchor='w',padx=15,pady=(12,4))
            meta=ctk.CTkLabel(f,text=self._meta(p['progress_pct'],p['deadline']),font=font_body(),text_color=COLORS['text_secondary']); meta.pack(anchor='w',padx=15)
            sl=ctk.CTkSlider(f,from_=0,to=100,command=lambda v,i=p['id'],l=meta,d=p['deadline']:self._on_slide(i,v,l,d))
            sl.set(p['progress_pct']); sl.pack(fill='x',padx=15,pady=12)
    @staticmethod
    def _meta(pct,deadline): return f'{float(pct):.0f}% · {deadline or "No deadline"}'
    def _on_slide(self,pid,value,label,deadline):
        """Update the label immediately; commit to the DB only once the drag settles."""
        label.configure(text=self._meta(value,deadline))
        job=self._jobs.get(pid)
        if job is not None:
            try: self.after_cancel(job)
            except Exception: pass
        self._jobs[pid]=self.after(250,lambda: self._commit(pid,value))
    def _commit(self,pid,value):
        self._jobs.pop(pid,None); self.c.update_progress(pid,value)
    def add(self):
        win=ctk.CTkToplevel(self); win.title('Add Project'); win.geometry('450x360'); win.transient(self.winfo_toplevel()); win.grab_set(); fields=[]
        for ph in ['Project name','Deadline YYYY-MM-DD','GitHub link','Notes']:
            e=ctk.CTkEntry(win,placeholder_text=ph,height=38); e.pack(fill='x',padx=24,pady=8); fields.append(e)
        def save():
            if self.c.add(*[e.get() for e in fields]): win.destroy(); self.refresh()
            else: messagebox.showerror('Invalid','Enter a project name.',parent=win)
        ctk.CTkButton(win,text='Save',height=38,command=save).pack(pady=14)
        fields[0].focus_set()
