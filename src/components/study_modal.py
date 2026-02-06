
import flet as ft
from src.theme import AppTheme
import datetime

class StudyModal(ft.AlertDialog):
    def __init__(self, page: ft.Page=None, open=False):
        super().__init__()
        # self.page = page 
        # Note: self.page is internal to control if added, but we might pass it. 
        # But AlertDialog is added to page.dialog.
        self.open = open
        self.modal = True
        self.bgcolor = AppTheme.surface
        self.title_padding = 20
        self.content_padding = 20
        self.shape = ft.RoundedRectangleBorder(radius=10)
        
        # --- Date Toggles ---
        self.selected_date_opt = "HOJE"
        self.date_buttons_row = ft.Row()
        self.update_date_buttons()
        
        # --- Form Fields ---
        self.dropdown_category = self.create_dropdown("CATEGORIA", "Selecione...", options=["Teoria", "Questões", "VídeoAula", "Revisão"])
        self.dropdown_category.controls[1].on_change = self.on_category_change
        
        self.dropdown_disc = self.create_dropdown("DISCIPLINA", "Selecione ou crie uma nova")
        self.input_time = self.create_input("TEMPO DE ESTUDO", "00:00:00")
        self.input_topic = self.create_input("TÓPICO", "Selecione ou crie um novo")
        self.input_material = self.create_input("MATERIAL", "Ex.: Aula 01, PDF X")
        
        # --- Checkboxes ---
        self.check_theory = ft.Checkbox(label="TEORIA FINALIZADA", value=False, check_color=AppTheme.background, active_color="white", label_style=ft.TextStyle(color="white", size=12))
        self.check_planning = ft.Checkbox(label="CONTABILIZAR NO PLANEJAMENTO", value=True, check_color=AppTheme.background, active_color=AppTheme.primary, label_style=ft.TextStyle(color="white", size=12))
        self.check_review = ft.Checkbox(label="PROGRAMAR REVISÕES", value=False, check_color=AppTheme.background, active_color="white", label_style=ft.TextStyle(color="white", size=12))
        

        # --- Stats Group ---
        # Metrics by Type
        self.stats_questions = self.create_stat_box("QUESTÕES", ["ACERTOS", "ERROS"], ["0", "0"])
        self.stats_pages = self.create_stat_box("PÁGINAS", ["INÍCIO", "FIM"], ["0", "0"])
        self.stats_video = self.create_stat_box("VIDEOAULAS", ["TÍTULO", "INÍCIO", "FIM"], ["", "00:00", "00:00"])
        
        self.stats_container = ft.Row([
            self.stats_questions,
            self.stats_pages,
            self.stats_video
        ], alignment=ft.MainAxisAlignment.START, spacing=20)
        
        # Initially hide all or show based on default
        self.stats_questions.visible = False
        self.stats_pages.visible = False
        self.stats_video.visible = False
        
        self.title = ft.Row([
            ft.Text("Registro de Estudo", size=20, weight=ft.FontWeight.BOLD, color="white"),
            ft.IconButton(ft.Icons.CLOSE, on_click=self.close_modal)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        self.save_new_check = ft.Checkbox(label="SALVAR E CRIAR NOVO", label_style=ft.TextStyle(color="white", size=12))

        self.content = ft.Column(
            width=700,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Row([ft.Icon(ft.Icons.CALENDAR_MONTH, color="white"), self.date_buttons_row]),
                ft.Container(height=20),
                ft.Row([
                    ft.Column([self.dropdown_category], expand=1),
                    ft.Container(width=20),
                    ft.Column([self.dropdown_disc], expand=2),
                    ft.Container(width=20),
                    ft.Column([self.input_time], expand=1),
                ]),
                ft.Container(height=10),
                ft.Row([
                    ft.Column([self.input_topic], expand=2),
                     ft.Container(width=20),
                    ft.Column([self.input_material], expand=1),
                ]),
                ft.Container(height=20),
                ft.Row([self.check_theory, self.check_planning, self.check_review], wrap=True, spacing=20),
                ft.Container(height=20),
                self.stats_container,
                ft.Container(height=20),
                ft.Text("COMENTÁRIOS", size=10, weight=ft.FontWeight.BOLD, color="white"),
                ft.TextField(multiline=True, bgcolor="#2c2d3e", border_color=AppTheme.primary, text_style=ft.TextStyle(color="white")),
                ft.Container(height=10),
                self.save_new_check,
            ]
        )
        
        self.actions = [
             ft.OutlinedButton("Cancelar", on_click=self.close_modal, style=ft.ButtonStyle(color=AppTheme.primary, side=ft.BorderSide(1, AppTheme.primary))),
             ft.ElevatedButton("Salvar", bgcolor=AppTheme.primary, color="white", on_click=self.save_session)
        ]
        self.actions_alignment = ft.MainAxisAlignment.END

        self.load_subjects()

    def load_subjects(self):
        import src.data.crud as crud
        subjects = crud.get_all_subjects()
        # Clear existing options
        self.dropdown_disc.controls[1].options = []
        
        self.subject_map = {} # Name -> ID
        
        for s in subjects:
            self.dropdown_disc.controls[1].options.append(ft.dropdown.Option(s['name']))
            self.subject_map[s['name']] = s['id']
            
    def save_session(self, e):
        import src.data.crud as crud
        
        # Helper to parse time string "HH:MM:SS" to seconds
        def parse_time(t_str):
            try:
                parts = list(map(int, t_str.split(':')))
                if len(parts) == 3: return parts[0]*3600 + parts[1]*60 + parts[2]
                if len(parts) == 2: return parts[0]*3600 + parts[1]*60
                return 0
            except (ValueError, AttributeError):
                return 0
                
        # Get values
        subj_name = self.dropdown_disc.controls[1].value
        subj_id = self.subject_map.get(subj_name)
        
        # If no subject selected, for now just return (or show error)
        if not subj_id:
            print("No subject selected")
            return

        topic = self.input_topic.controls[1].value or "Tópico Geral"
        duration = parse_time(self.input_time.controls[1].value)
        
        # Checkboxes for Type
        # Logic: If category matches, use it. Else fall back to heuristic
        cat = self.dropdown_category.controls[1].value
        if cat:
            type_label = cat.upper()
        else:
            type_label = "TEORIA"
            if not self.check_theory.value:
                 type_label = "QUESTOES"
             
        # Stats
        # self.stats_questions.content (Column) -> controls[1] (Row) -> controls (List of Column) -> controls[1] (TextField)
        # Wait, create_stat_box structure changed
        # It's now Container -> Column -> Row -> [Column -> [Text, TextField], ...]
        
        try:
            # Questions
             q_row = self.stats_questions.content.controls[1].controls
             # q_row[0] is Column -> [Text, TextField]
             correct = int(q_row[0].controls[1].value) if q_row[0].controls[1].value else 0
             wrong = int(q_row[1].controls[1].value) if len(q_row) > 1 and q_row[1].controls[1].value else 0
        except (ValueError, IndexError, AttributeError):
             correct = 0
             wrong = 0
             
        crud.add_study_session(subj_id, topic, duration, type_label, correct, wrong)
        print(f"Saved session: {subj_name} - {duration}s")
        
        # Publish event
        if self.page:
             self.page.pubsub.send_all("study_saved")
        
        if self.save_new_check.value:
            # Just clear inputs, keep modal open
            # self.input_time.controls[1].value = "00:00:00"
            pass # TODO: Reset logic
        else:
            self.close_modal(e)

    def close_modal(self, e):
        self.open = False
        self.page.close_dialog()
        self.page.update()

    def update_date_buttons(self):
        opts = ["HOJE", "ONTEM", "OUTRO"]
        self.date_buttons_row.controls = []
        for o in opts:
             is_sel = (self.selected_date_opt == o)
             color = AppTheme.primary if is_sel else "#eee"
             text_color = "black" if is_sel else "black" # Light gray bg, black text
             self.date_buttons_row.controls.append(
                 ft.Container(
                    content=ft.Text(o, size=12, color=text_color, weight=ft.FontWeight.BOLD if is_sel else ft.FontWeight.NORMAL),
                    bgcolor=color,
                    padding=ft.padding.symmetric(horizontal=15, vertical=8),
                    border_radius=15,
                    on_click=lambda e, opt=o: self.toggle_date(opt)
                )
             )
        try:
             self.date_buttons_row.update()
        except Exception:
             pass  # Control not yet mounted

    def toggle_date(self, opt):
        self.selected_date_opt = opt
        self.update_date_buttons()

    def on_category_change(self, e):
        cat = self.dropdown_category.controls[1].value
        self.stats_questions.visible = (cat == "Questões")
        self.stats_pages.visible = (cat == "Teoria")
        self.stats_video.visible = (cat == "VídeoAula")
        self.stats_container.update()

    def create_dropdown(self, label, placeholder, options=None):
        if options is None:
            options = []
        return ft.Column([
            ft.Text(label, size=10, weight=ft.FontWeight.BOLD, color="white"),
            ft.Dropdown(
                options=[ft.dropdown.Option(o) for o in options],
                bgcolor="transparent",
                border_color=AppTheme.primary,
                border_width=0,
                border_radius=0,
                text_style=ft.TextStyle(color="white"),
                content_padding=5,
                hint_text=placeholder,
                hint_style=ft.TextStyle(color="grey"),
            ),
            ft.Container(height=1, bgcolor=AppTheme.primary, margin=ft.margin.only(top=-10)) # Underline manually
        ])

    def create_input(self, label, placeholder):
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
            ),
             ft.Container(height=1, bgcolor=AppTheme.primary, margin=ft.margin.only(top=-10))
        ])
    
    def create_stat_box(self, title, labels, values):
        # Simplification for box with border
        inputs = []
        for i, val in enumerate(values):
            label_text = labels[i] if i < len(labels) else ""
            inputs.append(
                ft.Column([
                    ft.Text(label_text, size=8, color="grey"),
                    ft.TextField(value=val, width=80, text_align=ft.TextAlign.CENTER, text_style=ft.TextStyle(color="white"), border_color=AppTheme.primary, content_padding=5, height=30)
                ], spacing=2)
            )
            
        return ft.Container(
            padding=10,
            border=ft.border.all(1, AppTheme.primary),
            border_radius=10,
            content=ft.Column([
                ft.Text(title, size=10, weight=ft.FontWeight.BOLD, color="white"),
                ft.Row(inputs, spacing=10)
            ])
        )
