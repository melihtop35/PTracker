import json
import requests
from bs4 import BeautifulSoup
import email_manager as email_manager
import time, random
from settings import get_language_data


def add_one_if_last_digit_is_nine(number):
    # Sayının son basamağını al
    last_digit = int(str(number)[-1])

    # Son basamak 9 ise
    if last_digit == 9:
        # Sayıya 1 ekle
        number += 1

    return number


def amazon_product_info(URL):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.1"
    }

    # Farklı parser'ları sırayla deneyelim
    parsers = ["html.parser", "lxml", "html5lib"]
    for parser in parsers:
        try:
            page = requests.get(URL, headers=headers)
            soup = BeautifulSoup(page.content, parser)

            title = soup.find("span", id="productTitle")
            if title:
                title = title.get_text().strip()

            price_tag = soup.find("span", class_="a-price-whole")
            if price_tag:
                price_text = price_tag.get_text()
                price_text = price_text.split(",")[0]
                price = int(price_text.replace("TL", "").replace(".", "").strip())
                price = add_one_if_last_digit_is_nine(price)

            # 1 veya 2 saniye arası rastgele bir gecikme ekle
            time.sleep(random.uniform(0.25, 1))

            return title, price
        except Exception as e:
            print(f"Parser {parser} ile çekme sırasında hata: {e}")

    # Tüm parser'lar denenip başarısız olursa None döndür
    return get_language_data("product_not_found"), None


def akakce_product_info(URL):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.1"
    }

    # Farklı parser'ları sırayla deneyelim
    parsers = ["html.parser", "lxml", "html5lib"]
    for parser in parsers:
        try:
            page = requests.get(URL, headers=headers)
            soup = BeautifulSoup(page.content, parser)

            title_tag = soup.find("h1")
            if title_tag:
                title = title_tag.get_text().strip()

            price_tag = soup.find("span", class_="pt_v8")
            if price_tag:
                price_text = price_tag.get_text()
                price_text = price_text.split(",")[0]
                price = int(price_text.replace("TL", "").replace(".", "").strip())
                price = add_one_if_last_digit_is_nine(price)

            # 1 veya 2 saniye arası rastgele bir gecikme ekle
            time.sleep(random.uniform(0.25, 1))

            return title, price
        except Exception as e:
            print(f"Parser {parser} ile çekme sırasında hata: {e}")

    # Tüm parser'lar denenip başarısız olursa None döndür
    return get_language_data("product_not_found"), None


def hepsiburada_product_info(URL):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.1"
    }

    # Farklı parser'ları sırayla deneyelim
    parsers = ["html.parser", "lxml", "html5lib"]
    for parser in parsers:
        try:
            page = requests.get(URL, headers=headers)
            soup = BeautifulSoup(page.text, parser)

            title_tag = soup.find("h1", class_="product-name")
            if title_tag:
                title = title_tag.get_text().strip()

            price_tag = soup.find(
                "span", {"data-bind": "markupText:'currentPriceBeforePoint'"}
            )
            if price_tag:
                price_text = price_tag.get_text()
                price_text = price_text.split(",")[0]
                price = int(price_text.replace("TL", "").replace(".", "").strip())
                price = add_one_if_last_digit_is_nine(price)

            # 1 veya 2 saniye arası rastgele bir gecikme ekle
            time.sleep(random.uniform(0.25, 1))

            return title, price
        except Exception as e:
            print(f"Parser {parser} ile çekme sırasında hata: {e}")

    # Tüm parser'lar denenip başarısız olursa None döndür
    return get_language_data("product_not_found"), None


def trendyol_product_info(URL):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.1"
    }

    # Farklı parser'ları sırayla deneyelim
    parsers = ["html.parser", "lxml", "html5lib"]
    for parser in parsers:
        try:
            page = requests.get(URL, headers=headers)
            soup = BeautifulSoup(page.content, parser)

            title_tag = soup.find("h1", class_="pr-new-br")
            if title_tag:
                title = title_tag.get_text().strip()

            price_tag = soup.find("div", class_="product-price-container")
            if price_tag:
                price_text = price_tag.get_text()
                price_text = price_text.split(",")[0]
                price = int(price_text.replace("TL", "").replace(".", "").strip())
                price = add_one_if_last_digit_is_nine(price)

            # 1 veya 2 saniye arası rastgele bir gecikme ekle
            time.sleep(random.uniform(0.25, 1))

            return title, price
        except Exception as e:
            print(f"Parser {parser} ile çekme sırasında hata: {e}")

    # Tüm parser'lar denenip başarısız olursa None döndür
    return get_language_data("product_not_found"), None


def letgo_product_info(URL):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.1"
    }

    # Farklı parser'ları sırayla deneyelim
    parsers = ["html.parser", "lxml", "html5lib"]
    for parser in parsers:
        try:
            page = requests.get(URL, headers=headers)
            soup = BeautifulSoup(page.content, parser)

            title_tag = soup.find("h1", class_="_1hJph")
            if title_tag:
                title = title_tag.get_text().strip()

            price_tag = soup.find("span", class_="T8y-z")
            if price_tag:
                price_text = price_tag.get_text()
                price_text = price_text.split(",")[0]
                price = int(price_text.replace("TL", "").replace(".", "").strip())
                price = add_one_if_last_digit_is_nine(price)

            # 1 veya 2 saniye arası rastgele bir gecikme ekle
            time.sleep(random.uniform(0.25, 1))

            return title, price
        except Exception as e:
            print(f"Parser {parser} ile çekme sırasında hata: {e}")

    # Tüm parser'lar denenip başarısız olursa None döndür
    return get_language_data("product_not_found"), None


def check_prices_and_send(products):
    email_body = ""
    current_prices = []
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
            title, price = get_language_data("unkown_product"), 0

        current_prices.append({"title": title, "price": price})

        if price is not None and target_price and price <= int(target_price):
            # Hedef fiyatın altında olduğu bilgisini ekleyelim
            price_difference = int(target_price) - price
            email_body += get_language_data("email_content").format(
                title, price, target_price, price_difference, URL
            )

    if email_body:
        email_manager.send_mail(email_body)

    with open("jsons/newProducts.json", "w") as file:
        json.dump(current_prices, file, indent=4)


try:
    with open("jsons/newProducts.json", "r") as file:
        pass  # Dosya zaten var, bu yüzden bir şey yapmamıza gerek yok
except FileNotFoundError:
    with open("jsons/newProducts.json", "w") as file:
        json.dump({}, file)


def check_prices_and_send_current(current_prices):
    email_body = ""
    for product in current_prices[:-1]:  # "saved_time" anahtarını dikkate alma
        title = product["title"]
        URL = product["URL"]
        price = product["price"]

        # Önceden kaydedilmiş fiyatlar ile karşılaştırma yap
        saved_price = next(
            (item["price"] for item in current_prices[:-1] if item["title"] == title),
            None,
        )

        if saved_price is not None and price < saved_price:
            # Önceden kaydedilen fiyattan daha düşükse e-posta gönder
            email_body += f"{title} - {URL} - {price}₺\n"

    if email_body:
        email_manager.send_mail(email_body)


try:
    with open("jsons/newProducts.json", "r") as file:
        pass  # Dosya zaten var, bu yüzden bir şey yapmamıza gerek yok
except FileNotFoundError:
    with open("jsons/newProducts.json", "w") as file:
        json.dump({}, file)
