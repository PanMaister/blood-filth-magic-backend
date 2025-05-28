import os

def load_lore(city_name: str) -> str:
    base_folder = "lore"
    lore_texts = []
    city_name = city_name.replace(" ", "_")

    city_files = [
        f"{city_name.lower()}_місто.txt",
        f"{city_name.lower()}_околиці.txt",
        f"{city_name.lower()}_локації.txt",
        f"{city_name.lower()}_персонажі.txt",
        f"{city_name.lower()}_організації.txt",
        f"{city_name.lower()}_район_дворфів.txt",
        f"{city_name.lower()}_район_ельфів.txt",
        f"{city_name.lower()}_район_жаболюдів.txt",
        f"{city_name.lower()}_район_людей.txt",
    ]

    shared_folder = os.path.join(base_folder, "shared")
    shared_files = []

    if os.path.isdir(shared_folder):
        shared_files = [os.path.join("shared", file) for file in os.listdir(shared_folder) if file.endswith(".txt")]

    all_files = shared_files + city_files

    for filename in all_files:
        file_path = os.path.join(base_folder, filename)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                lore_texts.append(file.read())
        else:
            print(f"[!] Файл {filename} не знайдено, пропущено.")

    if lore_texts:
        return "\n\n".join(lore_texts)
    else:
        return ""
