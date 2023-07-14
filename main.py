import asyncio
import hashlib
import os
import random

import aiosqlite
import openai
import tiktoken
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import dotenv_values
from openai.error import InvalidRequestError, RateLimitError
from pydub import AudioSegment
from requests.exceptions import ReadTimeout

# from ya_speechkit import get_ya_voice


env = {
    **dotenv_values("/home/ChatGPT_telegram_bot/.env.prod"),
    **dotenv_values(".env.dev"),  # override
}

CHECK_KEY = "check_key_lskJHjf32"
GET_ALL_USERS_COUNT = "get_all_users_count_lskJHjf32"
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
    env["API_KEY_CHATGPT_11"],
    env["API_KEY_CHATGPT_12"],
    env["API_KEY_CHATGPT_13"],
    env["API_KEY_CHATGPT_14"],
    env["API_KEY_CHATGPT_15"],
    env["API_KEY_CHATGPT_16"],
    env["API_KEY_CHATGPT_17"],
    env["API_KEY_CHATGPT_18"],
    env["API_KEY_CHATGPT_19"],
    env["API_KEY_CHATGPT_20"],
    env["API_KEY_CHATGPT_21"],
    env["API_KEY_CHATGPT_22"],
    env["API_KEY_CHATGPT_23"],
    env["API_KEY_CHATGPT_24"],
    env["API_KEY_CHATGPT_25"],
    env["API_KEY_CHATGPT_26"],
    env["API_KEY_CHATGPT_27"],
    env["API_KEY_CHATGPT_28"],
    env["API_KEY_CHATGPT_29"],
    env["API_KEY_CHATGPT_30"],
    env["API_KEY_CHATGPT_31"],
    env["API_KEY_CHATGPT_32"],
    env["API_KEY_CHATGPT_33"],
    env["API_KEY_CHATGPT_34"],
    env["API_KEY_CHATGPT_35"],
    env["API_KEY_CHATGPT_36"],
    env["API_KEY_CHATGPT_37"],
    env["API_KEY_CHATGPT_38"],
    env["API_KEY_CHATGPT_39"],
    env["API_KEY_CHATGPT_40"],
    env["API_KEY_CHATGPT_41"],
    env["API_KEY_CHATGPT_42"],
    env["API_KEY_CHATGPT_43"],
    env["API_KEY_CHATGPT_44"],
    env["API_KEY_CHATGPT_45"],
    env["API_KEY_CHATGPT_46"],
    env["API_KEY_CHATGPT_47"],
    env["API_KEY_CHATGPT_48"],
    env["API_KEY_CHATGPT_49"],
    env["API_KEY_CHATGPT_50"],
    env["API_KEY_CHATGPT_51"],
    env["API_KEY_CHATGPT_52"],
    env["API_KEY_CHATGPT_53"],
    env["API_KEY_CHATGPT_54"],
    env["API_KEY_CHATGPT_55"],
    env["API_KEY_CHATGPT_56"],
    env["API_KEY_CHATGPT_57"],
    env["API_KEY_CHATGPT_58"],
    env["API_KEY_CHATGPT_59"],
    env["API_KEY_CHATGPT_60"],
    env["API_KEY_CHATGPT_61"],
    env["API_KEY_CHATGPT_62"],
    env["API_KEY_CHATGPT_63"],
    env["API_KEY_CHATGPT_64"],
    env["API_KEY_CHATGPT_65"],
    env["API_KEY_CHATGPT_66"],
    env["API_KEY_CHATGPT_67"],
    env["API_KEY_CHATGPT_68"],
    env["API_KEY_CHATGPT_69"],
    env["API_KEY_CHATGPT_70"],
    env["API_KEY_CHATGPT_71"],
    env["API_KEY_CHATGPT_72"],
    env["API_KEY_CHATGPT_73"],
    env["API_KEY_CHATGPT_74"],
    env["API_KEY_CHATGPT_75"],
    env["API_KEY_CHATGPT_76"],
    env["API_KEY_CHATGPT_77"],
    env["API_KEY_CHATGPT_78"],
    env["API_KEY_CHATGPT_79"],
    env["API_KEY_CHATGPT_80"],
    env["API_KEY_CHATGPT_81"],
    env["API_KEY_CHATGPT_82"],
    env["API_KEY_CHATGPT_83"],
    env["API_KEY_CHATGPT_84"],
    env["API_KEY_CHATGPT_85"],
    env["API_KEY_CHATGPT_86"],
    env["API_KEY_CHATGPT_87"],
    env["API_KEY_CHATGPT_88"],
    env["API_KEY_CHATGPT_89"],
    env["API_KEY_CHATGPT_90"],
    env["API_KEY_CHATGPT_91"],
    env["API_KEY_CHATGPT_92"],
    env["API_KEY_CHATGPT_93"],
    env["API_KEY_CHATGPT_94"],
    env["API_KEY_CHATGPT_95"],
    env["API_KEY_CHATGPT_96"],
    env["API_KEY_CHATGPT_97"],
    env["API_KEY_CHATGPT_98"],
    env["API_KEY_CHATGPT_99"],
    env["API_KEY_CHATGPT_100"],
    env["API_KEY_CHATGPT_101"],
    env["API_KEY_CHATGPT_102"],
    env["API_KEY_CHATGPT_103"],
]
BOT_NAME = env["BOT_NAME"]
REKLAMA_MSG = [
    "🔥 Помошь бота ChatGPT трудно оценить, а чашка кофе стоит вполне конкретных денег. Налил себе - <a href='https://pay.freekassa.ru/?m=32133&oa=300&currency=RUB&o=1329664&s=578c86c20802cc09803d7a0e1d97169c&lang=ru&userid=612063160&type=donate'>угости ☕️</a> разработчиков, а то уйдут, спать.",
    "💰 Эххх, еслиб ты знал куда вложить валюту и получать - до <a href='https://crypto-fans.club'>12% годовых</a>",
    "🚀 Bybit удивляет<a href='https://cutt.ly/D7rsbVG'>инвесторов</a>, как в 2017 всех удивил <a href='https://cutt.ly/87rsjAV'>Binance</a>.",
    "🧐 Всего <a href='https://pay.freekassa.ru/?m=32133&oa=300&currency=RUB&o=1329664&s=578c86c20802cc09803d7a0e1d97169c&lang=ru&userid=612063160&type=donate'>ОДНА чашка кофе</a> способна запустить ChatGPT! Не веришь? Плесни кофеку, чтоб не заглохло",
    "💰 Как получать до 12% на валютном вкладе <a href='https://crypto-fans.club'>без геморроя</a>?",
    "🤬 Всё <a href='https://cutt.ly/87rsjAV'>меньше покупок</a> крипты у Binance. <a href='https://cutt.ly/D7rsbVG'>Инвесторы атакуют</a> ByBit.",
    "💰 Криптовалюта - будущее денег? Не, не слышал. ByBit успешно<a href='https://cutt.ly/D7rsbVG'>подражает лидеру</a> рынка",
    "👑 Binance <a href='https://cutt.ly/87rsjAV'>сдаёт позиции</a>. Капитал перетекает в сторону <a href='https://cutt.ly/D7rsbVG'>подражателей</a>.",
    "🚫 У Binance <a href='https://cutt.ly/87rsjAV'>серьёзные проблемы</a>. <a href='https://cutt.ly/D7rsbVG'>Капитал требует</a> свежую кровь.",
    "🧠 Умные активы выбирают умных людей, или <a href='https://cutt.ly/D7rsbVG'>наоборот</a>?",
    "💳 Дебетовую карту <a href='https://unicom24.ru/offer/rs/2srzlgjijs0il?partner=197374'>UnionPay</a>, для оплаты зарубежных сервисов, начали раздавать бесплатно",
    "🛳 Некто, скинул в общий доступ базу операторов круизных путешествий. Более 4200 направлений <a href='https://2my.site/E2Eoaa5'>в открытом доступе</a> по ценам операторов",
    "🤼‍♂️ Лютая схватка монстров ритейла шокировала обывателей. <a href='http://k.gdeslon.ru/ck/9d2999351c9dff9a3c57dbd6f0541a7d8cc2434c/337471'>АШАН</a>, <a href='http://k.gdeslon.ru/ck/9d2999351c9dff9a3c57dbd6f0541a7d8cc2434c/337473'>МАГНИТ</a>, <a href='http://k.gdeslon.ru/ck/9d2999351c9dff9a3c57dbd6f0541a7d8cc2434c/337474'>Пятёрочка</a>, <a href='http://k.gdeslon.ru/ck/9d2999351c9dff9a3c57dbd6f0541a7d8cc2434c/337470'>METRO</a> и <a href='http://k.gdeslon.ru/ck/9d2999351c9dff9a3c57dbd6f0541a7d8cc2434c/337472'>GLOBUS</a> ввели бесплатную доставку.",
]

