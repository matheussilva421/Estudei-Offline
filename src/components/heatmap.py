
import flet as ft
from src.theme import AppTheme
import datetime

class ConsistencyHeatmap(ft.Container):
    def __init__(self):
        super().__init__()
        self.bgcolor = "transparent"
        self.padding = ft.padding.symmetric(vertical=10)
        
        # Mock data: List of boolean/status for the last X days
        # e.g., 0 = none, 1 = studied, 2 = missed target
        # For visual fidelity to image: "Você está há 1 dia sem estudar!"
        
        today = datetime.date.today()
        # Create a horizontal scrollable row of circles
        
        self.days_row = ft.Row(scroll=ft.ScrollMode.HIDDEN, spacing=5)
        
        # Populate with mock squares/circles
        for i in range(30):
            status = i % 3  # Mock pattern
            color = "#2c2d3e" # Empty
            icon = None
            
            if status == 1:
                color = AppTheme.primary 
                icon = ft.Icons.CHECK
            elif status == 2:
                color = AppTheme.secondary
                icon = ft.Icons.CLOSE
                
            self.days_row.controls.append(
                ft.Container(
                    width=30, height=30,
                    bgcolor=color,
                    border_radius=15, # Circular
                    content=ft.Icon(icon, size=16, color="white") if icon else None,
                    alignment=ft.Alignment(0, 0)
                )
            )

        self.content = ft.Column(
            controls=[
                ft.Row(
                   controls=[
                       ft.Text("CONSTÂNCIA NOS ESTUDOS", size=12, weight=ft.FontWeight.BOLD, color="white"),
                       ft.Icon(ft.Icons.HELP_OUTLINE, size=14, color=AppTheme.text_secondary)
                   ] 
                ),
                ft.Text("Você está há 1 dia sem estudar! Seu maior tempo parado foi de 4 dias, volte a estudar hoje!", size=12, color=AppTheme.text_secondary),
                ft.Container(height=10),
                self.days_row
            ]
        )
