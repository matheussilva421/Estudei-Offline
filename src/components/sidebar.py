
import flet as ft
from src.theme import AppTheme

class Sidebar(ft.Container):
    def __init__(self, page: ft.Page, on_nav_change=None):
        super().__init__()
        # self.page = page # Cannot assign to read-only property
        self.on_nav_change = on_nav_change
        self.width = 250
        self.bgcolor = AppTheme.surface
        self.padding = 20
        self.border_radius = ft.border_radius.only(top_right=20, bottom_right=20)
        
        self.logo = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.BOOK, color=AppTheme.primary, size=30),
                    ft.Text("estudei", size=24, weight=ft.FontWeight.BOLD, color="white", font_family="Segoe UI"), # Basic font for now
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=ft.padding.only(bottom=40)
        )

        self.nav_items = [
            {"icon": ft.Icons.DASHBOARD, "label": "Dashboard", "selected": False},
            {"icon": ft.Icons.FOLDER, "label": "Planos", "selected": False}, 
            {"icon": ft.Icons.LAYERS, "label": "Disciplinas", "selected": False},
            {"icon": ft.Icons.DESCRIPTION, "label": "Edital", "selected": False},
            {"icon": ft.Icons.CALENDAR_MONTH, "label": "Planejamento", "selected": False},
            {"icon": ft.Icons.REPEAT, "label": "Revisões", "selected": False},
            {"icon": ft.Icons.HISTORY, "label": "Histórico", "selected": False},
            {"icon": ft.Icons.PIE_CHART, "label": "Estatísticas", "selected": False},
            {"icon": ft.Icons.LIST_ALT, "label": "Simulados", "selected": False},
        ]
        
        self.nav_controls_list = [] # Store references to update selection
        
        self.content = ft.Column(
            controls=[
                self.logo,
                self.build_nav_menu()
            ],
            scroll=ft.ScrollMode.AUTO,
        )

    def build_nav_menu(self):
        self.nav_controls_list = []
        for i, item in enumerate(self.nav_items):
            # Default "Planos" is selected for showcase, but let's make it dynamic
            is_selected = item["label"] == "Planos"
            
            # Content of the button
            btn_content = ft.Row(
                controls=[
                    ft.Icon(item["icon"], color=AppTheme.primary if is_selected else AppTheme.text_secondary, size=20),
                    ft.Text(item["label"], color="white" if is_selected else AppTheme.text_secondary, size=16, weight=ft.FontWeight.W_500 if is_selected else ft.FontWeight.NORMAL),
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=15
            )
            
            btn = ft.Container(
                content=btn_content,
                padding=ft.padding.symmetric(horizontal=15, vertical=12),
                border_radius=10,
                bgcolor=AppTheme.primary + "1A" if is_selected else None, 
                border=ft.border.only(left=ft.BorderSide(3, AppTheme.primary)) if is_selected else None,
                on_click=lambda e, idx=i: self.handle_click(idx),
                data=i # Store index
            )
            self.nav_controls_list.append(btn)

        return ft.Column(controls=self.nav_controls_list, spacing=5)

    def handle_click(self, index):
        # Update UI
        for i, btn in enumerate(self.nav_controls_list):
            item = self.nav_items[i]
            is_selected = (i == index)
            item["selected"] = is_selected
            
            # Rebuild inner content (crude but effective for Flet)
            btn.bgcolor = AppTheme.primary + "1A" if is_selected else None
            btn.border = ft.border.only(left=ft.BorderSide(3, AppTheme.primary)) if is_selected else None
            
            icon = btn.content.controls[0]
            text = btn.content.controls[1]
            icon.color = AppTheme.primary if is_selected else AppTheme.text_secondary
            text.color = "white" if is_selected else AppTheme.text_secondary
            text.weight = ft.FontWeight.W_500 if is_selected else ft.FontWeight.NORMAL
            
            btn.update()
            
        if self.on_nav_change:
            self.on_nav_change(self.nav_items[index]["label"])
