import aiofiles
import requests
from dotenv import dotenv_values

env = {
    **dotenv_values("/home/ChatGPT_telegram_bot/.env.prod"),
    **dotenv_values(".env.dev"),  # override
}
folder_id = env["YA_FOLDER_ID"]
api_key = env[
    "YA_SECRET_API_KEY"
]  # ID ресурса Key, который принадлежит сервисному аккаунту.
url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
headers = {"Authorization": "Api-Key " + api_key}


async def synthesize(text):
    data = {
        "folderId": folder_id,
        "text": text,
        "lang": "ru-RU",
        # 'voice':'alena', # премиум - жрет в 10 раз больше денег
        "voice": "jane",  # oksana
        "emotion": "evil",
        "speed": "1.0",
        # по умолчанию конвертит в oggopus, кот никто не понимает, зато занимат мало места
        "format": "mp3",
        "sampleRateHertz": 48000,
    }

    with requests.post(url, headers=headers, data=data, stream=True) as resp:
        if resp.status_code != 200:
            raise RuntimeError(
                "Invalid response received: code: %d, message: %s"
                % (resp.status_code, resp.text)
            )

        for chunk in resp.iter_content(chunk_size=None):
            yield chunk


async def get_ya_voice(text, file_id):
    """Пишет чанки в вайл."""

    filename = f"voice/audio{file_id}.mp3"
    async with aiofiles.open(filename, "wb") as f:
        async for audio_content in synthesize(text):
            await f.write(audio_content)

    return filename, f
