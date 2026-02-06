import flet as ft
from src.theme import AppTheme
import src.data.crud as crud
from datetime import datetime

class ReviewsPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page_ref = page
        self.expand = True
        self.padding = 30
        self.selected_tab = "PROGRAMADAS"
        
        self.build_ui()

    def build_ui(self):
        self.content = ft.Column(
            controls=[
                self.build_header(),
                ft.Container(height=20),
                self.build_tabs_row(),
                ft.Container(height=20),
                self.build_list_area()
            ],
            expand=True
        )
        self.load_data()

    def build_header(self):
        return ft.Row(
            controls=[
                ft.Text("Revisões", size=30, weight=ft.FontWeight.BOLD, color="white"),
                ft.Row([
                    ft.ElevatedButton("Nova Revisão", bgcolor=AppTheme.primary, color="white", on_click=self.open_add_modal),
                    ft.OutlinedButton("Filtros", icon=ft.Icons.FILTER_LIST),
                ])
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

    def build_tabs_row(self):
        # We need a container to update the tabs when counts change
        self.tabs_container = ft.Row(spacing=10)
        return self.tabs_container

    def build_list_area(self):
        self.list_container = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True)
        return self.list_container

    def load_data(self):
        reviews = crud.get_reviews() # returns list of dicts
        
        programadas = []
        atrasadas = []
        concluidas = []
        ignoradas = []
        
        now = datetime.now()
        
        for r in reviews:
            # Check if status exists, else fallback to is_completed
            # In fresh DB it's status. logic:
            status = r['status'] if 'status' in r.keys() and r['status'] is not None else (1 if r.get('is_completed') else 0)
            
            # Parse date - try multiple formats
            try:
                dt_obj = datetime.strptime(r['date_time'], "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                try:
                    dt_obj = datetime.strptime(r['date_time'], "%d/%m/%Y %H:%M")
                except (ValueError, TypeError):
                    dt_obj = now
            
            if status == 1:
                concluidas.append(r)
            elif status == 2:
                ignoradas.append(r)
            elif dt_obj < now:
                atrasadas.append(r)
            else:
                programadas.append(r)
                
        self.counts = {
            "PROGRAMADAS": len(programadas),
            "ATRASADAS": len(atrasadas),
            "CONCLUÍDAS": len(concluidas),
            "IGNORADAS": len(ignoradas)
        }
        
        self.data_map = {
            "PROGRAMADAS": programadas,
            "ATRASADAS": atrasadas,
            "CONCLUÍDAS": concluidas,
            "IGNORADAS": ignoradas
        }
        
        self.update_tabs_ui()
        self.update_list_ui()
        if self.page: self.update()

    def update_tabs_ui(self):
        tabs = ["PROGRAMADAS", "ATRASADAS", "IGNORADAS", "CONCLUÍDAS"]
        self.tabs_container.controls = []
        for t in tabs:
            active = (self.selected_tab == t)
            count = self.counts.get(t, 0)
            self.tabs_container.controls.append(self.create_tab(t, active, count))

    def create_tab(self, label, active, count):
        """Create a styled tab button with count badge."""
        from src.theme import AppTheme
        
        bg = AppTheme.primary if active else "#2c2d3e"
        text_color = "white"
        
        return ft.Container(
            content=ft.Row([
                ft.Text(label, size=12, weight=ft.FontWeight.BOLD, color=text_color),
                ft.Container(
                    content=ft.Text(str(count), size=10, color=text_color),
                    bgcolor="#00000033" if active else "#ffffff22",
                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                    border_radius=10,
                ) if count > 0 else ft.Container()
            ], spacing=8),
            bgcolor=bg,
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            border_radius=20,
            on_click=lambda e, t=label: self.select_tab(t)
        )

    def select_tab(self, tab_name):
        """Handle tab selection."""
        self.selected_tab = tab_name
        self.update_tabs_ui()
        self.update_list_ui()
        if self.page: self.update()

    def update_list_ui(self):
        self.list_container.controls = []
        items = self.data_map.get(self.selected_tab, [])
        
        if not items:
            msg = f"Nenhuma revisão em '{self.selected_tab}'."
            if self.selected_tab == "ATRASADAS":
                msg = "Legal, você não tem revisões atrasadas! ✅"
            self.list_container.controls.append(self.build_empty_state(msg))
        else:
            for item in items:
                self.list_container.controls.append(self.create_review_tile(item))

    def create_review_tile(self, item):
        # item: id, content, date_time, status
        status = item['status'] if 'status' in item.keys() and item['status'] is not None else (1 if item.get('is_completed') else 0)
        
        actions = []
        if status == 0: # Pending/Late
            actions.append(ft.IconButton(ft.Icons.CHECK_CIRCLE_OUTLINE, icon_color="grey", tooltip="Concluir", on_click=lambda e: self.set_status(item['id'], 1)))
            actions.append(ft.IconButton(ft.Icons.DO_NOT_DISTURB, icon_color="grey", tooltip="Ignorar", on_click=lambda e: self.set_status(item['id'], 2)))
        elif status == 1: # Done
            actions.append(ft.IconButton(ft.Icons.CHECK_CIRCLE, icon_color="green", tooltip="Reabrir", on_click=lambda e: self.set_status(item['id'], 0)))
        elif status == 2: # Ignored
            actions.append(ft.IconButton(ft.Icons.DO_NOT_DISTURB_ON, icon_color="red", tooltip="Reabrir", on_click=lambda e: self.set_status(item['id'], 0)))
            
        return ft.Container(
            bgcolor="#2c2d3e",
            padding=15,
            border_radius=10,
            margin=ft.margin.only(bottom=10),
            content=ft.Row([
                ft.Column([
                    ft.Text(item['date_time'], size=10, color="grey"),
                    ft.Text(item['content'], size=14, weight=ft.FontWeight.BOLD, color="white")
                ], expand=True),
                ft.Row(actions, spacing=0)
            ])
        )

    def set_status(self, rid, status):
        crud.update_reminder_status(rid, status)
        self.load_data()

    def build_empty_state(self, msg):
        return ft.Column(
            controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=80, color="#333"),
                ft.Text(msg, size=16, color="grey"),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True
        )

    def open_add_modal(self, e):
        from src.components.reminder_modal import ReminderModal
        # We want to pre-set category to "Revisão"
        self.modal = ReminderModal(self.page_ref, on_save=self.load_data)
        # Hacky way to set default, ideally Modal accepts init param
        self.modal.dropdown_cat.controls[1].value = "Revisão" 
        self.page_ref.dialog = self.modal
        self.modal.open = True
        self.page_ref.update()

def get_reviews_page(page):
    return ReviewsPage(page)
