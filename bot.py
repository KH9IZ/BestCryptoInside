import datetime
import time
import hashlib
import logging
import logging.config
import ssl
import time
from math import ceil

import pymysql as sql #
import requests
import telebot #
from telebot import apihelper
from aiohttp import web #
from dateutil import parser #
from web3 import Web3, HTTPProvider #

import const
import markups

WEBHOOK_HOST = '94.23.164.102'
WEBHOOK_PORT = 443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP address

WEBHOOK_SSL_CERT = './webhook_cert.pem'
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(const.token)


logging.config.fileConfig("/root/traderBot/logs/logging.conf")
logger = logging.getLogger('root')

loggerPy = logging.getLogger('bot.py')
loggerPy.setLevel(logging.DEBUG)
ch = logging.FileHandler('journal.log')
formatter = logging.Formatter('%(levelname)s : DATE ---> %(asctime)s - %(message)s')
ch.setFormatter(formatter)
loggerPy.addHandler(ch)

bot = telebot.TeleBot(const.token)

app = web.Application()


# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)


app.router.add_post('/{token}/', handle)


def connect():
    return sql.connect("localhost", "root", const.s, "TRADER", use_unicode=True, charset="utf8")


def daily_check():
    try:
        db = connect()
        cur = db.cursor()
        r = 'SELECT uid, end_date FROM payments'
        cur.execute(r)
        res = cur.fetchall()
        r = "SELECT state, days FROM demo WHERE id = 1"
        cur.execute(r)
        state, days_left = cur.fetchone()
        if state:
            if days_left <= 0:
                r = "UPDATE demo SET state = 0 WHERE id = 1"
            else:
                r = "UPDATE demo SET days = days - 1 WHERE id = 1"
            cur.execute(r)
        # today = str(datetime.datetime.now()).split(' ')[0]
        # after_tomorrow = parser.parse(today) + datetime.timedelta(days=3)

        # if not const.isWorkDay:
        #     bot.send_message(const.sysadmin, "Начинаю обновлять Даты окончания подписок. Сегодня был нерабочий день.")

        for user in res:
            end_date = parser.parse(str(user[1]))
            today = datetime.datetime.today()
            days_left = end_date - today

            r = 'SELECT val FROM additional WHERE var = "isWorkDay"'
            cur.execute(r)
            isWorkDay = cur.fetchone()[0]


            if not isWorkDay:
                date = str(end_date + datetime.timedelta(days=1)).split()[0]
                r = 'UPDATE payments SET end_date = %s WHERE uid = %s'
                cur.execute(r, (date, user[0]))
                time.sleep(0.1)
                continue

            # if after_tomorrow == parser.parse(str(user[1])):
            if days_left.days in [1, 2, 3]:
                text = 'Ваша подписка на раздел 💰 *Сигналы & Рекомендации* закончится через {} '.format(days_left.days)
                if days_left.days == 1:
                    text2 = "день."
                else:
                    text2 = "дня."
                try:
                    bot.send_message(user[0], text+text2, reply_markup=markups.payBtnMarkup(), parse_mode="Markdown")
                except Exception:
                    pass
                time.sleep(0.1)
            # if parser.parse(str(user[1])) <= parser.parse(today):
            if days_left.days <= 0:

                text = 'Время действия вашей подписки окончено.'
                try:
                    bot.send_message(user[0], text)
                except Exception:
                    pass
                r = 'DELETE FROM payments WHERE uid=%s'
                cur.execute(r, (user[0],))
                r = "INSERT INTO lost_subs(uid, end_date) VALUES (%s, %s)"
                cur.execute(r, (user[0], user[1]))
                time.sleep(0.1)
            db.commit()
        r = 'UPDATE additional SET val = %s WHERE var = %s'
        cur.execute(r, (False, 'isWorkDay'))
        db.commit()
        db.close()

    except Exception as e:
        bot.send_message(const.sysadmin, str(e))


def add_invitation(user_id, invited_user_id):
    db = connect()
    cur = db.cursor()
    r = "SELECT * FROM INVITATIONS WHERE INVITED=%s"
    cur.execute(r, invited_user_id)
    if not cur.fetchone() and int(user_id) != int(invited_user_id):
        r = "INSERT INTO INVITATIONS (ID, INVITED) VALUES (%s, %s)"
        cur.execute(r, (user_id, invited_user_id))
        db.commit()
    db.close()


def getRateETH():
    url = "https://api.coinmarketcap.com/v1/ticker/"
    response = requests.get(url)
    for i in response.json():
        if i.get('name') == "Ethereum":
            return float(i.get('price_usd'))


def getRateBTC():
    url = "https://api.coinmarketcap.com/v1/ticker/"
    response = requests.get(url)
    for i in response.json():
        if i.get('name') == "Bitcoin":
            return float(i.get('price_usd'))


@bot.message_handler(regexp="⬅️Назад")
@bot.message_handler(commands=["start"])
def start(message):
    text = message.text.split(" ")
    if len(text) == 2:
        if text[1].isdigit():
            initial_id = text[1]
            add_invitation(initial_id, message.chat.id)
    db = connect()
    cur = db.cursor()
    r = 'SELECT * FROM users WHERE uid = %s'
    cur.execute(r, message.chat.id)
    if not cur.fetchone():
        r = "INSERT INTO users (uid, first_name, last_name, alias) VALUE (%s,%s,%s,%s)"
        cur.execute(r, (message.chat.id, message.from_user.first_name,
                        message.from_user.last_name, message.from_user.username))
        db.commit()
    else:
        r = "UPDATE users SET first_name=%s, last_name=%s, alias=%s WHERE uid=%s"
        cur.execute(r, (message.from_user.first_name, message.from_user.last_name,
                        message.from_user.username, message.chat.id))
        db.commit()
        # 'UPDATE awaitReceipt SET comment = %s, amount = %s, days = %s WHERE uid = %s', (comment, amount, days, uid))
    sub = '*У вас активная демо-подписка.*\n\nВы получаете лишь небольшую часть сигналов. Для получения доступа ко всем сигналам Вам необходимо купить VIP подписку в меню бота.'
    cur.execute('SELECT * FROM payments WHERE uid = %s', message.chat.id)
    if cur.fetchone():
        sub = '*У вас активная VIP-подписка*'
    bot.send_message(message.chat.id, const.startMsg % (message.from_user.first_name, sub), reply_markup=markups.mainMenu(message.chat.id),
                     parse_mode="Markdown")
    db.close()


