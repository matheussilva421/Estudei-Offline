
import flet as ft
from src.theme import AppTheme

class SessionDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, on_start_timer=None):
        super().__init__()
        self.page = page
        self.on_start_timer = on_start_timer
        self.modal = True
        self.bgcolor = "#2c2d3e" # Darker surface
        self.shape = ft.RoundedRectangleBorder(radius=10)
        self.content_padding = 0
        
        # content
        self.content = ft.Container(
            width=400,
            padding=20,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.START,
                controls=[
                    ft.Row([
                         ft.Icon(ft.Icons.CIRCLE, color="#ff8a80", size=12),
                         ft.Text("Controle Externo e Legislação Institucional", size=14, color="white", weight=ft.FontWeight.BOLD, expand=True),
                         ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_color="grey", tooltip="Remover"),
                         ft.IconButton(ft.Icons.CLOSE, icon_color="white", on_click=self.close_dialog)
                    ]),
                    ft.Divider(color="grey"),
                    self.create_field(ft.Icons.ACCESS_TIME, "02:00"),
                    self.create_field(ft.Icons.CALENDAR_TODAY, "09/02/2026"),
                    ft.Dropdown(
                        options=[ft.dropdown.Option("Semanal: a cada 2 segunda-feiras")],
                        value="Semanal: a cada 2 segunda-feiras",
                        text_style=ft.TextStyle(color="white", size=12),
                        bgcolor="#1e1e2d", border_color="transparent", height=40
                    ),
                    self.create_field(ft.Icons.BOOKMARK_BORDER, "Tópico"),
                    ft.Container(height=20),
                    ft.Row([
                        ft.ElevatedButton("Iniciar Estudo", icon=ft.Icons.PLAY_ARROW, bgcolor="#1e1e2d", color=AppTheme.primary, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), on_click=self.start_study, expand=True),
                        ft.ElevatedButton("Adicionar Estudo", icon=ft.Icons.ADD, bgcolor="#1e1e2d", color=AppTheme.primary, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), expand=True),
                    ]),
                    ft.ElevatedButton("Últimos Estudos", icon=ft.Icons.HISTORY, bgcolor="white", color="black", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), width=400),
                    ft.ElevatedButton("Salvar", bgcolor=AppTheme.primary, color="white", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)), width=400, on_click=self.close_dialog),
                ],
                spacing=10
            ) 
        )

    def create_field(self, icon, value):
        return ft.TextField(
            value=value,
            prefix_icon=icon,
            text_style=ft.TextStyle(color="white", size=14),
            bgcolor="transparent",
            border_color="grey",
            border_width=0,
            content_padding=10,
            height=40
        )

    def close_dialog(self, e):
        self.open = False
        self.page.close_dialog()
        self.page.update()

    def start_study(self, e):
        self.close_dialog(e)
        if self.on_start_timer:
            self.on_start_timer()

