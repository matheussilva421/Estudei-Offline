"""
Navigation Manager for Estudei Offline.
Provides centralized navigation without destroying UI state.
"""

import flet as ft


class NavigationManager:
    """
    Singleton navigation manager that handles page transitions
    without using page.clean() which destroys UI state.
    
    Usage:
        # In main.py:
        nav = NavigationManager(page, content_area)
        
        # In any page:
        page.nav.push("plan_details", plan_id=123)
        page.nav.pop()
    """
    
    def __init__(self, page: ft.Page, content_container: ft.Container):
        self.page = page
        self.content_container = content_container
        self.history = []  # Stack of (page_name, kwargs)
        self.current_page_name = "dashboard"
        
        # Attach to page for global access
        page.nav = self
    
    def navigate_to(self, page_name: str, **kwargs):
        """Navigate to a page, clearing history (main navigation)."""
        self.history = []
        self._load_page(page_name, **kwargs)
    
    def push(self, page_name: str, **kwargs):
        """Push a new page onto the stack (drill-down navigation)."""
        # Save current state to history
        self.history.append((self.current_page_name, {}))
        self._load_page(page_name, **kwargs)
    
    def pop(self):
        """Go back to the previous page in history."""
        if self.history:
            page_name, kwargs = self.history.pop()
            self._load_page(page_name, **kwargs)
            return True
        return False
    
    def _load_page(self, page_name: str, **kwargs):
        """Load a page by name with given parameters."""
        self.current_page_name = page_name
        
        # Lazy imports to avoid circular dependencies
        if page_name == "dashboard":
            from src.pages.dashboard import get_dashboard_page
            self.content_container.content = get_dashboard_page(self.page)
        
        elif page_name == "plans":
            from src.pages.plans import get_plans_page
            self.content_container.content = get_plans_page(self.page)
        
        elif page_name == "plan_details":
            from src.pages.plan_details import get_plan_details_page
            self.content_container.content = get_plan_details_page(
                self.page, kwargs.get("plan_id")
            )
        
        elif page_name == "subjects":
            from src.pages.subjects import get_subjects_page
            self.content_container.content = get_subjects_page(self.page)
        
        elif page_name == "subject_details":
            from src.pages.subject_details import get_subject_details_page
            self.content_container.content = get_subject_details_page(
                self.page, 
                kwargs.get("subject_id"),
                kwargs.get("plan_id")
            )
        
        elif page_name == "planning":
            from src.pages.planning import get_planning_page
            self.content_container.content = get_planning_page(
                self.page, kwargs.get("on_timer_click")
            )
        
        elif page_name == "reviews":
            from src.pages.reviews import get_reviews_page
            self.content_container.content = get_reviews_page(self.page)
        
        elif page_name == "history":
            from src.pages.history import get_history_page
            self.content_container.content = get_history_page(self.page)
        
        elif page_name == "statistics":
            from src.pages.statistics import get_statistics_page
            self.content_container.content = get_statistics_page(self.page)
        
        elif page_name == "mock_exams":
            from src.pages.mock_exams import get_mock_exams_page
            self.content_container.content = get_mock_exams_page(self.page)
        
        else:
            # Fallback to dashboard
            from src.pages.dashboard import get_dashboard_page
            self.content_container.content = get_dashboard_page(self.page)
        
        self.content_container.update()
