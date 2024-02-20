import json
import requests
from bs4 import BeautifulSoup
import smtplib
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime


def load_products_from_json(json_file):
    try:
        with open(json_file, "r") as file:
            products = json.load(file)
    except FileNotFoundError:
        products = []  # Dosya bulunamazsa boş bir liste oluştur
        # JSON dosyasını oluştur
        with open(json_file, "w") as file:
            json.dump(products, file)

    return products


def save_products_to_json(json_file, products):
    with open(json_file, "w") as file:
        json.dump(products, file, indent=4)


def add_product_and_close(window, products):
    try:
        link = link_entry.get()
        target_price = float(target_price_entry.get())
    except ValueError:
        messagebox.showinfo("Hata", "Geçerli bir hedef fiyat girin!")
        return
    if link and target_price:
        products.append({"URL": link, "target_price": target_price})
        save_products_to_json("products.json", products)
        messagebox.showinfo("Bilgi", "Ürün başarıyla eklendi.")
        window.destroy()
    elif not link and target_price:
        messagebox.showerror("Hata", "Link giriniz!")


def open_add_product_window(products):
    add_product_window = tk.Toplevel()
    add_product_window.title("Ürün Ekle")
    add_product_window.geometry("300x300+800+300")

    link_label = tk.Label(add_product_window, text="Ürün Linki:")
    link_label.pack(pady=5)

    global link_entry
    link_entry = tk.Entry(add_product_window)
    link_entry.pack(pady=5)

    target_price_label = tk.Label(add_product_window, text="Hedef Fiyat:")
    target_price_label.pack(pady=5)

    global target_price_entry
    target_price_entry = tk.Entry(add_product_window)
    target_price_entry.pack(pady=5)

    add_button = tk.Button(
        add_product_window,
        text="Ürünü Ekle",
        command=lambda: add_product_and_close(add_product_window, products),
    )
    add_button.pack(pady=5)


