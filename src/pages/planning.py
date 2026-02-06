
import flet as ft
from src.theme import AppTheme
from src.components.session_dialog import SessionDialog

class PlanningPage(ft.Container):
    def __init__(self, page, start_timer_callback):
        super().__init__()
        self.page_ref = page
        self.start_timer_callback = start_timer_callback
        self.padding = 30
        self.expand = True
        
        # Session Dialog
        self.session_dialog = SessionDialog(page, on_start_timer=self.start_timer_callback)

        # Mock Planning Columns
        self.columns = []
        
        # Helper to create a card
        def create_card(title, time, color):
            return ft.Container(
                bgcolor=color,
                padding=10,
                border_radius=5,
                margin=ft.margin.only(bottom=10),
                content=ft.Column([
                    ft.Text(title, size=10, weight=ft.FontWeight.BOLD, color="black"),
                    ft.Container(bgcolor="black", padding=5, border_radius=10, content=ft.Text(time, size=8, color="white"))
                ]),
                on_click=lambda e: self.open_session_detail(e, title)
            )

        # Mock Data for Columns
        planning_data = [
            ("Controle Externo", "#ff8a80"), # Red/Pink
            ("Direito Constitucional", "#ffe57f"), # Yellow
            ("Direito Civil", "#9fa8da"), # Blue
            ("Direito Penal", "#bcaaa4"), # Brown
            ("Raciocínio Lógico", "#a5d6a7"), # Green
        ]
        
        row_controls = []
        for title, color in planning_data:
            # Create a vertical column for each category
            row_controls.append(
                ft.Container(
                    width=150,
                    bgcolor=AppTheme.surface,
                    border_radius=10,
                    padding=10,
                    content=ft.Column([
                        ft.Text(title, size=10, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Divider(color=AppTheme.background),
                        create_card(title, "2h00min", color),
                         create_card(title, "1h30min", color),
                    ])
                )
            )

        self.content = ft.Column([
            ft.Text("Planejamento Semanal", size=24, weight=ft.FontWeight.BOLD, color="white"),
            ft.Row(controls=row_controls, scroll=ft.ScrollMode.AUTO, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)
        ])

    def open_session_detail(self, e, title):
        self.page_ref.dialog = self.session_dialog
        self.session_dialog.open = True
        self.page_ref.dialog.open = True
        self.page_ref.update()

def get_planning_page(page=None, start_timer_callback=None):
    return PlanningPage(page, start_timer_callback)
