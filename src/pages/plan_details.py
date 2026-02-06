
import flet as ft
from src.theme import AppTheme
import src.data.crud as crud

class PlanDetailsPage(ft.Container):
    def __init__(self, page: ft.Page, plan_id):
        super().__init__()
        self.page_ref = page
        self.plan_id = plan_id
        self.expand = True
        self.padding = 30
        self.plan_data = None
        self.subjects_data = []
        
        self.build_ui()

    def build_ui(self):
        self.header_row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Dashboard Tab Content
        self.summary_container = ft.Container()
        self.subjects_grid = ft.GridView(
            runs_count=3,
            max_extent=300,
            child_aspect_ratio=1.2,
            spacing=20,
            run_spacing=20,
            expand=True
        )
        self.dashboard_content = ft.Column([
            ft.Container(height=20),
            self.summary_container,
            ft.Divider(color="grey"),
            ft.Row([
                ft.Text("Disciplinas do Plano", size=18, weight=ft.FontWeight.BOLD, color="white"),
                ft.ElevatedButton("Nova Disciplina", icon=ft.Icons.ADD, on_click=self.open_add_subject_modal, bgcolor=AppTheme.primary, color="white")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=10),
            self.subjects_grid
        ], expand=True, scroll=ft.ScrollMode.AUTO)

        # Full Syllabus Tab Content
        self.syllabus_content = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(text="Visão Geral", content=self.dashboard_content),
                ft.Tab(text="Edital Verticalizado", content=self.syllabus_content),
            ],
            expand=True,
            on_change=self.on_tab_change
        )
        
        self.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.IconButton(ft.Icons.ARROW_BACK, on_click=self.go_back, icon_color="white"),
                    alignment=ft.Alignment(-1, 0)
                ),
                self.header_row,
                ft.Container(height=10),
                self.tabs
            ],
            expand=True
        )
        self.load_data()

    def on_tab_change(self, e):
        if self.tabs.selected_index == 1:
            self.load_full_syllabus()
        self.update()

    def load_data(self):
        self.plan_data = crud.get_plan_by_id(self.plan_id)
        if not self.plan_data:
            self.content = ft.Text("Plano não encontrado.")
            if self.page: self.update()
            return

        self.subjects_data = crud.get_subjects_by_plan(self.plan_id)
        
        self.update_header()
        self.update_summary()
        self.update_subjects_grid()
        
        # If syllabus tab active, reload it too
        if self.tabs.selected_index == 1:
            self.load_full_syllabus()
            
        if self.page: self.update()

    def load_full_syllabus(self):
        self.syllabus_content.controls = []
        if not self.subjects_data:
            self.syllabus_content.controls.append(ft.Text("Nenhuma disciplina cadastrada.", color="grey"))
            return

        for subject in self.subjects_data:
            topics = crud.get_topics_by_subject(subject['id'])
            if not topics: continue # Skip empty subjects? Or show header? Show header.
            
            # Subject Header
            color = subject['color'] or AppTheme.primary
            self.syllabus_content.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=5, height=20, bgcolor=color),
                        ft.Text(subject['name'], size=16, weight=ft.FontWeight.BOLD, color="white")
                    ]),
                    padding=ft.padding.only(top=20, bottom=10)
                )
            )
            
            # Topics List
            for t in topics:
                link = t['material_link'] if 'material_link' in t.keys() else ""
                
                row = ft.Row([
                    ft.Checkbox(value=(t['completed']==1), on_change=lambda e, tid=t['id']: self.toggle_topic(tid, e.control.value)),
                    ft.Text(t['title'], expand=True, size=14, color="white"),
                    ft.IconButton(
                        ft.Icons.LINK, 
                        icon_color="blue" if link else "grey", 
                        tooltip=link or "Adicionar Link", 
                        on_click=lambda e, tid=t['id'], l=link: self.edit_link(tid, l)
                    )
                ])
                self.syllabus_content.controls.append(ft.Container(content=row, bgcolor="#333", border_radius=5, padding=5, margin=ft.margin.only(bottom=5)))

        self.syllabus_content.update()

    def toggle_topic(self, tid, val):
        crud.toggle_topic_complete(tid, val)
        # We don't need full reload, but summary stats will be outdated in Tab 0.
        # It's fine for now, or we can trigger self.update_summary() in background.
        self.update_summary() # Update stats in case user switches back

    def edit_link(self, tid, current_link):
        def save_link(e):
            new_link = txt_link.value
            crud.update_topic(tid, title=None, material_link=new_link) 
            self.page_ref.close_dialog()
            self.load_full_syllabus() # Refresh list to update icon color

        txt_link = ft.TextField(value=current_link, label="URL / Link", autofocus=True)
        dlg = ft.AlertDialog(
            title=ft.Text("Adicionar Link de Material"),
            content=txt_link,
            actions=[ft.TextButton("Salvar", on_click=save_link)]
        )
        self.page_ref.dialog = dlg
        dlg.open = True
        self.page_ref.update()

    def update_header(self):
        self.header_row.controls = [
            ft.Column([
                ft.Text(self.plan_data['name'], size=30, weight=ft.FontWeight.BOLD, color="white"),
                ft.Text(self.plan_data['observations'] or "Sem observações", size=14, color="grey")
            ])
        ]

    def update_summary(self):
        # Calculate totals
        total_subs = len(self.subjects_data)
        total_topics = sum(s['total_topics'] for s in self.subjects_data)
        completed_topics = sum(s['completed_topics'] for s in self.subjects_data)
        
        # Determine stats (mocked or calculated if we had study sessions linked to plan)
        # For now, let's use subject aggregate data
        
        pct = int((completed_topics / total_topics * 100)) if total_topics > 0 else 0
        
        self.summary_container.content = ft.Row(
            controls=[
                self.create_stat_card("Disciplinas", str(total_subs), ft.Icons.BOOK),
                self.create_stat_card("Tópicos", f"{completed_topics}/{total_topics}", ft.Icons.LIST),
                self.create_stat_card("Progresso Estimado", f"{pct}%", ft.Icons.PERCENT),
            ],
            spacing=20
        )

    def create_stat_card(self, label, value, icon):
        return ft.Container(
            bgcolor="#2c2d3e",
            padding=15,
            border_radius=10,
            expand=True,
            content=ft.Row([
                ft.Icon(icon, color=AppTheme.primary, size=30),
                ft.Column([
                    ft.Text(label, size=12, color="grey"),
                    ft.Text(value, size=20, weight=ft.FontWeight.BOLD, color="white")
                ])
            ], alignment=ft.MainAxisAlignment.CENTER)
        )

    def update_subjects_grid(self):
        self.subjects_grid.controls = []
        for s in self.subjects_data:
            self.subjects_grid.controls.append(self.create_subject_card(s))

    def create_subject_card(self, subject):
        prog = (subject['completed_topics'] / subject['total_topics']) if subject['total_topics'] > 0 else 0
        color = subject['color'] if 'color' in subject.keys() and subject['color'] else AppTheme.primary
        
        return ft.Container(
            bgcolor="#2c2d3e",
            padding=15,
            border_radius=15,
            border=ft.border.only(left=ft.BorderSide(5, color)),
            content=ft.Column([
                ft.Text(subject['name'], size=16, weight=ft.FontWeight.BOLD, color="white", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(subject['category'] or "Geral", size=10, color="grey"),
                ft.Container(height=10),
                ft.ProgressBar(value=prog, color=color, bgcolor="#444"),
                ft.Row([
                    ft.Text(f"{subject['completed_topics']}/{subject['total_topics']} tópicos", size=10, color="grey"),
                    ft.Text(f"{int(prog*100)}%", size=10, color="white")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]),
            on_click=lambda e, s=subject: self.open_subject_view(s),
            ink=True
        )

    def open_subject_view(self, subject):
        # If user wants to edit topics/structure, they used to click the card. 
        # But now request says "Ao abrir uma disciplina específica...".
        # Let's change the card click to Open Details, and put Edit button inside Details?
        # OR: Card click opens Details. Details has "Edit" button.
        # Requirements for PlanDetails said: "Gestão de Disciplinas: Nova, etc".
        # Let's pivot: Card click -> SubjectDetailsPage. 
        # SubjectDetailsPage header -> "Edit" button opens SubjectEditModal.
        
        from src.pages.subject_details import get_subject_details_page
        self.page_ref.clean()
        self.page_ref.add(get_subject_details_page(self.page_ref, subject['id'], self.plan_id))

    def go_back(self, e):
        # We need to recreate PlansPage or standard navigation
        # This depends on how main.py handles routing. 
        # For now, let's assume we can set page content back to PlansPage
        from src.pages.plans import get_plans_page
        self.page_ref.clean()
        self.page_ref.add(get_plans_page(self.page_ref))

    def open_add_subject_modal(self, e):
        from src.components.subject_modal import SubjectModal
        self.modal = SubjectModal(self.page_ref, plan_id=self.plan_id, on_save=self.load_data)
        self.page_ref.dialog = self.modal
        self.modal.open = True
        self.page_ref.update()

def get_plan_details_page(page, plan_id):
    return PlanDetailsPage(page, plan_id)
