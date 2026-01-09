# REQUIREMENT
import mysql.connector
import bcrypt

# DATABASE CONFIGURATION
database_host_address = "localhost"
database_user_login = "root"
database_user_password = "password"
database_port_number = "3306"
database_name = "specialized_room_tracker_backup"

# CHECK IF EMAIL, PASSWORD MATCH RECORD IN DATABASE
def verify_user_credentials(input_email_address, input_plain_password):
    database_connection_link = mysql.connector.connect(
        host=database_host_address,
        user=database_user_login,
        password=database_user_password,
        port=database_port_number,
        database=database_name
    )

    if database_connection_link.is_connected():
        database_execution_cursor = database_connection_link.cursor()

        # INTERACT WITH DATABASE (HAHANAPIN MGA USERS)
        search_query_string = "SELECT password_hash, role, username, user_id FROM users WHERE email = %s"        
        search_data_tuple = (input_email_address,)
        database_execution_cursor.execute(search_query_string, search_data_tuple)

        found_user_record = database_execution_cursor.fetchone()

        if found_user_record is not None:
            stored_password_hash = found_user_record[0]
            user_role_from_db = found_user_record[1]
            user_name_from_db = found_user_record[2]
            user_id_from_db = found_user_record[3]
            
            if isinstance(stored_password_hash, str):
                stored_password_hash = stored_password_hash.encode('utf-8')

            input_password_as_bytes = input_plain_password.encode('utf-8')

            # bcrypt to check password
            is_password_correct = bcrypt.checkpw(input_password_as_bytes, stored_password_hash)

            if is_password_correct == True:
                database_execution_cursor.close()
                database_connection_link.close()
                return ["SUCCESS", user_role_from_db, user_name_from_db, user_id_from_db]
            else:
                database_execution_cursor.close()
                database_connection_link.close()
                return ["FAILED", "Incorrect password."] 
        
        else:
            database_execution_cursor.close()
            database_connection_link.close()
            return ["FAILED", "No account found."]
            
    else:
        return ["ERROR", "Could not connect to the database server."]