def get_user_balance(uid):
    db = connect()
    cur = db.cursor()
    r = "SELECT balance FROM users WHERE uid = %s"
    cur.execute(r, uid)
    balance = cur.fetchone()
    db.close()
    return balance[0]


def get_ids():
    db = connect()
    cur = db.cursor()
    r = "SELECT uid FROM users"
    cur.execute(r)
    data = cur.fetchall()
    db.close()
    res = []
    for i in data:
        res.append(i[0])
    return res


def get_paid_ids():
    db = connect()
    cur = db.cursor()

    r = 'UPDATE additional SET val = %s WHERE var = %s'
    cur.execute(r, (True, 'isWorkDay'))
    db.commit()

    r = "SELECT uid FROM payments"
    cur.execute(r)
    data = cur.fetchall()
    db.close()
    res = []
    for i in data:
        res.append(i[0])
    return res


def get_lost_subs_ids():
    db = connect()
    cur = db.cursor()
    r = "SELECT uid FROM lost_subs"
    cur.execute(r)
    data = cur.fetchall()
    db.close()
    res = []
    for i in data:
        res.append(i[0])
    return res


def get_all_user(uid):
    db = connect()
    cur = db.cursor()
    r = "SELECT * FROM users WHERE uid=%s"
    cur.execute(r, uid)
    user = cur.fetchone()
    text = user[2]
    if user[3]:
        text += " " + user[3]
    if user[4]:
        text += "\n@" + user[4]
    r = "SELECT * FROM payments WHERE uid = %s"
    cur.execute(r, uid)
    data = cur.fetchone()
    if data:
        now = time.time()  # Время в секундах настоящее
        sub_date = time.strptime(data[1], "%Y-%m-%d")  # Время в struct_time подписки
        sub_s = time.mktime(sub_date)  # Время подписки в секундах
        delta = ceil((sub_s - now) / (60 * 60 * 24))

        text += "\nКуплена подписка до %s\n" \
                "Оставшееся количество дней: %s " % (data[1], str(delta))
    else:
        text += "\nУ данного пользователя не куплена подписка"
    r = "SELECT INVITED FROM INVITATIONS WHERE ID = %s"
    cur.execute(r, uid)
    ids = cur.fetchall()
    if ids:
        text += "\nПригласил следующий список пользователей:\n"
        for user in ids:
            r = "SELECT first_name, last_name FROM users WHERE uid = %s"
            cur.execute(r, user[0])
            try:
                text += "<b>" + " ".join(cur.fetchone()) + "</b>\n"
            except TypeError:
                pass
                # text += "<b>" + str(user) + "</b>\n"
    else:
        text += "\nЕще не пригласил ни одного пользователя"
    db.close()
    return text


# Admin
@bot.message_handler(regexp="👤 Админ")
def admin(message):
    if message.chat.id in const.admin:
        bot.send_message(message.chat.id, "Админ-панель", reply_markup=markups.adminPanel())


@bot.callback_query_handler(func=lambda call: call.data == "admin")
def admin2(call):
    bot.edit_message_text("Админ-панель", call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markups.adminPanel())


@bot.callback_query_handler(func=lambda call: call.data == "addVideo")
def add_video(call):
    msg = bot.send_message(call.message.chat.id, "Введите ссылку на видео")
    bot.register_next_step_handler(msg, get_video)


@bot.callback_query_handler(func=lambda call: call.data == "usersTypes")
def user_types(call):
    bot.edit_message_text("Список пользователей", call.message.chat.id, call.message.message_id,
                          reply_markup=markups.usersTypes())


# @bot.callback_query_handler(func=lambda call: call.data == "search")
# def search(call):
#     bot.send_message(call.message.chat.id, 'Выберите cпособ поиска',reply_markup=markups.searchuser())


@bot.callback_query_handler(func=lambda call: call.data[:8] == "searchby")
def deepSearch(call):
    if call.data[8:] == 'name':
        msg=bot.send_message(call.message.chat.id,'Введите имя пользователя')
        bot.register_next_step_handler(msg,searchUserN)
    elif call.data[8:] == 'surname':
        msg=bot.send_message(call.message.chat.id,'Введите фамилию пользователя')
        bot.register_next_step_handler(msg,searchUserS)
    elif call.data[8:] == 'alias':
        msg=bot.send_message(call.message.chat.id,'Введите ник пользователя')
        bot.register_next_step_handler(msg, searchUserA)


def searchUserN(message):
    searchByName(message.text)
    bot.send_message(message.chat.id, "Найденные пользователи", reply_markup=markups.users())


def searchUserS(message):
    searchBySurname(message.text)
    bot.send_message(message.chat.id, "Найденные пользователи", reply_markup=markups.users())


def searchUserA(message):
    searchByAlias(message.text)
    bot.send_message(message.chat.id, "Найденные пользователи", reply_markup=markups.users())


def searchByName(msg):
    const.listPointer=0
    db = connect()
    cur = db.cursor()
    r = "SELECT * FROM users"
    cur.execute(r)
    r = "SELECT * FROM users WHERE first_name = %s"
    cur.execute(r, msg)
    search_data = cur.fetchall()
    const.userList.clear()
    db.close()
    for man in search_data:
        if man[4] is not None:
            s = "@" + man[4]
        else:
            s = man[2] + ' '
            if man[3] is not None:
                s += man[3] + ' '
        s += '%' + str(man[0])
        const.userList.append(s)
    const.userList.sort()
    return const.userList


