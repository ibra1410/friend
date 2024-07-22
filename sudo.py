def handle_report(bot, message, reported_messages, admin_id):
    if message.reply_to_message:
        reported_user_id = message.reply_to_message.from_user.id
        reported_text = message.reply_to_message.text
        reported_messages[reported_user_id] = reported_text
        bot.send_message(admin_id, f"تم الإبلاغ عن رسالة من المستخدم {reported_user_id}:\n\n{reported_text}")
