from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QLineEdit, QDialog, QGridLayout, 
                               QComboBox, QFrame, QDateEdit, QTimeEdit, QMessageBox, QApplication)
from PySide6.QtCore import Qt, QDate, QTime, QSize, Signal
from PySide6.QtGui import QPixmap, QIcon
import os

class StudentDashboard(QWidget):
    logout_requested = Signal() 

    def __init__(self, user, db_manager, theme_handler):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.theme_handler = theme_handler
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        self.setLayout(layout)

        # 1. Top Bar
        top_bar = QHBoxLayout()
        
        logo_label = QLabel()
        logo_path = os.path.join("resources", "logo.png") # PUP LOGO
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
        top_bar.addWidget(logo_label)
        
        title_box = QVBoxLayout()
        role_label = QLabel("User: Authorized Student") 
        role_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        app_title = QLabel("Specialized Room Tracker")
        app_title.setObjectName("DashboardHeader")
        app_title.setStyleSheet("font-size: 26px; font-weight: bold;")
        title_box.addWidget(role_label)
        title_box.addWidget(app_title)
        top_bar.addLayout(title_box)
        
        top_bar.addStretch()
        
        self.dark_mode_btn = QPushButton("Dark Mode")
        self.dark_mode_btn.setProperty("class", "MaroonBtn")
        self.dark_mode_btn.setFixedSize(120, 40)
        self.dark_mode_btn.clicked.connect(self.toggle_theme)
        
        logout_btn = QPushButton("Log Out")
        logout_btn.setProperty("class", "MaroonBtn")
        logout_btn.setFixedSize(120, 40)
        logout_btn.clicked.connect(self.logout_requested.emit) 
        
        top_bar.addWidget(self.dark_mode_btn)
        top_bar.addWidget(logout_btn)
        layout.addLayout(top_bar)
        
        layout.addSpacing(30)

        # 2. Controls
        controls_layout = QHBoxLayout()
        
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter by status:")
        filter_label.setStyleSheet("font-size: 16px;")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Approved", "Pending", "Cancelled", "Rejected"])
        self.filter_combo.setFixedWidth(180)
        self.filter_combo.setFixedHeight(35)
        self.filter_combo.currentTextChanged.connect(self.load_data)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        controls_layout.addLayout(filter_layout)
        
        controls_layout.addSpacing(40)
        
        search_layout = QHBoxLayout()
        search_label = QLabel("Search by Room/Name:")
        search_label.setStyleSheet("font-size: 16px;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter room or name")
        self.search_input.setFixedHeight(35)
        self.search_input.textChanged.connect(self.load_data)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        controls_layout.addLayout(search_layout)
        
        layout.addLayout(controls_layout)

        # 3. Table
        self.table = QTableWidget()
        cols = ["ID", "Room", "Name", "Course/Section", "Type", "Date & Time", "Purpose", "Status"]
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet("selection-background-color: #5d1010; selection-color: white;")
        layout.addWidget(self.table)

        # 4. Action Row (Reserve Room + Other Actions)
        action_row_layout = QHBoxLayout()
        action_row_layout.setContentsMargins(0, 0, 0, 0)
        action_row_layout.setSpacing(15)
        
        # Reserve Button Bar
        bottom_bar = QFrame()
        bottom_bar.setFixedHeight(60)
        # Removed fixed width to allow stretching
        bottom_bar.setStyleSheet("background-color: #5d1010; border-radius: 10px;") 
        
        bar_layout = QHBoxLayout(bottom_bar)
        bar_layout.setContentsMargins(10, 0, 10, 0)
        
        reserve_btn = QPushButton("+ Reserve Room")
        reserve_btn.setCursor(Qt.PointingHandCursor)
        reserve_btn.setStyleSheet("""
             QPushButton { 
                background-color: transparent; 
                color: white; 
                font-size: 18px; 
                font-weight: bold;
                border: none;
                text-align: center;
             }
             QPushButton:hover { color: #ccc; }
        """)
        reserve_btn.clicked.connect(self.open_reservation_modal)
        bar_layout.addWidget(reserve_btn, stretch=1)
        
        # Add to row with stretch factor 1 to fill available space
        action_row_layout.addWidget(bottom_bar, stretch=1)
        
        # Right Side Actions
        btn_style_small = """
            QPushButton {
                background-color: #3e0b0b;
                color: white;
                border: 1px solid #7B1818;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                height: 40px;
            }
            QPushButton:hover { background-color: #5d1010; }
        """
        
        details_btn = QPushButton("View details")
        details_btn.setStyleSheet(btn_style_small)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(btn_style_small)
        
        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet(btn_style_small)
        
        action_row_layout.addWidget(details_btn)
        action_row_layout.addWidget(cancel_btn)
        action_row_layout.addWidget(edit_btn)
        
        layout.addLayout(action_row_layout)
        
        # Initial Load
        self.load_data()

    def toggle_theme(self):
        mw = self.window()
        if hasattr(mw, 'toggle_theme'):
            mw.toggle_theme()

    def load_data(self):
        query = """
            SELECT r.id, rm.room_name, u.full_name, r.course_section, 
                   r.reservation_type, r.timestamp, r.reservation_date, r.start_time, 
                   r.status, r.purpose 
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.id
            JOIN users u ON r.user_id = u.id
            WHERE 1=1
        """
        params = []
        if self.filter_combo.currentText() != "All":
            query += " AND r.status = %s"
            params.append(self.filter_combo.currentText())
            
        search = self.search_input.text()
        if search:
            query += " AND (rm.room_name LIKE %s OR u.full_name LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])

        reservations = self.db_manager.fetch_all(query, tuple(params))
        self.table.setRowCount(len(reservations))
        
        for i, res in enumerate(reservations):
            self.table.setItem(i, 0, QTableWidgetItem(str(res['id'])))
            self.table.setItem(i, 1, QTableWidgetItem(res['room_name']))
            self.table.setItem(i, 2, QTableWidgetItem(res['full_name'] or "N/A"))
            self.table.setItem(i, 3, QTableWidgetItem(res['course_section'] or "-"))
            self.table.setItem(i, 4, QTableWidgetItem(res['reservation_type'] or "Academic"))
            dt_str = f"{res['reservation_date']} {res['start_time']}" if res['reservation_date'] else str(res['timestamp'])
            self.table.setItem(i, 5, QTableWidgetItem(dt_str))
            self.table.setItem(i, 6, QTableWidgetItem(res['purpose'] or "N/A"))
            
            status_widget = QLabel(res['status'])
            status_widget.setAlignment(Qt.AlignCenter)
            status_widget.setStyleSheet(self.get_status_style(res['status']))
            self.table.setCellWidget(i, 7, status_widget)
            
    def get_status_style(self, status):
        base = "padding: 5px; font-weight: bold;"
        if status == 'Approved': return base + "background-color: #8BC34A; color: black;"
        if status == 'Pending': return base + "background-color: #FF9800; color: black;"
        return base + "background-color: #EF9A9A; color: black;"

    def open_reservation_modal(self):
        ReservationDialog(self.db_manager, self.user, self.theme_handler.is_dark_mode, self).exec()
        self.load_data()