def check_prices(products):
    email_body = ""
    max_title_length = 0
    current_prices = {}
    for product in products:
        URL = product["URL"]
        target_price = product["target_price"]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.1"
        }
        page = requests.get(URL, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")

        title = soup.find("span", id="productTitle")
        if title:
            title = title.get_text().strip()
            max_title_length = max(max_title_length, len(title))
        else:
            title = "Title not found"

        price_tag = soup.find("span", class_="a-offscreen")
        if price_tag:
            price_text = price_tag.get_text()
            price_text = price_text.split(",")[0]
            price = float(price_text.replace("TL", "").replace(".", "").strip())
        else:
            price = None  # Fiyat bilgisi alınamadığında None olarak ayarla

        current_prices[title] = price

        if price is not None and target_price and price <= float(target_price):
            email_body += f"{title} Şimdi {price}₺\nLinki Kontrol Et: {URL}\n\n"

    if email_body:
        send_mail(email_body)

    # JSON'a güncel fiyatları kaydet
    with open("newProducts.json", "w") as file:
        json.dump(current_prices, file, indent=4)


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

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("melihtop35@gmail.com", "rozt ruln uywl smnx")

    subject = "Fiyat Düştü!"
    msg = f"Subject: {subject}\n\n{body}"
    msg = msg.encode("utf-8")

    server.sendmail("melihtop35@gmail.com", "melihtop35@gmail.com", msg)
    messagebox.showinfo("Bilgilendirme", "E-Posta Gönderildi!")
    server.quit()


def on_check_button_click(products):
    check_prices(products)


def show_current_prices(products):
    current_prices_window = tk.Toplevel()
    current_prices_window.title("Güncel Fiyatlar")
    current_prices_window.geometry(
        "+300+300"
    )  # Pencerenin konumunu (300, 300) olarak ayarlar

    current_prices = {}
    for product in products:
        URL = product["URL"]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.1"
        }
        page = requests.get(URL, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")

        title = soup.find("span", id="productTitle")
        if title:
            title = title.get_text().strip()
        else:
            title = "Title not found"

        price_tag = soup.find("span", class_="a-offscreen")
        if price_tag:
            price_text = price_tag.get_text()
            price_text = price_text.split(",")[0]
            price = float(price_text.replace("TL", "").replace(".", "").strip())
        else:
            price = "Fiyat bilgisi bulunamadı."

        # Güncel fiyatlar listesine ekle
        current_prices[title] = price

        label_text = f"{title} - {price}₺"
        tk.Label(current_prices_window, text=label_text, font=("Arial", 10)).pack(
            pady=5, padx=5
        )

        # Altına çizgi ekle
        tk.Frame(current_prices_window, height=1, bg="black").pack(fill="x")

    # Zamanı kaydet ve JSON dosyasına yaz
    current_prices["saved_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("newProducts.json", "w") as file:
        json.dump(current_prices, file, indent=4)

    # Eğer newProducts.json dosyası yoksa, boş bir sözlük oluşturarak başlayalım
    try:
        with open("newProducts.json", "r") as file:
            pass  # Dosya zaten var, bu yüzden bir şey yapmamıza gerek yok
    except FileNotFoundError:
        with open("newProducts.json", "w") as file:
            json.dump({}, file)


def show_saved_products(root):
    saved_prices_frame = tk.Frame(root)
    saved_prices_frame.pack(pady=10)

    try:
        with open("newProducts.json", "r") as file:
            saved_data = json.load(file)
            if isinstance(saved_data, dict):
                current_prices = saved_data
                # saved_time öğesini al
                saved_time = current_prices.get("saved_time")
            else:
                # Eğer saved_data bir liste ise, ilk öğeyi al ve saved_time öğesini al
                current_prices = saved_data[0]
                saved_time = current_prices.get("saved_time")
    except FileNotFoundError:
        current_prices = {}
        saved_time = None  # Dosya bulunamazsa veya içeriği yüklenemezse saved_time None olarak ayarlanır

    for product, price in current_prices.items():
        if product != "saved_time":
            label_text = f"{product} - {price}₺"
            tk.Label(saved_prices_frame, text=label_text, font=("Arial", 10)).pack(
                pady=5, padx=5
            )
            # Altına çizgi ekle
            tk.Frame(saved_prices_frame, height=1, bg="black").pack(fill="x")

    # Zaman etiketi ekle
    if saved_time:
        time_label = tk.Label(
            saved_prices_frame,
            text=f"Kaydedilme Zamanı: {saved_time}",
            font=("Arial", 10),
        )
        time_label.pack(pady=10)


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


# Tkinter uygulamasını oluşturma
root = tk.Tk()
root.configure(bg="lightgray")
root.title("Fiyat Kontrol Programı")
root.geometry("+300+300")

# Buton oluşturma
button_font = ("Arial", 10)
button_width = 20
button_pad_y = 5

add_product_button = tk.Button(
    root,
    text="Ürün Ekle",
    command=lambda: open_add_product_window(products),
    font=button_font,
    width=button_width,
)
add_product_button.pack(pady=(60, button_pad_y))

check_button = tk.Button(
    root,
    text="Kontrol Et",
    command=lambda: on_check_button_click(products),
    font=button_font,
    width=button_width,
)
check_button.pack(pady=button_pad_y)

show_current_prices_button = tk.Button(
    root,
    text="Güncel Fiyatları Göster",
    command=lambda: show_current_prices(products),
    font=button_font,
    width=button_width,
)
show_current_prices_button.pack(pady=button_pad_y)

# Kayıtlı ürünleri göster
show_saved_products(root)

# JSON dosyasından ürünleri yükle
products = load_products_from_json("products.json")

# E-posta değiştirme butonu
change_email_button = tk.Button(
    root,
    text="E-Posta Ekle",
    command=add_email,
    font=button_font,
    width=button_width,
)
change_email_button.pack(pady=button_pad_y)

# Pencereyi gösterme
root.mainloop()
