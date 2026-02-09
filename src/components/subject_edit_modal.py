
import flet as ft
from src.theme import AppTheme
import src.data.crud as crud

class SubjectEditModal(ft.AlertDialog):
    def __init__(self, page: ft.Page, plan_id, subject_data, on_save=None):
        super().__init__()
        self.page_ref = page
        self.plan_id = plan_id
        self.subject_id = subject_data['id']
        self.initial_name = subject_data['name']
        self.initial_color = subject_data['color'] or AppTheme.primary
        self.on_save = on_save
        
        self.modal = True
        self.bgcolor = AppTheme.surface
        self.shape = ft.RoundedRectangleBorder(radius=10)
        
        self.title = ft.Row([
            ft.Text("Editar Disciplina", size=18, weight=ft.FontWeight.BOLD, color="white"),
            ft.IconButton(ft.Icons.CLOSE, on_click=self.close_modal)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # --- Fields ---
        self.name_input = ft.TextField(
            value=self.initial_name, 
            label="Nome", 
            bgcolor="transparent", 
            text_style=ft.TextStyle(color="white"),
            border_color=AppTheme.primary,
            height=40,
            content_padding=10
        )
        
        self.selected_color = self.initial_color
        self.color_row = ft.Row(spacing=5)
        self.build_color_picker()
        
        # --- Topics ---
        self.topics_container = ft.Column(scroll=ft.ScrollMode.AUTO, height=300)
        self.load_topics()
        
        self.content = ft.Container(
            width=500,
            height=600,
            content=ft.Column([
                self.name_input,
                ft.Container(height=10),
                ft.Text("Cor", size=10, color="grey"),
                self.color_row,
                ft.Divider(color="grey", thickness=0.5),
                ft.Row([
                    ft.Text("Tópicos / Assuntos", size=14, weight=ft.FontWeight.BOLD, color="white"),
                    ft.IconButton(ft.Icons.ADD_CIRCLE, icon_color=AppTheme.primary, on_click=self.add_topic_ui)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.topics_container
            ])
        )
        
        self.actions = [
             ft.OutlinedButton("Remover do Plano", icon=ft.Icons.DELETE, icon_color="red", style=ft.ButtonStyle(color="red"), on_click=self.remove_from_plan),
             ft.OutlinedButton("Excluir Disciplina", icon=ft.Icons.DELETE_FOREVER, icon_color="red", style=ft.ButtonStyle(color="red"), on_click=self.confirm_delete_subject),
             ft.Container(expand=True),
             ft.OutlinedButton("Cancelar", on_click=self.close_modal),
             ft.ElevatedButton("Salvar", bgcolor=AppTheme.primary, color="white", on_click=self.save_changes)
        ]
        self.actions_alignment = ft.MainAxisAlignment.SPACE_BETWEEN

    def build_color_picker(self):
        colors = ["#00bfa5", "#ff4081", "#7c4dff", "#ffd740", "#ff6e40", "#2196f3", "#4caf50"]
        for c in colors:
            self.color_row.controls.append(
                ft.Container(
                    width=25, height=25, bgcolor=c, border_radius=12.5,
                    border=ft.border.all(2, "white" if c == self.selected_color else "transparent"),
                    on_click=lambda e, col=c: self.select_color(col, e.control)
                )
            )

    def select_color(self, color, control):
        self.selected_color = color
        for c in self.color_row.controls:
            c.border = ft.border.all(2, "transparent")
        control.border = ft.border.all(2, "white")
        control.update()

    def load_topics(self):
        self.topics_container.controls = []
        topics = crud.get_topics_by_subject(self.subject_id)
        for t in topics:
            self.topics_container.controls.append(self.create_topic_item(t))
        if self.page_ref: self.topics_container.update()

    def create_topic_item(self, topic):
        # View Mode
        text_view = ft.Text(topic['title'], size=12, color="white", expand=True)
        
        def save_edit(e, input_ctrl):
            new_title = input_ctrl.value
            if new_title:
                crud.update_topic(topic['id'], new_title)
                text_view.value = new_title
                edit_group.visible = False
                view_group.visible = True
                self.topics_container.update()

        def cancel_edit(e):
            edit_group.visible = False
            view_group.visible = True
            self.topics_container.update()
            
        def enable_edit(e):
            view_group.visible = False
            edit_group.visible = True
            self.topics_container.update()

        def delete_t(e):
            crud.delete_topic(topic['id'])
            self.load_topics()

        # Edit Mode Controls
        edit_input = ft.TextField(value=topic['title'], height=30, text_style=ft.TextStyle(size=12), content_padding=5, expand=True)
        edit_group = ft.Row([
            edit_input,
            ft.IconButton(ft.Icons.CHECK, icon_size=16, icon_color="green", on_click=lambda e: save_edit(e, edit_input)),
            ft.IconButton(ft.Icons.CLOSE, icon_size=16, icon_color="red", on_click=cancel_edit)
        ], visible=False)

        view_group = ft.Row([
            ft.Icon(ft.Icons.DRAG_HANDLE, size=16, color="grey"), # Placeholder for drag
            text_view,
            ft.IconButton(ft.Icons.EDIT, icon_size=16, icon_color="grey", on_click=enable_edit),
            ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_size=16, icon_color="red", on_click=delete_t)
        ])

        return ft.Container(
            content=ft.Column([view_group, edit_group]),
            bgcolor="#333",
            padding=5,
            border_radius=5,
            margin=ft.margin.only(bottom=5)
        )

    def add_topic_ui(self, e):
        # Add a temporary input at the top or bottom
        # Let's simple add to DB using a minimal dialog or just append a blank editable row?
        # Appending blank editable row:
        
        def confirm_add(e):
            if input_new.value:
                crud.add_topic(self.subject_id, input_new.value)
                self.load_topics()
        
        input_new = ft.TextField(hint_text="Novo Tópico", height=30, text_style=ft.TextStyle(size=12), content_padding=5, expand=True, autofocus=True)
        row = ft.Row([
            input_new,
            ft.IconButton(ft.Icons.CHECK, icon_size=16, icon_color="green", on_click=confirm_add),
            ft.IconButton(ft.Icons.DELETE, icon_size=16, icon_color="red", on_click=lambda e: self.load_topics()) # Cancel reloads
        ])
        
        self.topics_container.controls.append(ft.Container(content=row, bgcolor="#333", padding=5, border_radius=5))
        self.topics_container.update()

    def save_changes(self, e):
        # Save Subject Name/Color
        new_name = self.name_input.value
        crud.update_subject_details(self.subject_id, new_name, self.selected_color)
        
        if self.on_save:
            self.on_save()
        self.close_modal(e)

    def remove_from_plan(self, e):
        crud.remove_subject_from_plan(self.plan_id, self.subject_id)
        if self.on_save:
            self.on_save()
        self.close_modal(e)

    def confirm_delete_subject(self, e):
        def confirm_action(_):
            self.page_ref.close_dialog()
            self.delete_subject()

        dialog = ft.AlertDialog(
            title=ft.Text("Excluir disciplina"),
            content=ft.Text("Tem certeza? Essa ação remove sessões, tópicos e vínculos."),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.page_ref.close_dialog()),
                ft.TextButton("Excluir", on_click=confirm_action),
            ],
        )
        self.page_ref.dialog = dialog
        dialog.open = True
        self.page_ref.update()

    def delete_subject(self):
        crud.delete_subject(self.subject_id)
        if self.on_save:
            self.on_save()
        self.close_modal(None)

    def close_modal(self, e):
        self.open = False
        self.page_ref.close_dialog()
        self.page_ref.update()
