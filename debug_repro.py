
import flet as ft
from src.theme import AppTheme
from src.components.stat_card import StatCard
from src.components.heatmap import ConsistencyHeatmap
from src.components.charts import StudyChart

def main(page: ft.Page):
    page.theme = AppTheme.theme
    page.bgcolor = AppTheme.background
    
    print("Adding StatCards...")
    try:
        page.add(StatCard("Tempo", "10h"))
        page.add(StatCard("Progresso", "1%", progress=0.01))
        print("StatCards OK.")
    except Exception as e:
        print(f"StatCard Failed: {e}")

    print("Adding Heatmap...")
    try:
        page.add(ConsistencyHeatmap())
        print("Heatmap OK.")
    except Exception as e:
        print(f"Heatmap Failed: {e}")

    print("Adding Chart...")
    try:
        page.add(StudyChart())
        print("Chart OK.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Chart Failed: {e}")

    from src.components.sidebar import Sidebar
    print("Adding Sidebar...")
    try:
        page.add(Sidebar(page))
        print("Sidebar OK.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Sidebar Failed: {e}")

    from src.pages.dashboard import DashboardPage
    print("Adding DashboardPage...")
    try:
        page.add(DashboardPage())
        print("DashboardPage OK.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"DashboardPage Failed: {e}")

if __name__ == "__main__":
    ft.app(target=main)
