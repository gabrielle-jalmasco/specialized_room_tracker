create database if not exists specialized_room_tracker_backup;
use specialized_room_tracker_backup;

DROP DATABASE specialized_room_tracker_backup;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(225) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(100) NOT NULL
);

SELECT * FROM users;

CREATE TABLE IF NOT EXISTS rooms (
    ropom_id INT AUTO_INCREMENT PRIMARY KEY,
    room_name VARCHAR(255) NOT NULL,
    capacity INT NOT NULL,
    equipment_list TEXT,
    location VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS reservations (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    room_id INT NOT NULL,
    
    -- para sa student_dashboard.py (compatability)
    full_name VARCHAR(255),
    course_section VARCHAR(100),
    reservation_type VARCHAR(100),
    
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    activity_description LONGTEXT,
    current_status VARCHAR(100) DEFAULT 'Pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reservation_status_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    reservation_id INT NOT NULL,
    changed_by_user_id INT NOT NULL,
    old_status VARCHAR(100),
    new_status VARCHAR(100),
    rejection_reason MEDIUMTEXT,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reservation_id) REFERENCES reservations(reservation_id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by_user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    reservation_id INT NOT NULL,
    type VARCHAR(100),
    message_content MEDIUMTEXT,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (reservation_id) REFERENCES reservations(reservation_id) ON DELETE CASCADE
);