def searchByAlias(msg):
    const.listPointer=0
    db = connect()
    cur = db.cursor()
    r = "SELECT * FROM users"
    cur.execute(r)
    r = "SELECT * FROM users WHERE alias = %s"
    cur.execute(r, msg)
    search_data = cur.fetchall()
    const.userList.clear()
    db.close()
    for man in search_data:
        if man[4] is not None:
            s = "@" + man[4]
        else:
            s = man[2] + ' '
            if man[3] is not None:
                s += man[3] + ' '
        s += '%' + str(man[0])
        const.userList.append(s)
    const.userList.sort()
    return const.userList


def searchBySurname(msg):
    const.listPointer=0
    db = connect()
    cur = db.cursor()
    r = "SELECT * FROM users"
    cur.execute(r)
    r = "SELECT * FROM users WHERE last_name = %s"
    cur.execute(r,msg)
    search_data = cur.fetchall()
    const.userList.clear()
    db.close()
    for man in search_data:
        if man[4] is not None:
            s = "@" + man[4]
        else:
            s = man[2] + ' '
            if man[3] is not None:
                s += man[3] + ' '
        s += '%' + str(man[0])
        const.userList.append(s)
    const.userList.sort()
    return const.userList


@bot.callback_query_handler(func=lambda call: call.data[:5] == "users")
def show_users(call):
    const.listPointer = 0
    get_users(call.data[6:])
    bot.edit_message_text("Список пользователей ("+str(len(const.userList))+" человек/(ка) )",
                          call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markups.users())


@bot.callback_query_handler(func=lambda call: call.data == "nextList")
def listforward(call):
    const.listPointer += 1
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markups.users())


@bot.callback_query_handler(func=lambda call: call.data == "prevList")
def listback(call):
    const.listPointer -= 1
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markups.users())





def get_users(user_type):
    db = connect()
    cur = db.cursor()
    r = "SELECT * FROM users"
    cur.execute(r)
    data = cur.fetchall()

    if user_type == "paid":
        r = "SELECT * FROM payments"
        cur.execute(r)
        data_paid = cur.fetchall()
        db.close()
        const.userList.clear()
        for user in data:
            for user_p in data_paid:
                if user[0] == user_p[0]:
                    now = time.time()  # Время в секундах настоящее
                    sub_date = time.strptime(user_p[1], "%Y-%m-%d")  # Время в struct_time подписки
                    sub_s = time.mktime(sub_date)  # Время подписки в секундах
                    delta = ceil((sub_s - now) / (60 * 60 * 24))
                    if user[4] is not None:
                        s = "@" + user[4]
                    else:
                        s = user[2] + ' '
                        if user[3] is not None:
                            s += user[3] + ' '
                    s += ' (' + str(delta) + ')' + '%' + str(user[0])
                    const.userList.append(s)
        return const.userList
    elif user_type == "not_paid":
        r = "SELECT * FROM payments"
        cur.execute(r)
        data_paid = cur.fetchall()
        const.userList.clear()
        db.close()
        for user in data:
            if user[0] not in [user_p[0] for user_p in data_paid]:
                if user[4] is not None:
                    s = "@" + user[4]
                else:
                    s = user[2] + ' '
                    if user[3] is not None:
                        s += user[3] + ' '
                s += '%' + str(user[0])
                const.userList.append(s)
        return const.userList
    elif user_type == "lost":
        r = "SELECT * FROM lost_subs"
        cur.execute(r)
        data_paid = cur.fetchall()
        db.close()
        const.userList.clear()
        for user in data:
            for user_p in data_paid:
                if user[0] == user_p[0]:
                    now = time.time()  # Время в секундах настоящее
                    sub_date = time.strptime(user_p[1], "%Y-%m-%d")  # Время в struct_time подписки
                    sub_s = time.mktime(sub_date)  # Время подписки в секундах
                    delta = ceil((now - sub_s) / (60 * 60 * 24)) - 1
                    if user[4] is not None:
                        s = "@" + user[4]
                    else:
                        s = user[2] + ' '
                        if user[3] is not None:
                            s += user[3] + ' '
                    s += ' (' + str(delta) + ')' + '%' + str(user[0])
                    const.userList.append(s)
        return const.userList

    elif user_type[:4] == "name":
        r = "SELECT * from users WHERE LOWER(first_name) = %s"
        cur.execute(r, user_type[4:])
        search_data = cur.fetchall()
        const.userList.clear()
        db.close()
        for man in search_data:
            if man[4] is not None:
                s = "@" + man[4]
            else:
                s = man[2] + ' '
                if man[3] is not None:
                    s += man[3] + ' '
            s += '%' + str(man[0])
            const.userList.append(s)
        const.userList.sort()
        return const.userList

    else:
        const.userList.clear()
        db.close()
        for user in data:
            if user[4] is not None:
                s = "@" + user[4]
            else:
                s = user[2] + ' '
                if user[3] is not None:
                    s += user[3] + ' '
            s += '%' + str(user[0])
            const.userList.append(s)
        const.userList.sort()
        return const.userList


@bot.callback_query_handler(func=lambda call: call.data[0] == '<')
def detailed_info(call):
    text = get_all_user(call.data[1:])
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="html")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=markups.showDetails(call.data[1:]))


@bot.callback_query_handler(func=lambda call: call.data == "changePrices")
def change_prices(call):
    bot.edit_message_text("Изменить цену на подписку", call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                  reply_markup=markups.chooseMonth())


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
        db = connect()
        cur = db.cursor()
        r = "UPDATE prices SET price=%s WHERE days=15"
        cur.execute(r, float(message.text))
        db.commit()
        db.close()
        const.days15 = float(message.text)
        bot.send_message(message.chat.id, "Цена изменена", reply_markup=markups.adminPanel())
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат", reply_markup=markups.adminPanel())


