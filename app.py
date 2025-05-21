from flask import Flask, request, jsonify
import os

# Імпортуємо з ТВОГО основного файлу — там вже всі звʼязки з gpt_wrapper і lore_loader!
from chat_clear_ready import handle_player_action, reset_hero

app = Flask(__name__)

# === Основний endpoint для гри ===
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    email = data.get("email")
    slot = data.get("slot")
    city = data.get("city")
    user_input = data.get("user_input")
    is_new_game = data.get("is_new_game", False)

    # Валідація даних (базова)
    if not email or not slot or not city or user_input is None:
        return jsonify({"error": "Missing required fields"}), 400

    # Весь ігровий процес і всі імпорти живуть у chat_clear_ready
    response = handle_player_action(
        email=email,
        slot=slot,
        city=city,
        user_input=user_input,
        is_new_game=is_new_game
    )
    return jsonify({"response": response})

# === Endpoint для очищення героя (стерти прогрес) ===
@app.route("/reset_hero", methods=["POST"])
def reset_hero_endpoint():
    data = request.get_json()
    email = data.get("email")
    slot = data.get("slot")
    if not email or not slot:
        return jsonify({"success": False, "error": "Missing email or slot"}), 400

    # Функція очищення має бути у chat_clear_ready і працювати з усіма залежностями
    result = reset_hero(email, slot)
    return jsonify({"success": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
