import datetime
import time

import requests
from math import ceil
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from web3 import HTTPProvider, Web3
from dateutil import parser

from tbot import bot, const, markups
from tbot.models import *


@bot.message_handler(regexp="📱 Статус подписки")
def subscription_status(msg):
    end = Payments.get_or_none(Payments.uid == msg.chat.id)
    if end is not None:
        now = time.time()  # Время в секундах настоящее
        sub_date = time.strptime(end.end_date, "%Y-%m-%d")  # Время в struct_time подписки
        sub_s = time.mktime(sub_date)  # Время подписки в секундах
        delta = ceil((sub_s - now) / (60 * 60 * 24))
        bot.send_message(msg.chat.id, f"Количество оставшихся дней подписки: {delta}")
    else:
        bot.send_message(msg.chat.id, "Вы ещё не купили подписку")


@bot.message_handler(regexp="Рекомендации по торговле")
def recom(message):
    bot.send_message(message.chat.id, "https://t.me/joinchat/AAAAAEGc_n6ACFcpaZH9qg")


@bot.message_handler(regexp="FAQ")
def faq(message):
    bot.send_message(message.chat.id, const.faq, parse_mode="HTML")


@bot.message_handler(regexp="🌏 Купить VIP подписку")
def buy_vip(message):
    bot.send_message(message.chat.id, const.startWorkMsg,
                     reply_markup=markups.start_work())


@bot.callback_query_handler(func=lambda call: call.data == "processPayment")
def choose_duration(call):
    bot.send_message(call.message.chat.id, const.profitMsg, reply_markup=markups.pay_btn_markup())


@bot.callback_query_handler(func=lambda call: call.data == "conditions")
def show_conditions(call):
    bot.send_message(call.message.chat.id, const.conditionsMsg)


@bot.callback_query_handler(func=lambda call: call.data == "profit")
def show_profit(call):
    bot.send_message(call.message.chat.id, "Выберите подписку", reply_markup=markups.choose_duration())
    bot.send_message(call.message.chat.id,
                     "💡Так же подписку можно оплатить не только биткоинами, но и эфириумом, advcash, perfect money.\n\n"
                     "💫По вопросам приобретения подписки эфириумом, advcash, perfect money пишите сюда "
                     "@bestinvestor_admin")


@bot.callback_query_handler(func=lambda call: call.data[:4] == "days")
def process_payment(call):
    days = call.data[4:]
    markup = InlineKeyboardMarkup()
    btc = InlineKeyboardButton(text='Оплата BTC', callback_data='BTC' + days)
    eth = InlineKeyboardButton(text='Оплата ETH', callback_data='ETH' + days)
    markup.row(btc)
    markup.row(eth)

    bot.send_message(call.message.chat.id, 'Выберите способ оплаты.', parse_mode="html", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data[:3] == 'BTC')
def payBTC(c):
    days = c.data[3:]

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
    address = TempDetails.get_or_none(TempDetails.id == c.message.chat.id)
    if address is None:
        address = TempDetails.get_or_none(TempDetails.end_time < int(time.time()))
    if address is None:
        bot.send_message(c.message.chat.id, "К сожалению, в данный момент все кошельки для перевода заняты. "
                                            "Подождите и отправте запрос через 10 минут.", parse_mode="html")
        return
    TempDetails.update(end_time=int(time.time()) + 28800).where(TempDetails.id == address.id).execute()
    bot.send_message(c.message.chat.id, const.paymentMsg.format(pay, address.btc_address), parse_mode="html")


@bot.callback_query_handler(func=lambda call: call.data[:3] == 'ETH')
def payETH(call):
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
        days = 0
    comment = hex(call.message.chat.id)
    rates = get_rates()
    eth = rates['ETH']
    btc = rates['BTC']
    '''1 eth - n usd
        1 btc - n usd'''
    # get price btc in usd
    price_btc_usd = btc * pay
    price_usd_eth = price_btc_usd / eth
    markup = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(text="Что такое хэш транзакции?",
                               url="https://bestinvestor.ru/txhash-xesh-tranzakcii-ethereum/")
    markup.add(btn)
    createTransaction(call.message.chat.id, comment, '%.5f' % price_usd_eth, int(days))
    msg = bot.send_message(call.message.chat.id,
                           "Отправьте точно <b>%.5f</b> ETH на адрес <code>%s</code>\n"
                           "<b>ОБЯЗАТЕЛЬНО!</b> Укажите в комментарии строку <i>%s</i>,"
                           " чтобы мы могли проверить принадлежность транзакции именно вам.\n"
                           "<b>ВНИМАНИЕ!</b> в следующем сообщении пришлите хэш транзакции." % (price_usd_eth,
                                                                                                const.ethAddress,
                                                                                                comment),
                           parse_mode='html',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, validateTransaction)


