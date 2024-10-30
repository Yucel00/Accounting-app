import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
from tkinter import messagebox

"""'-----------------------------------------------Mail Islemleri-----------------------------------------------------------"""
MY_EMAIL = "your_emaıl" 
PASSWORD = 'your_password'
SMTP_SERVER = "smtp.gmail.com"
PORT = 587
RECIPIENT = "reciving_mail"
SUBJECT = "Deneme E-postası"
BODY = "Bu, threading kullanarak gönderilen bir deneme e-postasıdır."


def send_email(recipient_email, subject, body):
    try:
        sender_email = MY_EMAIL
        sender_password = PASSWORD

        # E-posta oluşturma
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # E-postayı HTML formatında ayarla
        msg.attach(MIMEText(body, 'html'))

        # SMTP Sunucusuna Bağlanma ve E-postayı Gönderme
        with smtplib.SMTP(SMTP_SERVER, PORT) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        # Başarı mesajı göster
        messagebox.showinfo("Başarı", f"E-posta başarıyla gönderildi.")

    except Exception as e:
        # Hata mesajı göster
        messagebox.showerror("Hata", f"E-posta gönderilirken bir hata oluştu: {e}")

def send_email_in_thread( recipient_email, subject, body):
    threading.Thread(target=send_email, args=(recipient_email, subject, body), daemon=True).start()
