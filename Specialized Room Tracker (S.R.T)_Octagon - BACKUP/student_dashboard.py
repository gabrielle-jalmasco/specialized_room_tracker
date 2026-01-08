from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QLineEdit, QDialog, QGridLayout,
                               QComboBox, QFrame, QDateEdit, QTimeEdit, QMessageBox, QApplication)
from PySide6.QtCore import Qt, QDate, QTime, QSize, Signal, QTimer
from PySide6.QtGui import QPixmap, QIcon
import os



class StudentDashboard(QWidget):
    logout_requested = Signal()

    def __init__(self, user, db_manager, theme_handler):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.theme_handler = theme_handler
        self.is_currently_dark = self.theme_handler.is_dark_mode
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        self.setLayout(layout)

        # 1. Top Bar
        top_bar = QHBoxLayout()

        logo_label = QLabel()
        # Use path relative to the script to ensure it works regardless of CWD
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, "resources", "logo.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(
                60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
        else:
            print(f"DEBUG: Student logo not found at {logo_path}")
        top_bar.addWidget(logo_label)

        title_box = QVBoxLayout()
        role_label = QLabel(f"User: {self.user['username']}")
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
        self.filter_combo.addItems(
            ["All", "Approved", "Pending", "Cancelled", "Rejected"])
        self.filter_combo.setFixedWidth(180)
        self.filter_combo.setFixedHeight(35)
        self.filter_combo.currentTextChanged.connect(lambda: self.load_data())
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
        self.search_input.textChanged.connect(lambda: self.load_data())
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        controls_layout.addLayout(search_layout)

        layout.addLayout(controls_layout)

        # 3. Table
        self.table = QTableWidget()
        cols = ["ID", "Room", "Name", "Course/Section",
                "Type", "Date & Time", "Purpose", "Status"]
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(45)  # Set row height
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True)  # Enable sorting
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setStyleSheet(
            "selection-background-color: #5d1010; selection-color: white;")
        layout.addWidget(self.table)

        # 4. Action Row (Reserve Room + Other Actions)
        action_row_layout = QHBoxLayout()
        action_row_layout.setContentsMargins(0, 0, 0, 0)
        action_row_layout.setSpacing(15)

        # Reserve Button Bar
        bottom_bar = QFrame()
        bottom_bar.setFixedHeight(60)
        # Removed fixed width to allow stretching
        bottom_bar.setStyleSheet(
            "background-color: #5d1010; border-radius: 10px;")

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
        details_btn.clicked.connect(self.view_details)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(btn_style_small)
        cancel_btn.clicked.connect(self.cancel_request)

        edit_btn = QPushButton("Edit")
        edit_btn.setStyleSheet(btn_style_small)
        edit_btn.clicked.connect(self.edit_reservation)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet(
            btn_style_small + "QPushButton { background-color: #4CAF50; } QPushButton:hover { background-color: #45a049; }")
        self.refresh_btn.clicked.connect(self.load_data)

        action_row_layout.addWidget(details_btn)
        action_row_layout.addWidget(cancel_btn)
        action_row_layout.addWidget(edit_btn)
        action_row_layout.addWidget(self.refresh_btn)

        layout.addLayout(action_row_layout)

        # Auto-Refresh Timer (30 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(30000)  # 30 seconds

        # Initial Load
        self.load_data()

    def toggle_theme(self):
        if self.is_currently_dark == False:
            self.is_currently_dark = True
            self.setStyleSheet("background-color: #333333; color: white;")
            print("System: Dark mode activated.")
        else:
            self.is_currently_dark = False
            self.setStyleSheet("background-color: white; color: black;")
            print("System: Light mode activated.")

    def load_data(self):
        query = """
            SELECT r.reservation_id, rm.room_name, r.full_name, r.course_section,
                   r.reservation_type, r.start_time, r.current_status, r.activity_description
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.room_id
            WHERE r.user_id = %s
        """
        params = [self.user['id']]
        
        filter_text = self.filter_combo.currentText()
        if filter_text != "All":
            query = query + " AND r.current_status = %s"
            params.append(filter_text)

        search_text = self.search_input.text()
        if search_text != "":
            query = query + " AND rm.room_name LIKE %s"
            params.append("%" + search_text + "%")

        results = self.db_manager.fetch_all(query, tuple(params))
        self.table.setRowCount(len(results))

        for i, row in enumerate(results):
            self.table.setItem(i, 0, QTableWidgetItem(str(row['reservation_id'])))
            self.table.setItem(i, 1, QTableWidgetItem(str(row['room_name'])))
            self.table.setItem(i, 2, QTableWidgetItem(str(row['full_name'])))
            self.table.setItem(i, 3, QTableWidgetItem(str(row['course_section'])))
            self.table.setItem(i, 4, QTableWidgetItem(str(row['reservation_type'])))
            self.table.setItem(i, 5, QTableWidgetItem(str(row['start_time'])))
            self.table.setItem(i, 6, QTableWidgetItem(str(row['activity_description'])))

            status_label = QLabel(str(row['current_status']))
            status_label.setAlignment(Qt.AlignCenter)
            status_label.setStyleSheet("font-weight: bold; background-color: #FF9800; color: black;")
            self.table.setCellWidget(i, 7, status_label)

    def open_reservation_modal(self):
        ReservationDialog(self.db_manager, self.user, self.is_currently_dark, self).exec()
        self.load_data()
        
    def view_details(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            target_res_id = self.table.item(selected_row, 0).text()
            # Open the ReservationDialog in view-only mode
            dialog = ReservationDialog(self.db_manager, self.user, self.is_currently_dark, self, res_id=target_res_id, view_only=True)
            dialog.exec()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a row first.")

    def cancel_request(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            target_res_id = self.table.item(selected_row, 0).text()
            sql = "UPDATE reservations SET current_status = 'Cancelled' WHERE reservation_id = %s"
            if self.db_manager.execute_query(sql, (target_res_id,)):
                QMessageBox.information(self, "Success", "Reservation Cancelled.")
                self.load_data()

    def edit_reservation(self):
        QMessageBox.information(self, "Note", "Edit is currently locked for this demo.")

    def delete_reservation(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection",
                                "Please select a reservation to delete.")
            return

        res_id = self.table.item(row, 0).text()

        # Check time limit (5 minutes)
        results = self.db_manager.fetch_all(
            "SELECT created_at FROM reservations WHERE reservation_id = %s", (res_id,))
        if not results:
            return

        from datetime import datetime, timedelta
        # MySQL datetime might be returned as a string or datetime depending on driver/config
        res = results[0]
        created_at = res['created_at']
        if isinstance(created_at, str):
            created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")

        now = datetime.now()
        if now - created_at > timedelta(minutes=5):
            QMessageBox.warning(self, "Action Denied",
                                "You can only delete a reservation within 5 minutes of creation.\n"
                                f"Created at: {created_at.strftime('%I:%M %p')}\n"
                                "Please contact an administrator if you need to cancel this.")
            return

        confirm = QMessageBox.question(self, "Confirm Deletion",
                                       "Are you sure you want to delete this reservation?",
                                       QMessageBox.Yes | QMessageBox.No)

        if confirm == QMessageBox.Yes:
            if self.db_manager.execute_query("DELETE FROM reservations WHERE reservation_id = %s", (res_id,)):
                QMessageBox.information(
                    self, "Deleted", "Reservation successfully deleted.")
                self.load_data()
            else:
                QMessageBox.critical(
                    self, "Error", "Failed to delete reservation.")


class ReservationDialog(QDialog):
    def __init__(self, db_manager, user, is_dark_mode, parent=None, res_id=None, view_only=False):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user = user
        self.res_id = res_id
        self.view_only = view_only
        
        if self.view_only:
            self.setWindowTitle("View Reservation Details")
        elif self.res_id:
            self.setWindowTitle("Edit Reservation")
        else:
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

        header = QLabel(self.windowTitle())
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(
            f"font-size: 24px; margin-bottom: 20px; color: {'white' if is_dark_mode else 'black'};")
        layout.addWidget(header)

        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(10)

        # Fields
        self.room_combo = QComboBox()
        rooms = self.db_manager.fetch_all("SELECT * FROM rooms")
        for r in rooms:
            self.room_combo.addItem(r['room_name'], r['room_id'])

        self.name_input = QLineEdit()
        self.name_input.setText(self.user.get('full_name', ''))
        self.name_input.setPlaceholderText("Enter your name")

        self.email_input = QLineEdit()
        self.email_input.setText(self.user['email'])
        self.email_input.setReadOnly(False)
        self.email_input.setPlaceholderText(
            "e.g. example@iskolarngbayan.pup.edu.ph")

        self.course_input = QLineEdit()
        self.course_input.setPlaceholderText("e.g. BSIT 1-1")

        # Changed to ComboBox
        self.type_input = QComboBox()
        self.type_input.addItems(
            ["Academic", "Event", "Formal/Formal Event", "Org Meeting", "Other"])

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
        submit_btn.setStyleSheet(
            "background-color: #8BC34A; color: black; font-size: 16px; border-radius: 5px; padding: 10px; font-weight: bold;")
        submit_btn.setFixedHeight(45)
        submit_btn.clicked.connect(self.submit)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet(
            "background-color: #EF9A9A; color: black; font-size: 16px; border-radius: 5px; padding: 10px; font-weight: bold;")
        cancel_btn.setFixedHeight(45)
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(submit_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        # Handle View Only Mode
        if self.view_only:
            submit_btn.setVisible(False)
            cancel_btn.setText("Close")
            
            self.room_combo.setEnabled(False)
            self.name_input.setReadOnly(True)
            self.email_input.setReadOnly(True)
            self.course_input.setReadOnly(True)
            self.type_input.setEnabled(False)
            self.date_input.setEnabled(False)
            self.time_input.setEnabled(False)
            self.duration_input.setReadOnly(True)
            self.purpose_input.setReadOnly(True)

        if self.res_id:
            self.load_existing_data()

    def load_existing_data(self):
        results = self.db_manager.fetch_all(
            "SELECT * FROM reservations WHERE reservation_id = %s", (self.res_id,))
        if results:
            # Match current index for room
            res = results[0]
            for i in range(self.room_combo.count()):
                if self.room_combo.itemData(i) == res['room_id']:
                    self.room_combo.setCurrentIndex(i)
                    break

            self.name_input.setText(res['full_name'])
            self.course_input.setText(res['course_section'])

            # Match current text for type
            idx = self.type_input.findText(res['reservation_type'])
            if idx >= 0:
                self.type_input.setCurrentIndex(idx)

            from datetime import datetime
            if res['start_time']:
                start_dt = res['start_time']
                if isinstance(start_dt, str):
                    start_dt = datetime.strptime(start_dt, "%Y-%m-%d %H:%M:%S")
                
                self.date_input.setDate(QDate(start_dt.year, start_dt.month, start_dt.day))
                self.time_input.setTime(QTime(start_dt.hour, start_dt.minute, start_dt.second))

                if res.get('end_time'):
                    end_dt = res['end_time']
                    if isinstance(end_dt, str):
                        end_dt = datetime.strptime(end_dt, "%Y-%m-%d %H:%M:%S")
                    
                    # Calculate duration
                    diff = end_dt - start_dt
                    hours = diff.total_seconds() / 3600
                    self.duration_input.setText(str(round(hours, 1)))

            self.purpose_input.setText(res.get('activity_description', ''))

    def submit(self):
        # Validation
        if not self.name_input.text().strip() or \
           not self.email_input.text().strip() or \
           not self.course_input.text().strip() or \
           not self.purpose_input.text().strip() or \
           not self.duration_input.text().strip():
            QMessageBox.warning(self, "Incomplete Form", "Please fill in all fields.")
            return

        dt_str = self.date_input.date().toString("yyyy-MM-dd") + " " + self.time_input.time().toString("HH:mm:ss")
        
        # Calculate end time based on duration
        from datetime import datetime, timedelta
        try:
            duration = float(self.duration_input.text())
        except ValueError:
            duration = 1.0
            
        start_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        end_dt = start_dt + timedelta(hours=duration)
        end_dt_str = end_dt.strftime("%Y-%m-%d %H:%M:%S")
        
        query = """
            INSERT INTO reservations (user_id, room_id, full_name, course_section, 
            reservation_type, start_time, end_time, activity_description, current_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Pending')
        """
        params = (self.user['id'], self.room_combo.currentData(), self.name_input.text(), 
                  self.course_input.text(), self.type_input.currentText(), dt_str, end_dt_str, self.purpose_input.text())

        if self.db_manager.execute_query(query, params):
            QMessageBox.information(self, "Success", "Reservation Request Sent!")
            self.accept()