import customtkinter as ctk
from controllers.focus_controller import FocusController
from themes.dark_theme import COLORS, font_body, font_heading, font_display
from views.page_common import title,card

class FocusView(ctk.CTkFrame):
    def __init__(self,master): super().__init__(master,fg_color=COLORS['background']); self.c=FocusController(); self.running=False; self.remaining=25*60; self._timer_job=None; self._build()
    def _build(self):
        title(self,'Focus Mode','A distraction-free countdown for deep work.')
        f=card(self); f.pack(fill='x',padx=28,pady=20); self.timer=ctk.CTkLabel(f,text='25:00',font=font_display(52),text_color=COLORS['accent']); self.timer.pack(pady=30); self.status=ctk.CTkLabel(f,text='Ready',font=font_body(),text_color=COLORS['text_secondary']); self.status.pack()
        b=ctk.CTkFrame(f,fg_color='transparent'); b.pack(pady=25); self.start=ctk.CTkButton(b,text='Start Focus',height=38,command=self.start_timer); self.start.pack(side='left',padx=5); ctk.CTkButton(b,text='Reset',height=38,command=self.reset,fg_color=COLORS['surface_alt']).pack(side='left',padx=5)
    def _cancel_job(self):
        if self._timer_job is not None:
            try: self.after_cancel(self._timer_job)
            except Exception: pass
            self._timer_job=None
    def start_timer(self):
        if self.running:return
        self._cancel_job()
        self.running=True; self.start.configure(state='disabled'); self.status.configure(text='Focus in progress…'); self.tick()
    def tick(self):
        if not self.running:return
        self._timer_job=None
        self.timer.configure(text=f'{self.remaining//60:02d}:{self.remaining%60:02d}')
        if self.remaining<=0:
            self.running=False; self.c.record(25,5); self.status.configure(text='Focus session completed!'); self.start.configure(state='normal'); return
        self.remaining-=1; self._timer_job=self.after(1000,self.tick)
    def reset(self): self.running=False; self._cancel_job(); self.remaining=25*60; self.start.configure(state='normal'); self.status.configure(text='Ready'); self.timer.configure(text='25:00')
