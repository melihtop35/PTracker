import json
import email_manager as email_manager
from settings import get_language_data
from selenium import webdriver
from selenium.webdriver.common.by import By
import concurrent.futures


def add_one_if_last_digit_is_nine(number):
    # Sayının son basamağını al
    last_digit = int(str(number)[-1])

    # Son basamak 9 ise
    if last_digit == 9:
        # Sayıya 1 ekle
        number += 1

    return number


def amazon_product_info(URL):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Başlıksız modda çalıştırmak için
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"
    )

    # Selenium'un Chrome WebDriver'ını başlatın
    driver = webdriver.Chrome(options=options)
    # URL'ye git
    driver.get(URL)

    # Ürün adını ve fiyatını bulmak için XPath'leri kullanarak elementleri bul
    try:
        product_name = driver.find_element(
            By.XPATH,
            "/html/body/div[2]/div/div[7]/div[3]/div[4]/div[1]/div/h1/span",
        ).text.strip()

        product_price = driver.find_element(
            By.XPATH,
            "/html/body/div[2]/div/div[7]/div[3]/div[4]/div[12]/div/div/div[3]/div[1]/span[2]/span[2]/span[1]",
        ).text.strip()
        product_price = product_price.split(",")[0]
        product_price = int(product_price.replace("TL", "").replace(".", "").strip())
        product_price = add_one_if_last_digit_is_nine(product_price)

        # WebDriver'ı kapat
        driver.quit()

        return product_name, product_price
    except:
        # Tüm parser'lar denenip başarısız olursa None döndür
        return get_language_data("product_not_found"), None


def akakce_product_info(URL):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Başlıksız modda çalıştırmak için
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"
    )

    # Selenium'un Chrome WebDriver'ını başlatın
    driver = webdriver.Chrome(options=options)
    # URL'ye git
    driver.get(URL)

    # Ürün adını ve fiyatını bulmak için XPath'leri kullanarak elementleri bul
    try:
        product_name = driver.find_element(
            By.XPATH,
            "/html/body/main/div[1]/div[1]/div[1]/h1",
        ).text.strip()

        product_price = driver.find_element(
            By.XPATH,
            "/html/body/main/div[1]/div[1]/div[3]/span[1]/span",
        ).text.strip()
        product_price = product_price.split(",")[0]
        product_price = int(product_price.replace("TL", "").replace(".", "").strip())
        product_price = add_one_if_last_digit_is_nine(product_price)

        # WebDriver'ı kapat
        driver.quit()

        return product_name, product_price
    except:
        # Tüm parser'lar denenip başarısız olursa None döndür
        return get_language_data("product_not_found"), None


def hepsiburada_product_info(URL):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Başlıksız modda çalıştırmak için
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"
    )

    # Selenium'un Chrome WebDriver'ını başlatın
    driver = webdriver.Chrome(options=options)
    # URL'ye git
    driver.get(URL)

    # Ürün adını ve fiyatını bulmak için XPath'leri kullanarak elementleri bul
    try:
        product_name = driver.find_element(
            By.XPATH,
            "/html/body/div[2]/main/div[3]/section[3]/div/div/div[1]/h2",
        ).text.strip()

        product_price = driver.find_element(
            By.XPATH,
            "/html/body/div[2]/main/div[3]/section[1]/div[3]/div/div[4]/div[1]/div[2]/div/div[1]/div[1]/span/span[1]",
        ).text.strip()
        product_name = product_name.replace("Özellikleri", "")
        product_price = product_price.split(",")[0]
        product_price = int(product_price.replace("TL", "").replace(".", "").strip())
        product_price = add_one_if_last_digit_is_nine(product_price)

        # WebDriver'ı kapat
        driver.quit()

        return product_name, product_price
    except:
        # Tüm parser'lar denenip başarısız olursa None döndür
        return get_language_data("product_not_found"), None


def trendyol_product_info(URL):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Başlıksız modda çalıştırmak için
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"
    )

    # Selenium'un Chrome WebDriver'ını başlatın
    driver = webdriver.Chrome(options=options)
    # URL'ye git
    driver.get(URL)

    # Ürün adını ve fiyatını bulmak için XPath'leri kullanarak elementleri bul
    try:
        product_name = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div[5]/main/div/div[2]/div/div[2]/div[2]/div/div[1]/div[1]/div/div/div[1]/h1",
        ).text.strip()

        product_price = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div[5]/main/div/div[2]/div/div[2]/div[2]/div/div[1]/div[1]/div/div/div[3]/div/div/span",
        ).text.strip()
        product_price = product_price.split(",")[0]
        product_price = int(product_price.replace("TL", "").replace(".", "").strip())
        product_price = add_one_if_last_digit_is_nine(product_price)

        # WebDriver'ı kapat
        driver.quit()

        return product_name, product_price
    except:
        # Tüm parser'lar denenip başarısız olursa None döndür
        return get_language_data("product_not_found"), None


def letgo_product_info(URL):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Başlıksız modda çalıştırmak için
    options.add_argument(
        "user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"
    )

    # Selenium'un Chrome WebDriver'ını başlatın
    driver = webdriver.Chrome(options=options)
    # URL'ye git
    driver.get(URL)

    # Ürün adını ve fiyatını bulmak için XPath'leri kullanarak elementleri bul
    try:
        product_name = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/main/div/div/div/div[5]/div[1]/div/section/h1",
        ).text.strip()

        product_price = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/main/div/div/div/div[5]/div[1]/div/section/span",
        ).text.strip()
        product_price = product_price.split(",")[0]
        product_price = int(product_price.replace("TL", "").replace(".", "").strip())
        product_price = add_one_if_last_digit_is_nine(product_price)

        # WebDriver'ı kapat
        driver.quit()

        return product_name, product_price
    except:
        # Tüm parser'lar denenip başarısız olursa None döndür
        return get_language_data("product_not_found"), None


def check_prices_and_send(products):
    email_body = ""
    current_prices = []

    def fetch_product_info(URL):
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
            title, price = get_language_data("unknown_product"), 0
        return title, price

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_product = {
            executor.submit(fetch_product_info, product["URL"]): product
            for product in products
        }
        for future in concurrent.futures.as_completed(future_to_product):
            product = future_to_product[future]
            try:
                title, price = future.result()
                current_prices.append({"title": title, "price": price})

                if (
                    price is not None
                    and product["target_price"]
                    and price <= int(product["target_price"])
                ):
                    price_difference = int(product["target_price"]) - price
                    email_body += get_language_data("email_content").format(
                        title,
                        price,
                        product["target_price"],
                        price_difference,
                        product["URL"],
                    )
            except Exception as exc:
                print(exc)

    if email_body:
        email_manager.send_mail(email_body)

    with open("jsons/newProducts.json", "w") as file:
        json.dump(current_prices, file, indent=4)


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
