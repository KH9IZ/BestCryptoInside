import datetime
from dateutil import parser

from math import ceil

from tbot import bot, markups, const, admin_menu
from tbot.models import *
import time
from telebot import apihelper


@bot.message_handler(regexp="Рассылка")
def distribution_to_paid(message):
    msg = bot.send_message(message.chat.id, "Введите текст, который хотите отправить пользователям,"
                                            " которые оплатили подписку", reply_markup=markups.back())
    bot.register_next_step_handler(msg, to_paid)


def to_paid(msg):
    if msg.text.upper() == "НАЗАД":
        bot.send_message(msg.chat.id, "Отменено", reply_markup=markups.main_menu(msg.chat.id))
        admin_menu(msg)
        return
    Additional.update(val=True).where(Additional.var == 'isWorkDay').execute()
    users = Payments.select(Payments.uid)
    c = sender(users, msg.text)
    bot.send_message(msg.chat.id,
                     f"Сообщение успешно отправлено всем пользователям!\n\nКоличество доставленных сообщений: {c}",
                     reply_markup=markups.main_menu(msg.chat.id))


@bot.callback_query_handler(func=lambda call: call.data == "toAll")
def distribution_to_all(call):
    msg = bot.send_message(call.message.chat.id, "Введите текст, который хотите отправить всем пользователям",
                           reply_markup=markups.back())
    bot.register_next_step_handler(msg, to_all)


def to_all(msg):
    if msg.text.upper() == "НАЗАД":
        bot.send_message(msg.chat.id, "Отменено", reply_markup=markups.main_menu(msg.chat.id))
        admin_menu(msg)
        return
    users = Users().select(Users.uid)
    c = sender(users, msg.text)
    bot.send_message(msg.chat.id,
                     f"Сообщение успешно отправлено всем пользователям!\n\n "
                     f"Количество доставленных сообщений: {c}",
                     reply_markup=markups.main_menu(msg.chat.id))


@bot.callback_query_handler(func=lambda call: call.data == "toNotPaid")
def distribution_to_not_paid(call):
    msg = bot.send_message(call.message.chat.id, "Введите текст, который хотите отправить пользователям,"
                                                 " которые не оплатили подписку", reply_markup=markups.back())
    bot.register_next_step_handler(msg, to_not_paid)


def to_not_paid(msg):
    if msg.text.upper() == "НАЗАД":
        bot.send_message(msg.chat.id, "Отменено", reply_markup=markups.main_menu(msg.chat.id))
        admin_menu(msg)
        return
    users = Users.select(Users.uid).where(Users.uid.not_in(Payments.select(Payments.uid)))
    # Я сам в ахуе что это работет
    c = sender(users, msg.text)
    bot.send_message(msg.chat.id,
                     f"Сообщение успешно отправлено всем пользователям, которые не оплатили подписку!\n\n "
                     f"Количество доставленных сообщений: {c}",
                     reply_markup=markups.main_menu(msg.chat.id))


@bot.callback_query_handler(func=lambda call: call.data == "toLostSubs")
def distribution_to_lost(call):
    msg = bot.send_message(call.message.chat.id, "Введите текст, который хотите отправить пользователям,"
                                                 " у которых кончилась подписка", reply_markup=markups.back())
    bot.register_next_step_handler(msg, to_lost)


def to_lost(msg):
    if msg.text.upper() == "НАЗАД":
        bot.send_message(msg.chat.id, "Отменено", reply_markup=markups.main_menu(msg.chat.id))
        admin_menu(msg)
        return
    users = LostSubs.select(LostSubs.uid)
    c = sender(users, msg.text)
    bot.send_message(msg.chat.id,
                     f"Сообщение успешно отправлено пользователям, у которых кончилась подписка!\n\n "
                     f"Количество доставленных сообщений: {c}",
                     reply_markup=markups.main_menu(msg.chat.id))


def sender(users, text):
    count = 0
    for user in users:
        if user.uid in const.admin:
            continue
        if count % 20 == 0 and count > 0:
            time.sleep(1)
        try:
            bot.send_message(user.uid, text)
        except apihelper.ApiException:
            continue
        count += 1
    return count


@bot.callback_query_handler(func=lambda call: call.data == "usersTypes")
def user_types(call):
    bot.edit_message_text("Список пользователей", call.message.chat.id, call.message.message_id,
                          reply_markup=markups.usersTypes())


