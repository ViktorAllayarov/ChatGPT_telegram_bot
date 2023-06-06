from dotenv import dotenv_values
import openai
import random
import aiosqlite
import hashlib
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor, types
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

bot = Bot(token=env["TG_BOT_TOKEN"])
dp = Dispatcher(bot)
db_link = env["DB_LINK"]

REKLAMA_MSG = [
    "🔥 Валютный вклад для россиян (до 12% годовых) <a href='https://crypto-fans.club'>crypto-fans.club</a>",
    "🔥 Если думаешь купить или продать криптовалюту, рекомендую <a href='https://cutt.ly/D7rsbVG'>Bybit</a>",
    "🔥 Если думаешь купить или продать криптовалюту, рекомендую <a href='https://cutt.ly/87rsjAV'>Binance</a>",
]


async def write_to_db(message):
    conn = await aiosqlite.connect(db_link)
    cursor = await conn.cursor()
    select_id = await cursor.execute(
        "SELECT id FROM user WHERE chat_id = ?", (str(message.chat.id),)
    )
    select_id = await select_id.fetchone()
    if select_id:
        try:
            await cursor.execute(
                "UPDATE user SET last_msg=?, last_login=? WHERE chat_id=?",
                (
                    message.text,
                    str(message.date),
                    str(message.chat.id),
                ),
            )
        except:
            await conn.commit()
            await conn.close()
            await bot.send_message(
                612063160,
                f"Ошибка при добавлении (INSERT) данных в базе Пользователь: {message.chat.id}",
            )
    else:
        try:
            await cursor.execute(
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
            await conn.commit()
            await conn.close()
            await bot.send_message(
                612063160,
                f"Ошибка при добавлении (INSERT) данных в базе Пользователь: {message.chat.id}",
            )
    await conn.commit()
    await conn.close()


def check_length(answer, list_of_answers):
    if len(answer) > 4090 and len(answer) < 409000:
        list_of_answers.append(answer[0:4090] + "...")
        check_length(answer[4091:], list_of_answers)
    else:
        list_of_answers.append(answer[0:])
        return list_of_answers


async def make_request(message, api_key_numb, last_msg):
    chance = random.choices((0, 1, 2, 3, 4, 5, 6, 7, 8, 9))
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        engine = "gpt-3.5-turbo"
        completion = openai.ChatCompletion.create(
            model=engine, messages=[{"role": "user", "content": message.text}]
        )
        list_of_answers = check_length(
            completion.choices[0]["message"]["content"], []
        )
        await bot.send_chat_action(message.chat.id, "typing")
        if list_of_answers:
            for piece_of_answer in list_of_answers:
                await bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=last_msg.message_id,
                    text=piece_of_answer,
                )
            if chance == [1]:
                await message.answer(
                    random.choices(REKLAMA_MSG),
                    disable_web_page_preview=True,
                    parse_mode="HTML",
                )
        else:
            await make_request(message, api_key_numb, last_msg)
    except RateLimitError:
        if api_key_numb < len(API_KEYS_CHATGPT) - 1:
            api_key_numb += 1
            openai.api_key = API_KEYS_CHATGPT[api_key_numb]
            await make_request(message, api_key_numb)
        else:
            if not key_end:
                await bot.send_message(
                    612063160,
                    f"Ключи закончились!!!",
                )
            key_end = True
            await message.answer(
                "ChatGPT в данный момент перегружен запросами, пожалуйста повторите свой запрос чуть позже.",
            )
    except ReadTimeout:
        await message.answer(
            "ChatGPT в данный момент перегружен запросами, пожалуйста повторите свой запрос чуть позже.",
        )
    except InvalidRequestError:
        await message.answer(
            "Максимальная длина контекста составляет около 3000 слов, ответ превысил длину контекста. Пожалуйста, повторите вопрос, либо перефразируйте его.",
        )


