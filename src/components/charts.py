
import flet as ft
from src.theme import AppTheme

class StudyChart(ft.Container):
    def __init__(self):
        super().__init__()
        self.bgcolor = AppTheme.surface
        self.border_radius = 10
        self.padding = 20
        # self.height = 300 # Let it expand or fixed
        
        # self.height = 300 # Let it expand or fixed
        import src.data.crud as crud
        raw_data = crud.get_weekly_study_data()
        
        # Find max for scaling
        max_val = max([d[1] for d in raw_data]) if raw_data else 1
        if max_val == 0: max_val = 1
        
        self.total_week_hours = sum([d[1] for d in raw_data])
        
        chart_bars = []
        for label, value in raw_data:
            # Normalize to 1.0 based on a fixed reasonable max (e.g., 8h) or dynamic max
            # Let's use dynamic max for visibility, but if max is small, stick to at least 4h scale
            scale_max = max(4, max_val)
            percent = value / scale_max
            # Bar Column
            chart_bars.append(
                ft.Column(
                    controls=[
                        # Bar background track? Or just bar.
                        ft.Container(
                            height=150, # Max height of chart area
                            width=20,
                            alignment=ft.Alignment(0, 1),
                            content=ft.Container(
                                bgcolor=AppTheme.primary,
                                width=20,
                                height=int(150 * percent), # Scale height
                                border_radius=ft.border_radius.vertical(top=5),
                                # Hover effect?
                                # animate=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
                            ),
                            bgcolor="#2c2d3e", # Track background
                            border_radius=5,
                        ),
                        ft.Text(label, size=10, color=AppTheme.text_secondary, text_align=ft.TextAlign.CENTER)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5
                )
            )

        self.chart_row = ft.Row(
            controls=chart_bars,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.END
        )
        
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("ESTUDO SEMANAL", size=12, weight=ft.FontWeight.BOLD, color="white"),
                        ft.Container(
                            content=ft.Row([ft.Text(f"{self.total_week_hours:.1f}h", color="black", size=10)], alignment=ft.MainAxisAlignment.CENTER),
                            bgcolor=AppTheme.primary, border_radius=5, padding=ft.padding.symmetric(horizontal=10, vertical=5)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Container(height=20),
                self.chart_row
            ]
        )
