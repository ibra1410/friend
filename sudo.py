def handle_report(bot, message, reported_messages, admin_id):
    if message.reply_to_message:
        reported_user_id = message.reply_to_message.from_user.id
        reported_text = message.reply_to_message.text
        reported_messages[reported_user_id] = reported_text
        bot.send_message(admin_id, f"تم الإبلاغ عن رسالة من المستخدم {reported_user_id}:\n\n{reported_text}")

def handle_ban(bot, message, admin_id, banned_users):
    if message.from_user.id == admin_id:
        parts = message.text.split()
        if len(parts) == 2:
            user_id = int(parts[1])
            banned_users.add(user_id)
            bot.reply_to(message, f"تم حظر المستخدم {user_id}.")
        else:
            bot.reply_to(message, "يرجى تحديد المستخدم بشكل صحيح باستخدام الأمر /ban <user_id>.")

def handle_unban(bot, message, admin_id, banned_users):
    if message.from_user.id == admin_id:
        parts = message.text.split()
        if len(parts) == 2:
            user_id = int(parts[1])
            if user_id in banned_users:
                banned_users.remove(user_id)
                bot.reply_to(message, f"تم إلغاء حظر المستخدم {user_id}.")
            else:
                bot.reply_to(message, f"المستخدم {user_id} ليس محظورًا.")
        else:
            bot.reply_to(message, "يرجى تحديد المستخدم بشكل صحيح باستخدام الأمر /unban <user_id>.")

def handle_clear_bans(bot, message, admin_id, banned_users):
    if message.from_user.id == admin_id:
        banned_users.clear()
        bot.reply_to(message, "تم مسح قائمة المحظورين.")
