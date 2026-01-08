import mysql.connector

# DATABASE CONFIG
database_host_address = "localhost"
database_user_login = "root"
database_user_password = "password"
database_port_number = "3306"
database_name_string = "specialized_room_tracker_backup"

def database_connection():
    connection_link = mysql.connector.connect(
        host=database_host_address,
        user=database_user_login,
        password=database_user_password,
        port=database_port_number,
        database=database_name_string
    )
    return connection_link

def fetch_all(sql_query_string, parameters_tuple=()):
    database_connection_link = database_connection()
    database_cursor_tool = database_connection_link.cursor(dictionary=True)
    
    database_cursor_tool.execute(sql_query_string, parameters_tuple)
    
    all_rows_list = []
    if database_cursor_tool.description is not None:
        all_rows_list = database_cursor_tool.fetchall()

    database_cursor_tool.close()
    database_connection_link.close()
    return all_rows_list

def execute_query(sql_query, parameters=()):
    database_link = database_connection()
    database_execution = database_link.cursor()

    database_execution.execute(sql_query, parameters)
    database_link.commit()

    success = False # flag
    if database_execution.rowcount > 0:
        success = True

    database_execution.close()
    database_link.close()
    return success