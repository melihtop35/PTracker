import json
import requests
from bs4 import BeautifulSoup
import smtplib
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime


# Ürünleri JSON dosyasından yükleme
def load_products_from_json(json_file):
    try:
        with open(json_file, "r") as file:
            products = json.load(file)
    except FileNotFoundError:
        products = []
        with open(json_file, "w") as file:
            json.dump(products, file)

    return products


# Ürünleri JSON dosyasına kaydetme
def save_products_to_json(json_file, products):
    with open(json_file, "w") as file:
        json.dump(products, file, indent=4)


# Ürün ekleme penceresini açma
def open_add_product_window(products):
    add_product_window = tk.Toplevel()
    add_product_window.title("Ürün Ekle")
    add_product_window.geometry("300x300+800+300")

    link_label = tk.Label(add_product_window, text="Ürün Linki:")
    link_label.pack(pady=5)

    global link_entry
    link_entry = tk.Entry(add_product_window)
    link_entry.pack(pady=5)

    name_label = tk.Label(add_product_window, text="Ürün Adı:")
    name_label.pack(pady=5)

    global name_entry
    name_entry = tk.Entry(add_product_window)
    name_entry.pack(pady=5)

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


# Ürün ekleme ve pencereyi kapatma
def add_product_and_close(window, products):
    try:
        link = link_entry.get()
        name = name_entry.get()
        target_price = float(target_price_entry.get())
    except ValueError:
        messagebox.showinfo("Hata", "Geçerli bir hedef fiyat girin!")
        return
    if link and name and target_price:
        products.append({"name": name, "URL": link, "target_price": target_price})
        save_products_to_json("products.json", products)
        messagebox.showinfo("Bilgi", "Ürün başarıyla eklendi.")
        window.destroy()
    elif not link and name and target_price:
        messagebox.showerror("Hata", "Link giriniz!")
    elif link and not name and target_price:
        messagebox.showerror("Hata", "Ad giriniz!")
    elif link and name and not target_price:
        messagebox.showerror("Hata", "Hedef fiyat giriniz!")


# Ürünleri düzenleme penceresini açma
def open_edit_products_window(products):
    def delete_product(index):
        # İlgili ürünü listeden ve JSON dosyasından kaldır
        del products[index]
        save_products_to_json("products.json", products)  # JSON dosyasını güncelle
        # Güncellenmiş ürün listesiyle pencereyi tekrar aç
        edit_products_window.destroy()
        open_edit_products_window(products)

    def save_products_to_json(json_file, products):
        with open(json_file, "w") as file:
            json.dump(products, file, indent=4)

    edit_products_window = tk.Toplevel()
    edit_products_window.title("Ürünleri Düzenle")
    edit_products_window.geometry("900x400+400+300")

    # Scrollbar için frame oluştur
    scroll_frame = tk.Frame(edit_products_window)
    scroll_frame.pack(fill="both", expand=True)

    # Scrollbar oluştur
    scrollbar = tk.Scrollbar(scroll_frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")

    # Editlenecek ürünlerin listesini göstermek için bir frame oluştur
    products_frame = tk.Frame(scroll_frame)
    products_frame.pack(fill="both", expand=True)

    # Canvas oluştur
    canvas = tk.Canvas(products_frame, yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)

    # Ürün listesine scroll bar bağla
    products_frame.bind(
        "<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all"))
    )
    scrollbar.config(command=canvas.yview)

    # Ürünler listesini canvas içine yerleştir
    inner_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    # Her bir ürün için gerekli giriş kutularını oluştur
    for i, product in enumerate(products):
        # Label
        tk.Label(inner_frame, text=f"Ürün {i+1}").grid(row=i, column=0, padx=5, pady=5)

        # Ad
        tk.Label(inner_frame, text="Adı:").grid(row=i, column=1, padx=5, pady=5)
        name_entry = tk.Entry(inner_frame, width=40)
        name_entry.insert(0, product.get("name", ""))
        name_entry.grid(row=i, column=2, padx=5, pady=5)

        # Link
        tk.Label(inner_frame, text="Linki:").grid(row=i, column=3, padx=5, pady=5)
        link_entry = tk.Entry(inner_frame, width=40)
        link_entry.insert(0, product.get("URL", ""))
        link_entry.grid(row=i, column=4, padx=5, pady=5)

        # Hedef Fiyat
        tk.Label(inner_frame, text="Hedef Fiyat:").grid(row=i, column=5, padx=5, pady=5)
        target_price_entry = tk.Entry(inner_frame, width=10)
        target_price_entry.insert(0, str(product.get("target_price", "")))
        target_price_entry.grid(row=i, column=6, padx=5, pady=5)

        # Sil düğmesi
        delete_button = tk.Button(
            inner_frame,
            text="Sil",
            command=lambda index=i: delete_product(index),
            width=5,
        )
        delete_button.grid(row=i, column=7, padx=5, pady=5)

    # Güncelleme düğmesi
    update_button = tk.Button(
        edit_products_window,
        text="Ürünleri Güncelle",
        command=lambda: update_products(products, inner_frame, edit_products_window),
    )
    update_button.pack(pady=10)

    # Canvas'ı scroll bar ile bağla
    canvas.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    # Diğer işlemleri engelle
    edit_products_window.transient(root)
    edit_products_window.grab_set()
    root.wait_window(edit_products_window)

