import telebot

import const


def startMenu(uid):
    markup = telebot.types.ReplyKeyboardMarkup(True, False)
    markup.row("Отзывы", "Начать работу")
    if uid in const.admin:
        markup.row("Рассылка", "👤 Админ")
    return markup


def mainMenu(uid):
    markup = telebot.types.ReplyKeyboardMarkup(True, False)
    if uid in const.admin:
        markup.row("Рассылка", "👤 Админ")
    markup.row("💰 Сигналы и рекомендации")
    markup.row("📊 Результаты", "💌 Отзывы")
    markup.row("👥 Партнерская программа")
    markup.row("🔧 Связаться со службой поддержки")

    return markup

def signals(uid):
    markup = telebot.types.ReplyKeyboardMarkup(True, False)
    if uid in const.admin:
        markup.row("Рассылка", "👤 Админ")
    markup.row("📱 Статус подписки", "🌏 Купить VIP подписку")
    markup.row("Рекомендации по торговле")
    markup.row("FAQ", "⬅️Назад")

    return markup


def adminPanel():
    markup = telebot.types.InlineKeyboardMarkup()
    allBtn = telebot.types.InlineKeyboardButton(text="Рассылка всем пользователям", callback_data="toAll")
 #   paid = telebot.types.InlineKeyboardButton(text="Рассылка по подписке", callback_data="toPaid")
    not_paid = telebot.types.InlineKeyboardButton(text="Рассылка не по подписке", callback_data="toNotPaid")
    lost_subs = telebot.types.InlineKeyboardButton(text="Рассылка пользователям c оконченной подпиской", callback_data="toLostSubs")
    video = telebot.types.InlineKeyboardButton(text="Добавить видео", callback_data="addVideo")
    users = telebot.types.InlineKeyboardButton(text="Список пользователей", callback_data="usersTypes")
    demo_on = telebot.types.InlineKeyboardButton(text="Включить демо доступ", callback_data="demo on")
    demo_off = telebot.types.InlineKeyboardButton(text="Выключить демо доступ", callback_data="demo off")
    changePrice = telebot.types.InlineKeyboardButton(text="Изменить цены на подписку", callback_data="changePrices")
    bonus = telebot.types.InlineKeyboardButton(text='Добавить дни подписки для каждого', callback_data='incrementAll')
  #  markup.row(paid)
    markup.row(allBtn)
    markup.row(not_paid)
    markup.row(lost_subs)
    markup.row(video)
    markup.row(users)
    markup.row(changePrice)
    markup.row(bonus)
    markup.add(demo_on, demo_off)

    return markup


def startWork():
    markup = telebot.types.InlineKeyboardMarkup()
    # profit = telebot.types.InlineKeyboardButton(text="Что я получу за %s BTC?" % const.days15, callback_data="profit")
    profit = telebot.types.InlineKeyboardButton(text="Стоимость подписки", callback_data="profit")
    payBtn = telebot.types.InlineKeyboardButton(text="Что входит в подписку?", callback_data="processPayment")
    conditions = telebot.types.InlineKeyboardButton(text="Условия", callback_data="conditions")
    news = telebot.types.InlineKeyboardButton(text="Новости", url="https://t.me/bestinvestor_news")
    socialNetworksBtn = telebot.types.InlineKeyboardButton(text="Социальные сети", callback_data="https://vk.com/best_investor")
    markup.add(payBtn)
    markup.add(profit)
    markup.row(news, socialNetworksBtn)
    markup.add(conditions)
    return markup


def payBtnMarkup():
    markup = telebot.types.InlineKeyboardMarkup()
    payBtn = telebot.types.InlineKeyboardButton(text="Оплатить", callback_data="profit")
    markup.add(payBtn)
    return markup


def socialNetworks():
    markup = telebot.types.InlineKeyboardMarkup()
    net1 = telebot.types.InlineKeyboardButton(text="Соц сеть 1", url="google.com")
    net2 = telebot.types.InlineKeyboardButton(text="Соц сеть 2", url="google.com")
    markup.add(net1)
    markup.add(net2)
    return markup


