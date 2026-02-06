
import flet as ft

class AppTheme:
    # Color Palette extracted from the reference image
    background = "#181824"  # Very dark blue/grey
    surface = "#212232"     # Slightly lighter for panels/cards
    primary = "#00BFA5"     # Teal/Green accent
    secondary = "#FF6E40"   # Orange/Red accent (for "errors" or special tags)
    text_primary = "#FFFFFF"
    text_secondary = "#8A8A9A"
    
    # Gradient for specific elements if needed
    sidebar_bg = "#1fdfac" # The bright teal from the sidebar image (approx)
    
    theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            surface=surface,
            primary=primary,
            secondary=secondary,
            on_surface=text_primary,
        ),
        visual_density=ft.VisualDensity.COMFORTABLE,
        # We can add font_family here later if we download fonts
    )

    # Common Styles
    card_style = {
        "bgcolor": surface,
        "border_radius": 10,
        "padding": 20,
    }
