from tbot import bot, const
from tbot.models import *


@bot.callback_query_handler(func=lambda call: call.data == "withdraw")
def withdraw(call):
    msg = bot.send_message(call.message.chat.id, "Введите сумму, которую хотите вывести")
    bot.register_next_step_handler(msg, check_sum)


def check_sum(msg):
    try:
        value = float(msg.text)
        if Users.get_by_id(msg.chat.id).balance >= value > 0:
            const.values[msg.chat.id] = value
            msg = bot.send_message(msg.chat.id, "Введите адрес, на который будет произведена выплата")
            bot.register_next_step_handler(msg, send_request)
        else:
            bot.send_message(msg.chat.id, "Недостаточно средств")
    except ValueError:
        bot.send_message(msg.chat.id, "Неккоректная сумма")


def send_request(msg):
    bot.send_message(const.admin[0], f"Новая заявка на вывод {const.values.get(msg.chat.id)} BTC на адрес {msg.text}")
    bot.send_message(msg.chat.id, "Ваша заявка отпралена!\nОжидайте подтверждения.")


@bot.callback_query_handler(func=lambda call: call.data == "inv_users")
def inv_users(c):
    inv_ids = Invitations.select().where(Invitations.id == c.message.chat.id)
    if inv_ids:
        s = "Вы пригласили: \n"
        for uid in inv_ids:
            user = Users.get_by_id(uid.invited)
            end_date = Payments.get_or_none(Payments.uid == uid.invited)
            s += user.first_name
            if user.last_name is not None:
                s += " " + user.last_name
            if end_date is not None:
                s += ", подписка до " + end_date.end_date
            s += '\n'
            bot.edit_message_text(s, c.message.chat.id, c.message.message_id)
    else:
        bot.edit_message_text("Вы никого не пригласили", c.message.chat.id, c.message.message_id)
