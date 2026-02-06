import flet as ft
from src.theme import AppTheme
from src.components.plan_modal import PlanModal
import src.data.crud as crud

class PlansPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page_ref = page
        self.expand = True
        self.padding = 30
        self.build_ui()

    def build_ui(self):
        # Header
        header = ft.Row(
            controls=[
                ft.Text("Meus Planos", size=30, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(width=20),
                ft.ElevatedButton(
                    "Criar Novo Plano", 
                    icon=ft.Icons.ADD, 
                    bgcolor=AppTheme.primary, 
                    color="white",
                    on_click=self.open_modal
                )
            ],
            alignment=ft.MainAxisAlignment.START
        )
        
        self.active_plans_grid = ft.GridView(
            expand=1,
            runs_count=5, # Increased for wider screens
            max_extent=300,
            child_aspect_ratio=1.0,
            spacing=20,
            run_spacing=20,
        )
        
        self.archived_col = ft.Column()

        self.content = ft.Column(
            controls=[
                header,
                ft.Divider(color="grey", thickness=0.5),
                ft.Text("ATIVOS", size=14, weight=ft.FontWeight.BOLD, color="grey"),
                ft.Container(content=self.active_plans_grid, expand=True, height=300), 
                ft.Divider(color="grey", thickness=0.5),
                ft.Text("ARQUIVADOS", size=14, weight=ft.FontWeight.BOLD, color="grey"),
                self.archived_col
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        self.load_data()

    def load_data(self):
        self.active_plans_grid.controls = []
        self.archived_col.controls = []
        
        # Add "New Plan" Card as first item in grid
        self.active_plans_grid.controls.append(self.create_add_card())
        
        plans = crud.get_plans(archived=0)
        for p in plans:
            self.active_plans_grid.controls.append(self.create_plan_card(p))
            
        archived = crud.get_plans(archived=1)
        for p in archived:
            self.archived_col.controls.append(self.create_archived_row(p))
        # Note: Don't call self.update() here - control may not be mounted yet

    def create_add_card(self):
        return ft.Container(
            bgcolor="#2c2d3e",
            border_radius=15,
            padding=20,
            content=ft.Column([
                ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, size=40, color=AppTheme.primary),
                ft.Text("Criar Novo Plano", size=16, weight=ft.FontWeight.BOLD, color="white")
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            on_click=self.open_modal,
            ink=True
        )

    def create_plan_card(self, plan):
        # plan keys: id, name, observations, has_image, is_generic
        return ft.Container(
            bgcolor=AppTheme.surface, 
            border_radius=15,
            padding=15,
            border=ft.border.all(1, "#333"),
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.BOOKMARK, color=AppTheme.primary),
                    ft.IconButton(ft.Icons.MORE_VERT, icon_color="grey")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(plan['name'], size=16, weight=ft.FontWeight.BOLD, color="white", max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(plan['observations'] or "Sem observações", size=12, color="grey", max_lines=3, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Container(expand=True),
                ft.Row([
                    ft.Chip(label=ft.Text("Genérico" if plan['is_generic'] else "Focado", size=10), bgcolor="#333")
                ])
            ]),
            on_click=lambda e, pid=plan['id']: self.open_plan_details(pid)
        )

    def open_plan_details(self, plan_id):
        # Use NavigationManager for proper navigation
        self.page_ref.nav.push("plan_details", plan_id=plan_id)

    def create_archived_row(self, plan):
        return ft.ListTile(
            leading=ft.Icon(ft.Icons.ARCHIVE, color="grey"),
            title=ft.Text(plan['name'], color="grey"),
            subtitle=ft.Text(plan['created_at'], color="grey"),
        )

    def open_modal(self, e):
        self.modal = PlanModal(self.page_ref, on_save=self.load_data)
        self.page_ref.dialog = self.modal
        self.modal.open = True
        self.page_ref.update()

# Helper for main
def get_plans_page(page):
    return PlansPage(page)
