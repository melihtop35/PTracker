import tkinter as tk
import json
import pystray
import PIL.Image
import time
import threading
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
    add_product_window.title(get_language_data("add_product_window_title"))
    add_product_window.geometry("300x300+800+300")

    link_label = tk.Label(add_product_window, text=get_language_data("link_label"))
    link_label.pack(pady=5)

    global link_entry
    link_entry = tk.Entry(add_product_window)
    link_entry.pack(pady=5)

    name_label = tk.Label(add_product_window, text=get_language_data("name_label"))
    name_label.pack(pady=5)

    global name_entry
    name_entry = tk.Entry(add_product_window)
    name_entry.pack(pady=5)

    target_price_label = tk.Label(
        add_product_window, text=get_language_data("target_price_label")
    )
    target_price_label.pack(pady=5)

    global target_price_entry
    target_price_entry = tk.Entry(add_product_window)
    target_price_entry.pack(pady=5)

    add_button = tk.Button(
        add_product_window,
        text=get_language_data("add_button_text"),
        command=lambda: add_product_and_close(add_product_window, products),
    )
    add_button.pack(pady=5)


def add_product_and_close(window, products):
    try:
        link = link_entry.get()
        name = name_entry.get()
        target_price = float(target_price_entry.get())
    except ValueError:
        messagebox.showinfo(
            get_language_data("error"), get_language_data("valid_price_error")
        )
        return
    if link and name and target_price:
        products.append({"name": name, "URL": link, "target_price": target_price})
        save_products_to_json("products.json", products)
        messagebox.showinfo(
            get_language_data("info"), get_language_data("product_added_info")
        )
        window.destroy()
    elif not link and name and target_price:
        messagebox.showerror(
            get_language_data("error"), get_language_data("link_error")
        )
    elif link and not name and target_price:
        messagebox.showerror(
            get_language_data("error"), get_language_data("name_error")
        )
    elif link and name and not target_price:
        messagebox.showerror(
            get_language_data("error"), get_language_data("price_error")
        )


# Ürünleri düzenleme penceresini açma
def open_edit_products_window(products):
    def delete_product(index):
        del products[index]
        save_products_to_json("products.json", products)
        edit_products_window.destroy()
        open_edit_products_window(products)

    def save_products_to_json(json_file, products):
        with open(json_file, "w") as file:
            json.dump(products, file, indent=4)

    edit_products_window = tk.Toplevel()
    edit_products_window.title(get_language_data("edit_products_window_title"))
    edit_products_window.geometry("900x400+400+300")

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
            row=i, column=0, padx=5, pady=5
        )

        tk.Label(inner_frame, text=get_language_data("name_label")).grid(
            row=i, column=1, padx=5, pady=5
        )
        name_entry = tk.Entry(inner_frame, width=40)
        name_entry.insert(0, product.get("name", ""))
        name_entry.grid(row=i, column=2, padx=5, pady=5)

        tk.Label(inner_frame, text=get_language_data("link_label")).grid(
            row=i, column=3, padx=5, pady=5
        )
        link_entry = tk.Entry(inner_frame, width=40)
        link_entry.insert(0, product.get("URL", ""))
        link_entry.grid(row=i, column=4, padx=5, pady=5)

        tk.Label(inner_frame, text=get_language_data("target_price_label")).grid(
            row=i, column=5, padx=5, pady=5
        )
        target_price_entry = tk.Entry(inner_frame, width=10)
        target_price_entry.insert(0, str(product.get("target_price", "")))
        target_price_entry.grid(row=i, column=6, padx=5, pady=5)

        delete_button = tk.Button(
            inner_frame,
            text=get_language_data("delete_button_text"),
            command=lambda index=i: delete_product(index),
            width=5,
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

    current_prices = {}
    for product in products:
        URL = product["URL"]
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
        tk.Frame(current_prices_window, height=1, bg="black").pack(fill="x")

    current_prices["saved_time"] = datetime.now().strftime("%d-%m-%y %H:%M:%S")
    with open("newProducts.json", "w", encoding="utf-8") as file:
        json.dump(current_prices, file, indent=4)

    try:
        with open("newProducts.json", "r", encoding="utf-8") as file:
            pass
    except FileNotFoundError:
        with open("newProducts.json", "w", encoding="utf-8") as file:
            json.dump({}, file)

    current_prices_window.protocol("WM_DELETE_WINDOW", restart_app)


def show_saved_products(root):
    saved_prices_frame = tk.Frame(root)
    saved_prices_frame.pack(pady=10)

    try:
        with open("newProducts.json", "r", encoding="utf-8") as file:
            saved_data = json.load(file)
            if isinstance(saved_data, dict):
                current_prices = saved_data
                saved_time = current_prices.get("saved_time")
            else:
                current_prices = saved_data[0]
                saved_time = current_prices.get("saved_time")
    except FileNotFoundError:
        current_prices = {}
        saved_time = None

    for product, price in current_prices.items():
        if product != "saved_time":
            label_text = f"{product} - {price}₺"
            tk.Label(saved_prices_frame, text=label_text, font=("Arial", 10)).pack(
                pady=5, padx=5
            )
            tk.Frame(saved_prices_frame, height=1, bg="black").pack(fill="x")

    if saved_time:
        time_label = tk.Label(
            saved_prices_frame,
            text=f"{get_language_data('saved_time_label')}: {saved_time}",
            font=("Arial", 10),
        )
        time_label.pack(pady=10)


def save_settings_to_json(settings):
    with open("settings.json", "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def load_settings_from_json():
    try:
        with open("settings.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"minimize_to_tray": False, "button_text": "600"}


def open_settings():
    def toggle_minimize_to_tray():
        settings["minimize_to_tray"] = not settings["minimize_to_tray"]
        save_settings_to_json(settings)
        if settings["minimize_to_tray"]:
            toggle_button_minimize.config(text=get_language_data("on_text"))
        else:
            toggle_button_minimize.config(text=get_language_data("off_text"))

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

        toggle_button_timer.config(text=str(int(next_number / 60)))
        settings["button_text"] = str(next_number)
        save_settings_to_json(settings)

    def change_language(language):
        if language == "Türkçe":
            settings["language"] = "Türkçe"
            save_settings_to_json(settings)
            update_language(settings["language"])
        elif language == "English":
            settings["language"] = "English"
            save_settings_to_json(settings)
            update_language(settings["language"])

    def update_language(language):
        with open("language_data.json", "r", encoding="utf-8") as lang_file:
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

    settings = load_settings_from_json()
    settings_window = tk.Toplevel(root)
    settings_window.geometry("330x150+500+300")

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
        text=str(int(int(settings["button_text"]) / 60)),
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

    update_language(settings["language"])

    settings_window.wm_protocol("WM_DELETE_WINDOW", restart_app)


def get_language_data(key):
    # settings["language"] değerine göre doğru dilin altındaki öğeleri döndür
    return language_data[settings["language"]].get(key, "")


def main():
    global settings
    global language_data
    products = load_products_from_json("products.json")
    with open("language_data.json", "r", encoding="utf-8") as lang_file:
        language_data = json.load(lang_file)
    settings = load_settings_from_json()

    global root
    root = tk.Tk()
    root.configure(bg="lightgray")
    root.title(get_language_data("app_title"))
    root.geometry("+300+300")

    def show_icon():
        def on_clicked(icon, item):
            if str(item) == get_language_data("show_text"):
                root.deiconify()
                root.lift()
                root.focus_force()
                icon.stop()
            elif str(item) == language_data("exit_text"):
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

    settings_icon = tk.PhotoImage(file="settings.ico")
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
