
import flet as ft
from src.theme import AppTheme
import src.data.crud as crud
from datetime import datetime, timedelta

class StatisticsPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page_ref = page
        self.expand = True
        self.padding = 30
        self.build_ui()

    def build_ui(self):
        self.indicators_row = ft.Row(spacing=20)
        
        # Charts Area (Placeholder for now as Flet charts can be complex)
        # We will use simple progress bars or text stats if charts need more setup.
        # But let's try a simple BarChart for evolution.
        self.chart_container = ft.Container(height=300, bgcolor="#2c2d3e", border_radius=10, padding=20)
        
        # Topics Performance Table
        self.topics_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Disciplina")),
                ft.DataColumn(ft.Text("Tópico")),
                ft.DataColumn(ft.Text("Questões")),
                ft.DataColumn(ft.Text("Desempenho")),
            ],
            rows=[]
        )

        self.content = ft.Column(
            controls=[
                ft.Text("Estatísticas", size=30, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(height=20),
                self.indicators_row,
                ft.Container(height=20),
                ft.Text("Evolução (Últimos 7 dias)", size=18, weight=ft.FontWeight.BOLD, color="white"),
                self.chart_container,
                ft.Container(height=20),
                ft.Text("Desempenho por Tópico", size=18, weight=ft.FontWeight.BOLD, color="white"),
                ft.Container(content=self.topics_table, bgcolor="#2c2d3e", border_radius=10, padding=10),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
        self.load_data()

    def load_data(self):
        # 1. Indicators
        total_q = crud.db.fetch_one("SELECT SUM(questions_correct + questions_wrong) as t FROM study_sessions")['t'] or 0
        correct_q = crud.db.fetch_one("SELECT SUM(questions_correct) as c FROM study_sessions")['c'] or 0
        pct_global = int(correct_q / total_q * 100) if total_q > 0 else 0
        
        pages = crud.db.fetch_one("SELECT SUM(pages_end - pages_start) as p FROM study_sessions")['p'] or 0
        
        pending_topics = crud.db.fetch_one("SELECT COUNT(*) as c FROM topics WHERE completed = 0")['c'] or 0
        
        self.indicators_row.controls = [
            self.create_indicator(f"{total_q}", "Questões Resolvidas", ft.Icons.QUESTION_ANSWER),
            self.create_indicator(f"{pct_global}%", "Desempenho Geral", ft.Icons.PIE_CHART),
            self.create_indicator(f"{pages}", "Páginas Lidas", ft.Icons.BOOK),
            self.create_indicator(f"{pending_topics}", "Tópicos Pendentes", ft.Icons.LIST),
        ]
        
        # 2. Chart (Evolution - Last 7 days questions)
        # Doing a simple visual representation using Row of Columns (Manual histogram)
        # Real Chart requires ft.BarChart with data groups.
        self.build_chart_ui()
        
        # 3. Table
        self.build_topics_table()
        # Note: Don't call self.update() here - control may not be mounted yet

    def create_indicator(self, value, label, icon):
        return ft.Container(
            bgcolor="#2c2d3e",
            padding=15,
            border_radius=10,
            expand=True,
            content=ft.Row([
                ft.Icon(icon, color=AppTheme.primary, size=24),
                ft.Column([
                    ft.Text(label, size=10, color="grey"),
                    ft.Text(str(value), size=18, weight=ft.FontWeight.BOLD, color="white")
                ], spacing=2)
            ], alignment=ft.MainAxisAlignment.CENTER)
        )

    def build_chart_ui(self):
        # Get last 7 days data
        data = []
        today = datetime.now()
        max_q = 0
        
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            d_str = d.strftime("%Y-%m-%d")
            # Parameterized query to prevent SQL injection
            res = crud.db.fetch_one(
                "SELECT SUM(questions_correct + questions_wrong) as t FROM study_sessions WHERE date LIKE ?",
                (f"{d_str}%",)
            )
            val = res['t'] or 0
            data.append((d.strftime("%d/%m"), val))
            if val > max_q: max_q = val
            
        # Draw columns
        bar_groups = []
        for label, val in data:
            height_factor = (val / max_q) if max_q > 0 else 0
            bar_height = max(10, height_factor * 200) # Max height 200px
            
            bar_groups.append(
                ft.Column([
                    ft.Container(height=bar_height, width=20, bgcolor=AppTheme.primary, border_radius=5, tooltip=f"{val} questões"),
                    ft.Text(label, size=10, color="grey")
                ], alignment=ft.MainAxisAlignment.END, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
            
        self.chart_container.content = ft.Row(bar_groups, alignment=ft.MainAxisAlignment.SPACE_EVENLY, vertical_alignment=ft.CrossAxisAlignment.END)

    def build_topics_table(self):
        # Query Topics with sessions stats
        # Need complex join or python processing.
        # Let's get sessions grouped by topic
        rows = crud.db.fetch_all('''
            SELECT 
                s.name as subject, 
                ss.topic, 
                SUM(ss.questions_correct) as c, 
                SUM(ss.questions_wrong) as w 
            FROM study_sessions ss
            JOIN subjects s ON ss.subject_id = s.id
            GROUP BY ss.subject_id, ss.topic
        ''')
        
        self.topics_table.rows = []
        for r in rows:
            total = r['c'] + r['w']
            if total == 0: continue
            pct = int(r['c'] / total * 100)
            
            self.topics_table.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(r['subject'])),
                ft.DataCell(ft.Text(r['topic'])),
                ft.DataCell(ft.Text(str(total))),
                ft.DataCell(ft.Text(f"{pct}%")),
            ]))

def get_statistics_page(page):
    return StatisticsPage(page)
