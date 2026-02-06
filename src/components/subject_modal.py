
import flet as ft
from src.theme import AppTheme
import src.data.crud as crud

class SubjectModal(ft.AlertDialog):
    def __init__(self, page: ft.Page, plan_id=None, on_save=None):
        super().__init__()
        self.page_ref = page
        self.plan_id = plan_id
        self.on_save = on_save
        self.modal = True
        self.bgcolor = AppTheme.surface
        self.shape = ft.RoundedRectangleBorder(radius=10)
        
        self.title = ft.Row([
            ft.Text("Nova Disciplina", size=18, weight=ft.FontWeight.BOLD, color="white"),
            ft.IconButton(ft.Icons.CLOSE, on_click=self.close_modal)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Form
        self.name_input = ft.TextField(label="Nome da Disciplina", bgcolor="transparent", text_style=ft.TextStyle(color="white"), border_color=AppTheme.primary)
        self.category_input = ft.TextField(label="Categoria (ex: Direito)", bgcolor="transparent", text_style=ft.TextStyle(color="white"), border_color=AppTheme.primary)
        
        # Color Picker (Mocked with simple choices)
        self.selected_color = AppTheme.primary
        self.color_row = ft.Row(spacing=10)
        colors = ["#00bfa5", "#ff4081", "#7c4dff", "#ffd740", "#ff6e40"]
        for c in colors:
            self.color_row.controls.append(
                ft.Container(
                    width=30, height=30, bgcolor=c, border_radius=15, 
                    on_click=lambda e, col=c: self.select_color(col, e.control),
                    border=ft.border.all(2, "white" if c == self.selected_color else "transparent")
                )
            )

        self.content = ft.Column(
            height=300,
            width=400,
            controls=[
                self.name_input,
                ft.Container(height=10),
                self.category_input,
                ft.Container(height=20),
                ft.Text("Cor da Disciplina", size=12, color="grey"),
                self.color_row,
                ft.Container(height=20),
                ft.Text("Dica: Você pode digitar e criar uma nova, ou o sistema irá sugerir (futuro).", size=10, color="grey")
            ]
        )
        
        self.actions = [
             ft.OutlinedButton("Cancelar", on_click=self.close_modal),
             ft.ElevatedButton("Salvar", bgcolor=AppTheme.primary, color="white", on_click=self.save_subject)
        ]

    def select_color(self, color, control):
        self.selected_color = color
        for c in self.color_row.controls:
            c.border = ft.border.all(2, "transparent")
        control.border = ft.border.all(2, "white")
        control.update()

    def save_subject(self, e):
        name = self.name_input.value
        cat = self.category_input.value
        
        if not name:
            self.name_input.error_text = "Obrigatório"
            self.name_input.update()
            return
            
        # Create Subject
        # Check if exists? For now, always create new or finding existing by name is complex without a dropdown.
        # User said "Search/Select... or Create".
        # Let's simple create for now for MVP velocity.
        
        # 1. Create Subject
        import src.data.crud as crud
        new_sub_id = crud.add_subject_return_id(name, cat, self.selected_color)
        
        # 2. Link to Plan (if plan_id provided)
        if self.plan_id:
            crud.add_subject_to_plan(self.plan_id, new_sub_id)
            
        if self.on_save:
            self.on_save()
            
        self.close_modal(e)

    def close_modal(self, e):
        self.open = False
        self.page_ref.close_dialog()
        self.page_ref.update()