def change30(message):
    try:
        db = connect()
        cur = db.cursor()
        r = "UPDATE prices SET price=%s WHERE days=30"
        cur.execute(r, float(message.text))
        db.commit()
        db.close()
        const.days30 = float(message.text)
        bot.send_message(message.chat.id, "Цена изменена", reply_markup=markups.adminPanel())
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат", reply_markup=markups.adminPanel())


def change60(message):
    try:
        db = connect()
        cur = db.cursor()
        r = "UPDATE prices SET price=%s WHERE days=60"
        cur.execute(r, float(message.text))
        db.commit()
        db.close()
        const.days60 = float(message.text)
        bot.send_message(message.chat.id, "Цена изменена", reply_markup=markups.adminPanel())
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат", reply_markup=markups.adminPanel())


def change90(message):
    try:
        db = connect()
        cur = db.cursor()
        r = "UPDATE prices SET price=%s WHERE days=90"
        cur.execute(r, float(message.text))
        db.commit()
        db.close()
        const.days90 = float(message.text)
        bot.send_message(message.chat.id, "Цена изменена", reply_markup=markups.adminPanel())
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат", reply_markup=markups.adminPanel())


def change_forever(message):
    try:
        db = connect()
        cur = db.cursor()
        r = "UPDATE prices SET price=%s WHERE days=0"
        cur.execute(r, float(message.text))
        db.commit()
        db.close()
        const.days_forever = float(message.text)
        bot.send_message(message.chat.id, "Цена изменена", reply_markup=markups.adminPanel())
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат", reply_markup=markups.adminPanel())


@bot.callback_query_handler(func=lambda call: call.data[0:10] == "changeDate")
def change_date(call):
    const.chosenUserId = call.data[10:]
    msg = bot.send_message(call.message.chat.id, "Введите дату формате 2017-03-23 <b>(гггг-мм-дд)</b>\n",
                           parse_mode="html")
    bot.register_next_step_handler(msg, confirm_date)


def confirm_date(message):
    if len(message.text) == 10:
        date = message.text.replace(".", "-")
        db = connect()
        cur = db.cursor()
        r = "SELECT * FROM payments WHERE uid = %s"
        cur.execute(r, const.chosenUserId)
        if not cur.fetchone():
            r = "INSERT INTO payments (end_date, uid) VALUE (%s,%s)"
        else:
            r = "UPDATE payments SET end_date = %s WHERE uid = %s"
        cur.execute(r, (date, const.chosenUserId))
        db.commit()
        db.close()
        bot.send_message(message.chat.id, "Срок подписки изменен", reply_markup=markups.adminPanel())
    else:
        bot.send_message(message.chat.id, "Неправильный формат ввода", reply_markup=markups.adminPanel())


def get_video(message):
    db = connect()
    cur = db.cursor()
    r = 'INSERT INTO VIDEO (link) VALUES (%s)'
    cur.execute(r, message.text)
    db.commit()
    db.close()
    bot.send_message(message.chat.id, "Видео успешно добавлено!")


@bot.callback_query_handler(func=lambda call: call.data == "demo on")
def turn_on_demo(call):
    db = connect()
    cur = db.cursor()
    r = "SELECT state FROM demo"
    cur.execute(r)
    state = int(cur.fetchone()[0])
    db.close()
    if state:
        bot.send_message(call.message.chat.id, "Демо режим уже включен", reply_markup=markups.adminPanel())
    else:
        msg = bot.send_message(call.message.chat.id, "Введите количество дней, на которое хотите включить")
        bot.register_next_step_handler(msg, handle_days)


@bot.callback_query_handler(func=lambda call: call.data == "demo off")
def turn_off(call):
    db = connect()
    cur = db.cursor()
    r = "SELECT state, days FROM demo"
    cur.execute(r)
    state, days = cur.fetchone()
    db.close()
    if state:
        bot.send_message(call.message.chat.id, "Демо режим будет работать для пользователей еще %s дней" % str(days),
                         reply_markup=markups.adminPanel())
    else:
        bot.send_message(call.message.chat.id, "Демо режим выключен", reply_markup=markups.adminPanel())


def handle_days(message):
    try:
        days = int(message.text)
        db = connect()
        cur = db.cursor()
        r = "UPDATE demo SET state = 1"
        cur.execute(r)
        r = "UPDATE demo SET days = %s"
        cur.execute(r, days)
        r = "SELECT uid FROM users"
        cur.execute(r)
        ids = cur.fetchall()
        today = str(datetime.datetime.now()).split(' ')[0]
        end_day = str(parser.parse(today) + datetime.timedelta(days=days)).split(' ')[0]
        for user in ids:
            r = "SELECT * FROM payments WHERE uid = (%s)"
            cur.execute(r, user)
            if cur.fetchone():
                continue
            else:
                request = "INSERT INTO payments (uid, end_date) VALUE (%s,%s)"
                cur.execute(request, (user, end_day))
            time.sleep(0.1)
        db.commit()
        db.close()
        bot.send_message(message.chat.id, "Демо режим включен для всех пользователей на %s дней" % message.text,
                         reply_markup=markups.adminPanel())
    except ValueError:
        bot.send_message(message.chat.id, "Неправильный формат")


@bot.callback_query_handler(func=lambda call: call.data == "toAll")
def get_text(call):
    msg = bot.send_message(call.message.chat.id, "Введите текст, который хотите отправить всем пользователям", 
                           reply_markup=markups.back())
    bot.register_next_step_handler(msg, simple_distribution)


