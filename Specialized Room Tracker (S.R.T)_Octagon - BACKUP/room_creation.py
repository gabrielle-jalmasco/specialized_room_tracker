# BACKEND CODE FOR ROOM DATA INITIALIZATION

import mysql.connector
from specialized_room_list import special_room_list

# DATABASE CONFIGURATION
database_host_address = "localhost"
database_user_login = "root"
database_user_password = "password"
database_port_number = "3306"
database_name_identity = "specialized_room_tracker_backup"

def room_initialization_process():
    database_connection_link = mysql.connector.connect(
        host=database_host_address,
        user=database_user_login,
        password=database_user_password,
        port=database_port_number,
        database=database_name_identity
    )

    if database_connection_link.is_connected():
        database_command_cursor = database_connection_link.cursor()
        
        print("-" * 50)
        print("Starting Room Table Initialization...")

        for current_room_data_list in special_room_list:
            
            target_room_name_string = current_room_data_list[0]
            target_room_location_string = current_room_data_list[1]
            default_room_capacity_integer = 40 

            check_query_string = "SELECT room_id FROM rooms WHERE room_name = %s"
            check_data_tuple = (target_room_name_string,)
            database_command_cursor.execute(check_query_string, check_data_tuple)
            
            existing_room_record = database_command_cursor.fetchone()

            if existing_room_record is not None:
                print("Updating location for: " + target_room_name_string)
                update_query_string = "UPDATE rooms SET location = %s WHERE room_name = %s"
                update_data_values = (target_room_location_string, target_room_name_string)
                database_command_cursor.execute(update_query_string, update_data_values)
            else:
                print("Inserting new room: " + target_room_name_string)
                insert_query_string = "INSERT INTO rooms (room_name, capacity, location) VALUES (%s, %s, %s)"
                insert_data_values = (target_room_name_string, default_room_capacity_integer, target_room_location_string)
                database_command_cursor.execute(insert_query_string, insert_data_values)

            database_connection_link.commit()

        print("-" * 50)
        print("ROOM INITIALIZATION COMPLETED SUCCESSFULLY.")
        
        database_command_cursor.close()
        database_connection_link.close()
    else:
        print("Error: Could not connect to the database to initialize rooms.")

room_initialization_process()