def get_rates():
    url = "https://api.coinmarketcap.com/v1/ticker/"
    response = requests.get(url)
    ans = {}
    for i in response.json():
        if i.get('name') == "Bitcoin":
            ans.update({"BTC": float(i.get('price_usd'))})
        if i.get('name') == "Ethereum":
            ans.update({"ETH": float(i.get('price_usd'))})
        if len(ans) == 2:
            return ans


def createTransaction(uid, comment, amount, days):
    ar, created = AwaitReceipt.get_or_create(uid=uid, defaults={"comment": comment,
                                                                "amount": amount,
                                                                "days": days})
    if not created:
        AwaitReceipt.update({AwaitReceipt.comment: comment,
                             AwaitReceipt.amount: amount,
                             AwaitReceipt.days: days}).where(AwaitReceipt.uid == uid).execute()


def validateTransaction(message):
    msg, error = getTransactionByHash(message.text, message.chat.id)
    if error != '':
        bot.send_message(248835526, 'Ошибка получения транзакции\n' + error)
    bot.send_message(message.chat.id, msg)


def getTransactionByHash(tx_hash, uid):
    w3 = Web3(HTTPProvider("https://mainnet.infura.io/v3/408cdad1df7a4e6987ce2f515d5b48dc"))
    try:
        d = w3.eth.getTransaction(tx_hash)

        if d:
            value = float(w3.fromWei(d.get('value'), 'ether'))
            comment = d.get('input')
            ar = AwaitReceipt.get(AwaitReceipt.uid == uid)
            input_field = ar.comment
            amount = ar.amount
            days = ar.days
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
            return "Ваш перевод еще не в Blockchain. Ваш перевод обрабатывается.\n\n" \
                   "Попробуйте ввести хэш повторно позже!", ''
    except Exception as e:
        return "Упс! Что-то пошло не так.\nНапишите в тех.поддержку.", str(e)


def isCompletedTransaction(tx_hash):
    data = CompletedTransactions.get_or_none(CompletedTransactions.tx_hash == tx_hash)
    if data is not None:
        return True
    return False


def createPayment(uid, days):
    if days == 0:
        days = 3650
    today = str(datetime.datetime.now()).split(' ')[0]
    date = parser.parse(today) + datetime.timedelta(days=days)
    data, created = Payments.get_or_create(uid=uid, defaults={"end_date": date})
    if not created:
        date = str(parser.parse(data.end_date) + datetime.timedelta(days=days)).split()[0]
        Payments.update(end_date=date).where(Payments.uid == data.uid).execute()

    q = LostSubs.delete().where(LostSubs.uid == uid).execute()
    q.execute()
    user = Users.get_by_id(uid)
    if user.alias or user.alias == "@None":
        nick = '@' + user.alias
    else:
        nick = user.first_name
    bot.send_message(399004222, 'Пользователь %s опалатил подписку до %s' % (nick, date))


def incrementReferal(uid, days):
    price = Prices.get(Prices.days == days).price
    add_first = price * 0.1
    add_second = price * 0.04
    add_third = price * 0.01
    inv = Invitations.get_or_none(Invitations.invited == uid)

    if inv is not None:
        initial_id = inv.id
        q = Users.update({Users.balance: Users.balance + add_first}).where(Users.uid == initial_id)
        q.execute()
        print('ras')
        inv = Invitations.get_or_none(Invitations.invited == initial_id)
        if inv is not None:
            print('ras')
            initial_id = inv.id
            q = Users.update({Users.balance: Users.balance + add_second}).where(Users.uid == initial_id)
            q.execute()

            inv = Invitations.get_or_none(Invitations.invited == initial_id)
            if inv is not None:
                print('ras')
                initial_id = inv.id
                q = Users.update({Users.balance: Users.balance + add_third}).where(Users.uid == initial_id)
                q.execute()


def completeTransaction(tx_hash):
    CompletedTransactions.create(tx_hash=tx_hash)


def getDate(uid):
    p = Payments.get(Payments.uid == uid)
    return p.end_date
