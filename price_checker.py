import json
import requests
from bs4 import BeautifulSoup
import email_manager as email_manager


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
            email_body += (
                f"{title} Şimdi {price}₺ ({target_price}₺'nin %.2f TL altında)\nLinki Kontrol Et: {URL}\n\n"
                % price_difference
            )

    if email_body:
        email_manager.send_mail(email_body)

    with open("newProducts.json", "w") as file:
        json.dump(current_prices, file, indent=4)
