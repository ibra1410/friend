import os
import requests
import wget
from pyrogram import Client, filters, enums
from youtube_search import YoutubeSearch
from yt_dlp import YoutubeDL

# إعدادات البوت (تأكد من استبدال القيم بأخرى صحيحة)
API_ID = '27252915'
API_HASH = '4eb2ca0eabde2aa09cbbb58dac1958e9'
BOT_TOKEN = '7408633253:AAFO8nD7XrVqa2L-XMzJoXpZ7XnVoQEy1fA'
OWNER = ["xibra_v"]  # تأكد من إضافة اسم المستخدم الخاص بك هنا

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
        results = YoutubeSearch(query, max_results=6).to_dict()
        text = ""
        for i in range(6):
            text += f"عنوان - {results[i]['title']}\n"
            text += f"المدة - {results[i]['duration']}\n"
            text += f"المشاهدات - {results[i]['views']}\n"
            text += f"القناة - {results[i]['channel']}\n"
            text += f"https://youtube.com{results[i]['url_suffix']}\n\n"
        await m.edit(text, disable_web_page_preview=True)
    except Exception as e:
        await message.reply_text(str(e))

def remove_if_exists(path):
    if os.path.exists(path):
        os.remove(path)

# وظيفة تنزيل الأغاني أو الفيديوهات
@app.on_message(filters.command(["/song", "/video", "نزل", "تنزيل", "حمل", "تحميل"], ""))
async def downloaded(client: Client, message):
    if len(message.command) == 1:
        if message.chat.type == enums.ChatType.PRIVATE:
            ask = await client.ask(message.chat.id, "ارسل اسم الأغنية الآن")
            query = ask.text
            m = await ask.reply_text("**جاري البحث، انتظر قليلاً 🔎**")
        else:
            try:
                ask = await client.ask(message.chat.id, "ارسل اسم الأغنية الآن.", filters=filters.user(message.from_user.id), reply_to_message_id=message.id, timeout=8)
            except:
                return
            query = ask.text
            m = await ask.reply_text("**جاري البحث، انتظر قليلاً ⚡**")
    else:
        query = message.text.split(None, 1)[1]
        m = await message.reply_text("**جاري البحث، انتظر قليلاً 🔎**")
    
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]' if message.command[0] in ["/song", "نزل", "تنزيل"] else 'best',
        'keepvideo': True,
        'prefer_ffmpeg': False,
        'geo_bypass': True,
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
    }

    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        duration = results[0]["duration"]
    except Exception as e:
        await m.edit("فشل العثور على النتيجة المطلوبة ❌")
        return

    try:
        await m.edit("جاري التحميل، انتظر قليلاً ⚡")
    except:
        return

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = f"• uploader @{OWNER[0]} "
        host = str(info_dict["uploader"])
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(float(dur_arr[i])) * secmul
            secmul *= 60
        try:
            await m.edit("جاري التحميل، انتظر قليلاً ⚡")
        except:
            pass
        await message.reply_audio(
            audio_file,
            caption=rep,
            performer=host,
            thumb=thumb_name,
            title=title,
            duration=dur,
        )
        await m.delete()

    except Exception as e:
        await m.edit("حدث خطأ أثناء التحميل، انتظر حتى يتم إصلاحه")
    finally:
        remove_if_exists(audio_file)
        remove_if_exists(thumb_name)

app.run()
