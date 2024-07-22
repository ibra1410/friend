import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from sudo import handle_report, handle_ban, handle_unban, handle_clear_bans

TOKEN = '7408633253:AAFO8nD7XrVqa2L-XMzJoXpZ7XnVoQEy1fA'
bot = telebot.TeleBot(TOKEN)

admin_id = 7426723728
banned_users = set()
reported_messages = {}

# قائمة كبيرة من الاهتمامات
interests_list = [
    'رياضة', 'برمجة', 'سفر', 'طبخ', 'قراءة', 'أفلام', 'موسيقى', 'ألعاب الفيديو',
    'تصوير', 'فنون', 'كتابة', 'رسم', 'يوغا', 'مسرح', 'حدائق', 'رحلات', 'سيارات', 'دراجات',
    'حيوانات أليفة', 'تسوق', 'موضة', 'كوميديا', 'رقص', 'تنمية بشرية', 'شعر', 'لغات',
    'تكنولوجيا', 'علوم', 'ثقافة', 'تاريخ', 'جغرافيا', 'سياسة', 'اقتصاد', 'تصميم', 'ديكور'
]

# تخزين اهتمامات المستخدمين وجلسات الدردشة
user_interests = {}
chat_sessions = {}

# رسالة الترحيب وفكرة البوت
welcome_message = (
    "مرحبًا بك في بوت الصداقة!\n\n"
    "فكرة البوت هي مساعدتك في العثور على أصدقاء جدد بناءً على اهتماماتك المشتركة.\n"
    "استخدم الأوامر التالية:\n"
    "- /set_interest لتحديد اهتماماتك\n"
    "- /find_friend للعثور على أصدقاء جدد\n"
    "- /report للإبلاغ عن محتوى\n"
    "- /exit لإنهاء الدردشة\n"
)

# رسالة الأوامر
commands_message = (
    "هذه هي الأوامر المتاحة:\n"
    "- /set_interest لتحديد اهتماماتك\n"
    "- /find_friend للعثور على أصدقاء جدد\n"
    "- /report للإبلاغ عن محتوى\n"
    "- /exit لإنهاء الدردشة\n"
)

# رسالة الترحيب للمطور
admin_welcome_message = (
    "أهلا بك عزيزي المطور الأساسي!\n\n"
    "هذه هي أوامر الأعضاء:\n"
    "- /set_interest لتحديد اهتماماتك\n"
    "- /find_friend للعثور على أصدقاء جدد\n"
    "- /report للإبلاغ عن محتوى\n"
    "- /exit لإنهاء الدردشة\n\n"
    "وهذه هي أوامر المطور:\n"
    "- /ban <user_id> لحظر المستخدم\n"
    "- /unban <user_id> لإلغاء حظر المستخدم\n"
    "- /clear_bans لمسح قائمة المحظورين\n"
)

# وظيفة البدء
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id == admin_id:
        bot.reply_to(message, admin_welcome_message)
    else:
        markup = InlineKeyboardMarkup()
        button = InlineKeyboardButton("الأوامر", callback_data="commands")
        markup.add(button)
        bot.reply_to(message, welcome_message, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "commands")
def show_commands(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=commands_message)

