
import flet as ft
from src.theme import AppTheme
import time
import threading

class TimerOverlay(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        print("Initializing TimerOverlay (Fresh)...")
        # self.page = page
        self.visible = False
        self.expand = True
        self.bgcolor = "#000000dd" # Semi-transparent black
        self.alignment = ft.Alignment(0, 0)
        self.blur = ft.Blur(10, 10, ft.BlurTileMode.MIRROR)
        
        self.timer_running = False
        self.seconds = 0
        self.topic = "Tópico Desconhecido"
        
        self.time_display = ft.Text("00:00:00", size=100, weight=ft.FontWeight.BOLD, color="white", font_family="monospace")
        self.topic_display = ft.Text(self.topic, size=20, weight=ft.FontWeight.BOLD, color="white")
        self.sub_display = ft.Text("Você está estudando:", size=14, color="#888")
        
        self.btn_play = ft.IconButton(ft.Icons.PLAY_ARROW, icon_size=40, bgcolor="white", icon_color="black", on_click=self.toggle_timer)
        self.btn_stop = ft.IconButton(ft.Icons.STOP, icon_size=30, bgcolor=AppTheme.primary, icon_color="white", on_click=self.stop_timer)
        
        self.content = ft.Stack(
            controls=[
                # Close button top right
                ft.Container(
                    content=ft.IconButton(ft.Icons.CLOSE, icon_color="white", on_click=self.hide),
                    alignment=ft.Alignment(1, -1),
                    padding=30
                ),
                # Main Center Content
                ft.Column(
                    controls=[
                        ft.Image(src="/logo.png", width=100) if False else ft.Text("estudei", size=30, color=AppTheme.primary, weight=ft.FontWeight.BOLD), # Logo placeholder
                        ft.Container(height=20),
                        self.sub_display,
                        self.topic_display,
                        ft.Divider(color=AppTheme.primary, thickness=3),
                        self.time_display,
                        ft.Container(height=30),
                        ft.Row(
                            [self.btn_play, self.btn_stop],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20
                        ),
                        ft.Container(height=20),
                        ft.Text("CRONÔMETRO \nTIMER", size=12, color=AppTheme.primary, text_align=ft.TextAlign.CENTER)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            ],
            expand=True
        )

    def show(self, topic="Controle Externo e Legislação Institucional", subject_id=None):
        self.topic = topic
        self.subject_id = subject_id
        self.topic_display.value = topic
        self.visible = True
        self.update()

    def hide(self, e=None):
        self.timer_running = False
        self.visible = False
        self.update()

    def toggle_timer(self, e):
        self.timer_running = not self.timer_running
        self.btn_play.icon = ft.Icons.PAUSE if self.timer_running else ft.Icons.PLAY_ARROW
        self.btn_play.update()
        if self.timer_running:
            # Simple thread for timer demo
            # In production, use asyncio or page.run_task
            threading.Thread(target=self.run_timer, daemon=True).start()

    def run_timer(self):
        while self.timer_running:
            self.seconds += 1
            mins, secs = divmod(self.seconds, 60)
            hours, mins = divmod(mins, 60)
            self.time_display.value = "{:02d}:{:02d}:{:02d}".format(hours, mins, secs)
            try:
                self.time_display.update()
            except Exception:
                break  # Page closed or control unmounted
            time.sleep(1)

    def stop_timer(self, e):
        if self.seconds == 0:
            self.hide()
            return
            
        self.timer_running = False
        
        # Open Modal to Confirm/Save
        # Or just save directly? Requirements say "Connect Timer to Study Session".
        # Let's auto-save or prompt. Auto-save simplest for now or show StudyModal pre-filled.
        # Let's prompt with a simple snackbar and save.
        
        import src.data.crud as crud
        # We need subject_id. For now, let's assume '0' or we need to pass subject_id to show()
        # Fallback: if subject_id not set, use a placeholder or ask.
        # self.subject_id should be set in show()
        
        sid = getattr(self, 'subject_id', None)
        if not sid:
            # Try to find by name
            all_subs = crud.get_all_subjects()
            for s in all_subs:
                if s['name'] == self.topic:
                    sid = s['id']
                    break
        
        if sid:
            crud.add_study_session(sid, "Estudo Cronometrado", self.seconds, "TEORIA", 0, 0)
            if self.page:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Sessão de {self.time_display.value} salva!"))
                self.page.snack_bar.open = True
                self.page.pubsub.send_all("study_saved")
                self.page.update()
        else:
            if self.page:
                 self.page.snack_bar = ft.SnackBar(ft.Text("Erro: Disciplina não identificada para salvar."))
                 self.page.snack_bar.open = True
                 self.page.update()

        self.seconds = 0
        self.time_display.value = "00:00:00"
        self.btn_play.icon = ft.Icons.PLAY_ARROW
        self.update()
        self.hide()