# Ürünleri güncelleme
def update_products(products, inner_frame, edit_products_window):
    for i, product in enumerate(products):
        name_entry = inner_frame.grid_slaves(row=i, column=2)[0]
        link_entry = inner_frame.grid_slaves(row=i, column=4)[0]
        target_price_entry = inner_frame.grid_slaves(row=i, column=6)[0]

        name = name_entry.get()
        link = link_entry.get()
        target_price = target_price_entry.get()

        if name and link and target_price:
            products[i]["name"] = name
            products[i]["URL"] = link
            products[i]["target_price"] = float(target_price)
        else:
            messagebox.showerror("Hata", "Tüm alanları doldurun.")
            return

    save_products_to_json("products.json", products)
    messagebox.showinfo("Bilgi", "Ürünler başarıyla güncellendi.")
    edit_products_window.destroy()  # Sekmeyi kapat


#
def amazon_product_info(URL):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.1"
    }
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    title = soup.find("span", id="productTitle")
    if title:
        title = title.get_text().strip()
    else:
        title = "Ürün Bulunamadı"

    price_tag = soup.find("span", class_="a-offscreen")
    if price_tag:
        price_text = price_tag.get_text()
        price_text = price_text.split(",")[0]
        price = float(price_text.replace("TL", "").replace(".", "").strip())
    else:
        price = None

    return title, price


def akakce_product_info(URL):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.1"
    }
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    title = soup.find("div", class_="pdt_v8")
    if title:
        title = title.get_text().strip()
    else:
        title = "Ürün Bulunamadı"

    price_tag = soup.find("span", class_="pt_v8")
    if price_tag:
        price_text = price_tag.get_text()
        price_text = price_text.split(",")[0]
        price = float(price_text.replace("TL", "").replace(".", "").strip())
    else:
        price = None

    return title, price


def hepsiburada_product_info(URL):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.1"
    }
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")

    title_tag = soup.find("h1", class_="product-name")
    if title_tag:
        title = title_tag.get_text().strip()
    else:
        title = "Ürün Bulunamadı"

    price_tag = soup.find("span", {"data-bind": "markupText:'currentPriceBeforePoint'"})
    if price_tag:
        price_text = price_tag.get_text()
        price_text = price_text.split(",")[0]
        price = float(price_text.strip())
    else:
        price = None

    return title, price


def trendyol_product_info(URL):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.1"
    }
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    title = soup.find("h1", class_="zLHJIGKJ")
    if title:
        title = title.get_text().strip()
    else:
        title = "Ürün Bulunamadı"

    price_tag = soup.find("span", class_="FteoagkF")
    if price_tag:
        price_text = price_tag.get_text()
        price_text = price_text.split(",")[0]
        price = float(price_text.replace("TL", "").replace(".", "").strip())
    else:
        price = None

    return title, price


