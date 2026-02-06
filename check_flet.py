
import flet as ft
print("Flet version:", ft.version)
try:
    print("BarChart exists:", ft.BarChart)
except AttributeError:
    print("BarChart MISSING in top level")
    import inspect
    print("Available attributes starting with Bar:", [m for m in dir(ft) if m.startswith("Bar")])
    print("Available attributes starting with Chart:", [m for m in dir(ft) if m.startswith("Chart")])