bot = Bot(token=env["TG_BOT_TOKEN"])
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db_link = env["DB_LINK"]
encoding = tiktoken.get_encoding("cl100k_base")
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")


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
        except Exception as e:
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
        except Exception as e:
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


async def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print(
            "Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301."
        )
        return await num_tokens_from_messages(
            messages, model="gpt-3.5-turbo-0301"
        )
    elif model == "gpt-4":
        print(
            "Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314."
        )
        return await num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4
        tokens_per_name = -1
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3
    return num_tokens


async def make_request(message, api_key_numb, last_msg, is_group=False):
    chance = random.choices((0, 1, 2, 3, 4))
    engine = "gpt-3.5-turbo"
    # добавляем сообщение в контекст
    messages = []
    messages.append({"role": "user", "content": message.text})
    await bot.send_chat_action(message.chat.id, "typing")
    try:
        # проверяем откуда пришло сообщение из чата или из группа
        if is_group:
            num_tokens = await num_tokens_from_messages(messages)
            if num_tokens > 4095:
                raise InvalidRequestError()
            completion = await openai.ChatCompletion.acreate(
                model=engine,
                messages=messages,
            )
            await bot.send_chat_action(message.chat.id, "typing")
            await last_msg.edit_text(
                completion.choices[0]["message"]["content"],
            )
            if chance == [1]:
                await message.answer(
                    random.choices(REKLAMA_MSG)[0],
                    disable_web_page_preview=True,
                    parse_mode="HTML",
                )
            return

        if storage.data.get(str(message.from_id)):
            if not storage.data.get(str(message.from_id)).get("messages"):
                storage.data.get(str(message.from_id))["messages"] = []
            storage.data.get(str(message.from_id))["messages"].append(
                messages[0]
            )
            num_tokens = await num_tokens_from_messages(
                storage.data.get(str(message.from_id))["messages"]
            )
            if num_tokens > 4095:
                storage.data.get(str(message.from_id)).get("messages").pop(1)
                storage.data.get(str(message.from_id)).get("messages").pop(1)
        completion = await openai.ChatCompletion.acreate(
            model=engine,
            messages=storage.data.get(str(message.from_id))["messages"],
        )
        await bot.send_chat_action(message.chat.id, "typing")
        await last_msg.edit_text(
            completion.choices[0]["message"]["content"],
        )
        storage.data.get(str(message.from_id))["messages"].append(
            {
                "role": "assistant",
                "content": completion.choices[0]["message"]["content"],
            }
        )
        if chance == [1]:
            await message.answer(
                random.choices(REKLAMA_MSG)[0],
                disable_web_page_preview=True,
                parse_mode="HTML",
            )

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
    await create_table()
    text = """Приветствую ✌

Я - ChatGPT, крупнейшая языковая модель, созданная OpenAI. 

Я разработана для обработки естественного языка и могу помочь вам с ответами на ваши вопросы.

Просто отправьте мне текстовое сообщение, и я постараюсь дать вам наилучший ответ.

Я умею сохранять контекст разговора, и для обновления контекста набери /new

Удачи! 🤖"""
    await bot.send_chat_action(message.chat.id, "typing")
    last_msg = await message.answer(
        "<code>Сообщение принято. Ждем ответа...</code>", parse_mode="HTML"
    )
    await write_to_db(message)
    await last_msg.edit_text(text)


