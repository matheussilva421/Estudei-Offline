
import flet as ft
from src.theme import AppTheme

class PlanModal(ft.AlertDialog):
    def __init__(self, page: ft.Page=None, on_save=None):
        super().__init__()
        self.page_ref = page
        self.on_save = on_save
        self.modal = True
        self.bgcolor = AppTheme.surface
        self.shape = ft.RoundedRectangleBorder(radius=10)
        
        self.title = ft.Row([
            ft.Text("Criar Novo Plano", size=20, weight=ft.FontWeight.BOLD, color="white"),
            ft.IconButton(ft.Icons.CLOSE, on_click=self.close_modal)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Inputs
        self.name_input = self.create_input("NOME DO PLANO", "Ex.: TJ-SP Escrevente")
        self.obs_input = self.create_input("OBSERVAÇÕES", "Detalhes...", multiline=True, height=80)
        
        self.check_generic = ft.Checkbox(
            label="Não estou estudando para nenhuma prova específica",
            label_style=ft.TextStyle(color="white", size=12),
            active_color=AppTheme.primary,
            check_color=AppTheme.background,
            on_change=self.toggle_generic
        )
        
        # Subject Selection (Hidden if generic)
        self.subjects_container = ft.Column(visible=True)
        self.load_subjects_checklist()

        # Mock Image Picker
        self.btn_image = ft.OutlinedButton(
            "Adicionar Imagem de Capa",
            icon=ft.Icons.IMAGE,
            style=ft.ButtonStyle(color="white", side=ft.BorderSide(1, "grey"))
        )
        
        self.content = ft.Column(
            width=600,
            height=500,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                self.name_input,
                ft.Container(height=20),
                self.obs_input,
                ft.Container(height=20),
                ft.Text("CONFIGURAÇÕES", size=10, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(height=10),
                self.check_generic,
                ft.Container(height=10),
                self.subjects_container,
                ft.Container(height=10),
                self.btn_image
            ]
        )
        
        self.actions = [
             ft.OutlinedButton("Cancelar", on_click=self.close_modal, style=ft.ButtonStyle(color=AppTheme.primary, side=ft.BorderSide(1, AppTheme.primary))),
             ft.ElevatedButton("Salvar Plano", bgcolor=AppTheme.primary, color="white", on_click=self.save_plan)
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def load_subjects_checklist(self):
        import src.data.crud as crud
        subjects = crud.get_all_subjects()
        self.subject_checks = []
        
        grid = ft.GridView(
            runs_count=3,
            max_extent=150,
            child_aspect_ratio=3.0,
            spacing=10,
            run_spacing=10,
        )
        
        for s in subjects:
            ck = ft.Checkbox(label=s['name'], value=False, label_style=ft.TextStyle(size=12, color="white"))
            ck.data = s['id'] # Store ID in data
            self.subject_checks.append(ck)
            grid.controls.append(ck)
            
        self.subjects_container.controls = [
            ft.Text("SELECIONE AS DISCIPLINAS", size=10, weight=ft.FontWeight.BOLD, color="white"),
            ft.Container(height=150, content=grid, border=ft.border.all(1, "grey"), border_radius=5, padding=10)
        ]

    def toggle_generic(self, e):
        is_gen = self.check_generic.value
        self.subjects_container.visible = not is_gen
        self.subjects_container.update()

    def create_input(self, label, placeholder, multiline=False, height=None):
        return ft.Column([
            ft.Text(label, size=10, weight=ft.FontWeight.BOLD, color="white"),
            ft.TextField(
                bgcolor="transparent",
                border_color=AppTheme.primary,
                border_width=0,
                border_radius=0,
                text_style=ft.TextStyle(color="white"),
                content_padding=5,
                hint_text=placeholder,
                hint_style=ft.TextStyle(color="grey"),
                multiline=multiline,
                height=height
            ),
             ft.Container(height=1, bgcolor=AppTheme.primary, margin=ft.margin.only(top=-10))
        ])

    def save_plan(self, e):
        import src.data.crud as crud
        name = self.name_input.controls[1].value
        obs = self.obs_input.controls[1].value
        is_generic = self.check_generic.value
        
        if not name:
             self.name_input.controls[1].border_color = "red"
             self.name_input.update()
             return

        # Collect Subject IDs
        selected_ids = []
        if not is_generic and hasattr(self, 'subject_checks'):
             for ck in self.subject_checks:
                 if ck.value:
                     selected_ids.append(ck.data)

        crud.add_plan(name, obs, has_image=False, is_generic=is_generic, subject_ids=selected_ids)
        
        if self.page_ref:
             self.page_ref.snack_bar = ft.SnackBar(ft.Text(f"Plano '{name}' criado!"))
             self.page_ref.snack_bar.open = True
             self.page_ref.update()
             
        if self.on_save:
            self.on_save()
            
        self.close_modal(e)

    def close_modal(self, e):
        self.open = False
        if self.page_ref:
            self.page_ref.close_dialog()
            self.page_ref.update()
