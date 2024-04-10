import tkinter as tk
import json
import pystray
import concurrent.futures
import PIL.Image
import time
import threading
from tkinter import messagebox, simpledialog
from datetime import datetime
from settings import save_settings_to_json, load_settings_from_json, get_language_data
from product_manager import (
    load_products_from_json,
    save_products_to_json,
    update_products,
)
from email_manager import add_email, get_receiver_email
from price_checker import (
    amazon_product_info,
    letgo_product_info,
    akakce_product_info,
    trendyol_product_info,
    hepsiburada_product_info,
    check_prices_and_send,
    check_prices_and_send_current,
)

image = PIL.Image.open("icons/form.ico")


def open_add_product_window(products):
    add_product_window = tk.Toplevel()
    add_product_window.title(get_language_data("add_product_window_title"))
    add_product_window.geometry("300x300+800+300")
    # Pencerenin minimum  ve maximum genişlik ve yükseklik değerlerini ayarla
    add_product_window.minsize(300, 300)
    add_product_window.maxsize(500, 400)

    link_label = tk.Label(add_product_window, text=get_language_data("link_label"))
    link_label.pack(pady=5, fill=tk.X)

    global link_entry
    link_entry = tk.Entry(add_product_window)
    link_entry.pack(pady=10, padx=(80, 80), fill=tk.X)

    name_label = tk.Label(add_product_window, text=get_language_data("name_label"))
    name_label.pack(pady=5, fill=tk.X)

    global name_entry
    name_entry = tk.Entry(add_product_window)
    name_entry.pack(pady=10, padx=(80, 80), fill=tk.X)

    target_price_label = tk.Label(
        add_product_window, text=get_language_data("target_price_label")
    )
    target_price_label.pack(pady=5, fill=tk.X)

    global target_price_entry
    target_price_entry = tk.Entry(add_product_window)
    target_price_entry.pack(pady=10, padx=(80, 80), fill=tk.X)

    add_button = tk.Button(
        add_product_window,
        text=get_language_data("add_button_text"),
        command=lambda: add_product_and_close(add_product_window, products),
    )
    add_button.pack(pady=10, padx=(80, 80), fill=tk.X)

    add_product_window.transient(root)
    add_product_window.grab_set()
    root.wait_window(add_product_window)


def add_product_and_close(window, products):
    link = link_entry.get()
    name = name_entry.get()
    target_price = target_price_entry.get()
    if not link and not name and not target_price:
        messagebox.showerror(get_language_data("error"), get_language_data("fill_all"))
    elif link and name and target_price:
        try:
            target_price = float(target_price)
        except ValueError:
            messagebox.showerror(
                get_language_data("error"), get_language_data("valid_price_error")
            )
            return
        products.append({"name": name, "URL": link, "target_price": target_price})
        save_products_to_json("jsons/products.json", products)
        messagebox.showinfo(
            get_language_data("info"), get_language_data("product_added_info")
        )
        window.destroy()
    elif not link:
        messagebox.showerror(
            get_language_data("error"), get_language_data("link_error")
        )
    elif not name:
        messagebox.showerror(
            get_language_data("error"), get_language_data("name_error")
        )
    elif not target_price:
        messagebox.showerror(
            get_language_data("error"), get_language_data("price_error")
        )


