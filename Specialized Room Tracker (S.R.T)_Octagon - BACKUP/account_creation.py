# BACKEND CODE FOR AUTHORIZED STUDENT LEADER RECORD INSERTION
# CAN ONLY RUN ONCE TO AVOID DUPLICATE RECORDS UNLESS DATABASE IS RESET OR ADDED NEW PREDEFINED USERS
# BACKEND BY GAB


# REQUIREMENTS
import mysql.connector
import bcrypt

# IMPORT
from predefined_accounts import predefined_accounts

# DATABASE CONFIGURATION SETTINGS
database_host_address = "localhost"
database_user_login = "root"
database_user_password = "password"
database_port_number = "3306"
database_name_string = "specialized_room_tracker_backup"


# FUNCTION PARA MAGKAROON RECORDS IN DATABASE
def account_initiation():
    database_connection = mysql.connector.connect(
        host=database_host_address,
        user=database_user_login,
        password=database_user_password,
        port=database_port_number,
        database=database_name_string
    )

    # CHECK IF CONNECTION IS SUCCESSFUL
    if database_connection.is_connected():
        database_execution = database_connection.cursor()

        print("-"*30)
        print("Successfully connected to database! Processsing predefined accounts...")

        # LOOP THROUGH LIST DICTIONARY
        for persons in predefined_accounts:
            account_username = persons["username"]
            account_email = persons["user_email"]
            account_plain_password = persons["password"]
            account_role = persons["user_role"] 

            # Hashing logic
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(account_plain_password.encode('utf-8'), salt)

            search_query = "SELECT user_id FROM users WHERE email = %s"
            search_data = (account_email,) 
            database_execution.execute(search_query, search_data)
            existing_record_found = database_execution.fetchone()

            if existing_record_found is not None:
                update_sql_command = "UPDATE users SET username = %s, password_hash = %s, role = %s WHERE email = %s"
                update_values = (account_username, hashed_password, account_role, account_email)
                database_execution.execute(update_sql_command, update_values)
            else:
                insert_sql_command = "INSERT INTO users (username, password_hash, email, role) VALUES (%s, %s, %s, %s)"
                insert_values = (account_username, hashed_password, account_email, account_role)
                database_execution.execute(insert_sql_command, insert_values)
            
            database_connection.commit()

        print("-"*30)
        print("ALL ACCOUNTS PROCESSED SUCCESSFULLY.")
        print("-"*30)
        database_execution.close()
        database_connection.close()
        

    else:
        print("Error: Could not reach database server.")


# LOGGING TERMINAL
for person in predefined_accounts:
    print("-"*30)
    print(f"ID: {person['user_id']}")
    print(f"ROLE: {person['user_role']}")
    print(f"USERNAME: {person['username']}")
    print(f"PASSWORD: {person['password']}")
    print(f"Hashed Password: {bcrypt.hashpw(person['password'].encode('utf-8'), bcrypt.gensalt())}")
    print(f"EMAIL: {person['user_email']}")
    print("-"*30)   

account_initiation()