
import flet as ft
from src.theme import AppTheme


from src.components.import_modal import ImportSyllabusModal

class SubjectsPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page_ref = page
        self.padding = 30
        self.expand = True
        
        # --- Top Header Stats ---
        self.header = ft.Container(
            bgcolor=AppTheme.surface,
            padding=20,
            border_radius=10,
            content=ft.Row(
                controls=[
                    ft.Column([ft.Text("TEMPO DE ESTUDO", size=10, weight=ft.FontWeight.BOLD, color="white"), ft.Text("2h55min", size=24, color="white")]),
                    ft.Column([ft.Text("DESEMPENHO", size=10, weight=ft.FontWeight.BOLD, color="white"), ft.Row([ft.Text("42 Acertos", size=10, color="green"), ft.Text("37 Erros", size=10, color="red")]), ft.Text("53%", size=24, color="white")]),
                    ft.Column([ft.Text("PROGRESSO NO EDITAL", size=10, weight=ft.FontWeight.BOLD, color="white"), ft.Text("1 Tópicos Concluidos", size=10, color="#FF6E40"), ft.Text("3%", size=24, color="white")]),
                    ft.Column([ft.Text("PÁGINAS LIDAS", size=10, weight=ft.FontWeight.BOLD, color="white"), ft.Text("12.0 páginas por hora", size=10, color="grey"), ft.Text("24", size=24, color="white")]),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )
        
        # --- History Section (Placeholder / Mock for now as DB history is basic) ---
        self.history_section = ft.Container(
            bgcolor=AppTheme.surface, padding=20, border_radius=10, margin=ft.margin.only(top=20),
            content=ft.Column([
                ft.Text("HISTÓRICO DE REGISTROS", size=12, weight=ft.FontWeight.BOLD, color="white"),
                ft.Row([
                    ft.Text("Data", width=80, color="grey", size=12),
                    ft.Text("Categoria", width=100, color="grey", size=12),
                    ft.Text("Tempo", width=80, color="grey", size=12),
                    ft.Text("✓", width=30, color="green", size=12),
                    ft.Text("X", width=30, color="red", size=12),
                    ft.Text("%", width=30, color="white", size=12),
                    ft.Text("Tópico", expand=1, color="grey", size=12),
                ]),
                ft.Divider(color=AppTheme.background),
                self.create_history_row("20/01/26", "QUESTÕES", "00:55:01", 19, 31, 38, "2. O orçamento públ..."),
                self.create_history_row("14/01/26", "TEORIA", "02:00:00", 23, 6, 79, "1.1. Conceito."),
            ])
        )

        # --- Edital Verticalizado (Detailed Topic List) ---
        self.topic_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        
        # Load subjects dropdown to filter topics (Mock for now, just load all first subject?)
        # For prototype, let's load all topics from DB if any, or show "No topics" message
        
        self.topics_section = ft.Container(
            bgcolor=AppTheme.surface, padding=20, border_radius=10, margin=ft.margin.only(top=20),
            expand=True,
            content=ft.Column([
                ft.Row([
                    ft.Text("EDITAL VERTICALIZADO", size=12, weight=ft.FontWeight.BOLD, color="white"),
                    ft.ElevatedButton("Importar Edital (PDF)", icon=ft.Icons.UPLOAD_FILE, height=30, 
                                      style=ft.ButtonStyle(color="white", bgcolor=AppTheme.primary, shape=ft.RoundedRectangleBorder(radius=5)),
                                      on_click=self.open_import_modal),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.Row([
                    ft.Text("Tópicos", expand=1, color="grey"),
                    ft.Text("Status", width=60, color="grey"),
                ]),
                 ft.Divider(color=AppTheme.background),
                 self.topic_list
            ])
        )
        
        self.content = ft.Column(
            controls=[
                self.header,
                self.history_section,
                self.topics_section
            ],
            scroll=ft.ScrollMode.AUTO
        )
        
        self.load_topics()

    def open_import_modal(self, e):
        modal = ImportSyllabusModal(self.page_ref, on_import_success=self.load_topics)
        self.page_ref.dialog = modal
        modal.open = True
        self.page_ref.update()

    def load_topics(self):
        import src.data.crud as crud
        self.topic_list.controls.clear()
        
        # Heuristic: just load from first subject that has topics, or all
        # To make it simple, let's just query ALL topics from the first subject found?
        subjects = crud.get_all_subjects()
        if not subjects: return
        
        # Try to find one with topics
        target_sub = subjects[0]
        topics = crud.get_topics_by_subject(target_sub['id'])
        
        # If no topics, try others
        if not topics:
             for s in subjects:
                 t = crud.get_topics_by_subject(s['id'])
                 if t:
                     topics = t
                     target_sub = s
                     break
        
        if topics:
             self.topic_list.controls.append(ft.Text(f"Disciplina: {target_sub['name']}", color=AppTheme.primary, size=14, weight=ft.FontWeight.BOLD))
             for t in topics:
                 self.topic_list.controls.append(
                     self.create_topic_row_db(t['id'], t['title'], t['completed'])
                 )
        else:
             self.topic_list.controls.append(ft.Text("Nenhum tópico encontrado. Importe um edital.", color="grey"))
             
        self.page_ref.update()

    def create_topic_row_db(self, t_id, title, completed):
        import src.data.crud as crud
        def toggle(e):
            crud.toggle_topic_complete(t_id, e.control.value)
            print(f"Topic {t_id} toggled: {e.control.value}")
            
        return ft.Container(
            padding=5,
            content=ft.Row([
                ft.Text(title, expand=1, size=12, color="white" if not completed else "grey"),
                ft.Checkbox(value=bool(completed), on_change=toggle)
            ])
        )

    def create_history_row(self, date, cat, time, correct, error, perc, topic):
        color_cat = "#66bb6a" if cat == "QUESTÕES" else "#ab47bc"
        return ft.Row([
            ft.Text(date, width=80, color="white", size=12),
            ft.Container(ft.Text(cat, size=10, color="black", weight=ft.FontWeight.BOLD), bgcolor=color_cat, padding=3, border_radius=3, width=80, alignment=ft.Alignment(0,0)), # Fixed alignment
            ft.Text(time, width=80, color="white", size=12),
            ft.Text(str(correct), width=30, color="green", size=12),
            ft.Text(str(error), width=30, color="red", size=12),
            ft.Container(ft.Text(str(perc), size=10, color="white", weight=ft.FontWeight.BOLD), bgcolor=("red" if perc < 50 else "green"), padding=2, border_radius=3, width=30, alignment=ft.Alignment(0,0)),
            ft.Text(topic, expand=1, color="white", size=12),
        ])

    def create_topic_row(self, title, correct, error, total, perc, active=False):
        # Legacy Helper (kept just in case)
        pass


def get_subjects_page(page=None):
    return SubjectsPage(page)