def open_edit_products_window(products):
    def delete_product(index):
        del products[index]
        save_products_to_json("jsons/products.json", products)
        edit_products_window.destroy()
        open_edit_products_window(products)

    def save_products_to_json(json_file, products):
        with open(json_file, "w") as file:
            json.dump(products, file, indent=4)

    edit_products_window = tk.Toplevel()
    edit_products_window.title(get_language_data("edit_products_window_title"))
    edit_products_window.geometry("940x400+400+300")
    edit_products_window.minsize(940, 400)
    scroll_frame = tk.Frame(edit_products_window)
    scroll_frame.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(scroll_frame, orient="vertical")
    scrollbar.pack(side="right", fill="y")

    products_frame = tk.Frame(scroll_frame)
    products_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(products_frame, yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)

    products_frame.bind(
        "<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all"))
    )
    scrollbar.config(command=canvas.yview)

    inner_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    for i, product in enumerate(products):
        tk.Label(inner_frame, text=f"{get_language_data('product')} {i+1}").grid(
            row=i, column=0, padx=5, pady=5, sticky="e"
        )

        tk.Label(inner_frame, text=get_language_data("name_label")).grid(
            row=i, column=1, padx=(5, 0), pady=5, sticky="e"
        )
        name_entry = tk.Entry(inner_frame, width=40)
        name_entry.insert(0, product.get("name", ""))
        name_entry.grid(row=i, column=2, padx=5, pady=5, sticky="w")

        tk.Label(inner_frame, text=get_language_data("link_label")).grid(
            row=i, column=3, padx=(5, 0), pady=5, sticky="e"
        )
        link_entry = tk.Entry(inner_frame, width=40)
        link_entry.insert(0, product.get("URL", ""))
        link_entry.grid(row=i, column=4, padx=5, pady=5, sticky="w")

        tk.Label(inner_frame, text=get_language_data("target_price_label")).grid(
            row=i, column=5, padx=(5, 0), pady=5, sticky="e"
        )
        target_price_entry = tk.Entry(inner_frame, width=10)
        target_price_entry.insert(0, str(product.get("target_price", "")))
        target_price_entry.grid(row=i, column=6, padx=5, pady=5, sticky="w")

        delete_button = tk.Button(
            inner_frame,
            text=get_language_data("delete_button_text"),
            command=lambda index=i: delete_product(index),
            width=7,
        )
        delete_button.grid(row=i, column=7, padx=5, pady=5)

    update_button = tk.Button(
        edit_products_window,
        text=get_language_data("update_button_text"),
        command=lambda: update_products(products, inner_frame, edit_products_window),
    )
    update_button.pack(pady=10)

    canvas.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    edit_products_window.transient(root)
    edit_products_window.grab_set()
    root.wait_window(edit_products_window)


def show_current_prices(products):
    current_prices_window = tk.Toplevel()
    current_prices_window.title(get_language_data("current_prices_window_title"))
    current_prices_window.geometry("+300+300")

    current_prices = []

    canvas = tk.Canvas(current_prices_window)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(
        current_prices_window, orient=tk.VERTICAL, command=canvas.yview
    )
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    inner_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    def fetch_product_info(URL):
        if "amazon" in URL:
            return amazon_product_info(URL)
        elif "hepsiburada" in URL:
            return hepsiburada_product_info(URL)
        elif "trendyol" in URL:
            return trendyol_product_info(URL)
        elif "letgo" in URL:
            return letgo_product_info(URL)
        elif "akakce" in URL:
            return akakce_product_info(URL)
        else:
            return None

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {
            executor.submit(fetch_product_info, product["URL"]): product
            for product in products
        }
        for future in concurrent.futures.as_completed(future_to_url):
            product = future_to_url[future]
            try:
                title, price = future.result()
                if title is not None and price is not None:
                    current_prices.append(
                        {"title": title, "URL": product["URL"], "price": price}
                    )
                    label_text = f"{title} - {price}₺"
                    label = tk.Label(inner_frame, text=label_text, font=("Arial", 10))
                    label.pack(pady=5, padx=5, anchor="w")
                    tk.Frame(inner_frame, height=1, bg="black").pack(fill="x")
            except Exception as exc:
                print(exc)

    inner_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    max_label_width = max(label.winfo_width() for label in inner_frame.winfo_children())
    canvas.config(width=max_label_width + scrollbar.winfo_width())

    saved_time = datetime.now().strftime("%d-%m-%y %H:%M:%S")
    current_prices.append({"saved_time": saved_time})

    check_prices_and_send_current(current_prices)

    with open("jsons/newProducts.json", "w", encoding="utf-8") as file:
        json.dump(current_prices, file, indent=4)

    current_prices_window.protocol("WM_DELETE_WINDOW", restart_app)

    current_prices_window.transient(root)
    current_prices_window.grab_set()
    root.wait_window(current_prices_window)