def letgo_product_info(URL):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.1"
    }
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")

    title_tag = soup.find("h1", class_="_1hJph")
    if title_tag:
        title = title_tag.get_text().strip()
    else:
        title = "Ürün Bulunamadı"

    price_tag = soup.find("span", class_="T8y-z")
    if price_tag:
        price_text = price_tag.get_text()
        price_text = price_text.split(",")[0]
        price = float(price_text.replace("TL", "").replace(".", "").strip())
    else:
        price = None

    return title, price


def check_prices(products):
    email_body = ""
    current_prices = {}
    for product in products:
        URL = product["URL"]
        target_price = product["target_price"]

        # URL'ye göre doğru işlevi çağır
        if "amazon" in URL:
            title, price = amazon_product_info(URL)
        elif "hepsiburada" in URL:
            title, price = hepsiburada_product_info(URL)
        elif "trendyol" in URL:
            title, price = trendyol_product_info(URL)
        elif "akakce" in URL:
            title, price = akakce_product_info(URL)
        elif "letgo" in URL:
            title, price = letgo_product_info(URL)
        else:
            title, price = "Bilinmeyen Ürün", 0

        current_prices[title] = price

        if price is not None and target_price and price <= float(target_price):
            # Hedef fiyatın altında olduğu bilgisini ekleyelim
            price_difference = float(target_price) - price
            email_body += f"{title} Şimdi {price}₺ ({target_price}₺'nin %.2f TL altında)\nLinki Kontrol Et: {URL}\n\n" % price_difference

    if email_body:
        send_mail(email_body)

    with open("newProducts.json", "w") as file:
        json.dump(current_prices, file, indent=4)



#
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

    sender_email = "gönderen@gmail.com"  # Gönderenin e-posta adresi
    sender_name = "Price Tracker"  # Gönderenin adı

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(sender_email, "sifre")  # Gönderenin e-posta hesabının şifresi

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


def show_current_prices(products):
    current_prices_window = tk.Toplevel()
    current_prices_window.title("Güncel Fiyatlar")
    current_prices_window.geometry(
        "+300+300"
    )  # Pencerenin konumunu (300, 300) olarak ayarlar

    current_prices = {}
    for product in products:
        URL = product["URL"]
        # URL'ye göre doğru işlevi çağır
        if "amazon" in URL:
            title, price = amazon_product_info(URL)
        elif "hepsiburada" in URL:
            title, price = hepsiburada_product_info(URL)
        elif "trendyol" in URL:
            title, price = trendyol_product_info(URL)
        elif "letgo" in URL:
            title, price = letgo_product_info(URL)
        elif "akakce" in URL:
            title, price = akakce_product_info(URL)
        else:
            return

        current_prices[title] = price

        label_text = f"{title} - {price}₺"
        tk.Label(current_prices_window, text=label_text, font=("Arial", 10)).pack(
            pady=5, padx=5
        )
        tk.Frame(current_prices_window, height=1, bg="black").pack(
            fill="x"
        )  # Altına çizgi ekle

    # Zamanı kaydet ve JSON dosyasına yaz
    current_prices["saved_time"] = datetime.now().strftime("%d-%m-%y %H:%M:%S")
    with open("newProducts.json", "w") as file:
        json.dump(current_prices, file, indent=4)

    # Eğer newProducts.json dosyası yoksa, boş bir sözlük oluşturarak başlayalım
    try:
        with open("newProducts.json", "r") as file:
            pass  # Dosya zaten var, bu yüzden bir şey yapmamıza gerek yok
    except FileNotFoundError:
        with open("newProducts.json", "w") as file:
            json.dump({}, file)

    # Pencere kapatıldığında uygulamayı yeniden başlat
    current_prices_window.protocol("WM_DELETE_WINDOW", restart_app)


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




# Ana fonksiyon
def main():
    global root
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
    add_product_button.pack(pady=button_pad_y)

    edit_products_button = tk.Button(
        root,
        text="Ürünleri Düzenle",
        command=lambda: open_edit_products_window(products),
        font=button_font,
        width=button_width,
    )
    edit_products_button.pack(pady=button_pad_y)

    check_button = tk.Button(
        root,
        text="Ürün Kontrolü Yap",
        command=lambda: check_prices(products),
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


# Uygulamayı yeniden başlatma
def restart_app():
    root.destroy()
    main()


if __name__ == "__main__":
    products = load_products_from_json("products.json")
    main()
