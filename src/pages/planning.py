
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
                        self._create_card(title, "2h00min", color),
                        self._create_card(title, "1h30min", color),
                    ])
                )
            )

        self.content = ft.Column([
            ft.Text("Planejamento Semanal", size=24, weight=ft.FontWeight.BOLD, color="white"),
            ft.Row(controls=row_controls, scroll=ft.ScrollMode.AUTO, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START)
        ])

    def _create_card(self, title, time, color):
        """Create a card with proper closure capture."""
        return ft.Container(
            bgcolor=color,
            padding=10,
            border_radius=5,
            margin=ft.margin.only(bottom=10),
            content=ft.Column([
                ft.Text(title, size=10, weight=ft.FontWeight.BOLD, color="black"),
                ft.Container(bgcolor="black", padding=5, border_radius=10, content=ft.Text(time, size=8, color="white"))
            ]),
            # Fix: capture title by value using default argument
            on_click=lambda e, t=title: self.open_session_detail(e, t)
        )

    def open_session_detail(self, e, title):
        """Open the session dialog."""
        print(f"Opening session detail for: {title}")  # Debug
        self.session_dialog.open = True
        if self.page_ref:
            self.page_ref.open(self.session_dialog)

def get_planning_page(page=None, start_timer_callback=None):
    return PlanningPage(page, start_timer_callback)

