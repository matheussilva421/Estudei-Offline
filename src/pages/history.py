
import flet as ft
from src.theme import AppTheme
import src.data.crud as crud
from datetime import datetime

class HistoryPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page_ref = page
        self.expand = True
        self.padding = 30
        
        self.build_ui()

    def build_ui(self):
        self.indicators_row = ft.Row(spacing=20)
        self.list_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)

        self.content = ft.Column(
            controls=[
                ft.Text("Histórico de Estudos", size=30, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(height=20),
                self.indicators_row,
                ft.Container(height=20),
                ft.Text("Sessões Registradas", size=18, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(height=10),
                self.list_container
            ],
            expand=True
        )
        self.load_data()

    def load_data(self):
        self.update_indicators()
        self.load_history_list()
        # Note: Don't call self.update() here - the control may not be mounted yet.
        # The parent container will handle the initial render.

    def update_indicators(self):
        stats = crud.get_history_stats()
        total_sec = stats['total_seconds'] if stats else 0
        total_h = total_sec / 3600
        corr = stats['total_correct'] if stats else 0
        wrong = stats['total_wrong'] if stats else 0
        total = corr + wrong
        pct = int((corr / total) * 100) if total > 0 else 0
        pages = stats['total_pages'] if stats else 0
        pages_h = int(pages / total_h) if total_h > 0 else 0

        topics = crud.get_topics_stats()
        total_t = topics['total_topics'] if topics else 0
        done_t = topics['completed_topics'] if topics else 0
        prog_pct = int(done_t / total_t * 100) if total_t > 0 else 0

        self.indicators_row.controls = [
            self.create_indicator(f"{total_h:.1f}h", "Tempo Total", ft.Icons.ACCESS_TIME),
            self.create_indicator(f"{pct}%", f"{corr}C / {wrong}E", ft.Icons.PIE_CHART),
            self.create_indicator(f"{prog_pct}%", f"{done_t}/{total_t} Tópicos", ft.Icons.CHECK_CIRCLE),
            self.create_indicator(f"{pages}", f"{pages_h} pág/h", ft.Icons.BOOK),
        ]

    def create_indicator(self, value, label, icon):
        return ft.Container(
            bgcolor="#2c2d3e",
            padding=15,
            border_radius=10,
            expand=True,
            content=ft.Row([
                ft.Icon(icon, color=AppTheme.primary, size=24),
                ft.Column([
                    ft.Text(label, size=10, color="grey"),
                    ft.Text(value, size=18, weight=ft.FontWeight.BOLD, color="white")
                ], spacing=2)
            ], alignment=ft.MainAxisAlignment.CENTER)
        )

    def load_history_list(self):
        sessions = crud.get_all_study_sessions()
        
        self.list_container.controls = []
        if not sessions:
            self.list_container.controls.append(ft.Text("Nenhum estudo registrado.", color="grey", italic=True))
            return
            
        # Group by Day? Or simple list? Request says "Lista sessões por data".
        # Let's do a simple list with date headers if convenient, but for now simple list.
        
        current_date = None
        
        for s in sessions:
            # Date Parsing
            try:
                dt = datetime.strptime(s['date'], "%Y-%m-%d %H:%M:%S")
                date_str = dt.strftime("%d de %B, %Y")
                time_str = dt.strftime("%H:%M")
            except:
                date_str = s['date']
                time_str = ""
                
            if date_str != current_date:
                self.list_container.controls.append(ft.Container(
                    content=ft.Text(date_str, weight=ft.FontWeight.BOLD, color=AppTheme.primary),
                    margin=ft.margin.only(top=10, bottom=5)
                ))
                current_date = date_str
                
            # Content
            h = s['duration_seconds'] // 3600
            m = (s['duration_seconds'] % 3600) // 60
            dur = f"{h}h {m}m"
            perf = f"{s['questions_correct']}C / {s['questions_wrong']}E"
            
            self.list_container.controls.append(ft.Container(
                bgcolor="#333", border_radius=5, padding=10,
                content=ft.Row([
                    ft.Column([
                        ft.Text(f"{time_str} - {s['subject_name']}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{s['topic']} ({s['type']})", size=12, color="grey")
                    ], expand=True),
                    ft.Column([
                        ft.Text(dur, size=12, weight=ft.FontWeight.BOLD),
                        ft.Text(perf, size=10, color="green" if s['questions_correct'] > s['questions_wrong'] else "red")
                    ], width=80),
                    ft.Row([
                        ft.IconButton(ft.Icons.EDIT, icon_size=18, icon_color="grey", tooltip="Editar (Não impl.)"),
                        ft.IconButton(ft.Icons.DELETE, icon_size=18, icon_color="red", on_click=lambda e, sid=s['id']: self.delete_session(sid))
                    ], spacing=0)
                ])
            ))

    def delete_session(self, sid):
        crud.db.execute_query("DELETE FROM study_sessions WHERE id = ?", (sid,))
        self.load_data()

def get_history_page(page):
    return HistoryPage(page)
