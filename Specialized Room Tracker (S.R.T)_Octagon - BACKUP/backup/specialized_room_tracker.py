# requirements
import mysql.connector
import bcrypt
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QPalette, QPixmap
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QFrame, QHBoxLayout, 
                               QSizePolicy, QSpacerItem, QMessageBox)

# FRONTEND - KEN
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Specialized Room Reservation")


        # BACKEND - GAB (DATABASE CONFIGURATION & CONNECTION)
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'password',
            'port': '3306',
            'database': 'specialized_room_tracker'
        }
        
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
        logo_pixmap = QPixmap("resources/logo.png")
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

        # BACKEND CONFIGURATION BY GAB
        self.login_btn.clicked.connect(self.handle_login_logic) # BACKEND - GAB (CONNECTION USER CLICK EVENT SA BUTTON / CONNECTION FOR DATABASE)
        
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

    #  BACKEND LOGIC - GAB (LOGIN LOGIC)
    def handle_login_logic(self): 
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Validation", "Please enter email and password.") 
            return
        
        # CONNECTING DATABASE
        try:
            connect = mysql.connector.connect(**self.db_config)
            cursor = connect.cursor(dictionary=True)

            # FETCH USER FROM DATABASE
            query = "SELECT user_id, username, email, user_password, password_hash, role FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user_data = cursor.fetchone()
            
            connect.close()

            if user_data:
                stored_hash = user_data['password_hash']
                if isinstance(stored_hash, str):
                    stored_hash = stored_hash.encode('utf-8')
                
                # ENCRYPTION OF PASSWORD / PASSWORD BCRYPT
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                        
                        print("\n" + "="*50)
                        print(" USER DATA RETRIEVED ")
                        print("="*50)
                        print(f" User ID  : {user_data['user_id']}")
                        print(f" Username : {user_data['username']}")
                        print(f" Email    : {user_data['email']}")
                        print(f" Role     : {user_data['role']}")
                        print("="*50 + "\n")
            
                        QMessageBox.information(self, "Success", f"Welcome, {user_data['role']}!")

                else: 
                    QMessageBox.critical(self, "Login Failed", "Incorrect password.")
            else:
                QMessageBox.critical(self, "Login Failed", "User not found.")
                print("Login attempt failed: Email not found.")
        
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Error connecting to database: {err}")

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