@dp.message_handler(commands=["help"])
async def send_start(message: types.Message):
    text = """Чтобы начать взаимодействие с ChatGPT, просто отправьте сообщение и бот ответит вам. 

Вы можете задавать ему любые вопросы, он обычно отвечает на них адекватно и быстро. 

Также вы можете использовать бота для выполнения различных задач, например, он может вывести расписание фильмов, погоду, новости, анекдоты и многое другое.

Кроме того, ChatGPT может быть использован для проведения небольших игр и конкурсов с пользователями. 

Возможности бота очень широки, и вы можете экспериментировать и сами пробовать всевозможные примеры работы с ним. Не стесняйтесь обращаться к ChatGPT за помощью, он всегда готов вам помочь!

👋Если вопрос касается сотрудничества, обратитесь к - @Favic0n или @osintall
"""
    await bot.send_chat_action(message.chat.id, "typing")
    last_msg = await message.answer(
        "<code>Сообщение принято. Ждем ответа...</code>", parse_mode="HTML"
    )
    await write_to_db(message)
    await last_msg.edit_text(text)


@dp.message_handler(commands=["new"])
async def send_start(message: types.Message):
    text = """Контекст очищен"""
    await bot.send_chat_action(message.chat.id, "typing")
    last_msg = await message.answer(
        "<code>Сообщение принято. Ждем ответа...</code>", parse_mode="HTML"
    )
    await write_to_db(message)
    if not storage.data.get(str(message.from_id)).get("messages"):
        storage.data.get(str(message.from_id))["messages"] = []
    storage.data.get(str(message.from_id))["messages"].clear()
    await last_msg.edit_text(text)


