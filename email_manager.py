import json
import smtplib
from tkinter import messagebox, simpledialog
from settings import get_language_data


def get_receiver_email():
    try:
        with open("jsons/email.json", "r") as file:
            data = json.load(file)
            if isinstance(data, dict):
                # Veri bir sözlükse, 'receiver_email' öğesini al
                receiver_email = data.get("email")
            else:
                # Veri bir liste veya başka bir tipse, varsayılan olarak None döndür
                messagebox.showinfo(
                    get_language_data("error"), get_language_data("format_error")
                )
    except FileNotFoundError:
        # Dosya bulunamazsa veya içeriği yüklenemezse, varsayılan olarak None döndür
        messagebox.showinfo(
            get_language_data("error"), get_language_data("empty_email")
        )

    return receiver_email


def send_mail(body):
    receiver_email = get_receiver_email()
    if not receiver_email:
        return

    sender_email = "ptracker587@gmail.com"  # Gönderenin e-posta adresi
    sender_name = "Price Tracker"  # Gönderenin adı

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(
        sender_email, "piia zxxu wctr xczn"
    )  # Gönderenin e-posta hesabının şifresi

    subject = get_language_data("subject")
    msg = f"From: {sender_name}\nSubject: {subject}\n\n{body}"
    msg = msg.encode("utf-8")

    server.sendmail(sender_email, receiver_email, msg)
    server.quit(
        get_language_data("mbox_info_success1"), get_language_data("mbox_email_send")
    )
    messagebox.showinfo()


def add_email():
    try:
        with open("jsons/email.json", "r") as file:
            data = json.load(file)
            if "email" in data:
                # E-posta adresi zaten var, değiştirmek için iste
                current_email = data["email"]
                change_email = messagebox.askyesno(
                    get_language_data("change_email"),
                    get_language_data("mbox_message_first")
                    + current_email
                    + get_language_data("mbox_message_second"),
                )
                if change_email:
                    new_email = simpledialog.askstring(
                        get_language_data("change_email"),
                        get_language_data("new_email"),
                    )
                    if new_email:
                        data["email"] = new_email
                        with open("jsons/email.json", "w") as file:
                            json.dump(data, file)
                        messagebox.showinfo(
                            get_language_data("mbox_info_success1"),
                            get_language_data("mbox_info_message"),
                        )
            else:
                # email.json dosyası var ama içinde e-posta yok, e-posta ekle
                new_email = simpledialog.askstring(
                    get_language_data("simple_dialog_askstring1"),
                    get_language_data("simple_dialog_askstring2"),
                )
                if new_email:
                    with open("jsons/email.json", "w") as file:
                        json.dump({"email": new_email}, file)
                    messagebox.showinfo(
                        get_language_data("mbox_info_success1"),
                        get_language_data("mbox_info_success2"),
                    )
    except FileNotFoundError:
        # email.json dosyası yok, e-posta eklemek için oluştur
        new_email = simpledialog.askstring(
            get_language_data("simple_dialog_askstring1"),
            get_language_data("simple_dialog_askstring2"),
        )
        if new_email:
            with open("jsons/email.json", "w") as file:
                json.dump({"email": new_email}, file)
            messagebox.showinfo(get_language_data("mbox_info_success"))
