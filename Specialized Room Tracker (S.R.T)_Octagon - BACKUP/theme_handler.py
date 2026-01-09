import os

class ThemeHandler:
    # PUP Color Palette
    MAROON = "#7B1818"
    GOLD = "#FFD700"
    GREEN = "#8BC34A"
    ORANGE = "#FF9800"
    RED_LIGHT = "#EF9A9A"
    
    LIGHT_MODE = {
        "is_dark": False,
        "main_bg": "#FFFFFF",
        "text": "#000000",
        "input_bg": "#F0F0F0",
        "input_text": "#000000",
        "table_bg": "#FFFFFF",
        "table_item_text": "#000000",
        "header_bg": "#7B1818", # Maroon
        "header_text": "#FFFFFF",
        "btn_primary": "#7B1818",
        "btn_text": "#FFFFFF",
        "border": "#CCCCCC"
    }

    DARK_MODE = {
        "is_dark": True,
        "main_bg": "#2b2b2b",
        "text": "#FFFFFF",
        "input_bg": "#4d4d4d",
        "input_text": "#FFFFFF",
        "table_bg": "#2b2b2b",
        "table_item_text": "#FFFFFF",
        "header_bg": "#7B1818", # Maroon
        "header_text": "#FFFFFF",
        "btn_primary": "#7B1818",
        "btn_text": "#FFFFFF",
        "border": "#555555"
    }

    def __init__(self):
        self.is_dark_mode = False

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        return self.get_current_theme()

    def get_current_theme(self):
        return self.DARK_MODE if self.is_dark_mode else self.LIGHT_MODE

    def get_stylesheet(self):
        theme = self.get_current_theme()
        
        # Base Styles
        qss = f"""
            QWidget {{
                background-color: {theme['main_bg']};
                color: {theme['text']};
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }}
            
            /* Inputs */
            QLineEdit, QComboBox, QPlainTextEdit {{
                background-color: {theme['input_bg']};
                color: {theme['input_text']};
                border: 1px solid {theme['border']};
                border-radius: 5px;
                padding: 5px 10px;
            }}
            
            /* Tables */
            QTableWidget {{
                background-color: {theme['table_bg']};
                gridline-color: {theme['border']};
                border: 1px solid {theme['border']};
            }}
            QTableWidget::item {{
                color: {theme['table_item_text']};
                padding: 5px;
            }}
            QHeaderView::section {{
                background-color: {self.MAROON};
                color: white;
                padding: 8px;
                font-weight: bold;
                border: 1px solid {theme['border']};
            }}
            
            /* Buttons */
            QPushButton {{
                border-radius: 5px;
                font-weight: bold;
                padding: 8px 15px;
            }}
            
            /* Custom Classes matching Design */
            
            /* Maroon Button (e.g. Dark Mode Toggle, Edit, Cancel, Logout) */
            .MaroonBtn {{
                background-color: {self.MAROON};
                color: white;
                border: 1px solid #5a1010;
            }}
            .MaroonBtn:hover {{
                background-color: #8f2020;
            }}
            
            /* Green Button (Approve, Submit) */
            .GreenBtn {{
                background-color: {self.GREEN};
                color: black;
                border: 1px solid #7cb342;
            }}
            .GreenBtn:hover {{
                background-color: #9ccc65;
            }}
            
            /* Red/Pink Button (Cancel in Modal) */
            .PinkBtn {{
                background-color: {self.RED_LIGHT};
                color: black;
                border: 1px solid #e57373;
            }}
            
            /* Orange Button (Pending Status look-alike) */
            .OrangeBtn {{
                background-color: {self.ORANGE};
                color: black;
            }}
            
            /* Header Label */
            #DashboardHeader {{
                font-size: 24px;
                font-weight: bold;
                color: {theme['text']};
            }}
            
            /* Filter/Search Labels */
            QLabel#ControlLabel {{
                font-size: 16px;
                color: {theme['text']};
            }}
        """
        return qss