def simple_distribution(message):
    if message.text.upper() == "НАЗАД":
        bot.send_message(message.chat.id, "Отменено", reply_markup=markups.mainMenu(message.chat.id))
        admin(message)
        return


    count = 0
    for user_id in get_ids():
        if user_id in const.admin:
            continue
        if count == 20:
            time.sleep(1)
        try:
            bot.send_message(user_id, message.text)
        except telebot.apihelper.ApiException:
            continue
        count += 1
    bot.send_message(message.chat.id, "Сообщение успешно отправлено всем пользователям!", 
                     reply_markup=markups.mainMenu(message.chat.id))


# @bot.callback_query_handler(func=lambda call: call.data == "toPaid")
# def get_text1(call):
#     msg = bot.send_message(call.message.chat.id, "Введите текст, который хотите отправить пользователям,"
#                                                  " которые оплатили подписку")
#     bot.register_next_step_handler(msg, paid_distribution)

@bot.message_handler(regexp="Рассылка")
def get_text1(message):
     msg = bot.send_message(message.chat.id, "Введите текст, который хотите отправить пользователям,"
                                             " которые оплатили подписку", reply_markup=markups.back())
     bot.register_next_step_handler(msg, paid_distribution)


def paid_distribution(message):
    if message.text.upper() == "НАЗАД":
        bot.send_message(message.chat.id, "Отменено", reply_markup=markups.mainMenu(message.chat.id))
        admin(message)
        return
    count = 0

    for user_id in get_paid_ids():
        if user_id in const.admin:
            continue
        if count % 20 == 0:
            time.sleep(1)
        try:
            bot.send_message(user_id, message.text)
        except telebot.apihelper.ApiException:
            continue
        count += 1
    bot.send_message(message.chat.id, "Сообщение успешно отправлено всем пользователям!", 
                     reply_markup=markups.mainMenu(message.chat.id))


@bot.callback_query_handler(func=lambda call: call.data == "toLostSubs")
def get_text2(call):
    msg = bot.send_message(call.message.chat.id, "Введите текст, который хотите отправить пользователям,"
                                                 " у которых кончилась подписка", reply_markup=markups.back())
    bot.register_next_step_handler(msg, lost_subs_distribution)


def lost_subs_distribution(message):
    if message.text.upper() == "НАЗАД":
        bot.send_message(message.chat.id, "Отменено", reply_markup=markups.mainMenu(message.chat.id))
        admin(message)
        return
    count = 0
    for user_id in get_lost_subs_ids():
        if user_id in const.admin:
            continue
        if count == 20:
            time.sleep(1)
        try:
            bot.send_message(user_id, message.text)
        except:
            continue
        count += 1
    bot.send_message(message.chat.id, "Сообщение успешно отправлено пользователям, у которых кончилась подписка!", 
                     reply_markup=markups.mainMenu(message.chat.id))


@bot.callback_query_handler(func=lambda call: call.data == "toNotPaid")
def get_text3(call):
    msg = bot.send_message(call.message.chat.id, "Введите текст, который хотите отправить пользователям,"
                                                 " которые не оплатили подписку", reply_markup=markups.back())
    bot.register_next_step_handler(msg, not_paid_distribution)


def not_paid_distribution(message):
    if message.text.upper() == "НАЗАД":
        bot.send_message(message.chat.id, "Отменено", reply_markup=markups.mainMenu(message.chat.id))
        admin(message)
        return
    count = 0
    get_users("not_paid")
    for user in const.userList:
        symbol = user.find('%')
        uid = int(user[symbol + 1:])
        if uid in const.admin:
            continue
        if count % 20 == 0:
            time.sleep(1)
        try:
            bot.send_message(uid, message.text)
        except:
            continue
        count += 1
    bot.send_message(message.chat.id, "Сообщение успешно отправлено всем пользователям, которые не оплатили подписку!", 
                     reply_markup=markups.mainMenu(message.chat.id))


@bot.callback_query_handler(func=lambda call: call.data == 'incrementAll')
def incrementAll(call):
    msg = bot.send_message(call.message.chat.id, 'Введите количество дней, чтобы добавить всем пользователям.')
    bot.register_next_step_handler(msg, addDays)


# Первая клавиатура
@bot.message_handler(regexp="👥 Партнерская программа")
def materials(message):
    db = connect()
    cur = db.cursor()
    r = "SELECT ID FROM INVITATIONS WHERE INVITED=%s"
    cur.execute(r, str(message.chat.id))
    by_user = cur.fetchone()
    inv_by = ""
    if by_user:
        r = "SELECT first_name, last_name from users WHERE uid=%s"
        cur.execute(r, str(by_user[0]))
        inv_by = "Вы приглашены пользователем " + " ".join(cur.fetchone()) + '\n\n'
    db.close()

    balance = "<b>Ваш баланс:</b> %s BTC\n" % get_user_balance(message.chat.id)
    text = "<b>Ваша реферальная ссылка:</b>\nhttps://t.me/BestCryptoInsideBot?start=%s" % message.chat.id
    bot.send_message(message.chat.id, inv_by + const.marketingMsg + balance + text, parse_mode="html",
                     reply_markup=markups.withdrawBtn())


@bot.callback_query_handler(func=lambda call: call.data == "withdraw")
def withdraw(call):
    msg = bot.send_message(call.message.chat.id, "Введите сумму, которую хотите вывести")
    bot.register_next_step_handler(msg, check_sum)


def check_sum(message):
    try:
        value = float(message.text)
        if get_user_balance(message.chat.id) >= value > 0:
            const.values[message.chat.id] = value
            msg = bot.send_message(message.chat.id, "Введите адрес, на который будет произведена выплата")
            bot.register_next_step_handler(msg, send_request)
        else:
            bot.send_message(message.chat.id, "Недостаточно средств")
    except ValueError:
        bot.send_message(message.chat.id, "Неккоректная сумма")


def send_request(message):
    bot.send_message(const.admin[0], "Новая заявка на вывод %s BTC на адрес %s"
                     % (const.values.get(message.chat.id), message.text))
    bot.send_message(message.chat.id, "Ваша заявка отпралена!\nОжидайте подтверждения.")


