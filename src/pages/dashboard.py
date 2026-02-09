
import flet as ft
from src.theme import AppTheme
from src.components.stat_card import StatCard, PerformanceCard
from src.components.heatmap import ConsistencyHeatmap
from src.components.charts import StudyChart

class DashboardPage(ft.Container):
    def __init__(self, page: ft.Page = None):
        super().__init__()
        self.page_ref = page
        self.padding = 30
        self.expand = True
        self._subscribed = False
        
        # Subscribe to events (will unsubscribe when navigating away)
        self._subscribe_to_events()
             
        self.build_ui()
    
    def _subscribe_to_events(self):
        """Subscribe to pubsub events."""
        if self.page_ref and not self._subscribed:
            self.page_ref.pubsub.subscribe(self.on_message)
            self._subscribed = True
    
    def _unsubscribe_from_events(self):
        """Unsubscribe from pubsub events to prevent memory leaks."""
        if self.page_ref and self._subscribed:
            try:
                self.page_ref.pubsub.unsubscribe(self.on_message)
            except Exception:
                pass  # May fail if already unsubscribed
            self._subscribed = False
    
    def will_unmount(self):
        """Called when page is being replaced - cleanup subscriptions."""
        self._unsubscribe_from_events()
        
    def on_message(self, message):
        if message == "study_saved":
            print("Dashboard received study_saved. Reloading...")
            self.reload_data()
            if self.page:
                self.update()

    def build_ui(self):
        # Section 1: Top Stats
        import src.data.crud as crud
        stats = crud.get_dashboard_stats()
        total_time_sec = stats['total_seconds'] if stats else 0
        hours = int(total_time_sec // 3600)
        mins = int((total_time_sec % 3600) // 60)
        time_str = f"{hours}h{mins}min"
        
        correct = stats['total_correct'] if stats else 0
        wrong = stats['total_wrong'] if stats else 0
        total = correct + wrong
        pct = int((correct / total) * 100) if total > 0 else 0
        
        self.top_stats = ft.Row(
            controls=[
                ft.Column(controls=[StatCard("Tempo de Estudo", time_str)]),
                ft.Column(controls=[PerformanceCard("Desempenho", str(pct)+"%", correct, wrong)]),
                ft.Column(controls=[StatCard("Progresso no Edital", "1%", subtext="542 Tópicos Pendentes", progress=0.01, color="#888")]),
                ft.Column(controls=[StatCard("Faça sua sorte!", "", subtext="", color=None)]), # Placeholder for quote
            ],
            spacing=20
        )
        
        # Section 2: Heatmap
        self.heatmap = ConsistencyHeatmap()

        # Section 3: Main Content (Planning vs Sidebar)
        self.planning_section = ft.Container(
            bgcolor="#1e1e2d", padding=20, border_radius=10, expand=6,
            content=ft.Column([
                ft.Text("PLANEJAMENTO DO DIA", weight=ft.FontWeight.BOLD, size=12, color="grey"),
                ft.Divider(height=10, color="transparent"),
                self.build_todays_plan()
            ])
        )
        
        self.sidebar_section = ft.Column(
            expand=4, 
            spacing=20,
            controls=[
                # Reviews Block
                ft.Container(
                    bgcolor="#1e1e2d", padding=20, border_radius=10,
                    content=ft.Column([
                        ft.Text("REVISÕES", weight=ft.FontWeight.BOLD, size=12, color="grey"),
                        ft.Container(height=10),
                        ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color="green"),
                            ft.Text("Você não tem revisões para hoje!", size=12, expand=True)
                        ], alignment=ft.MainAxisAlignment.CENTER)
                    ])
                ),
                # Reminders Block
                ft.Container(
                    bgcolor="#1e1e2d", padding=20, border_radius=10,
                    content=ft.Column([
                         ft.Row([
                             ft.Text("LEMBRETES", weight=ft.FontWeight.BOLD, size=12, color="grey"),
                             ft.IconButton(ft.Icons.ADD, icon_size=16, tooltip="Novo Lembrete", on_click=self.open_reminder_modal)
                         ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                         ft.Container(height=5),
                         self.build_reminders_list()
                    ])
                ),
                # Recent Activity Block
                ft.Container(
                    bgcolor="#1e1e2d", padding=20, border_radius=10,
                    content=ft.Column([
                        ft.Text("ÚLTIMAS ATIVIDADES", weight=ft.FontWeight.BOLD, size=12, color="grey"),
                        self.build_recent_activity()
                    ])
                )
            ]
        )
        
        self.content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                self.top_stats,
                ft.Container(height=10),
                self.heatmap,
                ft.Container(height=10),
                ft.Row(
                    controls=[self.planning_section, self.sidebar_section],
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=20,
                )
            ]
        )

    def reload_data(self):
        self.build_ui()
        if self.page:
            self.update()
        
    def build_todays_plan(self):
        # Reusing similar logic to old Subject Panel but simplified for "Today"
        list_col = ft.Column(spacing=10)
        import src.data.crud as crud
        subjects = crud.get_all_subjects()
        
        if not subjects:
             return ft.Text("Nenhuma disciplina cadastrada.", color="grey")
             
        for sub in subjects:
            # Mock daily goal calculation (e.g. 2 hours per sub)
            # Real logic would check if subject is in today's schedule
            prog = 0.0
            if sub['weight'] > 0: prog = 0.3 # Fake progress for demo
            
            list_col.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(sub['name'], size=12, weight=ft.FontWeight.BOLD, expand=True),
                            ft.Text(f"0h00 / 2h00", size=10, color="grey") # Mock goal
                        ]),
                        ft.ProgressBar(value=prog, color=AppTheme.primary, bgcolor="#2c2d3e", height=5)
                    ])
                )
            )
        return list_col

    def build_reminders_list(self):
        import src.data.crud as crud
        reminders = crud.get_reminders()
        col = ft.Column(spacing=5)
        
        if not reminders:
            col.controls.append(ft.Text("Sem lembretes.", size=12, color="grey"))
        else:
            for r in reminders:
                # r = (id, content, cat, date, completed)
                # date string format check?
                date_display = r['date_time'].split(' ')[0] # just date or time?
                col.controls.append(
                    ft.Row([
                        ft.Icon(ft.Icons.CIRCLE, size=8, color=AppTheme.primary),
                        ft.Text(f"{r['content']} ({date_display})", size=12, expand=True, no_wrap=True),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE, size=14, icon_color="red", on_click=lambda e, rid=r['id']: self.delete_reminder_action(rid))
                    ])
                )
        return col

    def open_reminder_modal(self, e):
        from src.components.reminder_modal import ReminderModal
        self.rem_modal = ReminderModal(self.page_ref, on_save=self.reload_data)
        self.page_ref.dialog = self.rem_modal
        self.rem_modal.open = True
        self.page_ref.update()

    def delete_reminder_action(self, rid):
        import src.data.crud as crud
        crud.delete_reminder(rid)
        self.reload_data()

    def build_recent_activity(self):
        import src.data.crud as crud
        sessions = crud.get_recent_sessions(3)
        if not sessions:
            return ft.Text("Nenhuma atividade recente.", size=12, color="grey")
            
        col = ft.Column(spacing=10)
        for s in sessions:
            # s = (date, name, duration)
            # Format date "DD/MM" maybe
            # Format time "1h 30m"
            dur = s['duration_seconds']
            time_str = f"{int(dur//3600)}h {int((dur%3600)//60)}m"
            sub_name = s['subject_name']
            
            col.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.ACCESS_TIME, size=12, color="grey"),
                    ft.Text(sub_name, size=11, expand=True, no_wrap=True, tooltip=sub_name),
                    ft.Text(time_str, size=11, color="green")
                ])
            )
        return col

# Simple export to be used in main
def get_dashboard_page(page=None):
    return DashboardPage(page)
