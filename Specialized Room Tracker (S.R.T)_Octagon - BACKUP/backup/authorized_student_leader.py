# BACKEND - GAB
# THIS CAN ONLY BE RUN ONCE! WAG NA GALAWIN!
# THIS IS IN ORDER TO HAVE A RECORD IN THE DATABASE!

import mysql.connector
import bcrypt

# DATABASE CONFIGURATION
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'port': '3306',
    'database': 'specialized_room_tracker_backup'
}

def create_authorized_leader():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # USER DETAILS
        email = "president@pup.edu.ph" # EMAIL TO LOG IN / TODO: UPDATE EMAIL TO @iskolarngbayan.pup.edu.ph
        username = "president_gab"
        plain_pw = "presidentpass123" # PASSWORD TO LOG IN
        role = "Classroom President"

        # HASHING PASSWORD BCRYPT
        hashed_pw = bcrypt.hashpw(plain_pw.encode('utf-8'), bcrypt.gensalt())


        # INSERT IN DATABASE ACCOUNT
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            print(f"User {email} exists. Updating password...")
            sql = "UPDATE users SET user_password = %s, password_hash = %s WHERE email = %s"
            cursor.execute(sql, (hashed_pw, hashed_pw, email))
        else:
            print(f"Creating new user {email}...")
            sql = "INSERT INTO users (username, user_password, password_hash, email, role) VALUES (%s, %s, %s, %s, %s)" # %s ->  FORMATTER
            cursor.execute(sql, (username, hashed_pw, hashed_pw, email, role))

        # ACCEPT CHANGES IN THE DATABASE
        connection.commit()

        # LOGGING CONNECTION
        print("="*50)
        print("Account Ready.")
        print(f"Email: {email}")
        print(f"Password: {plain_pw}")
        print(f"Role: {role}")
        print("="*50)

        # END CONNECTION
        connection.close()
    
    # ERROR HANDLING (INCASE HINDI PA NAGAWA ANG DATABASE)
    except mysql.connector.Error as error:
        print(f"Database Error: {error}")
    
    finally:
        # END CONNECTION
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_authorized_leader()