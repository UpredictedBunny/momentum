import customtkinter as ctk
from controllers.statistics_controller import StatisticsController
from themes.dark_theme import COLORS, font_body, font_heading, font_display
from views.page_common import title,card

class StatisticsView(ctk.CTkFrame):
    def __init__(self,master): super().__init__(master,fg_color=COLORS["background"]); self.c=StatisticsController(); self._build()
    def _build(self):
        title(self,"Statistics","Your recent productivity metrics.")
        self.cards=ctk.CTkFrame(self,fg_color='transparent'); self.cards.pack(fill='x',padx=28,pady=10)
        self.week=ctk.CTkScrollableFrame(self,fg_color='transparent'); self.week.pack(fill='both',expand=True,padx=28,pady=10); self.refresh()
    def refresh(self):
        for w in self.cards.winfo_children():w.destroy()
        s=self.c.summary(); vals=[('Habits done',s['habit_done']),('Pomodoros',s['pomodoros']),('Focus minutes',s['focus_minutes']),('Study hours',round(s['study_hours'],2))]
        for name,val in vals:
            f=card(self.cards); f.pack(side='left',fill='x',expand=True,padx=5); ctk.CTkLabel(f,text=str(val),font=font_display(28),text_color=COLORS['accent']).pack(pady=(18,2)); ctk.CTkLabel(f,text=name,font=font_body(),text_color=COLORS['text_secondary']).pack(pady=(0,18))
        for w in self.week.winfo_children():w.destroy()
        ctk.CTkLabel(self.week,text='Last 7 days',font=font_heading(),text_color=COLORS['text_primary']).pack(anchor='w',pady=8)
        for d,h,s in self.c.weekly():
            f=card(self.week); f.pack(fill='x',pady=4); ctk.CTkLabel(f,text=f'{d}   •   habits completed: {h}   •   study: {s:.2f} h',font=font_body(),text_color=COLORS['text_secondary']).pack(anchor='w',padx=14,pady=10)
