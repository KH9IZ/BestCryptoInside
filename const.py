# token = "317025779:AAFLih4bH_BjKIm8_giC-wD1geEd8d_tLCI"
token = "352564414:AAGW7tYoe43sbYUYJ-pKhP2-gjK_hebKGF8" #old
#token = "457162261:AAFLVZFlcHL1NoRK-OB-za-GISsW3eKRmRI"  # ТБ №7

startMsg = "*Рад Вас видеть, %s!*\n\n" + \
           "Наша команда профессионалов занимается биржевой торговлей криптовалют более чем 3 года. " + \
           "Так же мы сотрудничаем с другими трейдерами, у нас проплачены лучшие зарубежные и отечественные информационные каналы по сигналам.\n\n" + \
           "Наша цель, предоставлять лучшие сигналы для торговли криптовалют. Вам не нужно быть профессионалом в биржевой торговли, все это мы берем на себя. " + \
           "Все что вам нужно, это вовремя реагировать на наши сигналы.\n\n" + \
           "В боте Вы можете посмотреть наши результаты по торговле (РЕЗУЛЬТАТЫ) , отзывы (ОТЗЫВЫ), приобрести подписку на сигналы , посмотреть рекомендации по торговле, а так же получить партнерское вознаграждение за привлечения клиентов.\n\n" + \
           "%s"

marketingMsg = "Рекомендуй BestCryptoInsideBot своим друзьям и знакомым и получай моментальные выплаты" \
               " на свой BitCoin кошелек за каждую активацию подписки на 3 уровня в глубину:\n" \
               "1 уровень - <b>10 %</b>\n" \
               "2 уровень - <b>4 %</b>\n" \
               "3 уровень - <b>1 %</b>\n\n"

startWorkMsg = "Вам необходимо активировать подписку для пользования функционалом бота." \
               " Рекомендую подписаться на новостной канал в Telegram и на соц. сети," \
               " все материалы публикуемые там бесплатны!" \
               " Активируя аккаунт Вы автоматически соглашаетесь с условиями использования бота."

conditionsMsg = "Вся информация, предоставляемой BestCryptoInsideBot, является частной собственностью" \
                " и защищена законом «О защите информации». " \
                "Распространение и размещение информации на сторонних ресурсах строго запрещено!" \
                " При несоблюдении данного правила личный кабинет нарушителя блокируется без права на восстановление."

channelLink = "link on a channel"
re = "0u_mazafa"
profitMsg = "Активировав подписку на BestCryptoInsideBot вы получите:\n" \
            "* Помощь в формировании высокодоходного инвестиционного портфеля.\n" \
            "* Инструменты для автоматизации и удобства ведения торговли.\n" \
            "* Рассылку актуальной и свежей информации криптовалютного рынка.\n" \
            "* Сигналы для совершения краткосрочных прибыльных сделок."
paymentMsg = 'Отправьте точно <b>{0}</b> BTC на адрес <b>{1}</b>\n ' \
             'Ваша подписка будет автоматически активирована после одного подтверждения в сети BitCoin.\n' \
             'Скорость получения подписки зависит от установленной Вами комиссии транзакции. \n\n'\
             '‼️ ВНИМАНИЕ! Средства принимаются в течение <b>восьми часов</b>, ' \
             'начиная с момента отправки этого сообщения! ‼\n️'\
             'По прошествии <b>восьми часов</b> кошелёк может быть переназначен на другого пользователя. ' \
             'По всем вопросам обращайтесь в службу поддержки.'

