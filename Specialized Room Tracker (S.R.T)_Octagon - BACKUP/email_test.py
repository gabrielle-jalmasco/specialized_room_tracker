import smtplib
from email.mime.text import MIMEText
import user_email_list
import os

def send_real_email(recipient_email_address_string, email_subject_string, email_body_content_string):
    sender_email_address_string = "jalmascogab002@gmail.com" # SIMULATED ADMIN EMAIL
    sender_app_password_string = "amdw ocfr corr mkvj" # Google App Password, not login password

    email_message_object = MIMEText(email_body_content_string)
    email_message_object['Subject'] = email_subject_string
    email_message_object['From'] = sender_email_address_string
    email_message_object['To'] = recipient_email_address_string

    smtp_server_connection = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    
    smtp_server_connection.login(sender_email_address_string, sender_app_password_string)
    
    smtp_server_connection.send_message(email_message_object)
    
    smtp_server_connection.quit()
    
    return True

if __name__ == "__main__":
    print("System: Checking internet connectivity...")
    
    ping_result_code = os.system("ping -n 1 smtp.gmail.com > nul")
    
    if ping_result_code != 0:
        print("Error: Unable to connect to the email server.")
        print("Please check your internet connection and try again.")
    else:
        print("System: Internet connection confirmed. Sending emails...")
        
        for current_email_address_string in user_email_list.list_of_active_user_email_addresses:
            
            print("Attempting to send test email to " + current_email_address_string + "...")
            
            send_real_email(current_email_address_string, "SRT System Test", "This is a test email from the Specialized Room Tracker system.")
            
            print("Test Passed: Email sent successfully to " + current_email_address_string)
