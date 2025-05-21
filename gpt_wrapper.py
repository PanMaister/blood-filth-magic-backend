# gpt_wrapper.py

import os
import tiktoken
from openai import OpenAI
from dotenv import load_dotenv
from lore_loader import load_lore

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === МІСТО ГРАВЦЯ ===
current_city = None

def set_current_city(city_name: str):
    global current_city
    current_city = city_name

def get_current_city():
    return current_city

# === Лічильник токенів ===
def count_tokens(messages, model="gpt-4.1"):
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")

    num_tokens = 0
    for message in messages:
        num_tokens += 4  # кожне повідомлення має оверхед
        for key, value in message.items():
            num_tokens += len(enc.encode(value))
    num_tokens += 2  # примітка на кінець
    print(f"📏 Скільки токенів у запиті: {num_tokens}")
    return num_tokens

def call_gpt(messages, temperature=0.9, model="gpt-4.1", max_tokens=2000, add_lore=True) -> str:
    """
    Викликає GPT-4o з переданими параметрами.
    Додає приклад сцени та лор міста до контексту автоматично.
    """

    # Завантажити приклад сцени
    example_scene_path = os.path.join("lore", "shared", "example_scene.txt")
    example_scene_text = ""
    if os.path.exists(example_scene_path):
        with open(example_scene_path, "r", encoding="utf-8") as f:
            example_scene_text = f.read()
    else:
        print("[!] Файл прикладу сцени не знайдено.")

    # Завантажити актуальний лор для поточного міста
    from gpt_wrapper import get_current_city
    city_name = get_current_city()
    lore_text = ""
    if city_name:
        from gpt_wrapper import smart_load_city_lore
        lore_text = smart_load_city_lore(city_name, max_tokens=20000)

    # Формуємо фінальні messages
    system_messages = []

    # 1. Приклад сцени
    if example_scene_text:
        system_messages.append({
            "role": "system",
            "content": f"📖 ПРИКЛАД СЦЕНИ ДЛЯ СТИЛЮ:\n{example_scene_text}"
        })

    # 2. Лор тільки по тегу
    if add_lore and lore_text:
        system_messages.append({
            "role": "system",
            "content": f"📚 ЛОР ТІЛЬКИ ПО ТЕГУ:\nВикористовуй тільки фрагменти, що мають тег #{city_name.lower()}.\nНе змішуй різні міста. Якщо тег не співпадає — ігноруй.\n\n{lore_text}"
        })

    full_messages = system_messages + messages

    # Лічимо токени
    count_tokens(full_messages, model=model)

    response = client.chat.completions.create(
        model=model,
        messages=full_messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()

def smart_load_city_lore(city_name: str, max_tokens: int = 20000, model_name="gpt-4o") -> str:
    """
    Завантажує лор міста з пріоритетом: спочатку персонажі і організації, потім решта.
    """
    base_folder = "lore"
    encoding = tiktoken.encoding_for_model(model_name)

    # Список у новому пріоритеті
    priority_files = [
        f"{city_name.lower()}_персонажі.txt",
        f"{city_name.lower()}_організації.txt",
        f"{city_name.lower()}_місто.txt",
        f"{city_name.lower()}_околиці.txt",
        f"{city_name.lower()}_район_людей.txt",
        f"{city_name.lower()}_район_жаболюдів.txt",
        f"{city_name.lower()}_район_дворфів.txt",
        f"{city_name.lower()}_район_ельфів.txt",
        f"{city_name.lower()}_локації.txt",

    ]

    shared_folder = os.path.join(base_folder, "shared")
    shared_files = []

    if os.path.isdir(shared_folder):
        shared_files = [file for file in os.listdir(shared_folder) if file.endswith(".txt")]

    all_files = priority_files + [os.path.join("shared", file) for file in shared_files]

    lore_texts = []
    current_tokens = 0

    for filename in all_files:
        file_path = os.path.join(base_folder, filename)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                tokens = encoding.encode(text)
                if current_tokens + len(tokens) <= max_tokens:
                    lore_texts.append(text)
                    current_tokens += len(tokens)
                else:
                    # Якщо текст перевищує ліміт — більше не додаємо
                    continue
        else:
            print(f"[!] Файл {filename} не знайдено, пропущено.")

    return "\n\n".join(lore_texts)