@bot.callback_query_handler(func=lambda call: call.data[:5] == "users")
def show_users(call):
    _, page, u_type = call.data.split('_')
    page = int(page)

    if u_type.startswith("searchname"):
        users = Users.select().where(Users.first_name == u_type[10:]).order_by(Users.first_name).paginate(page, 10)
    elif u_type.startswith("searchsurname"):
        users = Users.select().where(Users.last_name == u_type[13:]).order_by(Users.first_name).paginate(page, 10)
    elif u_type.startswith("searchalias"):
        users = Users.select().where(Users.alias == u_type[11:]).order_by(Users.first_name).paginate(page, 10)

    elif u_type == "paid":
        users = Users.select() \
            .where(Users.uid.in_(Payments.select(Payments.uid))) \
            .order_by(Users.first_name).paginate(page, 10)
    elif u_type == 'notpaid':
        users = Users.select() \
            .where(Users.uid.not_in(Payments.select(Payments.uid))) \
            .order_by(Users.first_name).paginate(page, 10)
    elif u_type == 'lost':
        users = Users.select() \
            .where(Users.uid.in_(LostSubs.select(LostSubs.uid))) \
            .order_by(Users.first_name).paginate(page, 10)
    else:
        users = Users.select().order_by(Users.first_name).paginate(page, 10)
    count = users.count(clear_limit=True)

    bot.edit_message_text(f"Список пользователей ({count} человек/(ка) )",
                          call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=markups.users_mp(users, page, u_type, count))


@bot.callback_query_handler(func=lambda call: call.data[0] == '<')
def detailed_info(call):
    user = Users.get_by_id(int(call.data[1:]))
    text = f"{user.first_name} {user.last_name or ''}\n" \
        f"{user.alias or ''}\n"

    payment = Payments.get_or_none(Payments.uid == user.uid)
    if payment:
        now = time.time()  # Время в секундах настоящее
        sub_date = time.strptime(payment.end_date, "%Y-%m-%d")  # Время в struct_time подписки
        sub_s = time.mktime(sub_date)  # Время подписки в секундах
        delta = ceil((sub_s - now) / (60 * 60 * 24))
        text += f"Куплена подписка до {payment.end_date}\n" \
            f"Оставшееся количество дней: {delta}\n"
    else:
        text += "У данного пользователя не куплена подписка\n"
    invs = Users.select().where(
        Users.uid.in_(Invitations.select(Invitations.invited).where(Invitations.id == user.uid)))
    if invs:
        text += "Пригласил следующий список пользователей:\n"
        for inv in invs:
            text += f"{inv.first_name} {inv.last_name or ''}\n"
    else:
        text += "Еще не пригласил ни одного пользователя"
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=markups.show_details(user.uid))


@bot.callback_query_handler(func=lambda call: call.data[0:10] == "changeDate")
def change_date(call):
    const.chosen_user_id = call.data[10:]
    msg = bot.send_message(call.message.chat.id, "Введите дату формате 2017-03-23 <b>(гггг-мм-дд)</b>\n",
                           parse_mode="html")
    bot.register_next_step_handler(msg, confirm_date)


def confirm_date(message):
    if len(message.text) == 10:
        date = message.text.replace(".", "-")

        payment, created = Payments.get_or_create(uid=const.chosen_user_id, defaults={'end_date': date})
        if not created:
            Payments.update(end_date=date).where(Payments.uid == const.chosen_user_id).execute()
        bot.send_message(message.chat.id, "Срок подписки изменен", reply_markup=markups.adminPanel())
    else:
        bot.send_message(message.chat.id, "Неправильный формат ввода", reply_markup=markups.adminPanel())


@bot.callback_query_handler(func=lambda call: call.data[:8] == "searchby")
def deepSearch(call):
    if call.data[8:] == 'name':
        msg = bot.send_message(call.message.chat.id, 'Введите имя пользователя')
        bot.register_next_step_handler(msg, searchUserN)
    elif call.data[8:] == 'surname':
        msg = bot.send_message(call.message.chat.id, 'Введите фамилию пользователя')
        bot.register_next_step_handler(msg, searchUserS)
    elif call.data[8:] == 'alias':
        msg = bot.send_message(call.message.chat.id, 'Введите ник пользователя')
        bot.register_next_step_handler(msg, searchUserA)


def searchUserN(message):
    users = Users.select().where(Users.first_name == message.text).order_by(Users.first_name).paginate(1, 10)
    count = users.count(clear_limit=True)
    bot.send_message(message.chat.id, f"Список пользователей ({count} человек/(ка) )",
                     reply_markup=markups.users_mp(users, 1, f"searchname{message.text}", count))


def searchUserS(message):
    users = Users.select().where(Users.last_name == message.text).order_by(Users.first_name).paginate(1, 10)
    count = users.count(clear_limit=True)
    bot.send_message(message.chat.id, f"Список пользователей ({count} человек/(ка) )",
                     reply_markup=markups.users_mp(users, 1, f"searchsurname{message.text}", count))


def searchUserA(message):
    users = Users.select().where(Users.alias == message.text).order_by(Users.first_name).paginate(1, 10)
    count = users.count(clear_limit=True)
    bot.send_message(message.chat.id, f"Список пользователей ({count} человек/(ка) )",
                     reply_markup=markups.users_mp(users, 1, f"searchalias{message.text}", count))


@bot.callback_query_handler(func=lambda call: call.data == "changePrices")
def change_prices(call):
    bot.edit_message_text("Изменить цену на подписку", call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markups.chooseMonth())