class ReservationDialog(QDialog):
    def __init__(self, db_manager, user, is_dark_mode, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user = user
        self.setWindowTitle("Create Room Reservation")
        self.setFixedSize(550, 700)
        
        # Dynamic Styling for Modal
        if is_dark_mode:
            self.setStyleSheet("""
                QDialog { background-color: #1e1e1e; color: white; border: 1px solid #7B1818; }
                QLabel { color: white; font-weight: bold; font-size: 14px; }
                QLineEdit, QComboBox, QDateEdit, QTimeEdit {
                    background-color: #2d2d2d;
                    border: 1px solid #7B1818;
                    border-radius: 5px;
                    color: white;
                    padding: 5px;
                }
                QComboBox QAbstractItemView { background-color: #2d2d2d; color: white; selection-background-color: #7B1818; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background-color: #f5f5f5; color: black; border: 1px solid #ccc; }
                QLabel { color: black; font-weight: bold; font-size: 14px; }
                QLineEdit, QComboBox, QDateEdit, QTimeEdit {
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    color: black;
                    padding: 5px;
                }
                QComboBox QAbstractItemView { background-color: #ffffff; color: black; selection-background-color: #ccc; }
            """)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        self.setLayout(layout)
        
        header = QLabel("Create Room Reservation")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"font-size: 24px; margin-bottom: 20px; color: {'white' if is_dark_mode else 'black'};")
        layout.addWidget(header)
        
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(10)
        
        # Fields
        self.room_combo = QComboBox()
        rooms = self.db_manager.fetch_all("SELECT * FROM rooms")
        for r in rooms:
            self.room_combo.addItem(r['room_name'], r['id'])
        
        self.name_input = QLineEdit()
        self.name_input.setText(self.user.get('full_name', ''))
        self.name_input.setPlaceholderText("Enter your name")

        self.email_input = QLineEdit()
        self.email_input.setText(self.user['email'])
        self.email_input.setReadOnly(False) 
        self.email_input.setPlaceholderText("e.g. example@iskolarngbayan.pup.edu.ph")
        
        self.course_input = QLineEdit()
        self.course_input.setPlaceholderText("e.g. BSIT 1-1")
        
        # Changed to ComboBox
        self.type_input = QComboBox()
        self.type_input.addItems(["Academic", "Event", "Formal/Formal Event", "Org Meeting", "Other"])
        
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        
        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())
        
        self.duration_input = QLineEdit()
        self.duration_input.setText("2")
        
        self.purpose_input = QLineEdit()
        self.purpose_input.setFixedHeight(50)
        
        # Rows
        labels = ["Select Room:", "Full Name:", "Webmail:", "Course/Section:", 
                  "Reservation Type:", "Date:", "Time:", "Duration (hours):", "Purpose:"]
        widgets = [self.room_combo, self.name_input, self.email_input, self.course_input,
                   self.type_input, self.date_input, self.time_input, self.duration_input, self.purpose_input]
        
        for i, (lbl, widget) in enumerate(zip(labels, widgets)):
            form_layout.addWidget(QLabel(lbl), i, 0)
            form_layout.addWidget(widget, i, 1)

        layout.addLayout(form_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        submit_btn = QPushButton("Submit Reservation")
        submit_btn.setStyleSheet("background-color: #8BC34A; color: black; font-size: 16px; border-radius: 5px; padding: 10px; font-weight: bold;")
        submit_btn.setFixedHeight(45)
        submit_btn.clicked.connect(self.submit)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #EF9A9A; color: black; font-size: 16px; border-radius: 5px; padding: 10px; font-weight: bold;")
        cancel_btn.setFixedHeight(45)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(submit_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def submit(self):
        # Validation
        fields = {
            "Full Name": self.name_input.text().strip(),
            "Webmail": self.email_input.text().strip(),
            "Course/Section": self.course_input.text().strip(),
            "Purpose": self.purpose_input.text().strip(),
            "Duration": self.duration_input.text().strip()
        }
        
        empty_fields = [label for label, value in fields.items() if not value]
        if empty_fields:
            QMessageBox.warning(self, "Incomplete Form", 
                               f"Please fill up all fields. Missing:\n- {', '.join(empty_fields)}")
            return

        if self.name_input.text() != self.user.get('full_name'):
             self.db_manager.execute_query("UPDATE users SET full_name = %s WHERE id = %s", 
                                           (self.name_input.text(), self.user['id']))
        
        room_id = self.room_combo.currentData()
        
        query = """
            INSERT INTO reservations 
            (user_id, room_id, course_section, reservation_type, reservation_date, start_time, duration_hours, purpose, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
        """
        params = (
            self.user['id'], 
            room_id,
            self.course_input.text(),
            self.type_input.currentText(), # ComboBox text
            self.date_input.date().toString("yyyy-MM-dd"),
            self.time_input.time().toString("HH:mm:ss"),
            self.duration_input.text(),
            self.purpose_input.text()
        )
        
        if self.db_manager.execute_query(query, params):
            QMessageBox.information(self, "Success", "Reservation Submitted Successfully")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to submit reservation")
