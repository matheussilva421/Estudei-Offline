
import flet as ft
from src.theme import AppTheme
from src.components.sidebar import Sidebar
from src.pages.dashboard import get_dashboard_page
from src.pages.plans import get_plans_page
from src.pages.subjects import get_subjects_page
from src.pages.planning import get_planning_page
from src.pages.reviews import get_reviews_page
from src.pages.history import get_history_page
from src.pages.statistics import get_statistics_page
from src.pages.mock_exams import get_mock_exams_page
from src.components.study_modal import StudyModal
from src.components.timer_overlay import TimerOverlay
from src.components.planning_wizard import PlanningWizard

def main(page: ft.Page):
    # wrapper to allow checking the page via browser subagent if needed
    # page.window_width = 1400
    # page.window_height = 900
    
    page.title = "Estudei - Gerenciador de Estudos"
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = AppTheme.theme
    page.bgcolor = AppTheme.background
    page.padding = 0
    page.spacing = 0
    
    # Global App Bar (Topo direito: ajuda, notificações, configurações, perfil)
    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.Icons.MENU_BOOK, color=AppTheme.primary),
        leading_width=40,
        title=ft.Text("Estudei Offline", weight=ft.FontWeight.BOLD, color="white"),
        center_title=False,
        bgcolor="#1e1e2d", # Dark header matching sidebar/theme
        actions=[
            ft.IconButton(ft.Icons.HELP_OUTLINE, icon_color="white", tooltip="Ajuda"),
            ft.IconButton(ft.Icons.NOTIFICATIONS_NONE, icon_color="white", tooltip="Notificações"),
            ft.IconButton(ft.Icons.SETTINGS, icon_color="white", tooltip="Configurações"),
            ft.CircleAvatar(
                content=ft.Text("US", size=12, weight=ft.FontWeight.BOLD),
                bgcolor=AppTheme.primary,
                radius=15,
            ),
            ft.Container(width=10) # Padding right
        ]
    )

    content_area = ft.Container(expand=True, content=get_dashboard_page(page))

    # Timer Overlay
    timer_overlay = TimerOverlay(page)
    page.overlay.append(timer_overlay)
    
    # Wizard instance
    planning_wizard = PlanningWizard(page)

    def nav_change(label):
        if label == "Dashboard":
            content_area.content = get_dashboard_page(page)
        elif label == "Planos":
             content_area.content = get_plans_page(page)
        elif label == "Disciplinas" or label == "Edital":
             content_area.content = get_subjects_page(page)
        elif label == "Planejamento":
             content_area.content = get_planning_page(page, lambda: timer_overlay.show())
        elif label == "Revisões":
             content_area.content = get_reviews_page(page)
        elif label == "Histórico":
             content_area.content = get_history_page(page)
        elif label == "Estatísticas":
             content_area.content = get_statistics_page(page)
        elif label == "Simulados":
             content_area.content = get_mock_exams_page(page)
        else:
             content_area.content = get_dashboard_page(page) # Default
        
        content_area.update()

    # Modal instance
    study_modal = StudyModal()
    
    def open_study_modal(e):
        page.dialog = study_modal
        study_modal.open = True
        page.dialog.open = True
        page.update()

    # Floating Action Button to open Modal
    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=AppTheme.primary,
        on_click=open_study_modal
    )
    
    # Basic layout scaffold
    def app_layout():
        return ft.Row(
            controls=[
                # Sidebar
                Sidebar(page, on_nav_change=nav_change),
                # Main Content placeholder
                content_area
            ],
            expand=True
        )

    page.add(app_layout())
    page.update()

if __name__ == "__main__":
    ft.app(target=main)