# وظيفة تعيين الاهتمامات
@bot.message_handler(commands=['set_interest'])
def set_interest(message):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [KeyboardButton(interest) for interest in interests_list]
    markup.add(*buttons)
    bot.reply_to(message, "اختر اهتماماتك من القائمة أدناه:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in interests_list)
def handle_interest_selection(message):
    user_id = message.from_user.id
    interest = message.text

    if user_id not in user_interests:
        user_interests[user_id] = []

    if interest not in user_interests[user_id]:
        user_interests[user_id].append(interest)
        bot.reply_to(message, f"تم إضافة {interest} إلى اهتماماتك!")

    # عرض الخيارات المتبقية بعد اختيار المستخدم للاهتمامات
    remaining_interests = [i for i in interests_list if i not in user_interests[user_id]]
    if remaining_interests:
        markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buttons = [KeyboardButton(interest) for interest in remaining_interests]
        markup.add(*buttons)
        bot.send_message(user_id, "اختر المزيد من الاهتمامات أو اكتب /done عند الانتهاء.", reply_markup=markup)
    else:
        bot.send_message(user_id, "لقد اخترت كل الاهتمامات المتاحة. اكتب /done عند الانتهاء.", reply_markup=ReplyKeyboardRemove())

@bot.message_handler(commands=['done'])
def finish_setting_interests(message):
    user_id = message.from_user.id
    if user_id in user_interests:
        bot.reply_to(message, "تم حفظ اهتماماتك بنجاح! يمكنك الآن استخدام الأمر /find_friend للعثور على أصدقاء جدد.", reply_markup=ReplyKeyboardRemove())
    else:
        bot.reply_to(message, "يرجى تحديد اهتماماتك أولاً باستخدام /set_interest.", reply_markup=ReplyKeyboardRemove())

# وظيفة العثور على أصدقاء
@bot.message_handler(commands=['find_friend'])
def find_friend(message):
    user_id = message.from_user.id
    if user_id not in user_interests:
        bot.reply_to(message, "يرجى تحديد اهتماماتك أولاً باستخدام /set_interest.")
        return

    user_interest = set(user_interests[user_id])
    potential_friends = []

    for uid, interests in user_interests.items():
        if uid != user_id and user_interest & set(interests):
            potential_friends.append(uid)

    if potential_friends:
        friend_id = potential_friends[0]
        chat_sessions[user_id] = friend_id
        chat_sessions[friend_id] = user_id

        markup = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button = KeyboardButton("ابدأ الدردشة")
        markup.add(button)

        bot.send_message(user_id, f"وجدنا صديقًا مشتركًا في الاهتمامات! {friend_id}", reply_markup=markup)
        bot.send_message(friend_id, "تم ربطك بصديق مشترك في الاهتمامات!", reply_markup=markup)
    else:
        bot.reply_to(message, "لم نجد أصدقاء مشتركين في الاهتمامات في الوقت الحالي.")

# وظيفة بدء الدردشة
@bot.message_handler(func=lambda message: message.text == "ابدأ الدردشة")
def start_chat(message):
    user_id = message.from_user.id
    if user_id in chat_sessions:
        friend_id = chat_sessions[user_id]
        if friend_id == admin_id:
            bot.send_message(user_id, "أنت تتحدث الآن مع المطور إبراهيم.")
        bot.send_message(user_id, "ابدأ الدردشة الآن!")
        bot.send_message(friend_id, "ابدأ الدردشة الآن!")

        # إزالة زر "ابدأ الدردشة" بعد الضغط عليه
        markup = ReplyKeyboardRemove()
        bot.send_message(user_id, "لقد بدأت الدردشة!", reply_markup=markup)
        bot.send_message(friend_id, "لقد بدأت الدردشة!", reply_markup=markup)
    else:
        bot.reply_to(message, "لم يتم العثور على جلسة دردشة.")

# وظيفة إنهاء الدردشة
@bot.message_handler(commands=['exit'])
def exit_chat(message):
    user_id = message.from_user.id
    if user_id in chat_sessions:
        friend_id = chat_sessions[user_id]
        bot.send_message(friend_id, "تم إنهاء الدردشة من قبل الطرف الآخر.")
        bot.send_message(user_id, "تم إنهاء الدردشة.")
        del chat_sessions[user_id]
        del chat_sessions[friend_id]
    else:
        bot.reply_to(message, "أنت لست في جلسة دردشة حالياً.")

# وظيفة معالجة الرسائل وتوجيهها
@bot.message_handler(func=lambda message: message.from_user.id in chat_sessions)
def handle_messages(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.reply_to(message, "تم حظرك من استخدام هذا البوت.")
        return
    
    friend_id = chat_sessions[user_id]
    bot.send_message(friend_id, f"💬 {message.text}")

# وظيفة التبليغ
@bot.message_handler(commands=['report'])
def report_message(message):
    handle_report(bot, message, reported_messages, admin_id)

# وظيفة حظر المستخدم
@bot.message_handler(commands=['ban'])
def ban_user(message):
    handle_ban(bot, message, admin_id, banned_users)

# وظيفة إلغاء حظر المستخدم
@bot.message_handler(commands=['unban'])
def unban_user(message):
    handle_unban(bot, message, admin_id, banned_users)

# وظيفة مسح المحظورين
@bot.message_handler(commands=['clear_bans'])
def clear_bans(message):
    handle_clear_bans(bot, message, admin_id, banned_users)

bot.polling()