@bot.callback_query_handler(func=lambda call: call.data == "admin")
def admin2(call):
    bot.edit_message_text("Админ-панель", call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markups.adminPanel())


@bot.callback_query_handler(func=lambda call: call.data[0:2] == "$$")
def show_info(call):
    text = "Текущая цена подписки: {price}\nВведите новую цену в биткойнах, цифры разделены точкой (0.15)"
    if call.data[2:] == "15":
        text = text.format(price=str(const.days15))
        msg = bot.send_message(call.message.chat.id, text)
        bot.register_next_step_handler(msg, change15)
    if call.data[2:] == "30":
        text = text.format(price=str(const.days30))
        msg = bot.send_message(call.message.chat.id, text)
        bot.register_next_step_handler(msg, change30)
    if call.data[2:] == "60":
        text = text.format(price=str(const.days60))
        msg = bot.send_message(call.message.chat.id, text)
        bot.register_next_step_handler(msg, change60)
    if call.data[2:] == "90":
        text = text.format(price=str(const.days90))
        msg = bot.send_message(call.message.chat.id, text)
        bot.register_next_step_handler(msg, change90)
    if call.data[2:] == "forever":
        text = text.format(price=str(const.days_forever))
        msg = bot.send_message(call.message.chat.id, text)
        bot.register_next_step_handler(msg, change_forever)


def change15(message):
    try:
        const.days15 = float(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат", reply_markup=markups.adminPanel())
        return
    Prices.update(price=const.days15).where(Prices.days == 15).execute()
    bot.send_message(message.chat.id, "Цена изменена", reply_markup=markups.adminPanel())


def change30(message):
    try:
        const.days30 = float(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат", reply_markup=markups.adminPanel())
        return
    Prices.update(price=const.days30).where(Prices.days == 30).execute()
    bot.send_message(message.chat.id, "Цена изменена", reply_markup=markups.adminPanel())


def change60(message):
    try:
        const.days60 = float(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат", reply_markup=markups.adminPanel())
        return
    Prices.update(price=const.days60).where(Prices.days == 60).execute()
    bot.send_message(message.chat.id, "Цена изменена", reply_markup=markups.adminPanel())


def change90(message):
    try:
        const.days90 = float(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат", reply_markup=markups.adminPanel())
        return
    Prices.update(price=const.days90).where(Prices.days == 90).execute()
    bot.send_message(message.chat.id, "Цена изменена", reply_markup=markups.adminPanel())


def change_forever(message):
    try:
        const.days_forever = float(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат", reply_markup=markups.adminPanel())
        return
    Prices.update(price=const.days_forever).where(Prices.days == 0).execute()
    bot.send_message(message.chat.id, "Цена изменена", reply_markup=markups.adminPanel())


@bot.callback_query_handler(func=lambda call: call.data == 'incrementAll')
def increment_all(call):
    msg = bot.send_message(call.message.chat.id, 'Введите количество дней, чтобы добавить всем пользователям.')
    bot.register_next_step_handler(msg, add_days)


def add_days(message):
    try:
        int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, 'Неверный формат ввода.')
        return

    data = Payments.select()
    for each in data:
        old_date = each.end_date
        date = str(parser.parse(old_date) + datetime.timedelta(days=int(message.text))).split()[0]
        Payments.update(end_date=date).where(Payments.uid == each.uid).execute()
    bot.send_message(message.chat.id, 'Всем пользователям добавлено %s дней' % message.text)


@bot.callback_query_handler(func=lambda call: call.data == "demo on")
def turn_on_demo(call):
    demo = Demo.select(Demo.state)[0]

    if demo.state:
        bot.send_message(call.message.chat.id, "Демо режим уже включен", reply_markup=markups.adminPanel())
    else:
        msg = bot.send_message(call.message.chat.id, "Введите количество дней, на которое хотите включить")
        bot.register_next_step_handler(msg, handle_days)


@bot.callback_query_handler(func=lambda call: call.data == "demo off")
def turn_off(call):
    demo = Demo.select()[0]

    if demo.state:
        bot.send_message(call.message.chat.id,
                         "Демо режим будет работать для пользователей еще %s дней" % str(demo.days),
                         reply_markup=markups.adminPanel())
    else:
        bot.send_message(call.message.chat.id, "Демо режим выключен", reply_markup=markups.adminPanel())


def handle_days(message):
    try:
        days = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат")
        return

    Demo.set_by_id(1, {Demo.state: 1, Demo.days: days})

    today = str(datetime.datetime.now()).split(' ')[0]
    end_day = str(parser.parse(today) + datetime.timedelta(days=days)).split(' ')[0]
    users = Users.select(Users.uid).where(Users.uid.not_in(Payments.select(Payments.uid)))
    payments = [Payments(uid=user.uid, end_date=end_day) for user in users]
    Payments.bulk_create(payments)

    bot.send_message(message.chat.id, "Демо режим включен для всех пользователей на %s дней" % message.text,
                     reply_markup=markups.adminPanel())