@bot.callback_query_handler(func=lambda call: call.data == "inv_users")
def inv_users(call):
    db = connect()
    cur = db.cursor()
    r = "SELECT INVITED FROM INVITATIONS WHERE ID = %s"
    cur.execute(r, str(call.message.chat.id))
    inv_ids = cur.fetchall()
    if inv_ids:
        s = "Вы пригласили: \n"
        for uid in inv_ids:
            r = "SELECT * FROM users WHERE uid=%s"
            cur.execute(r, uid[0])
            user = cur.fetchone()
            r = "SELECT end_date FROM payments WHERE uid=%s"
            cur.execute(r, uid[0])
            end_date = cur.fetchone()
            s += user[2]
            if user[3] is not None:
                s += " " + user[3]
            if end_date:
                s += ", подписка до " + end_date[0]
            s += '\n'
            bot.edit_message_text(s, call.message.chat.id, call.message.message_id)
    else:
        bot.edit_message_text("Вы никого не пригласили", call.message.chat.id, call.message.message_id)
    db.close()


@bot.message_handler(regexp="💌 Отзывы")
def send(message):
    bot.send_message(message.chat.id, "Результаты вы можете посмотреть по кнопке ниже",
                     reply_markup=telebot.types.InlineKeyboardMarkup().row(telebot.types.InlineKeyboardButton(
                         "Отзывы",
                         url='https://t.me/otzivi_bestinvestor')))


@bot.message_handler(regexp="💰 Сигналы и рекомендации")
def sign(message):
    bott="<a href=\"https://web.telegram.org/#/im?p=@BTC_CHANGE_BOT\"> бота </a>"
    bittrex="<a href=\"https://bittrex.com/\"> BITTREX </a>"
    binance="<a href=\"https://www.binance.com/?ref=11117995\"> BINANCE </a>"
    razdel="<a href=\"https://bestinvestor.ru/faq-po-torgovle-na-birzhe/\"> этот раздел </a>"
    bot.send_message(message.chat.id,const.newsignals%(bott,bittrex,binance,razdel), parse_mode="HTML", reply_markup=markups.signals(message.chat.id))


@bot.message_handler(regexp="FAQ")
def faq(message):
    bot.send_message(message.chat.id,const.faq,parse_mode="HTML")


@bot.message_handler(regexp="Рекомендации по торговле")
def recom(message):
    bot.send_message(message.chat.id,"https://t.me/joinchat/AAAAAEGc_n6ACFcpaZH9qg")


@bot.message_handler(regexp="Начать работу")
def start_work(message):
    bot.send_message(message.chat.id, "Текст 2 ", reply_markup=markups.mainMenu(message.chat.id))


# Вторая клавиатура
@bot.message_handler(regexp="📱 Статус подписки")
def subscription_status(msg):
    db = connect()
    cur = db.cursor()
    r = "SELECT end_date FROM payments WHERE uid = %s"
    cur.execute(r, msg.chat.id)
    end = cur.fetchone()
    db.close()
    if end:
        now = time.time()  # Время в секундах настоящее
        sub_date = time.strptime(end[0], "%Y-%m-%d")  # Время в struct_time подписки
        sub_s = time.mktime(sub_date)  # Время подписки в секундах
        delta = ceil((sub_s - now) / (60 * 60 * 24))
        bot.send_message(msg.chat.id, "Количество оставшихся дней подписки: " + str(delta))
    else:
        bot.send_message(msg.chat.id, "Вы ещё не купили подписку")


@bot.message_handler(regexp="🌏 Купить VIP подписку")
def buy_vip(message):
    bot.send_message(message.chat.id, const.startWorkMsg,
                     reply_markup=markups.startWork())


@bot.message_handler(regexp="🔧 Связаться со службой поддержки")
def support(msg):

    bot.send_message(msg.chat.id, "Опишите свою проблему,написав по адресу: @bestinvestor_admin ",parse_mode="HTML")
    # bot.register_next_step_handler(message, send_to_support)


# def send_to_support(message):
#     if message.text.upper() != "ОТМЕНА":
#         cur = connect().cursor()
#         r = "SELECT first_name, alias FROM users WHERE uid = %s"
#         cur.execute(r, str(message.chat.id))
#         user = cur.fetchone()
#         msg = "Новое обращение в службу поддержки:\n" + message.text + "\n\n" + user[0]
#         if user[1] is not None:
#             msg += " @"+user[1]
#         bot.send_message(const.admin[0], msg)
#         bot.send_message(message.chat.id, "Ваше сообщение принято на рассмотрение, "
#                                           "администратор свяжетя с вами в ближайшее время.",
#                          reply_markup=markups.mainMenu(message.chat.id))
#     else:
#         bot.send_message(message.chat.id, "Отменено",
#                          reply_markup=markups.mainMenu(message.chat.id))


@bot.message_handler(regexp="📊 Результаты")
def results(msg):
    bot.send_message(msg.chat.id, "Результаты вы можете посмотреть по кнопке ниже",
                     reply_markup=telebot.types.InlineKeyboardMarkup().row(telebot.types.InlineKeyboardButton(
                         "Результаты",
                         url='https://t.me/results_crypto_signal')))


@bot.callback_query_handler(func=lambda call: call.data == "conditions")
def show_conditions(call):
    bot.send_message(call.message.chat.id, const.conditionsMsg)


@bot.callback_query_handler(func=lambda call: call.data == "news")
def channel_link(call):
    bot.send_message(call.message.chat.id, const.channelLink)


@bot.callback_query_handler(func=lambda call: call.data == "socialNetworks")
def show_media(call):
    bot.edit_message_text("текст", call.message.chat.id, call.message.message_id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markups.socialNetworks())


