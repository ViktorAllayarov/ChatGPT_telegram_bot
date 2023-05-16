from dotenv import dotenv_values
import openai
import random
import sqlite3
import telebot
from requests.exceptions import ReadTimeout
from openai.error import RateLimitError, InvalidRequestError


CHECK_KEY = "check_key_lskJHjf32"

env = {
    **dotenv_values("/home/ChatGPT_telegram_bot/.env.prod"),
    **dotenv_values(".env.dev"),  # override
}

API_KEYS_CHATGPT = [
    env["API_KEY_CHATGPT"],
    env["API_KEY_CHATGPT_1"],
    env["API_KEY_CHATGPT_2"],
    env["API_KEY_CHATGPT_3"],
    env["API_KEY_CHATGPT_4"],
    env["API_KEY_CHATGPT_5"],
    env["API_KEY_CHATGPT_6"],
    env["API_KEY_CHATGPT_7"],
    env["API_KEY_CHATGPT_8"],
    env["API_KEY_CHATGPT_9"],
    env["API_KEY_CHATGPT_10"],
]
bot = telebot.TeleBot(env["TG_BOT_TOKEN"])
db_link = env["DB_LINK"]

REKLAMA_MSG = [
    "🔥 Валютный вклад для россиян (до 12% годовых) <a href='https://crypto-fans.club'>crypto-fans.club</a>",
    "🔥 Если думаешь купить или продать криптовалюту, рекомендую <a href='https://cutt.ly/D7rsbVG'>Bybit</a>",
    "🔥 Если думаешь купить или продать криптовалюту, рекомендую <a href='https://cutt.ly/87rsjAV'>Binance</a>",
]


def write_to_db(message):
    conn = sqlite3.connect(db_link)
    cursor = conn.cursor()
    select_id = cursor.execute(
        "SELECT id FROM user WHERE chat_id = ?", (str(message.chat.id),)
    )
    select_id = select_id.fetchone()
    if select_id:
        try:
            cursor.execute(
                "UPDATE user SET last_msg=?, last_login=? WHERE chat_id=?",
                (
                    message.text,
                    str(message.date),
                    str(message.chat.id),
                ),
            )
        except:
            conn.commit()
            conn.close()
            bot.send_message(
                612063160,
                f"Ошибка при добавлении (INSERT) данных в базе Пользователь: {message.chat.id}",
            )
    else:
        try:
            cursor.execute(
                "INSERT INTO user (chat_id, last_login, username, first_name, last_name, last_msg) VALUES (?,?,?,?,?,?)",
                (
                    str(message.chat.id),
                    str(message.date),
                    message.chat.username if message.chat.username else "-",
                    message.chat.first_name
                    if message.chat.first_name
                    else "-",
                    message.chat.last_name if message.chat.last_name else "-",
                    message.text,
                ),
            )
        except:
            conn.commit()
            conn.close()
            bot.send_message(
                612063160,
                f"Ошибка при добавлении (INSERT) данных в базе Пользователь: {message.chat.id}",
            )
    conn.commit()
    conn.close()


def check_length(answer, list_of_answers):
    if len(answer) > 4090 and len(answer) < 409000:
        list_of_answers.append(answer[0:4090] + "...")
        check_length(answer[4091:], list_of_answers)
    else:
        list_of_answers.append(answer[0:])
        return list_of_answers


def make_request(message, api_key_numb):
    chance = random.choices((0, 1, 2, 3, 4, 5, 6, 7, 8, 9))
    try:
        # engine = "text-davinci-003"
        engine = "gpt-3.5-turbo"
        # engine = "gpt-4"
        # completion = openai.Completion.create(
        #     engine=engine,
        #     prompt=message.text,
        #     temperature=0.5,
        #     max_tokens=4090,
        # )
        completion = openai.ChatCompletion.create(
            model=engine, messages=[{"role": "user", "content": message.text}]
        )
        # print(completion.choices[0]["message"])
        list_of_answers = check_length(
            completion.choices[0]["message"]["content"], []
        )

        if list_of_answers:
            for piece_of_answer in list_of_answers:
                bot.send_message(message.chat.id, piece_of_answer)
            if chance == [1]:
                bot.send_message(
                    message.chat.id,
                    random.choices(REKLAMA_MSG),
                    disable_web_page_preview=True,
                    parse_mode="HTML",
                )
        else:
            make_request(message, api_key_numb)
    except RateLimitError:
        if api_key_numb < len(API_KEYS_CHATGPT) - 1:
            api_key_numb += 1
            openai.api_key = API_KEYS_CHATGPT[api_key_numb]
            make_request(message, api_key_numb)
        else:
            if not key_end:
                bot.send_message(
                    612063160,
                    f"Ключи закончились!!!",
                )
            key_end = True
            bot.send_message(
                message.chat.id,
                "ChatGPT в данный момент перегружен запросами, пожалуйста повторите свой запрос чуть позже.",
            )
    except ReadTimeout:
        bot.send_message(
            message.chat.id,
            "ChatGPT в данный момент перегружен запросами, пожалуйста повторите свой запрос чуть позже.",
        )
    except InvalidRequestError:
        bot.send_message(
            message.chat.id,
            "Максимальная длина контекста составляет около 3000 слов, ответ превысил длину контекста. Пожалуйста, повторите вопрос, либо перефразируйте его.",
        )


def create_table():
    """Create table if not exists."""

    conn = sqlite3.connect(db_link)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            last_login TEXT,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            last_msg TEXT
        );
        """
    )
    conn.commit()
    conn.close()


@bot.message_handler(commands=["start"])
def send_start(message):
    text = """Приветствую ✌

Я - ChatGPT, крупнейшая языковая модель, созданная OpenAI. 

Я разработана для обработки естественного языка и могу помочь вам ответить на вопросы, 
обсудить темы или предоставить информацию на различные темы.

🔥В том числе на русском языке....🔥

👇Я постараюсь ответить на твои вопросы👇
"""
    write_to_db(message)
    bot.send_message(message.chat.id, text)


def check_key(message):
    key = message.text[19:]
    openai.api_key = key
    try:
        # engine = "text-davinci-003"
        # completion = openai.Completion.create(
        #     engine=engine,
        #     prompt=message.text,
        #     temperature=0.5,
        #     max_tokens=1000,
        # )
        engine = "gpt-3.5-turbo"
        # engine = "gpt-4"
        completion = openai.ChatCompletion.create(
            model=engine, messages=[{"role": "user", "content": message.text}]
        )
        bot.send_message(message.chat.id, f"Ключ {key} работает.")
    except:
        bot.send_message(message.chat.id, f"Ключ {key} НЕ рабочий либо истек.")


@bot.message_handler(content_types=["text"])
def send_msg_to_chatgpt(message):
    if CHECK_KEY == message.text[:19]:
        check_key(message)
        return
    api_key_numb = 0
    openai.api_key = random.choice(API_KEYS_CHATGPT)
    write_to_db(message)
    make_request(message, api_key_numb)


if __name__ == "__main__":
    key_end = False
    create_table()
    target = bot.infinity_polling()
