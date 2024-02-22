import json
from tkinter import messagebox

def load_products_from_json(json_file):
    try:
        with open(json_file, "r") as file:
            products = json.load(file)
    except FileNotFoundError:
        products = []
        with open(json_file, "w") as file:
            json.dump(products, file)

    return products


def save_products_to_json(json_file, products):
    with open(json_file, "w") as file:
        json.dump(products, file, indent=4)


def add_product(product, products, json_file):
    products.append(product)
    save_products_to_json(json_file, products)


def delete_product(index, products, json_file):
    del products[index]
    save_products_to_json(json_file, products)

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
