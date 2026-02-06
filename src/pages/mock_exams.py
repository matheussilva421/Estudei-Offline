
import flet as ft
from src.theme import AppTheme
import src.data.crud as crud

class MockExamsPage(ft.Container):
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
                ft.Row([
                    ft.Text("Simulados", size=30, weight=ft.FontWeight.BOLD, color="white"),
                    ft.ElevatedButton("Novo Simulado", icon=ft.Icons.ADD, bgcolor=AppTheme.primary, color="white", on_click=self.open_add_modal)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=20),
                self.indicators_row,
                ft.Container(height=20),
                ft.Text("Histórico de Simulados", size=18, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(height=10),
                self.list_container
            ],
            expand=True
        )
        self.load_data()

    def load_data(self):
        exams = crud.db.fetch_all("SELECT * FROM mock_exams ORDER BY date DESC")
        
        total = len(exams)
        last_exam = exams[0] if exams else None
        
        last_score = f"{last_exam['score']:.1f}" if last_exam and last_exam['score'] else "-"
        
        self.indicators_row.controls = [
            self.create_indicator(str(total), "Simulados Realizados", ft.Icons.ASSIGNMENT),
            self.create_indicator(last_score, "Nota do Último", ft.Icons.SCORE),
        ]
        
        self.list_container.controls = []
        for ex in exams:
            self.list_container.controls.append(self.create_exam_card(ex))
            
        if self.page: self.update()

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

    def create_exam_card(self, ex):
        return ft.Container(
            bgcolor="#2c2d3e",
            padding=15,
            border_radius=10,
            margin=ft.margin.only(bottom=10),
            content=ft.Row([
                ft.Column([
                    ft.Text(ex['name'], size=16, weight=ft.FontWeight.BOLD, color="white"),
                    ft.Text(f"{ex['date']} | {ex['board'] or 'Banca ND'} | {ex['style'] or 'Estilo ND'}", size=12, color="grey"),
                ], expand=True),
                ft.Column([
                    ft.Text("Nota", size=10, color="grey"),
                    ft.Text(f"{ex['score']}", size=16, weight=ft.FontWeight.BOLD, color="white"),
                ]),
                ft.IconButton(ft.Icons.VISIBILITY, icon_color="white", tooltip="Ver Detalhes (Em breve)")
            ])
        )

    def open_add_modal(self, e):
        from src.components.mock_exam_modal import MockExamModal
        self.modal = MockExamModal(self.page_ref, on_save=self.load_data)
        self.page_ref.dialog = self.modal
        self.modal.open = True
        self.page_ref.update()

def get_mock_exams_page(page):
    # crud.db.init_db() # Ensure tables exist if lazy
    return MockExamsPage(page)
