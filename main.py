
import flet as ft
from src.theme import AppTheme
from src.components.sidebar import Sidebar
from src.pages.dashboard import get_dashboard_page
from src.components.study_modal import StudyModal
from src.components.timer_overlay import TimerOverlay
from src.components.planning_wizard import PlanningWizard
from src.utils.navigation import NavigationManager

def main(page: ft.Page):
    page.title = "Estudei - Gerenciador de Estudos"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = AppTheme.theme
    page.bgcolor = AppTheme.background
    page.padding = 0
    page.spacing = 0
    
    # Global App Bar
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.MENU_BOOK, color=AppTheme.primary),
        leading_width=40,
        title=ft.Text("Estudei Offline", weight=ft.FontWeight.BOLD, color="white"),
        center_title=False,
        bgcolor="#1e1e2d",
        actions=[
            ft.IconButton(ft.Icons.HELP_OUTLINE, icon_color="white", tooltip="Ajuda"),
            ft.IconButton(ft.Icons.NOTIFICATIONS_NONE, icon_color="white", tooltip="Notificações"),
            ft.IconButton(ft.Icons.SETTINGS, icon_color="white", tooltip="Configurações"),
            ft.CircleAvatar(
                content=ft.Text("US", size=12, weight=ft.FontWeight.BOLD),
                bgcolor=AppTheme.primary,
                radius=15,
            ),
            ft.Container(width=10)
        ]
    )

    # Content Area - This container holds the current page
    content_area = ft.Container(expand=True, content=get_dashboard_page(page))
    
    # Initialize Navigation Manager (attaches to page.nav)
    nav = NavigationManager(page, content_area)

    # Timer Overlay
    timer_overlay = TimerOverlay(page)
    page.overlay.append(timer_overlay)
    
    # Wizard instance
    planning_wizard = PlanningWizard(page)

    def nav_change(label):
        """Handle sidebar navigation clicks."""
        page_map = {
            "Dashboard": "dashboard",
            "Planos": "plans",
            "Disciplinas": "subjects",
            "Edital": "subjects",
            "Planejamento": "planning",
            "Revisões": "reviews",
            "Histórico": "history",
            "Estatísticas": "statistics",
            "Simulados": "mock_exams"
        }
        page_name = page_map.get(label, "dashboard")
        
        if page_name == "planning":
            nav.navigate_to(page_name, on_timer_click=lambda: timer_overlay.show())
        else:
            nav.navigate_to(page_name)

    # Modal instance
    study_modal = StudyModal()
    
    def open_study_modal(e):
        page.dialog = study_modal
        study_modal.open = True
        page.dialog.open = True
        page.update()

    # Floating Action Button
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=AppTheme.primary,
        on_click=open_study_modal
    )
    
    # Layout scaffold
    def app_layout():
        return ft.Row(
            controls=[
                Sidebar(page, on_nav_change=nav_change),
                content_area
            ],
            expand=True
        )

    page.add(app_layout())
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