@bot.callback_query_handler(func=lambda call: call.data == "profit")
def show_profit(call):
    bot.send_message(call.message.chat.id, "Выберите подписку", reply_markup=markups.chooseDuration())
    bot.send_message(call.message.chat.id, "💡Так же подписку можно оплатить не только биткоинами, но и эфириумом, advcash, perfect money.\n\n"
                                           "💫По вопросам приобретения подписки эфириумом, advcash, perfect money пишите сюда @bestinvestor_admin")


@bot.callback_query_handler(func=lambda call: call.data == "processPayment")
def choose_duration(call):
    bot.send_message(call.message.chat.id, const.profitMsg, reply_markup=markups.payBtnMarkup())


@bot.callback_query_handler(func=lambda call: call.data[:4] == "days")
def process_payment(call):
    days = call.data[4:]
    markup = telebot.types.InlineKeyboardMarkup()
    btc = telebot.types.InlineKeyboardButton(text='Оплата BTC', callback_data='BTC'+days)
    eth = telebot.types.InlineKeyboardButton(text='Оплата ETH', callback_data='ETH' + days)
    markup.row(btc)
    markup.row(eth)

    bot.send_message(call.message.chat.id, 'Выберите способ оплаты.', parse_mode="html", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data[:3] == 'BTC')
def payBTC(call):
    days = call.data[3:]

    if days == "15":
        pay = const.days15
    elif days == "30":
        pay = const.days30
    elif days == "60":
        pay = const.days60
    elif days == "90":
        pay = const.days90
    else:
        pay = const.days_forever

    address = create_btc_address(call.message)[0]
    if not address:
        bot.send_message(call.message.chat.id, "К сожалению, в данный момент все кошельки для перевода заняты. "
                                               "Подождите и отправте запрос через 10 минут.", parse_mode="html")
        return
    db = connect()
    cur = db.cursor()
    now = int(time.time())
    r = 'UPDATE TEMP_DETAILS SET ID = %s, end_time = %s WHERE BTC_ADDRESS = %s'
    cur.execute(r, (call.message.chat.id, now + 28800, address,))
    db.commit()
    db.close()
    bot.send_message(call.message.chat.id, const.paymentMsg.format(pay, address), parse_mode="html")


@bot.callback_query_handler(func=lambda call: call.data[:3] == 'ETH')
def payETH(call):
    days = call.data[3:]
    print(days)
    if days == "15":
        pay = const.days15
    elif days == "30":
        pay = const.days30
    elif days == "60":
        pay = const.days60
    elif days == "90":
        pay = const.days90
    else:
        pay = const.days_forever
        days = 0
    print(pay)
    comment = hex(call.message.chat.id)
    eth = getRateETH()
    btc = getRateBTC()
    '''1 eth - n usd
        1 btc - n usd'''
    # get price btc in usd
    priceBTCUSD = btc * pay
    priceUSDETH = priceBTCUSD / eth
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton(text="Что такое хэш транзакции?", url="https://bestinvestor.ru/txhash-xesh-tranzakcii-ethereum/")
    markup.add(btn)
    createTransaction(call.message.chat.id, comment, '%.5f' % priceUSDETH, int(days))
    msg = bot.send_message(call.message.chat.id, "Отправьте точно <b>%.5f</b> ETH на адрес <code>%s</code>\n"
                                            "<b>ОБЯЗАТЕЛЬНО!</b> Укажите в комментарии строку <i>%s</i>,"
                                            " чтобы мы могли проверить принадлежность транзакции именно вам.\n"
                                            "<b>ВНИМАНИЕ!</b> в следующем сообщении пришлите хэш транзакции." % (
                           priceUSDETH, const.ethAddress, comment), parse_mode='html', reply_markup=markup)
    bot.register_next_step_handler(msg, validateTransaction)


def createTransaction(uid, comment, amount, days):
    db = connect()
    cur = db.cursor()
    cur.execute('SELECT * FROM awaitReceipt WHERE  uid = %s', uid)
    if not cur.fetchone():
        cur.execute('INSERT INTO awaitReceipt (uid, comment, amount, days) VALUES (%s,%s,%s,%s)', (uid, comment, amount, days))
    else:
        cur.execute('UPDATE awaitReceipt SET comment = %s, amount = %s, days = %s WHERE uid = %s', (comment, amount, days, uid))
    db.commit()
    db.close()


def validateTransaction(message):
    msg, error = getTransactionByHash(message.text, message.chat.id)
    if error != '':
        bot.send_message(248835526, 'Ошибка получения транзакции\n' + error)
    bot.send_message(message.chat.id, msg)


def getDate(uid):
    db = connect()
    cur = db.cursor()
    cur.execute('SELECT end_date FROM payments WHERE uid = %s', uid)
    res = cur.fetchone()[0]
    db.close()
    return res


def getTransactionByHash(tx_hash, uid):
    web3 = Web3(HTTPProvider('https://api.myetherapi.com/eth'))
    try:
        d = web3.eth.getTransaction(tx_hash)
        if d:
            value = float(web3.fromWei(d.get('value'), 'ether'))
            comment = d.get('input')
            db = connect()
            cur = db.cursor()
            cur.execute('SELECT comment, amount, days FROM awaitReceipt WHERE uid = %s', uid)
            data = cur.fetchone()
            db.close()
            input_field, amount, days = data
            if input_field == comment:
                if float(amount) == value:
                    if not isCompletedTransaction(tx_hash):
                        createPayment(uid, int(days))
                        incrementReferal(uid, int(days))
                        completeTransaction(tx_hash)
                        date = getDate(uid)
                        return "Ваша подписка оплачена до {date}".format(date=date), ''
                    else:
                        return 'Эта транзакция уже принята в нашей системе.', ''
                else:
                    return 'Сумма платежа не совпадает с запрошенной.', ''
            else:
                return 'Эта транзакция проведена не вами.', ''
        else:

            return "Ваш перевод еще не в Blockchain. Ваш перевод обрабатывается.\n\nПопробуйте ввести хэш повторно позже!", ''
    except Exception as e:
            return "Упс! Что-то пошло не так.\nНапишите в тех.поддержку.", str(e)


