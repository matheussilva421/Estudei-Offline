
import flet as ft
from src.theme import AppTheme

class StatCard(ft.Container):
    def __init__(self, title, value, subtext=None, progress=None, color=None):
        super().__init__()
        self.bgcolor = AppTheme.surface
        self.border_radius = 10
        self.padding = 20
        self.expand = True
        
        content_controls = [
            ft.Text(title.upper(), size=12, weight=ft.FontWeight.BOLD, color=AppTheme.text_secondary),
            ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color="white"),
        ]
        
        if subtext:
             content_controls.append(ft.Text(subtext, size=12, color=AppTheme.text_secondary))
             
        if progress is not None:
             # Progress bar
             content_controls.append(
                 ft.ProgressBar(value=progress, color=color if color else AppTheme.primary, bgcolor="#2c2d3e", height=5)
             )
        
        # If there are specific sub-stats like "261 Acertos", we can pass them as a custom control or format the subtext.
        # For valid specialized cards, subclassing might be better, but we'll keep it simple.

        self.content = ft.Column(
            controls=content_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

class PerformanceCard(StatCard):
    def __init__(self, title, percentage, correct, errors):
        # We override the init to customize the layout for "Desempenho"
        super().__init__(title, f"{percentage}%")
        
        self.content.controls.pop() # Remove the default simple value if needed or keep it
        self.content.controls = [
             ft.Text(title.upper(), size=12, weight=ft.FontWeight.BOLD, color=AppTheme.text_secondary),
             ft.Row(
                 controls=[
                     ft.Text(f"{percentage}%", size=28, weight=ft.FontWeight.BOLD, color="white"),
                     ft.Column(
                         controls=[
                             ft.Text(f"{correct} Acertos", size=10, color=AppTheme.primary),
                             ft.Text(f"{errors} Erros", size=10, color=AppTheme.secondary),
                         ],
                         spacing=2
                     )
                 ],
                 alignment=ft.MainAxisAlignment.SPACE_BETWEEN
             )
        ]

