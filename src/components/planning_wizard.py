
import flet as ft
from src.theme import AppTheme

class PlanningWizard(ft.AlertDialog):
    def __init__(self, page: ft.Page):
        super().__init__()
        # self.page = page
        self.modal = True
        self.bgcolor = "#2c2d3e"
        self.shape = ft.RoundedRectangleBorder(radius=10)
        self.content_padding = 0
        self.current_step = 1
        
        self.build_ui()

    def build_ui(self):
        self.content = ft.Container(
            width=800,
            height=600,
            padding=30,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.START,
                controls=[
                    self.build_header(),
                    ft.Container(height=20),
                    self.build_step_indicator(),
                    ft.Container(height=20),
                    ft.Container(
                        content=self.get_step_content(),
                        expand=True,
                    ),
                    ft.Container(height=20),
                    self.build_footer()
                ]
            )
        )

    def build_header(self):
        return ft.Row([
            ft.Text("Editar Planejamento", size=20, weight=ft.FontWeight.BOLD, color="white"),
            ft.IconButton(ft.Icons.CLOSE, on_click=self.close_modal)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def build_step_indicator(self):
        return ft.Row(
            controls=[
                self.create_step("01", "Organização", self.current_step >= 1),
                self.create_step_line(),
                self.create_step("02", "Disciplinas", self.current_step >= 2),
                self.create_step_line(),
                self.create_step("03", "Relevância", self.current_step >= 3),
                self.create_step_line(),
                self.create_step("04", "Horários", self.current_step >= 4),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

    def create_step(self, num, label, active):
        color = AppTheme.primary if active else "grey"
        return ft.Column([
            ft.Container(
                content=ft.Text(num, size=10, color="white" if active else "black"),
                bgcolor=color,
                border_radius=15,
                width=24, height=24, alignment=ft.Alignment(0, 0)
            ),
            ft.Text(label, size=10, color=color)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def create_step_line(self):
        return ft.Container(height=1, width=50, bgcolor="grey", margin=ft.margin.only(bottom=10))

    def get_step_content(self):
        if self.current_step == 1:
            return self.step_1_content()
        elif self.current_step == 2:
            return self.step_2_content()
        elif self.current_step == 3:
            return self.step_3_content()
        elif self.current_step == 4:
            return self.step_4_content()
        return ft.Container()

    def step_1_content(self):
        return ft.Column([
             ft.Text("Para iniciar o seu planejamento, escolha a melhor forma de visualização para você:", color="#ccc", size=14),
             ft.Container(height=20),
             ft.Row(
                controls=[
                    self.create_option_card("Ciclo de Estudos", "Estude as disciplinas em uma ordem rotativa...", ft.Icons.LOOP),
                    self.create_option_card("Planejamento Semanal", "Define quais matérias estudar em cada dia...", ft.Icons.CALENDAR_MONTH),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            )
        ])

    def step_2_content(self):
        import src.data.crud as crud
        subjects = crud.get_all_subjects() # returns list of dicts
        
        if not subjects:
             return ft.Text("Nenhuma disciplina cadastrada. Vá em 'Disciplinas' para adicionar.", color="red")

        grid = ft.GridView(
            runs_count=3,
            max_extent=250,
            child_aspect_ratio=3,
            spacing=10,
            run_spacing=10,
            expand=True
        )
        for sub in subjects:
            grid.controls.append(
                ft.Container(
                    content=ft.Text(sub['name'], size=10, text_align=ft.TextAlign.CENTER),
                    border=ft.border.all(1, AppTheme.primary),
                    border_radius=5,
                    alignment=ft.Alignment(0,0),
                    padding=5,
                    bgcolor="#25263a" # Selected state simulation
                    # on_click logic would go here to toggle selection
                )
            )
        return ft.Column([
            ft.Text("Selecione quais das suas disciplinas você deseja colocar no seu planejamento.", color="#ccc", size=14),
            ft.Container(height=10),
            ft.Container(content=grid, expand=True)
        ], expand=True)

    def step_3_content(self):
        import src.data.crud as crud
        subjects = crud.get_all_subjects()
        
        col = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
        for sub in subjects:
            col.controls.append(
                ft.Container(
                    bgcolor="#1e1e2d",
                    padding=15,
                    border_radius=10,
                    content=ft.Row([
                        ft.Column([
                            ft.Text(sub['name'], size=12, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                ft.Text("IMPORTÂNCIA", size=8, color="grey"),
                                ft.Slider(min=0, max=5, divisions=5, value=3, height=20, expand=True)
                            ]),
                            ft.Row([
                                ft.Text("CONHECIMENTO", size=8, color="grey"),
                                ft.Slider(min=0, max=5, divisions=5, value=2, height=20, expand=True)
                            ])
                        ], expand=True),
                        ft.Container(width=100, bgcolor="#ffcdd2", padding=5, border_radius=5, alignment=ft.Alignment(0,0), content=ft.Text("14%", color="black", weight=ft.FontWeight.BOLD))
                    ])
                )
            )
        return ft.Column([
            ft.Text("Para cada disciplina, selecione a importância e seu grau de conhecimento:", color="#ccc", size=14),
            ft.Container(height=10),
            ft.Container(content=col, expand=True)
        ], expand=True)

    def step_4_content(self):
         days = ["DOM", "SEG", "TER", "QUA", "QUI", "SEX", "SÁB"]
         rows = []
         for i in range(0, len(days), 2):
             d1 = days[i]
             row_controls = [self.create_day_input(d1)]
             if i+1 < len(days):
                 d2 = days[i+1]
                 row_controls.append(self.create_day_input(d2))
             rows.append(ft.Row(row_controls, alignment=ft.MainAxisAlignment.SPACE_BETWEEN))
         
         return ft.Column([
             ft.Text("Quais dias e quantas horas pretende estudar?", color="#ccc", size=14),
             ft.Column(rows, spacing=10),
             ft.Container(height=20),
             ft.Container(bgcolor="#1e1e2d", padding=10, border_radius=5, content=ft.Row([
                 ft.Text("Total na Semana: 30h", color=AppTheme.primary)
             ], alignment=ft.MainAxisAlignment.CENTER))
         ], scroll=ft.ScrollMode.AUTO)

    def create_day_input(self, day):
        # Using a simplified mock for the complex input
        return ft.Container(
            width=300,
            content=ft.Row([
                ft.Checkbox(value=True),
                ft.Container(bgcolor="grey", content=ft.Text(day, size=10, color="black"), padding=5, border_radius=3),
                ft.TextField(value="06:00", width=80, text_size=12, height=30, content_padding=5),
                ft.Text("horas diárias", size=12)
            ])
        )

    def build_footer(self):
        return ft.Row([
            ft.OutlinedButton("Voltar", on_click=self.prev_step, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5), side=ft.BorderSide(1, AppTheme.primary), color=AppTheme.primary)) if self.current_step > 1 else ft.Container(),
            ft.ElevatedButton("Próximo" if self.current_step < 4 else "Concluir", on_click=self.next_step, bgcolor=AppTheme.primary, color="white", style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)))
        ], alignment=ft.MainAxisAlignment.END if self.current_step == 1 else ft.MainAxisAlignment.SPACE_BETWEEN)

    def next_step(self, e):
        if self.current_step < 4:
            self.current_step += 1
            self.build_ui()
            self.update()
        else:
            self.close_modal(e)

    def prev_step(self, e):
        if self.current_step > 1:
            self.current_step -= 1
            self.build_ui()
            self.update()

    def create_option_card(self, title, desc, icon):
        return ft.Container(
            width=300,
            height=200,
            bgcolor="#1e1e2d",
            border=ft.border.all(1, AppTheme.primary),
            border_radius=10,
            padding=20,
            content=ft.Column([
                ft.Icon(icon, size=50, color=AppTheme.primary),
                ft.Text(title, weight=ft.FontWeight.BOLD, color="white", size=16),
                ft.Text(desc, color="#ccc", size=12, text_align=ft.TextAlign.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
            on_click=lambda e: self.next_step(e)
        )

    def close_modal(self, e):
        self.open = False
        self.page.close_dialog()
        self.page.update()
