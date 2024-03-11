import json


def save_settings_to_json(settings):
    with open("settings.json", "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def load_settings_from_json():
    try:
        with open("settings.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"minimize_to_tray": False, "button_text": "600", "language": "Türkçe"}


def get_language_data(key):
    settings = load_settings_from_json()
    global language_data  # mevcut dil verisini saklamak için global olarak tanımlıyoruz
    with open("language_data.json", "r", encoding="utf-8") as lang_file:
        language_data = json.load(lang_file)

    # settings["language"] değerine göre doğru dilin altındaki öğeleri döndür
    return language_data[settings["language"]].get(key, "")
