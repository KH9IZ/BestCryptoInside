import telebot

from tbot import const


def main_menu(uid):
    markup = telebot.types.ReplyKeyboardMarkup(True, False)
    if uid in const.admin:
        markup.row("Рассылка", "👤 Админ")
    markup.row("💰 Сигналы и рекомендации")
    markup.row("📊 Результаты", "💌 Отзывы")
    markup.row("👥 Партнерская программа")
    markup.row("🔧 Связаться со службой поддержки")
    return markup


def withdraw_btn():
    markup = telebot.types.InlineKeyboardMarkup(1)
    btn = telebot.types.InlineKeyboardButton(text="Вывести", callback_data="withdraw")
    btn2 = telebot.types.InlineKeyboardButton(text="Приглашённые пользователи", callback_data="inv_users")
    markup.add(btn, btn2)
    return markup


def signals(uid):
    markup = telebot.types.ReplyKeyboardMarkup(True, False)
    if uid in const.admin:
        markup.row("Рассылка", "👤 Админ")
    markup.row("📱 Статус подписки", "🌏 Купить VIP подписку")
    markup.row("Рекомендации по торговле")
    markup.row("FAQ", "⬅️Назад")

    return markup


def start_work():
    markup = telebot.types.InlineKeyboardMarkup()
    profit = telebot.types.InlineKeyboardButton(text="Стоимость подписки", callback_data="profit")
    pay_btn = telebot.types.InlineKeyboardButton(text="Что входит в подписку?", callback_data="processPayment")
    conditions = telebot.types.InlineKeyboardButton(text="Условия", callback_data="conditions")
    news = telebot.types.InlineKeyboardButton(text="Новости", url="https://t.me/bestinvestor_news")
    markup.add(pay_btn)
    markup.add(profit)
    markup.row(news)
    markup.add(conditions)
    return markup


def choose_duration():
    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton(text="15 дней — %s btc" % const.days15, callback_data="days15")
    btn2 = telebot.types.InlineKeyboardButton(text="30 дней — %s btc" % const.days30, callback_data="days30")
    btn3 = telebot.types.InlineKeyboardButton(text="60 дней — %s btc" % const.days60, callback_data="days60")
    btn4 = telebot.types.InlineKeyboardButton(text="90 дней — %s btc" % const.days90, callback_data="days90")
    btn5 = telebot.types.InlineKeyboardButton(text="Бессрочно — %s btc" % const.days_forever,
                                              callback_data='days_forever')
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    markup.add(btn4)
    markup.add(btn5)
    return markup


def pay_btn_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    pay_btn = telebot.types.InlineKeyboardButton(text="Оплатить", callback_data="profit")
    markup.add(pay_btn)
    return markup


def back():
    mp = telebot.types.ReplyKeyboardMarkup(True, True)
    mp.row("Назад")
    return mp


def adminPanel():
    mp = telebot.types.InlineKeyboardMarkup(row_width=1)
    mp.add(
        telebot.types.InlineKeyboardButton(text="Рассылка всем пользователям", callback_data="toAll"),
        telebot.types.InlineKeyboardButton(text="Рассылка не по подписке", callback_data="toNotPaid"),
        telebot.types.InlineKeyboardButton(text="Рассылка пользователям c оконченной подпиской",
                                           callback_data="toLostSubs"),
        telebot.types.InlineKeyboardButton(text="Список пользователей", callback_data="usersTypes"),
        telebot.types.InlineKeyboardButton(text="Изменить цены на подписку", callback_data="changePrices"),
        telebot.types.InlineKeyboardButton(text='Добавить дни подписки для каждого', callback_data='incrementAll'),
    )
    mp.row(
        telebot.types.InlineKeyboardButton(text="Включить демо доступ", callback_data="demo on"),
        telebot.types.InlineKeyboardButton(text="Выключить демо доступ", callback_data="demo off"),
    )
    return mp


def usersTypes():
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    btn_all = telebot.types.InlineKeyboardButton(text="Все пользователи", callback_data="users_1_all")
    btn_paid = telebot.types.InlineKeyboardButton(text="Пользователи купившие подписку", callback_data="users_1_paid")
    btn_not_paid = telebot.types.InlineKeyboardButton(text="Пользователи без подписки",
                                                      callback_data="users_1_notpaid")
    btn_lost = telebot.types.InlineKeyboardButton(text="Пользователи c закончившейся подпиской",
                                                  callback_data="users_1_lost")
    search_name = telebot.types.InlineKeyboardButton(text="Поиск по имени", callback_data="searchbyname")
    search_surname = telebot.types.InlineKeyboardButton(text="Поиск по фамилии", callback_data="searchbysurname")
    search_alias = telebot.types.InlineKeyboardButton(text="Поиск по нику", callback_data="searchbyalias")
    menu = telebot.types.InlineKeyboardButton(text="Меню", callback_data="admin")
    markup.add(btn_all, btn_paid, btn_not_paid, btn_lost, search_name, search_surname, search_alias, menu)
    return markup


def chooseMonth():
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        telebot.types.InlineKeyboardButton(text="15 дней", callback_data="$$15"),
        telebot.types.InlineKeyboardButton(text="30 дней", callback_data="$$30"),
        telebot.types.InlineKeyboardButton(text="60 дней", callback_data="$$60"),
        telebot.types.InlineKeyboardButton(text="90 дней", callback_data="$$90"),
        telebot.types.InlineKeyboardButton(text="Бессрочно", callback_data="$$forever"),
        telebot.types.InlineKeyboardButton(text="Назад", callback_data="admin"),
    )
    return markup


def users_mp(users, page, u_type, count):
    mp = telebot.types.InlineKeyboardMarkup(row_width=2)
    for user in users:
        if user.alias:
            text = "@"+user.alias
        else:
            text = user.first_name
        mp.row(
            telebot.types.InlineKeyboardButton(text=text, callback_data=f"<{user.uid}")
        )

    arrows = []
    if page != 1:
        arrows.append(telebot.types.InlineKeyboardButton("⬅️", callback_data=f"users_{page-1}_{u_type}"))
    if page*10 < count:
        arrows.append(telebot.types.InlineKeyboardButton("➡️", callback_data=f"users_{page+1}_{u_type}"))
    mp.add(*arrows)

    menu = telebot.types.InlineKeyboardButton(text="Меню", callback_data="admin")
    back_to = telebot.types.InlineKeyboardButton(text="Назад", callback_data="usersTypes")
    mp.row(back_to)
    mp.row(menu)
    return mp


def show_details(uid):
    markup = telebot.types.InlineKeyboardMarkup()
    change_data = telebot.types.InlineKeyboardButton(text="Изменить срок подписки", callback_data=f"changeDate{uid}")
    back_btn = telebot.types.InlineKeyboardButton(text="Назад", callback_data="usersTypes")
    markup.row(change_data)
    markup.row(back_btn)
    return markup
