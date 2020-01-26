from telebot import TeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from tbot import const, markups
from tbot.models import *

bot = TeleBot(token=const.tg_token, threaded=False)


@bot.message_handler(regexp="⬅️Назад")
@bot.message_handler(commands=["start"])
def start(msg):
    text = msg.text.split(" ")
    if len(text) == 2:
        if text[1].isdigit() and int(text[1]) != msg.chat.id:
            Invitations.get_or_create(invited=msg.chat.id, defaults={'ID': text[1]})
    user, created = Users.get_or_create(uid=msg.chat.id,
                                        defaults={
                                            'uid': msg.chat.id,
                                            'first_name': msg.from_user.first_name,
                                            'last_name': msg.from_user.last_name,
                                            'alias': msg.from_user.username
                                        })
    if not created:
        Users.update(
            first_name=msg.from_user.first_name,
            last_name=msg.from_user.last_name,
            alias=msg.from_user.username,
        ).where(Users.uid == user.uid).execute()
    sub = '*У вас активная демо-подписка.*\n\n' \
          'Вы получаете лишь небольшую часть сигналов. ' \
          'Для получения доступа ко всем сигналам Вам необходимо купить VIP подписку в меню бота.'
    payment = Payments.get_or_none(Payments.uid == msg.chat.id)
    if payment is not None:
        sub = '*У вас активная VIP-подписка*'
    bot.send_message(msg.chat.id, const.startMsg % (msg.from_user.first_name, sub),
                     reply_markup=markups.main_menu(msg.chat.id),
                     parse_mode="Markdown")


@bot.message_handler(regexp="💌 Отзывы")
def send(message):
    bot.send_message(message.chat.id, "Результаты вы можете посмотреть по кнопке ниже",
                     reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(
                         text="Отзывы",
                         url='https://t.me/otzivi_bestinvestor'
                     )))


@bot.message_handler(regexp="📊 Результаты")
def results(msg):
    bot.send_message(msg.chat.id, "Результаты вы можете посмотреть по кнопке ниже",
                     reply_markup=InlineKeyboardMarkup().row(InlineKeyboardButton(
                         text="Результаты",
                         url='https://t.me/results_crypto_signal'
                     )))


@bot.message_handler(regexp="🔧 Связаться со службой поддержки")
def support(msg):
    bot.send_message(msg.chat.id, "Опишите свою проблему,написав по адресу: @bestinvestor_admin ", parse_mode="HTML")


@bot.message_handler(regexp="👥 Партнерская программа")
def materials(msg):
    by_user = Invitations.get_or_none(Invitations.invited == msg.chat.id)
    inv_by = ""
    if by_user is not None:
        user = Users.get(Users.uid == by_user.id)
        inv_by = f"Вы приглашены пользователем {user.first_name} {user.last_name}\n\n"
    balance = f"<b>Ваш баланс:</b> {Users.get_by_id(msg.chat.id).balance} BTC\n"
    text = f"<b>Ваша реферальная ссылка:</b>\nhttps://t.me/BestCryptoInsideBot?start={msg.chat.id}"
    bot.send_message(msg.chat.id, inv_by + const.marketingMsg + balance + text, parse_mode="html",
                     reply_markup=markups.withdraw_btn())


@bot.message_handler(regexp="💰 Сигналы и рекомендации")
def sign(message):
    bott = "<a href=\"https://web.telegram.org/#/im?p=@BTC_CHANGE_BOT\"> бота </a>"
    bittrex = "<a href=\"https://bittrex.com/\"> BITTREX </a>"
    binance = "<a href=\"https://www.binance.com/?ref=11117995\"> BINANCE </a>"
    razdel = "<a href=\"https://bestinvestor.ru/faq-po-torgovle-na-birzhe/\"> этот раздел </a>"
    bot.send_message(message.chat.id, const.newsignals % (bott, bittrex, binance, razdel), parse_mode="HTML",
                     reply_markup=markups.signals(message.chat.id))


@bot.message_handler(regexp="👤 Админ")
def admin_menu(message):
    if message.chat.id in const.admin:
        bot.send_message(message.chat.id, "Админ-панель", reply_markup=markups.adminPanel())


from tbot import admin, subscription, refferal