def createPayment(uid, days):
    db = connect()
    cur = db.cursor()
    cur.execute('SELECT end_date FROM payments WHERE uid = %s', uid)
    data = cur.fetchone()[0]
    if data:
        if days == 0:
            date = str(parser.parse(data) + datetime.timedelta(days=3650)).split()[0]
        else:
            date = str(parser.parse(data) + datetime.timedelta(days=days)).split()[0]
        cur.execute('UPDATE payments SET end_date = %s WHERE uid = %s', (date, uid))
    else:
        today = str(datetime.datetime.now()).split(' ')[0]
        date = parser.parse(today) + datetime.timedelta(days=days)
        cur.execute('INSERT INTO payments (uid, end_date) VALUES (%s, %s)', (uid, date))
    cur.execute('DELETE FROM lost_subs WHERE uid = %s', uid)
    db.commit()

    cur.execute("SELECT alias, first_name FROM users WHERE uid = %s", uid)
    res = cur.fetchone()
    if res[0]:
        nick = '@' + res[0]
    else:
        nick = res[1]
    db.close()
    bot.send_message(399004222, 'Пользователь %s опалатил подписку до %s' % (nick, date))


def addDays(message):
    try:
        int(message.text)
    except:
        bot.send_message(message.chat.id, 'Неверный формат ввода.')
        return
    db = connect()
    cur = db.cursor()
    cur.execute('SELECT * FROM payments')
    data = cur.fetchall()
    print(data)
    for each in data:
        uid, oldDate = each
        date = str(parser.parse(oldDate) + datetime.timedelta(days=int(message.text))).split()[0]
        cur.execute('UPDATE payments SET end_date = %s WHERE uid = %s', (date, uid))
    db.commit()
    db.close()
    bot.send_message(message.chat.id, 'Всем пользователям добавлено %s дней' % message.text)


def incrementReferal(uid, days):
    db = connect()
    cur = db.cursor()
    cur.execute('SELECT price FROM prices WHERE days = %s', days)
    price = float(cur.fetchone()[0])
    cur.execute('SELECT ID FROM INVITATIONS WHERE INVITED = %s', uid)
    data = cur.fetchone()
    addFirst = price * 0.1
    addSecond = price * 0.04
    addThird = price * 0.01
    if data:
        initialId = data[0]
        cur.execute('UPDATE users SET balance = balance + %s WHERE uid = %s', (addFirst, initialId))
        cur.execute('SELECT ID FROM INVITATIONS WHERE INVITED = %s', initialId)
        data = cur.fetchone()
        if data:
            initialId = data[0]
            cur.execute('UPDATE users SET balance = balance + %s WHERE uid = %s', (addSecond, initialId))
            cur.execute('SELECT ID FROM INVITATIONS WHERE INVITED = %s', initialId)
            data = cur.fetchone()
            if data:
                initialId = data[0]
                cur.execute('UPDATE users SET balance = balance + %s WHERE uid = %s', (addThird, initialId))
    db.commit()
    db.close()


def isCompletedTransaction(tx_hash):
    db = connect()
    cur = db.cursor()
    cur.execute('SELECT * FROM completedTransactions WHERE tx_hash = %s', tx_hash)
    data = cur.fetchone()
    db.close()
    if data:
        return True
    return False


def completeTransaction(tx_hash):
    db = connect()
    cur = db.cursor()
    cur.execute('INSERT INTO completedTransactions (tx_hash) VALUES (%s)', tx_hash)
    db.commit()
    db.close()


def create_btc_address(msg):
    """
    sign = hashlib.md5("".join((const.wallet_id, const.walletApiKey)).encode()).hexdigest()
    data = {
        "wallet_id": const.wallet_id,
        "sign": sign,
        "action": "create_btc_address"
    }
    url = "https://wallet.free-kassa.ru/api_v1.php"
    response = requests.post(url, data).json()
    print(response)
    return response.get("data").get("address")"""
    db = connect()
    cur = db.cursor()
    now = time.time()
    cur.execute('SELECT BTC_ADDRESS FROM TEMP_DETAILS WHERE ID=%s', (msg.chat.id,))
    ans = cur.fetchone()
    if not ans:
        cur.execute('SELECT BTC_ADDRESS FROM TEMP_DETAILS WHERE end_time<%s', (int(now),))
        ans = cur.fetchone()
    db.close()

    return ans


def send_payment_message(cid):
    bot.send_message(256711367,
                     "Сообщение отправлено из блока send_payment_message с переданным сюда параметром " + cid)


def init_bot_polling():
    # apihelper.proxy = {'https': 'socks5://77.247.94.153:8888'} # RSocks:RSforTG2@telers4.rsocks.net:1490'} # socks5://telegram:telegram@doyss.teletype.live:1080'} # socks5://telegram:telegram@sr123.spry.fail:1080'}
    bot.remove_webhook()
    while True:
        try:
            bot.polling()
        except telebot.apihelper.ApiException as e:
            if e.message in ("Bad Gateway", "Timed out"):
                time.sleep(1)
        except Exception as e:
            bot.send_message(256711367, str(e))


def init_bot():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                    certificate=open(WEBHOOK_SSL_CERT, 'r'))

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)

    db = connect()
    cur = db.cursor()
    r = "SELECT * FROM prices ORDER BY days"
    cur.execute(r)
    prices = cur.fetchall()
    const.days_forever = float(prices[0][1])
    const.days15 = float(prices[1][1])
    const.days30 = float(prices[2][1])
    const.days60 = float(prices[3][1])
    const.days90 = float(prices[4][1])
    db.close()

    web.run_app(
        app,
        host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=context,
    )


if __name__ == '__main__':
    init_bot()
