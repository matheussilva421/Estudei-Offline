
import flet as ft
from src.theme import AppTheme
import src.data.crud as crud
from datetime import datetime

class SubjectDetailsPage(ft.Container):
    def __init__(self, page: ft.Page, subject_id, plan_id=None):
        super().__init__()
        self.page_ref = page
        self.subject_id = subject_id
        self.plan_id = plan_id # to go back
        self.expand = True
        self.padding = 30
        self.subject_data = None
        
        self.build_ui()

    def build_ui(self):
        self.header_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        self.indicators_row = ft.Row(spacing=20)
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Histórico de Estudo"),
                ft.Tab(text="Edital Verticalizado"),
            ],
            expand=True,
        )
        self.tab_content = ft.Container(expand=True)
        
        self.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.IconButton(ft.Icons.ARROW_BACK, on_click=self.go_back, icon_color="white"),
                    alignment=ft.Alignment(-1, 0)
                ),
                self.header_row,
                ft.Container(height=20),
                self.indicators_row,
                ft.Container(height=20),
                self.tabs,
                self.tab_content
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        
        # Wiring tabs logic
        self.tabs.on_change = self.on_tab_change
        
        self.load_data()

    def load_data(self):
        # Fetch Subject Info
        # Need a crud for get_subject_by_id. 
        # Using direct query placeholder or generic fetch
        self.subject_data = crud.db.fetch_one("SELECT * FROM subjects WHERE id = ?", (self.subject_id,))
        if not self.subject_data:
            self.content = ft.Text("Disciplina não encontrada.")
            return

        self.update_header()
        self.update_indicators()
        self.load_tab_content()
        # Note: Don't call self.update() here - control may not be mounted yet

    def update_header(self):
        color = self.subject_data['color'] or AppTheme.primary
        self.header_row.controls = [
            ft.Row([
                ft.Container(width=10, height=40, bgcolor=color, border_radius=5),
                ft.Column([
                    ft.Text(self.subject_data['name'], size=30, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text(self.subject_data['category'] or "Geral", size=14, color="grey")
                ])
            ]),
            ft.IconButton(ft.Icons.EDIT, icon_color="white", tooltip="Editar Disciplina", on_click=self.open_edit_modal)
        ]

    def open_edit_modal(self, e):
        from src.components.subject_edit_modal import SubjectEditModal
        # Re-fetch latest subject data just in case
        self.modal = SubjectEditModal(self.page_ref, self.plan_id, self.subject_data, on_save=self.load_data)
        self.page_ref.dialog = self.modal
        self.modal.open = True
        self.page_ref.update()

    def update_indicators(self):
        stats = crud.get_subject_stats(self.subject_id)
        total_seconds = stats['total_seconds'] if stats else 0
        total_hours = total_seconds / 3600
        
        # Performance
        correct = stats['total_correct'] if stats else 0
        wrong = stats['total_wrong'] if stats else 0
        pct = crud.calculate_performance(correct, wrong)
        
        # Pages
        pages_read = stats['total_pages'] if stats else 0
        pages_per_hour = int(pages_read / total_hours) if total_hours > 0 else 0
        
        # Topics
        topics_done = self.subject_data['completed_topics']
        topics_total = self.subject_data['total_topics']
        topics_pct = int(topics_done / topics_total * 100) if topics_total > 0 else 0

        self.indicators_row.controls = [
            self.create_indicator(f"{total_hours:.1f}h", "Tempo Estudado", ft.Icons.ACCESS_TIME),
            self.create_indicator(f"{pct}%", f"{correct}C / {wrong}E", ft.Icons.PIE_CHART),
            self.create_indicator(f"{topics_pct}%", f"{topics_done}/{topics_total} Tópicos", ft.Icons.CHECK_CIRCLE),
            self.create_indicator(f"{pages_read}", f"{pages_per_hour} pág/h", ft.Icons.BOOK),
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

    def on_tab_change(self, e):
        self.load_tab_content()
        self.tab_content.update()

    def load_tab_content(self):
        if self.tabs.selected_index == 0:
            self.tab_content.content = self.build_history_list()
        else:
            self.tab_content.content = self.build_syllabus_list()

    def build_history_list(self):
        sessions = crud.get_study_sessions_by_subject(self.subject_id)
        if not sessions:
            return ft.Text("Nenhum estudo registrado.", color="grey", italic=True)
            
        lv = ft.ListView(expand=True, spacing=10)
        
        # Headers
        lv.controls.append(ft.Row([
            ft.Text("Data", width=120, color="grey", weight=ft.FontWeight.BOLD),
            ft.Text("Tipo", width=80, color="grey", weight=ft.FontWeight.BOLD),
            ft.Text("Tempo", width=80, color="grey", weight=ft.FontWeight.BOLD),
            ft.Text("Desempenho", width=100, color="grey", weight=ft.FontWeight.BOLD),
            ft.Text("Tópico/Obs", expand=True, color="grey", weight=ft.FontWeight.BOLD),
            ft.Text("Ações", width=80, color="grey", weight=ft.FontWeight.BOLD),
        ]))
        
        for s in sessions:
            # Parse date
            try:
                dt_str = datetime.strptime(s['date'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m %H:%M")
            except:
                dt_str = s['date']
            
            # Duration
            h = s['duration_seconds'] // 3600
            m = (s['duration_seconds'] % 3600) // 60
            dur_str = f"{h}h {m}m"
            
            # Perf
            c = s['questions_correct']
            w = s['questions_wrong']
            perf_str = f"{c}C / {w}E"
            
            lv.controls.append(ft.Container(
                bgcolor="#333", border_radius=5, padding=10,
                content=ft.Row([
                    ft.Text(dt_str, width=120, size=12),
                    ft.Chip(label=ft.Text(s['type'], size=10), height=25, bgcolor="#444"),
                    ft.Text(dur_str, width=80, size=12),
                    ft.Text(perf_str, width=100, size=12, color="green" if c > w else "red"),
                    ft.Text(s['topic'], expand=True, size=12, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.IconButton(ft.Icons.DELETE, icon_size=16, icon_color="red", on_click=lambda e, sid=s['id']: self.delete_session(sid))
                ])
            ))
            
        return lv

    def delete_session(self, sid):
        crud.db.execute_query("DELETE FROM study_sessions WHERE id = ?", (sid,))
        self.load_data() # Refresh

    def build_syllabus_list(self):
        topics = crud.get_topics_by_subject(self.subject_id)
        if not topics:
            return ft.Text("Nenhum tópico cadastrado (Use o editor no painel do plano).", color="grey")
            
        lv = ft.ListView(expand=True, spacing=5)
        for t in topics:
            link = t['material_link'] if 'material_link' in t.keys() else ""
            
            row = ft.Row([
                ft.Checkbox(value=(t['completed']==1), on_change=lambda e, tid=t['id']: self.toggle_topic(tid, e.control.value)),
                ft.Text(t['title'], expand=True, size=14),
                ft.IconButton(ft.Icons.LINK, icon_color="blue" if link else "grey", tooltip=link or "Adicionar Link", on_click=lambda e, tid=t['id'], l=link: self.edit_link(tid, l))
            ])
            lv.controls.append(ft.Container(content=row, bgcolor="#333", border_radius=5, padding=5))
            
        return lv

    def toggle_topic(self, tid, val):
        crud.toggle_topic_complete(tid, val)
        # Refresh header stats only? Or full reload? Full reload easier.
        self.update_indicators() # Needed
        if self.page: self.indicators_row.update()

    def edit_link(self, tid, current_link):
        # Allow editing link via simple dialog
        def save_link(e):
            new_link = txt_link.value
            crud.update_topic(tid, title=None, material_link=new_link) # Needs update_topic patch
            self.page_ref.close_dialog()
            self.load_tab_content()
            self.tab_content.update()

        txt_link = ft.TextField(value=current_link, label="URL / Link", autofocus=True)
        dlg = ft.AlertDialog(
            title=ft.Text("Adicionar Link de Material"),
            content=txt_link,
            actions=[ft.TextButton("Salvar", on_click=save_link)]
        )
        self.page_ref.dialog = dlg
        dlg.open = True
        self.page_ref.update()

    def go_back(self, e):
        # Use NavigationManager to go back
        self.page_ref.nav.pop()

def get_subject_details_page(page, subject_id, plan_id=None):
    return SubjectDetailsPage(page, subject_id, plan_id)