def packets():
    markup = telebot.types.InlineKeyboardMarkup()
    investor = telebot.types.InlineKeyboardButton(text="Investor pack - %s BTC/месяц" % const.investorPrice,
                                                  callback_data="packinvestor")
    trader = telebot.types.InlineKeyboardButton(text="Trader pack - %s BTC/месяц" % const.traderPrice,
                                                callback_data="packtrader")
    full = telebot.types.InlineKeyboardButton(text="Full pack - %s BTC/месяц" % const.fullPrice,
                                              callback_data="packfull")
    markup.add(investor)
    markup.add(trader)
    markup.add(full)
    return markup


def chooseDuration():
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


def withdrawBtn():
    markup = telebot.types.InlineKeyboardMarkup(1)
    btn = telebot.types.InlineKeyboardButton(text="Вывести", callback_data="withdraw")
    btn2 = telebot.types.InlineKeyboardButton(text="Приглашённые пользователи", callback_data="inv_users")
    markup.add(btn, btn2)
    return markup


def usersTypes():
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    btn_all = telebot.types.InlineKeyboardButton(text="Все пользователи", callback_data="users_all")
    btn_paid = telebot.types.InlineKeyboardButton(text="Пользователи купившие подписку", callback_data="users_paid")
    btn_not_paid = telebot.types.InlineKeyboardButton(text="Пользователи без подписки", callback_data="users_not_paid")
    btn_lost = telebot.types.InlineKeyboardButton(text="Пользователи c закончившейся подпиской",
                                                  callback_data="users_lost")
    search_name = telebot.types.InlineKeyboardButton(text="Поиск по имени", callback_data="searchbyname")
    search_surname = telebot.types.InlineKeyboardButton(text="Поиск по фамилии", callback_data="searchbysurname")
    search_alias = telebot.types.InlineKeyboardButton(text="Поиск по нику", callback_data="searchbyalias")
    menu = telebot.types.InlineKeyboardButton(text="Меню", callback_data="admin")
    markup.add(btn_all, btn_paid, btn_not_paid,btn_lost, search_name,search_surname,search_alias, menu)
    return markup


def users():
    markup = telebot.types.InlineKeyboardMarkup()
    length = len(const.userList)
    if length != 0:
        for i in range(10):
            f, b = False, False
            if const.listPointer*10 + i > length - 1:
                break
            data = const.userList[const.listPointer * 10 + i]
            symbol = data.find('%')
            btn = telebot.types.InlineKeyboardButton(text=data[:symbol], callback_data="<" + data[symbol+1:])
            markup.row(btn)
        if i == 9:
            forward = telebot.types.InlineKeyboardButton(text="➡️", callback_data="nextList")
            f = True
        if const.listPointer != 0:
            back = telebot.types.InlineKeyboardButton(text="⬅️", callback_data="prevList")
            b = True
        if f and b:
            markup.row(back, forward)
        elif f:
            markup.row(forward)
        elif b:
            markup.row(back)
    menu = telebot.types.InlineKeyboardButton(text="Меню", callback_data="admin")
    back_to = telebot.types.InlineKeyboardButton(text="Назад", callback_data="usersTypes")
    markup.row(back_to)
    markup.row(menu)
    return markup


def showDetails(uid):
    markup = telebot.types.InlineKeyboardMarkup()
    changeData = telebot.types.InlineKeyboardButton(text="Изменить срок подписки", callback_data="changeDate" + uid)
    back = telebot.types.InlineKeyboardButton(text="Назад", callback_data="usersList")
    markup.row(changeData)
    markup.row(back)
    return markup


def chooseMonth():
    markup = telebot.types.InlineKeyboardMarkup()
    btn1 = telebot.types.InlineKeyboardButton(text="15 дней", callback_data="$$15")
    btn2 = telebot.types.InlineKeyboardButton(text="30 дней", callback_data="$$30")
    btn3 = telebot.types.InlineKeyboardButton(text="60 дней", callback_data="$$60")
    btn4 = telebot.types.InlineKeyboardButton(text="90 дней", callback_data="$$90")
    btn5 = telebot.types.InlineKeyboardButton(text="Бессрочно", callback_data="$$forever")
    back = telebot.types.InlineKeyboardButton(text="Назад", callback_data="admin")
    markup.row(btn1)
    markup.row(btn2)
    markup.row(btn3)
    markup.row(btn4)
    markup.row(btn5)
    markup.row(back)
    return markup


def back():
    mp = telebot.types.ReplyKeyboardMarkup(True, True)
    mp.row("Назад")
    return mp
