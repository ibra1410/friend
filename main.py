import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

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
    "- /info لعرض معلوماتك\n"
    "- /exit لإنهاء الدردشة\n"
)

# رسالة الأوامر
commands_message = (
    "هذه هي الأوامر المتاحة:\n"
    "- /set_interest لتحديد اهتماماتك\n"
    "- /find_friend للعثور على أصدقاء جدد\n"
    "- /report للإبلاغ عن محتوى\n"
    "- /info لعرض معلوماتك\n"
    "- /exit لإنهاء الدردشة\n"
)

# رسالة الترحيب للمطور
admin_welcome_message = (
    "أهلا بك عزيزي المطور الأساسي!\n\n"
    "هذه هي أوامر الأعضاء:\n"
    "- /set_interest لتحديد اهتماماتك\n"
    "- /find_friend للعثور على أصدقاء جدد\n"
    "- /report للإبلاغ عن محتوى\n"
    "- /info لعرض معلوماتك\n"
    "- /exit لإنهاء الدردشة\n\n"
    "وهذه هي أوامر المطور:\n"
    "- /ban <user_id> لحظر المستخدم\n"
    "- /unban <user_id> لإلغاء حظر المستخدم\n"
    "- /clear_bans لمسح قائمة المحظورين\n"
)

def handle_report(bot, message, reported_messages, admin_id):
    if message.reply_to_message:
        reported_user_id = message.reply_to_message.from_user.id
        reported_text = message.reply_to_message.text
        reported_messages[reported_user_id] = reported_text
        bot.send_message(admin_id, f"تم الإبلاغ عن رسالة من المستخدم {reported_user_id}:\n\n{reported_text}")
    else:
        bot.reply_to(message, "يرجى الرد على الرسالة التي تريد الإبلاغ عنها.")

def handle_ban(bot, message, admin_id, banned_users):
    if message.from_user.id == admin_id:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            banned_users.add(user_id)
            bot.reply_to(message, f"تم حظر المستخدم {user_id} من البوت.")
            # منع المستخدم من التفاعل مع البوت
            if user_id in chat_sessions:
                friend_id = chat_sessions[user_id]
                del chat_sessions[friend_id]
                del chat_sessions[user_id]
        else:
            bot.reply_to(message, "يرجى الرد على رسالة المستخدم الذي تريد حظره.")

def handle_unban(bot, message, admin_id, banned_users):
    if message.from_user.id == admin_id:
        parts = message.text.split()
        if len(parts) == 2:
            try:
                user_id = int(parts[1])
                if user_id in banned_users:
                    banned_users.remove(user_id)
                    bot.reply_to(message, f"تم إلغاء حظر المستخدم {user_id}.")
                else:
                    bot.reply_to(message, f"المستخدم {user_id} ليس محظورًا.")
            except ValueError:
                bot.reply_to(message, "يرجى تحديد معرف المستخدم بشكل صحيح.")
        else:
            bot.reply_to(message, "يرجى تحديد المستخدم بشكل صحيح باستخدام الأمر /unban <user_id>.")

def handle_clear_bans(bot, message, admin_id, banned_users):
    if message.from_user.id == admin_id:
        banned_users.clear()
        bot.reply_to(message, "تم مسح قائمة المحظورين.")

def handle_info(bot, message):
    user_id = message.from_user.id
    interests = user_interests.get(user_id, [])
    chat_session = chat_sessions.get(user_id, "لا توجد جلسة دردشة نشطة.")
    
    info_message = (
        f"معلومات المستخدم:\n"
        f"- معرف المستخدم: {user_id}\n"
        f"- الاهتمامات: {', '.join(interests) if interests else 'لم يتم تحديد اهتمامات'}\n"
        f"- حالة الدردشة: {chat_session}"
    )
    bot.reply_to(message, info_message)

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
        button_search = KeyboardButton("بحث عن شخص آخر")
        markup.add(button, button_search)

        bot.send_message(user_id, f"وجدنا صديقًا مشتركًا في الاهتمامات! {friend_id}", reply_markup=markup)
        bot.send_message(friend_id, "تم ربطك بصديق مشترك في الاهتمامات!", reply_markup=markup)
    else:
        bot.send_message(user_id, "لم يتم العثور على أصدقاء. حاول مرة أخرى لاحقًا.", reply_markup=ReplyKeyboardRemove())

# وظيفة بدء الدردشة مع صديق
@bot.message_handler(func=lambda message: message.text == "ابدأ الدردشة")
def start_chat(message):
    user_id = message.from_user.id
    if user_id in chat_sessions:
        friend_id = chat_sessions[user_id]
        bot.send_message(user_id, f"بدأت الدردشة مع المستخدم {friend_id}.")
        bot.send_message(friend_id, f"بدأت الدردشة مع المستخدم {user_id}.")
    else:
        bot.reply_to(message, "لم يتم العثور على صديق للدردشة معه. حاول مرة أخرى باستخدام /find_friend.")

# وظيفة البحث عن شخص آخر
@bot.message_handler(func=lambda message: message.text == "بحث عن شخص آخر")
def search_another_person(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "جاري البحث عن شخص آخر...")
    find_friend(message)

# وظيفة إنهاء الدردشة
@bot.message_handler(commands=['exit'])
def end_chat(message):
    user_id = message.from_user.id
    if user_id in chat_sessions:
        friend_id = chat_sessions[user_id]
        del chat_sessions[user_id]
        del chat_sessions[friend_id]
        bot.reply_to(message, "تم إنهاء الدردشة.")
        bot.send_message(friend_id, "قام المستخدم بإنهاء الدردشة.")
    else:
        bot.reply_to(message, "لا توجد دردشة نشطة لإنهائها.")

# وظيفة التعامل مع الرسائل
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.reply_to(message, "عذرًا، أنت محظور من استخدام هذا البوت.")
        return

    # التعامل مع الرسائل المرسلة خلال الدردشة
    if user_id in chat_sessions:
        friend_id = chat_sessions[user_id]
        bot.forward_message(friend_id, message.chat.id, message.message_id)
    
    # التعامل مع التبليغ
    if message.text.startswith('/report'):
        handle_report(bot, message, reported_messages, admin_id)
    
    # إذا كان الأمر /info
    if message.text.startswith('/info'):
        handle_info(bot, message)

# التعامل مع أوامر المطور
@bot.message_handler(commands=['ban'])
def ban_user(message):
    handle_ban(bot, message, admin_id, banned_users)

@bot.message_handler(commands=['unban'])
def unban_user(message):
    handle_unban(bot, message, admin_id, banned_users)

@bot.message_handler(commands=['clear_bans'])
def clear_bans(message):
    handle_clear_bans(bot, message, admin_id, banned_users)

# بدء البوت
bot.polling()
