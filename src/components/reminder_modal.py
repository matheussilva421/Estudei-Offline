
import flet as ft
from src.theme import AppTheme
import datetime

class ReminderModal(ft.AlertDialog):
    def __init__(self, page: ft.Page=None, on_save=None):
        super().__init__()
        self.page_ref = page
        self.on_save = on_save
        self.modal = True
        self.bgcolor = AppTheme.surface
        self.title_padding = 20
        self.content_padding = 20
        self.shape = ft.RoundedRectangleBorder(radius=10)
        
        self.title = ft.Row([
            ft.Text("Novo Lembrete", size=20, weight=ft.FontWeight.BOLD, color="white"),
            ft.IconButton(ft.Icons.CLOSE, on_click=self.close_modal)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Fields
        self.input_content = self.create_input("CONTEÚDO", "Ex.: Pagar boleto")
        self.dropdown_cat = self.create_dropdown("CATEGORIA", "Outros", ["Outros", "Simulado", "Revisão", "Material"])
        
        now = datetime.datetime.now()
        date_str = now.strftime("%d/%m/%Y")
        time_str = (now + datetime.timedelta(hours=1)).strftime("%H:%M")
        
        self.input_date = self.create_input("DATA", date_str)
        self.input_time = self.create_input("HORA", time_str)
        
        self.content = ft.Column(
            width=500,
            height=300,
            controls=[
                self.input_content,
                ft.Container(height=20),
                self.dropdown_cat,
                ft.Container(height=20),
                ft.Row([
                    ft.Column([self.input_date], expand=1),
                    ft.Container(width=20),
                    ft.Column([self.input_time], expand=1),
                ])
            ]
        )
        
        self.actions = [
             ft.OutlinedButton("Cancelar", on_click=self.close_modal, style=ft.ButtonStyle(color=AppTheme.primary, side=ft.BorderSide(1, AppTheme.primary))),
             ft.ElevatedButton("Salvar", bgcolor=AppTheme.primary, color="white", on_click=self.save_reminder)
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

    def save_reminder(self, e):
        import src.data.crud as crud
        content = self.input_content.controls[1].value
        cat = self.dropdown_cat.controls[1].value
        date = self.input_date.controls[1].value
        time = self.input_time.controls[1].value
        
        if not content:
            return
            
        full_date = f"{date} {time}"
        crud.add_reminder(content, cat, full_date)
        
        if self.page_ref:
             self.page_ref.snack_bar = ft.SnackBar(ft.Text("Lembrete salvo!"))
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

    def create_input(self, label, placeholder):
         return ft.Column([
            ft.Text(label, size=10, weight=ft.FontWeight.BOLD, color="white"),
            ft.TextField(
                value=placeholder,
                bgcolor="transparent",
                border_color=AppTheme.primary,
                border_width=0,
                border_radius=0,
                text_style=ft.TextStyle(color="white"),
                content_padding=5,
                hint_text=placeholder,
                hint_style=ft.TextStyle(color="grey"),
            ),
             ft.Container(height=1, bgcolor=AppTheme.primary, margin=ft.margin.only(top=-10))
        ])
        
    def create_dropdown(self, label, placeholder, options=[]):
        return ft.Column([
            ft.Text(label, size=10, weight=ft.FontWeight.BOLD, color="white"),
            ft.Dropdown(
                options=[ft.dropdown.Option(o) for o in options],
                value=options[0] if options else None,
                bgcolor="transparent",
                border_color=AppTheme.primary,
                border_width=0,
                border_radius=0,
                text_style=ft.TextStyle(color="white"),
                content_padding=5,
                hint_text=placeholder,
                hint_style=ft.TextStyle(color="grey"),
            ),
            ft.Container(height=1, bgcolor=AppTheme.primary, margin=ft.margin.only(top=-10)) 
        ])