def show_saved_products(root):
    saved_prices_frame = tk.Frame(root)
    saved_prices_frame.pack(pady=10)

    try:
        with open("jsons/newProducts.json", "r", encoding="utf-8") as file:
            saved_data = json.load(file)
    except FileNotFoundError:
        saved_data = []

    # En geniş yazının uzunluğunu bul
    max_width = 0
    for item in saved_data:
        if "title" in item:
            width = len(item["title"])
            if width > max_width:
                max_width = width

    # Scrollbar'ı eklemek için bir Canvas oluştur
    canvas = tk.Canvas(saved_prices_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Scrollbar oluştur
    scrollbar = tk.Scrollbar(
        saved_prices_frame, orient=tk.VERTICAL, command=canvas.yview
    )
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Frame içine fiyatları listeleyen etiketleri ekleyin
    inner_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    for item in saved_data:
        if "title" in item:
            label_text = f"{item['title']} - {item['price']}₺"
            label = tk.Label(inner_frame, text=label_text, font=("Arial", 10))
            label.pack(pady=5, padx=5, anchor="w")

            # Etiketin genişliğini ayarla
            label.update_idletasks()
            label_width = label.winfo_width()
            if label_width > max_width:
                max_width = label_width

            tk.Frame(inner_frame, height=1, bg="black").pack(fill="x")

    # Canvas boyutunu ayarlayın
    inner_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # Frame'in genişliğini ayarlayın
    canvas.config(width=max_width + scrollbar.winfo_width())


def open_settings():
    settings = load_settings_from_json()

    def toggle_minimize_to_tray():
        settings["minimize_to_tray"] = not settings["minimize_to_tray"]
        save_settings_to_json(settings)
        if settings["minimize_to_tray"]:
            toggle_button_minimize.config(text=get_language_data("on_text"))
        else:
            toggle_button_minimize.config(text=get_language_data("off_text"))
        update_window_size()

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

        toggle_button_timer.config(
            text=str(int(next_number / 60)) + " " + get_language_data("minutes_text")
        )
        settings["button_text"] = str(next_number)
        save_settings_to_json(settings)
        update_window_size()

    def change_language(language):
        if language == "Türkçe":
            settings["language"] = "Türkçe"
            save_settings_to_json(settings)
            update_language(settings["language"])
            update_window_size()
        elif language == "English":
            settings["language"] = "English"
            save_settings_to_json(settings)
            update_language(settings["language"])
            update_window_size()

    def update_language(language):
        with open("jsons/language_data.json", "r", encoding="utf-8") as lang_file:
            lang_data = json.load(lang_file)
            lang_texts = lang_data.get(language)
            settings_window.title(lang_texts["settings_window_title"])
            toggle_label_minimize.config(text=lang_texts["minimize_to_tray_label"])
            toggle_button_minimize.config(
                text=(
                    lang_texts["on_text"]
                    if settings["minimize_to_tray"]
                    else lang_texts["off_text"]
                )
            )
            toggle_label_timer.config(text=lang_texts["auto_run_time_label"])
            toggle_button_timer.config(
                text=str(int(int(settings["button_text"]) / 60))
                + " "
                + lang_texts["minutes_text"]
            )
            toggle_label_lang.config(text=lang_texts["language_label"])

    def update_window_size():
        # İçeriğin uzunluğuna göre pencere boyutunu güncelle
        settings_window.update_idletasks()
        width = max(
            settings_window.winfo_width(),
            toggle_label_minimize.winfo_reqwidth(),
            toggle_button_minimize.winfo_reqwidth(),
            toggle_label_timer.winfo_reqwidth(),
            toggle_button_timer.winfo_reqwidth(),
            toggle_label_lang.winfo_reqwidth(),
            language_menu.winfo_reqwidth(),
        )
        height = max(
            settings_window.winfo_height(),
            toggle_label_minimize.winfo_reqheight(),
            toggle_button_minimize.winfo_reqheight(),
            toggle_label_timer.winfo_reqheight(),
            toggle_button_timer.winfo_reqheight(),
            toggle_label_lang.winfo_reqheight(),
            language_menu.winfo_reqheight(),
        )
        settings_window.minsize(width, height)
        settings_window.maxsize(width, height)
        settings_window.destroy()
        open_settings()

    settings_window = tk.Toplevel(root)
    settings_window.geometry("+800+300")

    toggle_label_minimize = tk.Label(
        settings_window,
        text="",
        font=("Arial", 12),
    )
    toggle_label_minimize.grid(row=0, column=0, sticky="w", padx=10, pady=5)

    toggle_button_minimize = tk.Button(
        settings_window,
        text="",
        command=toggle_minimize_to_tray,
        font=("Arial", 12),
        width=10,
        height=1,
    )
    toggle_button_minimize.grid(row=0, column=1, padx=10, pady=5)

    toggle_label_timer = tk.Label(
        settings_window,
        text="",
        font=("Arial", 12),
    )
    toggle_label_timer.grid(row=1, column=0, sticky="w", padx=10, pady=5)

    toggle_button_timer = tk.Button(
        settings_window,
        text=str(int(int(settings["button_text"]) / 60))
        + get_language_data("minutes_text"),
        command=update_button_text,
        font=("Arial", 12),
        width=10,
        height=1,
    )
    toggle_button_timer.grid(row=1, column=1, padx=10, pady=5)

    toggle_label_lang = tk.Label(
        settings_window,
        text=get_language_data("language_label"),
        font=("Arial", 12),
    )
    toggle_label_lang.grid(row=2, column=0, sticky="w", padx=10, pady=5)

    language_options = ["Türkçe", "English"]
    selected_language = tk.StringVar()
    selected_language.set(settings["language"])
    language_menu = tk.OptionMenu(
        settings_window, selected_language, *language_options, command=change_language
    )
    language_menu.grid(row=2, columnspan=2, pady=10)

    settings_window.wm_protocol("WM_DELETE_WINDOW", restart_app)

    update_language(settings["language"])
    settings_window.transient(root)
    settings_window.grab_set()  # Modal pencereyi aç
    root.wait_window(settings_window)  # Pencere kapanana kadar beklet


def share_prices():
    try:
        with open("jsons/newProducts.json", "r") as f:
            product_data = json.load(f)
            if isinstance(product_data, list):
                urls_and_prices = []
                for item in product_data:
                    if isinstance(item, dict):
                        name = item.get("title")
                        price = item.get("price")
                        url = item.get("URL")
                        if name is not None and price is not None and url is not None:
                            urls_and_prices.append(
                                {"title": name, "price": price, "URL": url}
                            )
                    else:
                        print("Geçersiz veri türü: Liste içinde sözlük bekleniyor.")

                # Sıralama fonksiyonları
                sort_direction_name = False
                sort_direction_price = False

                def sort_by_name():
                    nonlocal sort_direction_name
                    urls_and_prices.sort(
                        key=lambda x: x["title"], reverse=sort_direction_name
                    )
                    sort_direction_name = not sort_direction_name
                    update_display()

                def sort_by_price():
                    nonlocal sort_direction_price
                    urls_and_prices.sort(
                        key=lambda x: x["price"], reverse=sort_direction_price
                    )
                    sort_direction_price = not sort_direction_price
                    update_display()

                def update_display():
                    link_text.delete("1.0", tk.END)
                    for data in urls_and_prices:
                        link_text.insert(
                            tk.END,
                            f"{data['title']}: {data['price']}\n{data['URL']}\n\n",
                        )

                # Linkleri göstermek için yeni bir pencere oluştur
                link_window = tk.Toplevel()
                link_window.title(get_language_data("url_tittle"))
                link_window.geometry("1000x500+400+300")

                # Linkleri metin kutusuna ekle
                link_text = tk.Text(link_window)
                link_text.pack(expand=True, fill=tk.BOTH)

                # Butonları ekle
                sort_name_button = tk.Button(
                    link_window,
                    text=get_language_data("sort_by_name"),
                    command=sort_by_name,
                )
                sort_name_button.pack(side=tk.LEFT, padx=5, pady=5)

                sort_price_button = tk.Button(
                    link_window,
                    text=get_language_data("sort_by_price"),
                    command=sort_by_price,
                )
                sort_price_button.pack(side=tk.LEFT, padx=5, pady=5)

                # Kopyala butonunu ekle
                copy_button = tk.Button(
                    link_window,
                    text=get_language_data("copy_link"),
                    command=lambda: link_text.clipboard_append(
                        link_text.get("1.0", tk.END)
                    ),
                )
                copy_button.pack(side=tk.LEFT, padx=5, pady=5)

                update_display()  # Başlangıçta adlara göre sıralı olarak göster

            else:
                print("Geçersiz veri türü: Liste bekleniyor.")
    except FileNotFoundError:
        print("newProducts.json dosyası bulunamadı.")


def main():
    global settings
    products = load_products_from_json("jsons/products.json")
    settings = load_settings_from_json()

    global root
    root = tk.Tk()
    root.configure(bg="lightgray")
    root.title(get_language_data("app_title"))
    root.geometry("+500+300")
    root.minsize(300, 150)

    if get_receiver_email() == None or "":
        add_email()

    def show_icon():
        def on_clicked(icon, item):
            if str(item) == get_language_data("show_text"):
                root.deiconify()
                root.lift()
                root.focus_force()
                icon.stop()
            elif str(item) == get_language_data("exit_text"):
                icon.stop()
                root.destroy()

        root.withdraw()

        icon = pystray.Icon(
            "Neural",
            image,
            get_language_data("price_tracker"),
            menu=pystray.Menu(
                pystray.MenuItem(get_language_data("show_text"), on_clicked),
                pystray.MenuItem(get_language_data("exit_text"), on_clicked),
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

    settings_icon = tk.PhotoImage(file="icons/settings.ico")
    settings_button = tk.Button(
        root,
        image=settings_icon,
        command=open_settings,
        bd=0,
        bg="lightgray",
        activebackground="lightgray",
    )
    settings_button.place(relx=1.0, rely=0.0, anchor="ne")

    add_product_button = tk.Button(
        root,
        text=get_language_data("add_product_text"),
        command=lambda: open_add_product_window(products),
        font=("Arial", 10),
        width=20,
    )
    add_product_button.pack(pady=5)

    edit_products_button = tk.Button(
        root,
        text=get_language_data("edit_products_text"),
        command=lambda: open_edit_products_window(products),
        font=("Arial", 10),
        width=20,
    )
    edit_products_button.pack(pady=5)

    check_button = tk.Button(
        root,
        text=get_language_data("check_button_text"),
        command=lambda: check_prices_and_send(products),
        font=("Arial", 10),
        width=20,
    )
    check_button.pack(pady=5)

    show_current_prices_button = tk.Button(
        root,
        text=get_language_data("show_current_prices_button_text"),
        command=lambda: show_current_prices(products),
        font=("Arial", 10),
        width=20,
    )
    show_current_prices_button.pack(pady=5)

    show_current_prices_button = tk.Button(
        root,
        text=get_language_data("share"),
        command=lambda: share_prices(),
        font=("Arial", 10),
        width=20,
    )
    show_current_prices_button.pack(pady=5)

    show_saved_products(root)

    add_email_button = tk.Button(
        root,
        text=get_language_data("add_email_button_text"),
        command=add_email,
        font=("Arial", 10),
        width=20,
    )
    add_email_button.pack(pady=5)

    # `check_prices_and_send` işlevini 10,20,60 dakika geciktirerek başlatan bir thread oluştur
    def check_prices_thread():
        time.sleep(int(settings["button_text"]))  # 10,20,60 dakika bekle
        while True:
            check_prices_and_send(products)

    prices_thread = threading.Thread(target=check_prices_thread)
    prices_thread.daemon = True  # Ana program sona erdiğinde bu thread sona ersin
    prices_thread.start()

    root.mainloop()


# Uygulamayı yeniden başlatma
def restart_app():
    root.deiconify()  # Tkinter penceresini yeniden göster
    root.destroy()
    main()
