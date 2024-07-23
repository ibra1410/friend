import os
import requests
from pyrogram import Client, filters, enums
from youtube_search import YoutubeSearch
from yt_dlp import YoutubeDL

# إعدادات البوت (تأكد من استبدال القيم بأخرى صحيحة)
API_ID = '27252915'
API_HASH = '4eb2ca0eabde2aa09cbbb58dac1958e9'
BOT_TOKEN = '7408633253:AAFO8nD7XrVqa2L-XMzJoXpZ7XnVoQEy1fA'
OWNER = ["xibra_v"]

app = Client("music_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# وظيفة البحث عن الفيديوهات على يوتيوب
@app.on_message(filters.command(["بحث"], ""))
async def ytsearch(client, message):
    try:
        if len(message.command) == 1:
            await message.reply_text("بحث: اكتب شيئاً للبحث ☢️")
            return
        
        query = message.text.split(None, 1)[1]
        m = await message.reply_text("جاري البحث، انتظر قليلاً ♻️")

        # استخدام طلب بحث سريع
        results = YoutubeSearch(query, max_results=6).to_dict()
        if not results:
            await m.edit("لم يتم العثور على نتائج.")
            return

        text = ""
        for result in results:
            text += f"عنوان - {result['title']}\n"
            text += f"المدة - {result['duration']}\n"
            text += f"المشاهدات - {result['views']}\n"
            text += f"القناة - {result['channel']}\n"
            text += f"https://youtube.com{result['url_suffix']}\n\n"
        
        await m.edit(text, disable_web_page_preview=True)
    except Exception as e:
        await message.reply_text(f"حدث خطأ: {str(e)}")

def remove_if_exists(path):
    if os.path.exists(path):
        os.remove(path)

# وظيفة تنزيل الأغاني أو الفيديوهات
@app.on_message(filters.command(["/song", "/video", "نزل", "تنزيل", "حمل", "تحميل"], ""))
async def downloaded(client: Client, message):
    try:
        if len(message.command) == 1:
            if message.chat.type == enums.ChatType.PRIVATE:
                ask = await client.ask(message.chat.id, "ارسل اسم الأغنية الآن")
                query = ask.text
                m = await ask.reply_text("**جاري البحث، انتظر قليلاً 🔎**")
            else:
                ask = await client.ask(message.chat.id, "ارسل اسم الأغنية الآن.", filters=filters.user(message.from_user.id), reply_to_message_id=message.id, timeout=8)
                query = ask.text
                m = await ask.reply_text("**جاري البحث، انتظر قليلاً ⚡**")
        else:
            query = message.text.split(None, 1)[1]
            m = await message.reply_text("**جاري البحث، انتظر قليلاً 🔎**")

        ydl_opts = {
            'format': 'bestaudio[ext=m4a]' if message.command[0] in ["/song", "نزل", "تنزيل"] else 'best',
            'keepvideo': True,
            'geo_bypass': True,
            'outtmpl': '%(title)s.%(ext)s',
            'quiet': True,
        }

        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await m.edit("فشل العثور على النتيجة المطلوبة ❌")
            return

        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        duration = results[0]["duration"]

        await m.edit("جاري التحميل، انتظر قليلاً ⚡")

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.download([link])

        rep = f"• uploader @{OWNER[0]} "
        host = str(info_dict["uploader"])
        dur = sum(int(x) * 60**i for i, x in enumerate(reversed(duration.split(":"))))

        await message.reply_audio(
            audio_file,
            caption=rep,
            performer=host,
            title=title,
            duration=dur,
        )
        await m.delete()

    except Exception as e:
        await m.edit(f"حدث خطأ أثناء التحميل: {str(e)}")
    finally:
        remove_if_exists(audio_file)
        remove_if_exists(thumb_name)

app.run()