async def create_table():
    """Create table if not exists."""

    conn = await aiosqlite.connect(db_link)
    cursor = await conn.cursor()
    await cursor.executescript(
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

        CREATE TABLE IF NOT EXISTS donate(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount TEXT,
            date TEXT,
            FOREIGN KEY(user_id) REFERENCES user(id)
        );

        CREATE TABLE IF NOT EXISTS premium(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount TEXT,
            date TEXT,
            FOREIGN KEY(user_id) REFERENCES user(id)
        );
        """
    )
    await conn.commit()
    await conn.close()


@dp.message_handler(commands=["start"])
async def send_start(message: types.Message):
    text = """Приветствую ✌

Я - ChatGPT, крупнейшая языковая модель, созданная OpenAI. 

Я разработана для обработки естественного языка и могу помочь вам с ответами на ваши вопросы.

Просто отправьте мне текстовое сообщение, и я постараюсь дать вам наилучший ответ.

Пожалуйста, имейте в виду, что я являюсь компьютерной программой и мои ответы не всегда могут быть точными или актуальными.

Удачи! 🤖"""
    await write_to_db(message)
    await message.answer(text)


@dp.message_handler(commands=["help"])
async def send_start(message: types.Message):
    text = """Приветствую ✌

Введи запрос и я отвечу на него, постараюсь поддержать разговор, предоставить информацию.


"""
    await write_to_db(message)
    await message.answer(text)


def md5sign(m, oa, secretWord1, currency, o):
    string = m + ":" + str(oa) + ":" + secretWord1 + ":" + currency + ":" + o
    return hashlib.md5(string.encode("utf-8")).hexdigest()


@dp.message_handler(commands=["donate"])
async def send_donate(message: types.Message):
    secretWord1 = "Jou^VC4buX_[1x?"
    url = "https://pay.freekassa.ru/?"

    # m - ID Вашего магазина merchantId
    m = "32133"
    # Сумма платежа
    oa = "200"
    # Валюта платежа
    currency = "RUB"
    # Номер заказа
    o = str(message.message_id)
    # Подпись
    s = md5sign(m, oa, secretWord1, currency, o)
    lang = "ru"
    userid = str(message.from_user.id)
    type = "donate"
    params = f"m={m}&oa={oa}&currency={currency}&o={o}&s={s}&lang={lang}&userid={userid}&type={type}"

    inline_btn_1 = types.InlineKeyboardButton(
        text="Угостить ☕️", url=url + params
    )
    keyboard = types.InlineKeyboardMarkup(
        row_width=1,
    )
    keyboard.add(inline_btn_1)
    text = """Бот ChatGPT работает бесплатно, но Вы всегда можете угостить чашечкой кофе ☕️ разработчиков - глядишь чего полезного изобретут🙏

ChatGPT bot is free, but you can always buy a cup of coffee ☕️ developers - see what they invent🙏
    """
    await message.reply(
        text,
        reply_markup=keyboard,
    )


async def check_key(message):
    key = message.text[19:]
    openai.api_key = key
    try:
        engine = "gpt-3.5-turbo"
        # engine = "gpt-4"
        await openai.ChatCompletion.create(
            model=engine, messages=[{"role": "user", "content": message.text}]
        )
        await message.answer(f"Ключ {key} работает.")
    except:
        await message.answer(f"Ключ {key} НЕ рабочий либо истек.")


@dp.message_handler(content_types=["text"])
async def send_msg_to_chatgpt(message: types.Message):
    if CHECK_KEY == message.text[:19]:
        check_key(message)
        return
    api_key_numb = 0
    openai.api_key = random.choice(API_KEYS_CHATGPT)
    last_msg = await message.answer(
        "<code>Сообщение принято. Ждем ответа...</code>", parse_mode="HTML"
    )
    await write_to_db(message)
    await make_request(message, api_key_numb, last_msg)


if __name__ == "__main__":
    openai.api_key = API_KEYS_CHATGPT[0]
    executor.start_polling(dp, skip_updates=True)
