from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QComboBox, QLineEdit, QMessageBox, QMenu,
                               QDialog, QGridLayout, QDateEdit, QTimeEdit)
from PySide6.QtCore import Qt, Signal, QTimer, QDate, QTime
from PySide6.QtGui import QPixmap, QAction, QCursor
import os

class AdminDashboard(QWidget):
    logout_requested = Signal()

    def __init__(self, user, db_manager, theme_handler):
        super().__init__()
        self.user = user
        self.db_manager = db_manager
        self.theme_handler = theme_handler
        self.is_dark_mode = getattr(theme_handler, 'is_dark_mode', False)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        # 1. Top Bar
        top_bar = QHBoxLayout()
        
        logo_label = QLabel()
        # Use path relative to the script to ensure it works regardless of CWD
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, "resources", "logo.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
        else:
            print(f"DEBUG: Admin logo not found at {logo_path}")
        top_bar.addWidget(logo_label)
        
        title_box = QVBoxLayout()
        role_label = QLabel("User: Campus Administrator")
        role_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        app_title = QLabel("Specialized Room Tracker")
        app_title.setObjectName("DashboardHeader")
        title_box.addWidget(role_label)
        title_box.addWidget(app_title)
        top_bar.addLayout(title_box)
        
        top_bar.addStretch()
        
        self.dark_mode_btn = QPushButton("Dark Mode")
        self.dark_mode_btn.setProperty("class", "MaroonBtn")
        self.dark_mode_btn.clicked.connect(self.toggle_theme)
        
        logout_btn = QPushButton("Log Out")
        logout_btn.setProperty("class", "MaroonBtn")
        logout_btn.clicked.connect(self.logout_requested.emit) 
        
        top_bar.addWidget(self.dark_mode_btn)
        top_bar.addWidget(logout_btn)
        layout.addLayout(top_bar)
        
        layout.addSpacing(20)

        # 2. Controls
        controls_layout = QHBoxLayout()
        
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter by status:")
        filter_label.setObjectName("ControlLabel")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Pending", "Approved", "Cancelled", "Rejected", "All"])
        self.filter_combo.setFixedWidth(150)
        self.filter_combo.currentTextChanged.connect(lambda: self.load_requests())
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        controls_layout.addLayout(filter_layout)
        
        controls_layout.addSpacing(20)
        
        search_layout = QHBoxLayout()
        search_label = QLabel("Search by Room/Name:")
        search_label.setObjectName("ControlLabel")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter room or name")
        self.search_input.textChanged.connect(lambda: self.load_requests())
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        controls_layout.addLayout(search_layout)
        
        controls_layout.addStretch()
        
        add_room_btn = QPushButton("Add Room")
        add_room_btn.setProperty("class", "MaroonBtn")
        add_room_btn.setMinimumWidth(150)
        add_room_btn.clicked.connect(self.open_add_room_dialog)
        controls_layout.addWidget(add_room_btn)
        
        layout.addLayout(controls_layout)

        # 3. Table
        self.table = QTableWidget()
        # Added checkbox column at index 0
        cols = ["", "ID", "Room", "Name", "Course/Section", "Type", "Date & Time", "Purpose", "Status"]
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels(cols)
        
        # Adjust Header resizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 40) # Small width for checkbox
        for i in range(1, len(cols)):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
            
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(45) # Set row height
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSortingEnabled(True) # Enable sorting
        self.table.setContextMenuPolicy(Qt.CustomContextMenu) # Enable Context Menu
        self.table.customContextMenuRequested.connect(self.open_context_menu)

        # Add "Select All" checkbox to header
        from PySide6.QtWidgets import QCheckBox
        self.header_checkbox = QCheckBox(self.table.horizontalHeader())
        self.header_checkbox.setGeometry(10, 8, 20, 20) # Position over the first column header
        self.header_checkbox.stateChanged.connect(self.toggle_select_all)
        
        layout.addWidget(self.table)
        
        # 4. Bottom Actions
        bottom_bar = QHBoxLayout()
        
        # Action Buttons (Approve / Reject)
        approve_btn = QPushButton("Approve Selected")
        approve_btn.setProperty("class", "GreenBtn")
        approve_btn.setMinimumWidth(200)
        approve_btn.setStyleSheet("""
             QPushButton { background-color: #8BC34A; color: black; padding: 10px; font-size: 16px; border-radius: 5px; font-weight: bold; }
             QPushButton:hover { background-color: #7cb342; }
        """)
        approve_btn.clicked.connect(lambda: self.process_batch("Approved"))
        
        reject_btn = QPushButton("Reject Selected")
        reject_btn.setProperty("class", "MaroonBtn")
        reject_btn.setMinimumWidth(200)
        reject_btn.setStyleSheet("""
             QPushButton { background-color: #D32F2F; color: white; padding: 10px; font-size: 16px; border-radius: 5px; font-weight: bold; }
             QPushButton:hover { background-color: #b71c1c; }
        """)
        reject_btn.clicked.connect(lambda: self.process_batch("Rejected"))
        
        cancel_sel_btn = QPushButton("Cancel Selected")
        cancel_sel_btn.setProperty("class", "MaroonBtn")
        cancel_sel_btn.setMinimumWidth(200)
        cancel_sel_btn.setStyleSheet("""
             QPushButton { background-color: #FF9800; color: black; padding: 10px; font-size: 16px; border-radius: 5px; font-weight: bold; }
             QPushButton:hover { background-color: #f57c00; }
        """)
        cancel_sel_btn.clicked.connect(lambda: self.process_batch("Cancelled"))

        delete_btn = QPushButton("Delete Selected")
        delete_btn.setProperty("class", "MaroonBtn")
        delete_btn.setMinimumWidth(200)
        delete_btn.setStyleSheet("""
             QPushButton { background-color: #333333; color: white; padding: 10px; font-size: 16px; border-radius: 5px; font-weight: bold; }
             QPushButton:hover { background-color: #000000; }
        """)
        delete_btn.clicked.connect(lambda: self.process_batch("Delete"))
        
        bottom_bar.addWidget(approve_btn)
        bottom_bar.addWidget(reject_btn)
        bottom_bar.addWidget(cancel_sel_btn)
        bottom_bar.addWidget(delete_btn)
        
        bottom_bar.addStretch()
        
        details_btn = QPushButton("View details")
        details_btn.setProperty("class", "MaroonBtn")
        details_btn.clicked.connect(self.view_details)
        
        edit_btn = QPushButton("Edit")
        edit_btn.setProperty("class", "MaroonBtn")
        edit_btn.clicked.connect(self.edit_request)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setProperty("class", "MaroonBtn")
        self.refresh_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; } QPushButton:hover { background-color: #45a049; }")
        self.refresh_btn.clicked.connect(self.load_requests)
    
        bottom_bar.addWidget(details_btn)
        bottom_bar.addWidget(edit_btn)
        bottom_bar.addWidget(self.refresh_btn)
        
        layout.addLayout(bottom_bar)

        # Auto-Refresh Timer (30 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.load_requests)
        self.refresh_timer.start(30000) # 30 seconds
        self.refresh_timer.start(2000) # 2 seconds for demo
        
        self.load_requests()

    def open_add_room_dialog(self):
        if RoomDialog(self.db_manager, self.theme_handler.is_dark_mode, self).exec():
            # Refresh if needed, though rooms aren't listed on admin dashboard currently
            pass

    def toggle_select_all(self, state):
        check_state = Qt.Checked if state == Qt.Checked or state == 2 else Qt.Unchecked
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                item.setCheckState(check_state)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        
        if self.is_dark_mode:
            self.setStyleSheet("background-color: #333333; color: white;")
        else:
            self.setStyleSheet("background-color: #f5f5f5; color: black;")
            
        # Update handler so dialogs see the change
        if hasattr(self.theme_handler, 'is_dark_mode'):
            self.theme_handler.is_dark_mode = self.is_dark_mode

    def load_requests(self):
        query = """
            SELECT r.reservation_id, rm.room_name, r.full_name, r.course_section, 
                   r.reservation_type, r.created_at, r.start_time, 
                   r.current_status, r.activity_description 
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.room_id
            LEFT JOIN users u ON r.user_id = u.user_id
            WHERE 1=1
        """
        params = []
        
        if self.filter_combo.currentText() != "All":
            query += " AND r.current_status = %s"
            params.append(self.filter_combo.currentText())
            
        search = self.search_input.text()
        if search:
            query += " AND (rm.room_name LIKE %s OR r.full_name LIKE %s)"
            params.extend([f"%{search}%", f"%{search}%"])

        requests = self.db_manager.fetch_all(query, tuple(params))
        self.table.setRowCount(len(requests))
        
        # Reset header checkbox state without triggering signal
        self.header_checkbox.blockSignals(True)
        self.header_checkbox.setCheckState(Qt.Unchecked)
        self.header_checkbox.blockSignals(False)
        
        self.table.setSortingEnabled(False) # Temporarily disable while loading
        
        for i, req in enumerate(requests):
            # 0. Checkbox
            check_item = QTableWidgetItem()
            check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            check_item.setCheckState(Qt.Unchecked)
            self.table.setItem(i, 0, check_item)

            # 1. ID (Numeric Sorting)
            id_item = QTableWidgetItem()
            id_item.setData(Qt.EditRole, int(req['reservation_id']))
            self.table.setItem(i, 1, id_item)
            
            # 2. Room
            self.table.setItem(i, 2, QTableWidgetItem(req['room_name']))
            # 3. Name
            self.table.setItem(i, 3, QTableWidgetItem(req['full_name'] or "N/A"))
            # 4. Course
            self.table.setItem(i, 4, QTableWidgetItem(req['course_section'] or "-"))
            # 5. Type
            self.table.setItem(i, 5, QTableWidgetItem(req['reservation_type'] or "Academic"))
            
            # 6. Date Time
            dt_str = str(req['start_time'])
            self.table.setItem(i, 6, QTableWidgetItem(dt_str))
            
            # 7. Purpose
            self.table.setItem(i, 7, QTableWidgetItem(req['activity_description'] or "N/A"))
            
            # 8. Status
            status_widget = QLabel(req['current_status'])
            status_widget.setAlignment(Qt.AlignCenter)
            status_widget.setProperty("class", "StatusBadge")
            
            style = "font-weight: bold; padding: 3px;"
            if req['current_status'] == 'Approved':
                style += "background-color: #8BC34A; color: black;"
            elif req['current_status'] == 'Pending':
                style += "background-color: #FF9800; color: black;"
            elif req['current_status'] in ['Cancelled', 'Rejected']:
                style += "background-color: #FFCDD2; color: #D32F2F;"
                
            status_widget.setStyleSheet(style)
            self.table.setCellWidget(i, 8, status_widget)

        self.table.setSortingEnabled(True) # Re-enable sorting after load

    def process_batch(self, new_status):
        ids_to_update = []
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.checkState() == Qt.Checked:
                # Column 1 is ID now
                res_id = self.table.item(row, 1).text()
                ids_to_update.append(res_id)
        
        if not ids_to_update:
            # Fallback to selected row if no checkboxes are checked
            selected_rows = sorted(list(set(index.row() for index in self.table.selectedIndexes())))
            for row in selected_rows:
                res_id = self.table.item(row, 1).text()
                ids_to_update.append(res_id)
        
        if not ids_to_update:
            QMessageBox.warning(self, "No Selection", "Please check boxes or select rows to process.")
            return

        action_text = "delete" if new_status == "Delete" else f"set to {new_status}"
        confirm = QMessageBox.question(self, "Confirm Batch Action", 
                                     f"Are you sure you want to {action_text} {len(ids_to_update)} requests?",
                                     QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes:
            return

        cnt = 0
        for rid in ids_to_update:
            if new_status == "Delete":
                query = "DELETE FROM reservations WHERE reservation_id = %s"
                params = (rid,)
            else:
                query = "UPDATE reservations SET current_status = %s WHERE reservation_id = %s"
                params = (new_status, rid)
                
            if self.db_manager.execute_query(query, params):
                 cnt += 1
        
        self.load_requests()
        # Reset header checkbox
        self.header_checkbox.setCheckState(Qt.Unchecked)
        QMessageBox.information(self, "Success", f"Successfully processed {cnt} request(s).")

    def open_context_menu(self, position):
        menu = QMenu()
        
        approve_action = QAction("Approve", self)
        reject_action = QAction("Reject", self) 
        cancel_action = QAction("Cancel", self)
        delete_action = QAction("Delete", self)
        view_action = QAction("View Details", self)
        edit_action = QAction("Edit", self)
        
        approve_action.triggered.connect(lambda: self.process_single_context("Approved"))
        reject_action.triggered.connect(lambda: self.process_single_context("Rejected"))
        cancel_action.triggered.connect(lambda: self.process_single_context("Cancelled"))
        delete_action.triggered.connect(lambda: self.process_single_context("Delete"))
        view_action.triggered.connect(self.view_details)
        edit_action.triggered.connect(self.edit_request)
        
        menu.addAction(view_action)
        menu.addAction(edit_action)
        menu.addSeparator()
        menu.addAction(approve_action)
        menu.addAction(reject_action)
        menu.addAction(cancel_action)
        menu.addSeparator()
        menu.addAction(delete_action)
        
        menu.exec_(self.table.viewport().mapToGlobal(position))

    def process_single_context(self, new_status):
        # Get selected row from context menu trigger
        row = self.table.currentRow()
        if row >= 0:
            res_id = self.table.item(row, 1).text()
            
            if new_status == "Delete":
                query = "DELETE FROM reservations WHERE reservation_id = %s"
                params = (res_id,)
            else:
                query = "UPDATE reservations SET current_status = %s WHERE reservation_id = %s"
                params = (new_status, res_id)

            if self.db_manager.execute_query(query, params):
                self.load_requests()

    def edit_request(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a reservation to edit.")
            return
        
        rid = self.table.item(row, 1).text()
        if AdminReservationEditDialog(self.db_manager, self.theme_handler.is_dark_mode, rid, self).exec():
            self.load_requests()
                
    def view_details(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a reservation to view details.")
            return

        rid = self.table.item(row, 1).text()
        
        query = """
            SELECT r.reservation_id, rm.room_name, r.room_id, r.full_name, r.course_section, 
                   r.reservation_type, r.start_time, r.created_at, 
                   r.activity_description, r.current_status
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.room_id
            WHERE r.reservation_id = %s
        """
        results = self.db_manager.fetch_all(query, (rid,))
        
        if results:
            res = results[0]
            from datetime import datetime
            created_at = res['created_at']
            if isinstance(created_at, datetime):
                created_at_str = created_at.strftime("%b %d, %Y %I:%M %p")
            elif isinstance(created_at, str):
                try:
                    dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                    created_at_str = dt.strftime("%b %d, %Y %I:%M %p")
                except ValueError:
                    created_at_str = created_at
            else:
                created_at_str = str(created_at)

            msg = (
                f"<b>Reservation ID:</b> {res['reservation_id']}<br>"
                f"<b>Student Name:</b> {res['full_name'] or 'N/A'}<br>"
                f"<b>Course & Section:</b> {res['course_section'] or 'N/A'}<br>"
                f"<b>Room:</b> {res['room_name']} (ID: {res['room_id']})<br>"
                f"<b>Type:</b> {res['reservation_type']}<br>"
                f"<b>Start Time:</b> {res['start_time']}<br>"
                f"<b>Time Created:</b> {created_at_str}<br>"
                f"<b>Status:</b> {res['current_status']}<br><br>"
                f"<b>Purpose:</b><br>{res['activity_description']}"
            )
            
            detail_box = QMessageBox(self)
            detail_box.setWindowTitle("Complete Reservation Details")
            detail_box.setTextFormat(Qt.RichText)
            detail_box.setText(msg)
            detail_box.setStandardButtons(QMessageBox.Ok)
            detail_box.exec()

class RoomDialog(QDialog):
    def __init__(self, db_manager, is_dark_mode, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Manage Rooms")
        self.setFixedSize(600, 500)
        
        if is_dark_mode:
            self.setStyleSheet("""
                QDialog { background-color: #1e1e1e; color: #FFFFFF !important; border: 1px solid #7B1818; }
                QLabel { color: #FFFFFF !important; font-weight: bold; font-size: 14px; }
                QLineEdit {
                    background-color: #2d2d2d;
                    border: 1px solid #7B1818;
                    border-radius: 5px;
                    color: #FFFFFF !important;
                    padding: 5px;
                    min-height: 35px;
                }
                QLineEdit::placeholder { color: #888888; }
                QTableWidget { background-color: #2d2d2d; color: #FFFFFF !important; border: 1px solid #7B1818; }
                QHeaderView::section { background-color: #7B1818; color: #FFFFFF !important; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background-color: #f5f5f5; color: #000000 !important; border: 1px solid #ccc; }
                QLabel { color: #000000 !important; font-weight: bold; font-size: 14px; }
                QLineEdit {
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    color: #000000 !important;
                    padding: 5px;
                    min-height: 35px;
                }
                QLineEdit::placeholder { color: #888888; }
                QTableWidget { background-color: #ffffff; color: #000000 !important; border: 1px solid #ccc; }
                QHeaderView::section { background-color: #7B1818; color: #FFFFFF !important; }
            """)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        self.setLayout(layout)
        
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        
        self.room_name = QLineEdit()
        self.room_name.setPlaceholderText("e.g. Computer Lab 1")
        
        self.capacity = QLineEdit()
        self.capacity.setPlaceholderText("e.g. 50")
        
        form_layout.addWidget(QLabel("Room Name:"), 0, 0)
        form_layout.addWidget(self.room_name, 0, 1)
        form_layout.addWidget(QLabel("Capacity:"), 1, 0)
        form_layout.addWidget(self.capacity, 1, 1)
        
        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Room")
        add_btn.setStyleSheet("background-color: #8BC34A; color: black; font-weight: bold; padding: 10px; border-radius: 5px;")
        add_btn.clicked.connect(self.add_room)
        
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)

        # Room List Section
        layout.addSpacing(20)
        layout.addWidget(QLabel("Existing Rooms:"))
        self.room_table = QTableWidget()
        self.room_table.setColumnCount(3)
        self.room_table.setHorizontalHeaderLabels(["Name", "Capacity", "Action"])
        self.room_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.room_table.verticalHeader().setVisible(False)
        self.room_table.verticalHeader().setDefaultSectionSize(45) # Set row height
        layout.addWidget(self.room_table)
        
        self.load_rooms()
        
        cancel_btn = QPushButton("Close")
        cancel_btn.setStyleSheet("background-color: #EF9A9A; color: black; font-weight: bold; padding: 10px; border-radius: 5px;")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

    def load_rooms(self):
        rooms = self.db_manager.fetch_all("SELECT * FROM rooms")
        self.room_table.setRowCount(len(rooms))
        for i, r in enumerate(rooms):
            self.room_table.setItem(i, 0, QTableWidgetItem(r['room_name']))
            self.room_table.setItem(i, 1, QTableWidgetItem(str(r['capacity'])))
            
            del_btn = QPushButton("Delete")
            del_btn.setStyleSheet("background-color: #FFCDD2; color: #D32F2F; font-weight: bold; padding: 2px;")
            del_btn.clicked.connect(lambda checked=False, rid=r['room_id']: self.delete_room(rid))
            self.room_table.setCellWidget(i, 2, del_btn)

    def delete_room(self, room_id):
        confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure? This will remove all reservations for this room.",
                                     QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            # First delete reservations to avoid foreign key issues
            self.db_manager.execute_query("DELETE FROM reservations WHERE room_id = %s", (room_id,))
            if self.db_manager.execute_query("DELETE FROM rooms WHERE room_id = %s", (room_id,)):
                self.load_rooms()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete room.")

    def add_room(self):
        name = self.room_name.text()
        capacity = self.capacity.text()
        
        if not name or not capacity:
            QMessageBox.warning(self, "Validation Error", "Please fill up all fields.")
            return
            
        try:
            cap = int(capacity)
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Capacity must be a number.")
            return

        query = "INSERT INTO rooms (room_name, capacity, is_active) VALUES (%s, %s, 1)"
        if self.db_manager.execute_query(query, (name, cap)):
            self.room_name.clear()
            self.capacity.clear()
            self.load_rooms()
        else:
            QMessageBox.critical(self, "Error", "Failed to add room.")

class AdminReservationEditDialog(QDialog):
    def __init__(self, db_manager, is_dark_mode, res_id, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.res_id = res_id
        self.setWindowTitle(f"Edit Reservation #{res_id}")
        self.setFixedSize(550, 700)
        
        if is_dark_mode:
            self.setStyleSheet("""
                QDialog { background-color: #1e1e1e; color: #FFFFFF !important; border: 1px solid #7B1818; }
                QLabel { color: #FFFFFF !important; font-weight: bold; font-size: 14px; }
                QLineEdit, QComboBox, QDateEdit, QTimeEdit {
                    background-color: #2d2d2d;
                    border: 1px solid #7B1818;
                    border-radius: 5px;
                    color: #FFFFFF !important;
                    padding: 5px;
                    min-height: 35px;
                }
                QLineEdit::placeholder { color: #888888; }
                QComboBox QAbstractItemView { background-color: #2d2d2d; color: #FFFFFF; selection-background-color: #7B1818; }
            """)
        else:
            self.setStyleSheet("""
                QDialog { background-color: #f5f5f5; color: #000000 !important; border: 1px solid #ccc; }
                QLabel { color: #000000 !important; font-weight: bold; font-size: 14px; }
                QLineEdit, QComboBox, QDateEdit, QTimeEdit {
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    color: #000000 !important;
                    padding: 5px;
                    min-height: 35px;
                }
                QLineEdit::placeholder { color: #888888; }
                QComboBox QAbstractItemView { background-color: #ffffff; color: #000000; selection-background-color: #ccc; }
            """)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        self.setLayout(layout)
        
        header = QLabel(f"Edit Reservation Details")
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
            self.room_combo.addItem(r['room_name'], r['room_id'])
        
        self.name_input = QLineEdit()
        self.course_input = QLineEdit()
        
        self.type_input = QComboBox()
        self.type_input.addItems(["Academic", "Event", "Formal/Formal Event", "Org Meeting", "Other"])
        
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        
        self.time_input = QTimeEdit()
        
        self.duration_input = QLineEdit()
        self.purpose_input = QLineEdit()
        self.purpose_input.setFixedHeight(50)
        
        labels = ["Select Room:", "Full Name:", "Course/Section:", 
                  "Reservation Type:", "Date:", "Time:", "Duration (hours):", "Purpose:"]
        widgets = [self.room_combo, self.name_input, self.course_input,
                   self.type_input, self.date_input, self.time_input, self.duration_input, self.purpose_input]
        
        for i, (lbl, widget) in enumerate(zip(labels, widgets)):
            form_layout.addWidget(QLabel(lbl), i, 0)
            form_layout.addWidget(widget, i, 1)

        layout.addLayout(form_layout)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet("background-color: #8BC34A; color: black; font-size: 16px; border-radius: 5px; padding: 10px; font-weight: bold;")
        save_btn.setFixedHeight(45)
        save_btn.clicked.connect(self.save_changes)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #EF9A9A; color: black; font-size: 16px; border-radius: 5px; padding: 10px; font-weight: bold;")
        cancel_btn.setFixedHeight(45)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.load_data()

    def load_data(self):
        results = self.db_manager.fetch_all("SELECT * FROM reservations WHERE reservation_id = %s", (self.res_id,))
        if results:
            res = results[0]
            for i in range(self.room_combo.count()):
                if self.room_combo.itemData(i) == res['room_id']:
                    self.room_combo.setCurrentIndex(i)
                    break
            
            self.name_input.setText(res['full_name'])
            self.course_input.setText(res['course_section'])
            
            idx = self.type_input.findText(res['reservation_type'])
            if idx >= 0: self.type_input.setCurrentIndex(idx)
            
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
                    
                    diff = end_dt - start_dt
                    hours = diff.total_seconds() / 3600
                    self.duration_input.setText(str(round(hours, 1)))

            self.purpose_input.setText(res.get('activity_description', ''))

    def save_changes(self):
        rid = self.room_combo.currentData()
        name = self.name_input.text()
        course = self.course_input.text()
        rtype = self.type_input.currentText()
        rdate = self.date_input.date().toString("yyyy-MM-dd")
        rtime = self.time_input.time().toString("HH:mm:ss")
        duration = self.duration_input.text()
        purpose = self.purpose_input.text()
        
        # Calculate end time
        from datetime import datetime, timedelta
        try:
            dur_hours = float(duration)
        except ValueError:
            dur_hours = 1.0
            
        start_dt_str = f"{rdate} {rtime}"
        start_dt = datetime.strptime(start_dt_str, "%Y-%m-%d %H:%M:%S")
        end_dt = start_dt + timedelta(hours=dur_hours)

        query = """
            UPDATE reservations 
            SET room_id=%s, full_name=%s, course_section=%s, reservation_type=%s, 
                start_time=%s, end_time=%s, activity_description=%s
            WHERE reservation_id=%s
        """
        params = (rid, name, course, rtype, start_dt, end_dt, purpose, self.res_id)
        
        if self.db_manager.execute_query(query, params):
            QMessageBox.information(self, "Success", "Reservation updated successfully.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to update reservation.")
