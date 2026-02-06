
import flet as ft
from src.theme import AppTheme
import src.data.crud as crud
from datetime import datetime

class MockExamModal(ft.AlertDialog):
    def __init__(self, page: ft.Page, on_save=None):
        super().__init__()
        self.page_ref = page
        self.on_save = on_save
        self.modal = True
        self.title = ft.Text("Novo Simulado")
        
        self.name_input = ft.TextField(label="Nome do Simulado", autofocus=True)
        self.date_input = ft.TextField(label="Data (YYYY-MM-DD)", value=datetime.now().strftime("%Y-%m-%d"))
        self.board_input = ft.TextField(label="Banca")
        self.style_dropdown = ft.Dropdown(
            label="Estilo",
            options=[
                ft.dropdown.Option("Múltipla Escolha"),
                ft.dropdown.Option("Certo/Errado"),
            ]
        )
        self.time_spent = ft.TextField(label="Tempo Gasto (HH:MM)")
        
        # Grid for Subjects
        self.subjects = crud.get_subjects_by_plan(None) # Get all subjects? 
        # Actually standard crud.get_subjects does not exist maybe? crud.get_plans...
        # Let's assume we want ALL subjects.
        self.subjects_all = crud.db.fetch_all("SELECT * FROM subjects")
        
        self.subject_rows = []
        
        self.content = ft.Container(
            width=600,
            content=ft.Column([
                ft.Row([self.name_input, self.date_input]),
                ft.Row([self.board_input, self.style_dropdown]),
                self.time_spent,
                ft.Divider(),
                ft.Text("Desempenho por Disciplina", weight=ft.FontWeight.BOLD),
                ft.Container(
                    height=300,
                    content=ft.ListView(controls=self.build_subject_inputs())
                )
            ], scroll=ft.ScrollMode.AUTO)
        )
        
        self.actions = [
            ft.TextButton("Cancelar", on_click=self.close_modal),
            ft.ElevatedButton("Salvar", on_click=self.save_exam, bgcolor=AppTheme.primary, color="white")
        ]

    def build_subject_inputs(self):
        rows = []
        for s in self.subjects_all:
            # Inputs: Correct, Wrong, Blank, Weight
            c_input = ft.TextField(label="C", width=60, value="0", text_size=12)
            w_input = ft.TextField(label="E", width=60, value="0", text_size=12)
            b_input = ft.TextField(label="B", width=60, value="0", text_size=12)
            weight_input = ft.TextField(label="Peso", width=60, value="1.0", text_size=12)
            
            self.subject_rows.append({
                "sub_id": s['id'],
                "c": c_input,
                "w": w_input,
                "b": b_input,
                "weight": weight_input
            })
            
            rows.append(ft.Row([
                ft.Text(s['name'], expand=True, size=12),
                weight_input,
                c_input,
                w_input,
                b_input
            ]))
        return rows

    def save_exam(self, e):
        # 1. Validation & Data Collection
        name = self.name_input.value
        date = self.date_input.value
        board = self.board_input.value
        style = self.style_dropdown.value
        time = self.time_spent.value
        
        if not name:
            self.name_input.error_text = "Nome é obrigatório"
            self.name_input.update()
            return
            
        items_data = []
        total_score = 0
        total_q = 0
        
        has_error = False
        
        for row in self.subject_rows:
            # Clear previous errors
            row['c'].error_text = None
            row['w'].error_text = None
            row['b'].error_text = None
            
            try:
                c = int(row['c'].value) if row['c'].value else 0
                w = int(row['w'].value) if row['w'].value else 0
                b = int(row['b'].value) if row['b'].value else 0
                weight = float(row['weight'].value) if row['weight'].value else 1.0
            except ValueError:
                # Mark fields with error
                row['c'].error_text = "!"
                has_error = True
                continue
                
            q_count = c + w + b
            if q_count == 0: continue
            
            # Score Calculation
            if style == "Certo/Errado":
                score = (c - w) * weight
            else:
                score = c * weight
                
            total_score += score
            total_q += q_count
            
            items_data.append((row['sub_id'], weight, c, w, b))
            
        if has_error:
            self.page_ref.show_snack_bar(ft.SnackBar(content=ft.Text("Corrija os valores inválidos (apenas números)."), bgcolor="red"))
            self.page_ref.update()
            return

        if not items_data:
            self.page_ref.show_snack_bar(ft.SnackBar(content=ft.Text("Preencha ao menos uma disciplina."), bgcolor="orange"))
            return

        # 2. Persist Data (Optimized)
        try:
            # Insert Exam Header
            cursor = crud.db.execute_query('''
                INSERT INTO mock_exams (name, date, score, total_questions, time_spent, style, board)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, date, total_score, total_q, time, style, board))
            exam_id = cursor.lastrowid
            
            # Bulk Insert Items
            crud.add_mock_exam_items_bulk(exam_id, items_data)
            
            # 3. UI Feedback
            self.close_modal(None)
            if self.on_save: self.on_save()
            
            self.page_ref.show_snack_bar(ft.SnackBar(content=ft.Text(f"Simulado salvo! Nota: {total_score:.2f}"), bgcolor="green"))
            
        except Exception as ex:
            self.page_ref.show_snack_bar(ft.SnackBar(content=ft.Text(f"Erro ao salvar: {str(ex)}"), bgcolor="red"))

    def close_modal(self, e):
        self.open = False
        self.page_ref.update()
