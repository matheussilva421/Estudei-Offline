
import flet as ft
from src.theme import AppTheme
from src.utils.pdf_parser import PDFParser
import src.data.crud as crud

class ImportSyllabusModal(ft.AlertDialog):
    def __init__(self, page: ft.Page, on_import_success=None):
        super().__init__()
        self.page_ref = page
        self.on_import_success = on_import_success
        self.modal = True
        self.bgcolor = AppTheme.surface
        self.title = ft.Text("Importar Edital (PDF)", color="white")
        
        # State
        self.selected_file = None
        self.extracted_topics = []
        
        # Components
        self.file_picker = ft.FilePicker(on_result=self.on_file_picked)
        self.page_ref.overlay.append(self.file_picker)
        
        self.btn_pick = ft.ElevatedButton("Selecionar PDF", icon=ft.Icons.UPLOAD_FILE, on_click=lambda _: self.file_picker.pick_files())
        self.status_text = ft.Text("", color="grey", size=12)
        
        self.dropdown_subject = ft.Dropdown(
            label="Vincular a Disciplina",
            options=[],
            width=300,
            text_style=ft.TextStyle(color="white"),
            bgcolor="#25263a",
            border_radius=5
        )
        
        self.preview_container = ft.Column(scroll=ft.ScrollMode.AUTO, height=200)
        
        self.content = ft.Container(
            width=500,
            content=ft.Column([
                ft.Text("Selecione um PDF do edital para extrair os tópicos automaticamente.", size=12, color="grey"),
                ft.Container(height=10),
                self.dropdown_subject,
                ft.Container(height=10),
                ft.Row([self.btn_pick, self.status_text]),
                ft.Divider(),
                ft.Text("Pré-visualização dos Tópicos:", weight=ft.FontWeight.BOLD, color="white", size=12),
                ft.Container(
                    bgcolor="#1e1e2d",
                    padding=10,
                    border_radius=5,
                    content=self.preview_container
                )
            ])
        )
        
        self.actions = [
            ft.TextButton("Cancelar", on_click=self.close_modal),
            ft.ElevatedButton("Importar", on_click=self.save_topics, bgcolor=AppTheme.primary, color="white")
        ]
        
        self.load_subjects()

    def load_subjects(self):
        subjects = crud.get_all_subjects()
        self.subject_map = {s['name']: s['id'] for s in subjects}
        self.dropdown_subject.options = [ft.dropdown.Option(name) for name in self.subject_map.keys()]

    def on_file_picked(self, e):
        if e.files:
            file_path = e.files[0].path
            self.status_text.value = e.files[0].name
            self.status_text.color = "white"
            self.status_text.update()
            
            # Parse
            parser = PDFParser()
            self.extracted_topics = parser.extract_topics(file_path)
            
            self.preview_container.controls.clear()
            if self.extracted_topics:
                 count = len(self.extracted_topics)
                 self.extract_count = count
                 for t in self.extracted_topics[:20]: # Show first 20
                     self.preview_container.controls.append(ft.Text(f"• {t}", size=12, color="grey"))
                 if count > 20:
                     self.preview_container.controls.append(ft.Text(f"... e mais {count-20} tópicos.", size=12, color=AppTheme.primary))
            else:
                 self.preview_container.controls.append(ft.Text("Nenhum tópico identificado. Tente outro formato.", color="red"))
            
            self.preview_container.update()

    def save_topics(self, e):
        subj_name = self.dropdown_subject.value
        if not subj_name:
            self.page_ref.snack_bar = ft.SnackBar(ft.Text("Selecione uma disciplina!"))
            self.page_ref.snack_bar.open = True
            self.page_ref.update()
            return

        if not self.extracted_topics:
            return

        subj_id = self.subject_map[subj_name]
        crud.add_topics_bulk(subj_id, self.extracted_topics)
        
        print(f"Imported {len(self.extracted_topics)} topics into {subj_name}")
        
        if self.on_import_success:
            self.on_import_success()
            
        self.close_modal(e)

    def close_modal(self, e):
        self.open = False
        self.page_ref.close_dialog()
        self.page_ref.update()
