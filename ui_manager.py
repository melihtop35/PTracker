import tkinter as tk
import json, pystray, PIL.Image, time, threading
from tkinter import messagebox
from datetime import datetime
from product_manager import (
    load_products_from_json,
    save_products_to_json,
    update_products,
)
from price_checker import check_prices_and_send
from email_manager import add_email
from price_checker import (
    amazon_product_info,
    letgo_product_info,
    akakce_product_info,
    trendyol_product_info,
    hepsiburada_product_info,
)

image = PIL.Image.open("form.ico")


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


def save_settings_to_json(settings):
    with open("settings.json", "w") as file:
        json.dump(settings, file, indent=4)


def load_settings_from_json():
    try:
        with open("settings.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"minimize_to_tray": False, "button_text": "600"}  # Varsayılan ayarlar


global settings


def open_settings():
    btn_height = 1
    btn_width = 10

    def toggle_minimize_to_tray():
        settings["minimize_to_tray"] = not settings["minimize_to_tray"]
        save_settings_to_json(settings)
        if settings["minimize_to_tray"]:
            toggle_button_minimize.config(text="Açık")
        else:
            toggle_button_minimize.config(text="Kapalı")

    def update_button_text():
        current_text = settings["button_text"]
        current_number = int(current_text)
        next_number = 0
        if current_number == 600:
            next_number = 1200
        elif current_number == 1200:
            next_number = 3600
        elif current_number == 3600:
            next_number = 600

        toggle_button_timer.config(text=str(int(next_number / 60)) + " Dakika")
        # JSON dosyasına kaydet
        settings["button_text"] = str(next_number)
        save_settings_to_json(settings)

    # Ayarları yükle
    settings = load_settings_from_json()

    # Ayarlar penceresini aç
    settings_window = tk.Toplevel(root)
    settings_window.title("Ayarlar")
    settings_window.geometry("400x200+500+300")

    # Minimize to tray ayarı için bir label oluştur
    toggle_label_minimize = tk.Label(
        settings_window,
        text="Pencereyi simge durumuna küçült",
        font=("Arial", 12),
    )
    toggle_label_minimize.grid(row=0, column=0, sticky="w", padx=10, pady=5)

    # Minimize to tray ayarı için bir buton oluştur
    toggle_button_minimize = tk.Button(
        settings_window,
        text="Açık" if settings["minimize_to_tray"] else "Kapalı",
        command=toggle_minimize_to_tray,
        font=("Arial", 12),
        width=btn_width,
        height=btn_height,
    )
    toggle_button_minimize.grid(row=0, column=1, padx=10, pady=5)

    # Uygulama otomatik çalışma zamanı için bir label oluştur
    toggle_label_timer = tk.Label(
        settings_window,
        text="Uygulama otomatik çalışma zamanı",
        font=("Arial", 12),
    )
    toggle_label_timer.grid(row=1, column=0, sticky="w", padx=10, pady=5)

    # Uygulama otomatik çalışma zamanı için bir buton oluştur
    toggle_button_timer = tk.Button(
        settings_window,
        text=settings["button_text"],
        command=update_button_text,
        font=("Arial", 12),
        width=btn_width,
        height=btn_height,
    )
    toggle_button_timer.grid(row=1, column=1, padx=10, pady=5)


def main():
    # Ayarları yükle
    settings = load_settings_from_json()
    global root
    root = tk.Tk()
    root.configure(bg="lightgray")
    root.title("Fiyat Kontrol Programı")
    root.geometry("+300+300")

    def show_icon():
        def on_clicked(icon, item):
            if str(item) == "Göster":
                root.deiconify()  # Ana pencereyi yeniden göster
                root.lift()  # Pencereyi en üste getir
                root.focus_force()  # Pencereye odaklan
                icon.stop()
            elif str(item) == "Çık":
                icon.stop()
                root.destroy()  # Programı kapat

        # Pencereyi gizle
        root.withdraw()

        # Simge çubuğuna simge ekleme
        icon = pystray.Icon(
            "Neural",
            image,
            "Fiyat Takibi",
            menu=pystray.Menu(
                pystray.MenuItem("Göster", on_clicked),
                pystray.MenuItem("Çık", on_clicked),
            ),
        )
        icon.run()

    def minimize_to_tray():
        settings = load_settings_from_json()
        if settings["minimize_to_tray"]:
            show_icon()
        else:
            root.destroy()

    root.wm_protocol("WM_DELETE_WINDOW", minimize_to_tray)

    # Buton oluşturma
    button_font = ("Arial", 10)
    button_width = 20
    button_pad_y = 5

    # İkon görüntüsünü yükleyin (yerine kendi ikonunuzun yolunu verin)
    settings_icon = tk.PhotoImage(file="settings.ico")
    # Ayarlar butonunu oluşturma
    settings_button = tk.Button(
        root,
        image=settings_icon,  # İkonu belirle
        command=open_settings,
        bd=0,  # Kenarlık kalınlığını sıfıra ayarla
        bg="lightgray",  # Arka plan rengini ayarla
        activebackground="lightgray",  # Tıklanma durumunda arka plan rengini ayarla
    )
    settings_button.place(relx=1.0, rely=0.0, anchor="ne")

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
        command=lambda: check_prices_and_send(products),
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

    # `check_prices_and_send` işlevini 10,20,60 dakika geciktirerek başlatan bir thread oluştur
    def check_prices_thread():
        time.sleep(int(settings["button_text"]))  # 10,20,60 dakika bekle
        while True:
            check_prices_and_send(products)

    prices_thread = threading.Thread(target=check_prices_thread)
    prices_thread.daemon = True  # Ana program sona erdiğinde bu thread sona ersin
    prices_thread.start()

    # Pencereyi gösterme
    root.mainloop()


# Uygulamayı yeniden başlatma
def restart_app():
    root.deiconify()  # Tkinter penceresini yeniden göster
    root.destroy()
    main()
