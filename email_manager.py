import json
import smtplib
from tkinter import messagebox, simpledialog

def get_receiver_email():
    try:
        with open("email.json", "r") as file:
            data = json.load(file)
            if isinstance(data, dict):
                # Veri bir sözlükse, 'receiver_email' öğesini al
                receiver_email = data.get("email")
            else:
                # Veri bir liste veya başka bir tipse, varsayılan olarak None döndür
                messagebox.showinfo("Hata", "Listi sikm")
    except FileNotFoundError:
        # Dosya bulunamazsa veya içeriği yüklenemezse, varsayılan olarak None döndür
        messagebox.showinfo("Hata", "E_Posta Boş!")

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
    server.login(sender_email, "piia zxxu wctr xczn")  # Gönderenin e-posta hesabının şifresi

    subject = "Fiyat Düştü!"
    msg = f"From: {sender_name}\nSubject: {subject}\n\n{body}"
    msg = msg.encode("utf-8")

    server.sendmail(sender_email, receiver_email, msg)
    messagebox.showinfo("Bilgilendirme", "E-Posta Gönderildi!")
    server.quit()

def add_email():
    try:
        with open("email.json", "r") as file:
            data = json.load(file)
            if "email" in data:
                # E-posta adresi zaten var, değiştirmek için iste
                current_email = data["email"]
                change_email = messagebox.askyesno(
                    "E-Posta Değiştir",
                    f"Mevcut E-Posta Adresiniz: {current_email}\nE-posta adresinizi değiştirmek ister misiniz?",
                )
                if change_email:
                    new_email = simpledialog.askstring(
                        "E-Posta Değiştir", "Yeni E-Posta Adresi:"
                    )
                    if new_email:
                        data["email"] = new_email
                        with open("email.json", "w") as file:
                            json.dump(data, file)
                        messagebox.showinfo("Bilgi", "E-Posta başarıyla değiştirildi.")
            else:
                # email.json dosyası var ama içinde e-posta yok, e-posta ekle
                new_email = simpledialog.askstring("E-Posta Ekle", "E-Posta Adresi:")
                if new_email:
                    with open("email.json", "w") as file:
                        json.dump({"email": new_email}, file)
                    messagebox.showinfo("Bilgi", "E-Posta başarıyla eklendi.")
    except FileNotFoundError:
        # email.json dosyası yok, e-posta eklemek için oluştur
        new_email = simpledialog.askstring("E-Posta Ekle", "E-Posta Adresi:")
        if new_email:
            with open("email.json", "w") as file:
                json.dump({"email": new_email}, file)
            messagebox.showinfo("Bilgi", "E-Posta başarıyla eklendi.")
