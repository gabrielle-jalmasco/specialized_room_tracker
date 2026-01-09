# requirements
import mysql.connector
import bcrypt
import sys
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPalette, QPixmap
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QFrame, QHBoxLayout, 
                               QSizePolicy, QSpacerItem, QMessageBox)

# import backend (gab)
import login_authentication
import database_manager

# import frontend (ken)
from student_dashboard import StudentDashboard
from admin_dashboard import AdminDashboard

# FRONTEND - KEN
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme_handler = self
        self.is_dark_mode = False

        self.setWindowTitle("Specialized Room Tracker")
      
        # FRONTEND - KEN
        # Determine screen geometry to set initial size, though we launch maximized/fullscreen
        screen = QApplication.primaryScreen().geometry()
        self.resize(1200, 800) # Default standalone size
        
        # Per user request: fullscreen but resizable (contents showing).
        # We start maximized to cover screen but keep decorations for resizing/moving if user restores.
        self.showMaximized() 

        # Main Central Widget - The Dark Background
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main Layout to center the Card
        self.main_layout = QVBoxLayout(self.central_widget)
        # Added margins to keep card away from edges as requested
        self.main_layout.setContentsMargins(0, 50, 0, 50) 
        self.main_layout.setAlignment(Qt.AlignCenter)

        # ScrollArea can be added here if the screen is too small, 
        # but for a simple login page, a direct layout is usually fine.
        
        # The Card Frame
        self.card = QFrame()
        self.card.setObjectName("LoginCard")
        # Fixed width for the card to match the look, or slightly responsive
        self.card.setFixedWidth(500)
        
        self.main_layout.addWidget(self.card) # Add card to the main layout
        
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(40, 50, 40, 50)
        self.card_layout.setSpacing(20)

        # 1. Logo (Placeholder)
        # We use a frame or label for the logo placeholder
        # 1. Logo
        self.logo_placeholder = QLabel()
        self.logo_placeholder.setObjectName("LogoPlaceholder")
        self.logo_placeholder.setFixedSize(100, 100)
        self.logo_placeholder.setAlignment(Qt.AlignCenter)
        
        # Load and set logo image
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, "resources", "logo.png")
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            self.logo_placeholder.setPixmap(logo_pixmap.scaled(
                100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        else:
            self.logo_placeholder.setText("LOGO") 
        # Center the logo horizontally
        logo_container = QHBoxLayout()
        logo_container.addStretch()
        logo_container.addWidget(self.logo_placeholder)
        logo_container.addStretch()
        self.card_layout.addLayout(logo_container)

        # 2. Titles
        self.title_label = QLabel("PUP - S.R.T.")
        self.title_label.setObjectName("MainTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        
        self.subtitle_label = QLabel("“Specialized Room Tracker")
        self.subtitle_label.setObjectName("Subtitle")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setWordWrap(True)

        self.card_layout.addWidget(self.title_label)
        self.card_layout.addWidget(self.subtitle_label)
        self.card_layout.addSpacing(10)

        # 3. Sign in Text
        self.signin_label = QLabel("Sign in to start")
        self.signin_label.setObjectName("SignInText")
        self.signin_label.setAlignment(Qt.AlignCenter)
        self.card_layout.addWidget(self.signin_label)
        
        # 4. Inputs
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setObjectName("InputBox")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setObjectName("InputBox")
        
        self.card_layout.addWidget(self.email_input)
        self.card_layout.addWidget(self.password_input)
        
        # 5. Login Button
        self.login_btn = QPushButton("Log in")
        self.login_btn.setObjectName("LoginButton")
        self.login_btn.setCursor(Qt.PointingHandCursor)

        self.login_btn.clicked.connect(self.handle_login_process) # connect button to login_authentication.py

        # Center button potentially, but block looks better
        self.card_layout.addSpacing(10)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.login_btn)
        btn_layout.addStretch()
        # To make it full width like design:
        self.card_layout.addWidget(self.login_btn)

        # 6. Forgot Password
        self.forgot_label = QLabel("Forgot password?")
        self.forgot_label.setObjectName("ForgotLink")
        self.forgot_label.setAlignment(Qt.AlignCenter)
        self.forgot_label.setCursor(Qt.PointingHandCursor)
        self.card_layout.addWidget(self.forgot_label)
        
        self.card_layout.addStretch()

        # 7. Disclaimers / Footer
        self.footer_text_1 = QLabel("A Student's “Specialized Room Tracker” for Special Room Reservation")
        self.footer_text_1.setObjectName("FooterText")
        self.footer_text_1.setWordWrap(True)
        self.footer_text_1.setAlignment(Qt.AlignCenter)
        self.card_layout.addWidget(self.footer_text_1)

        self.footer_text_2 = QLabel('By using this service, you understood and agree to the PUP Online Services\n Terms of use and Privacy Statement')
        self.footer_text_2.setObjectName("FooterSmall")
        self.footer_text_2.setWordWrap(True)
        self.footer_text_2.setAlignment(Qt.AlignCenter)
        self.card_layout.addWidget(self.footer_text_2)

        # Apply Styles
        self.apply_styles()

    # handle login logic backend - gab
    def handle_login_process(self):
        captured_user_email_text = self.email_input.text().strip()
        captured_user_password_text = self.password_input.text().strip()

        if captured_user_email_text == "" or captured_user_password_text == "":
            QMessageBox.warning(self, "Input Error", "Please enter both your email and your password.")
            return

        # It returns a list: [status, role, name, real_database_id]
        login_process_result_list = login_authentication.verify_user_credentials(
            captured_user_email_text, 
            captured_user_password_text
        )

        final_login_status_string = login_process_result_list[0]

        if final_login_status_string == "SUCCESS":
            # Extract specific details from the list
            authorized_user_role = login_process_result_list[1]
            authorized_user_display_name = login_process_result_list[2]
            authorized_user_database_id = login_process_result_list[3]

            authorized_user_data_dictionary = {
                "id": authorized_user_database_id,
                "username": authorized_user_display_name,
                "email": captured_user_email_text,
                "role": authorized_user_role
            }

            self.signin_label.setText("Welcome, " + authorized_user_display_name + "!")
            QMessageBox.information(self, "Login Successful", "Access Granted as: " + authorized_user_role)

            if authorized_user_role == "Campus Administrator":
                self.dashboard = AdminDashboard(
                    authorized_user_data_dictionary,
                    database_manager,
                    self.theme_handler
                )
            else:
                self.dashboard = StudentDashboard(
                    authorized_user_data_dictionary, 
                    database_manager, 
                    self.theme_handler
                )
            
            # Connect the logout signal from the dashboard to the handler
            self.dashboard.logout_requested.connect(self.handle_logout)

            self.dashboard.show()
            self.hide()

        # 6. Failure Logic
        elif final_login_status_string == "FAILED":
            # Extract the error message from the list
            error_explanation_message = login_process_result_list[1]
            QMessageBox.critical(self, "Login Failed", error_explanation_message)
            self.signin_label.setText("Invalid Login. Please try again.")

        else:
            # Handle system "ERROR" status
            error_explanation_message = login_process_result_list[1]
            QMessageBox.critical(self, "System Error", error_explanation_message)

    def handle_logout(self):
        if hasattr(self, 'dashboard'):
            self.dashboard.close()
        self.show()
        self.email_input.clear()
        self.password_input.clear()
                                 
    def apply_styles(self):
        # Colors approximated from image
        # Background: #4d0000 (Very dark red) or slightly lighter gradient? 
        # Making it solid #400505 based on plan.
        # Card: #6e2c2c (Muted brownish red)
        # Inputs: #8c4f4f / #9e5e5e transparent-ish
        # Text: White
        
        style_sheet = """
        QMainWindow {
            background-color: #400505;
        }
        
        QWidget {
            font-family: "Times New Roman", Times, serif;
            color: white;
        }

        #LoginCard {
            background-color: rgba(110, 44, 44, 255); 
            border-radius: 30px;
        }

        #LogoPlaceholder {
            background-color: transparent;
            /* Border removed for actual logo */
            border: none;
            border-radius: 50px; 
            color: rgba(255, 255, 255, 0.7);
            font-size: 14px;
        }

        #MainTitle {
            font-size: 28px;
            font-weight: normal;
            margin-top: 10px;
        }

        #Subtitle {
            font-size: 24px;
            font-style: italic;
            margin-bottom: 10px;
        }

        #SignInText {
            font-family: "Segoe UI", Arial, sans-serif;
            font-size: 14px;
            opacity: 0.8;
            margin-bottom: 5px;
        }

        #InputBox {
            background-color: rgba(140, 79, 79, 255);
            border: none;
            border-radius: 10px;
            padding: 10px 15px;
            font-size: 14px;
            font-family: "Segoe UI", Arial, sans-serif;
            color: white; /* Text color inside input */
            selection-background-color: #a36666;
        }
        #InputBox::placeholder {
            color: rgba(255, 255, 255, 0.8);
        }

        #LoginButton {
            background-color: #2b0505;
            color: white;
            border: none;
            border-radius: 15px;
            padding: 12px;
            font-size: 14px;
            font-weight: bold;
            min-height: 20px;
        }
        #LoginButton:hover {
            background-color: #3d0808;
        }
        #LoginButton:pressed {
            background-color: #1a0303;
        }

        #ForgotLink {
            font-size: 12px;
            font-family: "Segoe UI", Arial, sans-serif;
            margin-top: 5px;
        }
        #ForgotLink:hover {
            text-decoration: underline;
        }

        #FooterText {
            font-size: 13px;
            margin-top: 20px;
            opacity: 0.8;
        }
        
        #FooterSmall {
            font-size: 11px;
            color: #d1d1d1;
            margin-top: 5px;
        }
        """
        self.setStyleSheet(style_sheet)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())