def md5sign(m, oa, secretWord1, currency, o):
    string = m + ":" + str(oa) + ":" + secretWord1 + ":" + currency + ":" + o
    return hashlib.md5(string.encode("utf-8")).hexdigest()


@dp.message_handler(commands=["donate"])
async def send_donate(message: types.Message):
    secretWord1 = env["secretWord1"]
    url = "https://pay.freekassa.ru/?"

    # m - ID Вашего магазина merchantId
    m = "32133"
    # Сумма платежа
    oa = "300"
    # Валюта платежа
    currency = "RUB"
    # Номер заказа
    o = str(message.message_id)
    # Подпись
    s = md5sign(m, oa, secretWord1, currency, o)
    lang = "ru"
    userid = str(message.from_user.id)
    type = "donate"
    params = f"m={m}&oa={oa}&currency={currency}&o={o}&s={s}&lang={lang}&us_userid={userid}&us_type={type}"

    await bot.send_chat_action(message.chat.id, "typing")
    last_msg = await message.answer(
        "<code>Сообщение принято. Ждем ответа...</code>", parse_mode="HTML"
    )

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
    await last_msg.edit_text(text=text, reply_markup=keyboard)


async def check_key(message):
    key = message.text[19:]
    openai.api_key = key
    try:
        engine = "gpt-3.5-turbo"
        # engine = "gpt-4"
        await openai.ChatCompletion.acreate(
            model=engine, messages=[{"role": "user", "content": message.text}]
        )
        await message.answer(f"Ключ {key} работает.")
    except:
        await message.answer(f"Ключ {key} НЕ рабочий либо истек.")


async def get_all_users_count(message):
    conn = await aiosqlite.connect(db_link)
    cursor = await conn.cursor()
    count = await cursor.execute("""SELECT COUNT("id") FROM user""")
    count = await cursor.fetchone()
    await conn.commit()
    await conn.close()
    await message.answer(f"Всего пользователей: {count[0]}")


@dp.message_handler(content_types=["text"])
async def send_msg_to_chatgpt(message: types.Message):
    api_key_numb = 0
    is_group = False

    if message.chat.type == "supergroup":
        if BOT_NAME not in message.text:
            return
        is_group = True
        message.text = message.text[len(BOT_NAME) + 1 :]

    if CHECK_KEY == message.text[:19]:
        await check_key(message)
        return
    if GET_ALL_USERS_COUNT == message.text:
        await get_all_users_count(message)
        return
    openai.api_key = random.choice(API_KEYS_CHATGPT)
    last_msg = await message.answer(
        "<code>Сообщение принято. Ждем ответа...</code>", parse_mode="HTML"
    )
    await write_to_db(message)
    await make_request(message, api_key_numb, last_msg, is_group)


async def delete_temporary_files(*files):
    # await asyncio.sleep(10)
    loop = asyncio.get_running_loop()
    for file in files:
        try:
            await loop.run_in_executor(None, os.remove, file)
        except Exception as e:
            print(e)


@dp.message_handler(content_types=["voice"])
async def send_transcription(message: types.Message):
    api_key_numb = 0
    is_group = False

    if message.chat.type == "supergroup":
        return

    await bot.send_chat_action(message.chat.id, "typing")
    last_msg = await bot.send_message(
        text="<code>Сообщение принято. Ждем ответа...</code>",
        parse_mode="HTML",
        chat_id=message.chat.id,
        reply_to_message_id=message.message_id,
    )
    try:
        file_id = message.voice.file_id
        voice_file = await bot.get_file(file_id)
        voice_path = await voice_file.download()

        audio = AudioSegment.from_file(voice_path.name)
        mp3_path = f"voice/voice{message.voice.file_id}.mp3"
        audio.export(mp3_path, format="mp3")

        audio_file = open(mp3_path, "rb")
        transcript = await openai.Audio.atranscribe("whisper-1", audio_file)
        await bot.send_chat_action(message.chat.id, "typing")
        if transcript["text"]:
            await last_msg.edit_text(
                f"<code>Ваш запрос: {transcript['text']}</code>",
                parse_mode="HTML",
            )
        else:
            await last_msg.edit_text("К сожалению, не удалось распознать речь")
        message.text = transcript["text"]
        last_msg = await message.answer(
            "<code>Ждем ответа...</code>", parse_mode="HTML"
        )
        await make_request(message, api_key_numb, last_msg, is_group)
    finally:
        audio_file.close()
        voice_path.close()
        await delete_temporary_files(voice_path.name, mp3_path)


if __name__ == "__main__":
    openai.api_key = API_KEYS_CHATGPT[0]
    executor.start_polling(dp, skip_updates=True)