newsignals="💰 <b>Рекомендации & Сигналы</b>\n\n"\
           "В этом разделе Вы сможете получить ценные советы по инвестициям и осуществлению выгодной торговли криптовалютами.\n\n" \
           "Вам больше не придется тратить время на изучение рынка и постоянно подвергать свои средства большим рискам."\
           "Наши советы и рекомендации позволят получать максимальную прибыль при минимальных затратах времени.\n\n"\
           "<b>Подписка откроет вам доступ к следующим преимуществам:</b>\n\n"\
           "- 🚀 Качественные прогнозы на перспективные монеты, которые вскоре должны показать хороший рост курса\n"\
           "- 💼 Рекомендации по составлению портфеля долгосрочных инвестиций\n"\
           "- 📝 Оценка текущей рыночной ситуации\n"\
           "- 📅 Аналитика и новости – вся информация, которая позволит спрогнозировать курс монет\n"\
           "- 🔥 Достоверные инсайды\n\n"\
           "<b>Стать криптовалютным трейдером проще, чем вы думаете:</b>\n\n"\
           "1⃣  Купите BTC любым удобным для вас способом (например, через %s\n"\
           "2⃣  Пройдите регистрацию и пополнение счета BTC на бирже %s и %s\n"\
           "3⃣  Совершайте покупку монет по сигналам. Подробнее о торговле расскажет %s\n"\
           "4⃣  Осуществляйте продажу монет по сигналам, когда они достигнут указанной цены\n"\
           "5⃣  Фиксируйте профит 🔥\n\n"\
           "Все подробности, необходимые для успешного трейдинга, читайте в разделе «РЕКОМЕНДАЦИЯ ПО ТОРГОВЛЕ»"
e = "cKY" + re
faq= "1. <b>Что такое сигналы криптовалют?</b>\n"\
     "Сигналы на покупку монет - это прогнозы на рост определенных криптовалют, основанные на техническом и фундаментальном анализе от наших аналитиков и информации из проверенных источников\n"\
     "<b>Как выглядят сигналы?</b>\n"\
     "<code style=\"color:#ff0000\">  •   Указанный сигнал — это пример! Не закупайтесь по нему, он написан для ознакомления!</code>\n"\
     "BTM buy 0.000153\n"\
     "Sell\n"\
     "Target : 0.0000186\n"\
     "Stop loss: 0.0000139\n\n"\
     "Buy – это цена по которой мы покупаем криптовалюту BTM\n"\
     "Target – цена по которой мы продаем, потенциальная прибыль +21,5%\n"\
     "Stop loss – это ограничение убытка, в данном случае убыток может составить -10%\n\n"\
     "<b>Какие риски?</b>\n"\
     "Максимальный риск это убыток в 10%. Все сигналы даются со стоп-лоссом от 2 до 10%."\
     "Стоп-лосс это ограничение убытка, т.е. если ситуация на рынке изменилась и цена пошла не вверх как мы ожидали, а низ, то сработает стоп-лосс, сделка закроется с убытком от 2 до 10%."\
     "В среднем по стоп-лоссу закрывается 1-2 из 10 сделок, что при высоких доходах практически не влияет на наш депозит.\n\n"\
     "<b>С каким депозитом можно начинать торговать?</b>\n"\
     "Начать торговать можно со 100$\n\n"\
     "<b>Сколько сигналов приходит в сутки?</b>\n"\
     "Около 2-5 сигналов в сутки"


days15 = 0.008
days30 = 0.015
days60 = 0.028
days90 = 0.04
days_forever = 0.1
# admin = 399004222 # old

# ГЛАВНОГО АДМИНА В НАЧАЛО!!!!!!!!!!
sysadmin = 256711367
admin = [399004222, 211439710, 248835526, 256711367]  # KH9IZ ГЛАВНОГО АДМИНА В НАЧАЛО!!!!!!!!!!
# admin = 211439710
# admin = 248835526
values = {}

isWorkDay = False  # Переменная отвечающая убавлять ли дни подписки у сабов или нет
# (зависит от того писал ли админ только сабам в этот день или нет)

wallet_id = "F100744184"
walletApiKey = "D11E68DEE967B4240CD49EBD7A1B95F6"

listPointer = 0
userList = []
chosenUserId = ""
s = 'd0nt_CrackMe_Pleas'    #"fu" + e + "cker"

#ethAddress = "0xe4D3bDaf0051e581ed76bbb2145cC75d887e8bD4"  #wallet Artur's
ethAddress = "0x8ba713420a76668B21aE5e246dbA886038001a8B"
