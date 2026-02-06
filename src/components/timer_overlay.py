
import flet as ft
from src.theme import AppTheme
import time
import threading


class TimerOverlay(ft.Container):
    """
    Thread-safe timer overlay for study sessions.
    Uses threading.Lock for synchronization and safe UI updates.
    """
    
    def __init__(self, page: ft.Page):
        super().__init__()
        print("Initializing TimerOverlay (Fresh)...")
        self._page_ref = page  # Keep reference for safe access
        self.visible = False
        self.expand = True
        self.bgcolor = "#000000dd"
        self.alignment = ft.Alignment(0, 0)
        self.blur = ft.Blur(10, 10, ft.BlurTileMode.MIRROR)
        
        # Thread synchronization
        self._lock = threading.Lock()
        self._timer_running = False
        self._seconds = 0
        self._stop_event = threading.Event()
        
        self.topic = "Tópico Desconhecido"
        self.subject_id = None
        
        self.time_display = ft.Text(
            "00:00:00", size=100, weight=ft.FontWeight.BOLD, 
            color="white", font_family="monospace"
        )
        self.topic_display = ft.Text(
            self.topic, size=20, weight=ft.FontWeight.BOLD, color="white"
        )
        self.sub_display = ft.Text("Você está estudando:", size=14, color="#888")
        
        self.btn_play = ft.IconButton(
            ft.Icons.PLAY_ARROW, icon_size=40, bgcolor="white", 
            icon_color="black", on_click=self.toggle_timer
        )
        self.btn_stop = ft.IconButton(
            ft.Icons.STOP, icon_size=30, bgcolor=AppTheme.primary, 
            icon_color="white", on_click=self.stop_timer
        )
        
        self.content = ft.Stack(
            controls=[
                ft.Container(
                    content=ft.IconButton(ft.Icons.CLOSE, icon_color="white", on_click=self.hide),
                    alignment=ft.Alignment(1, -1),
                    padding=30
                ),
                ft.Column(
                    controls=[
                        ft.Text("estudei", size=30, color=AppTheme.primary, weight=ft.FontWeight.BOLD),
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

    @property
    def timer_running(self):
        with self._lock:
            return self._timer_running
    
    @timer_running.setter
    def timer_running(self, value):
        with self._lock:
            self._timer_running = value

    @property
    def seconds(self):
        with self._lock:
            return self._seconds
    
    @seconds.setter
    def seconds(self, value):
        with self._lock:
            self._seconds = value

    def show(self, topic="Controle Externo e Legislação Institucional", subject_id=None):
        self.topic = topic
        self.subject_id = subject_id
        self.topic_display.value = topic
        self.visible = True
        self._safe_update(self)

    def hide(self, e=None):
        self._stop_event.set()
        self.timer_running = False
        self.visible = False
        self._safe_update(self)

    def toggle_timer(self, e):
        if self.timer_running:
            # Pause
            self.timer_running = False
            self._stop_event.set()
        else:
            # Start/Resume
            self.timer_running = True
            self._stop_event.clear()
            threading.Thread(target=self._run_timer, daemon=True).start()
        
        self.btn_play.icon = ft.Icons.PAUSE if self.timer_running else ft.Icons.PLAY_ARROW
        self._safe_update(self.btn_play)

    def _run_timer(self):
        """Thread-safe timer loop."""
        while not self._stop_event.is_set():
            with self._lock:
                if not self._timer_running:
                    break
                self._seconds += 1
                secs = self._seconds
            
            mins, s = divmod(secs, 60)
            hours, mins = divmod(mins, 60)
            
            self.time_display.value = "{:02d}:{:02d}:{:02d}".format(hours, mins, s)
            
            if not self._safe_update(self.time_display):
                break  # Page closed or control unmounted
            
            # Wait with stop event check (more responsive than time.sleep)
            self._stop_event.wait(timeout=1.0)

    def _safe_update(self, control):
        """
        Thread-safe UI update.
        Returns False if update failed (page closed).
        """
        try:
            if self._page_ref and control.page:
                control.update()
                return True
        except Exception:
            pass
        return False

    def stop_timer(self, e):
        current_seconds = self.seconds
        
        if current_seconds == 0:
            self.hide()
            return
        
        # Stop the timer
        self._stop_event.set()
        self.timer_running = False
        
        # Save session
        import src.data.crud as crud
        
        sid = self.subject_id
        if not sid:
            # Try to find by name
            all_subs = crud.get_all_subjects()
            for s in all_subs:
                if s['name'] == self.topic:
                    sid = s['id']
                    break
        
        if sid:
            crud.add_study_session(sid, "Estudo Cronometrado", current_seconds, "TEORIA", 0, 0)
            self._show_snackbar(f"Sessão de {self.time_display.value} salva!")
            if self._page_ref:
                self._page_ref.pubsub.send_all("study_saved")
        else:
            self._show_snackbar("Erro: Disciplina não identificada para salvar.")
        
        # Reset
        self.seconds = 0
        self.time_display.value = "00:00:00"
        self.btn_play.icon = ft.Icons.PLAY_ARROW
        self._safe_update(self)
        self.hide()

    def _show_snackbar(self, message):
        """Helper to show snackbar safely."""
        try:
            if self._page_ref:
                self._page_ref.snack_bar = ft.SnackBar(ft.Text(message))
                self._page_ref.snack_bar.open = True
                self._page_ref.update()
        except Exception:
            pass
