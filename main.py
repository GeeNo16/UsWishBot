import telebot
from telebot import types
import text as t
import sqlite3
import sql

bot = telebot.TeleBot('7613225662:AAH8CZOQBwZ6PWFLLyw2l3Pc7MHwL4uMNO8')


@bot.message_handler(commands=['start'])
def start(message):
    try:
        markup = types.InlineKeyboardMarkup()
        start_button = types.InlineKeyboardButton('Начать работу', callback_data='start')
        markup.row(start_button)
        bot.send_message(message.chat.id, t.greeting_text, reply_markup=markup)
    except Exception:
        markup = types.InlineKeyboardMarkup()
        go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
        markup.row(go_back_button)

        bot.send_message(message.chat.id, 'Произошла ошибка', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callbacks(callback):
    try:
        if callback.data == 'start':
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()
            cur.execute(sql.init_table)

            cur.execute(sql.checking_if_in_table)
            usernames = [item[0] for item in cur.fetchall()]

            if callback.message.chat.username not in usernames:
                cur.execute(sql.insert_name_secondname_telegramid %
                            (callback.message.chat.first_name, callback.message.chat.last_name,
                             callback.message.chat.username.lower()))
            conn.commit()

            cur.close()
            conn.close()

            markup = types.InlineKeyboardMarkup()
            present_button = types.InlineKeyboardButton('Дарить', callback_data='present')
            make_list_button = types.InlineKeyboardButton('Управлять своим списком', callback_data='make_list')
            info_button = types.InlineKeyboardButton('О боте', callback_data='info')
            markup.row(present_button)
            markup.row(make_list_button)
            markup.row(info_button)

            bot.send_message(callback.message.chat.id, t.choose_text, reply_markup=markup)

        if callback.data == 'present':
            bot.send_message(callback.message.chat.id, t.enter_username)
            bot.register_next_step_handler(callback.message, get_wishlist)

        if callback.data == 'make_list':
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            private_exists = cur.execute(sql.checking_if_private_exists % callback.message.chat.username).fetchall()

            cur.close()
            conn.close()

            if private_exists[0][0] not in (0, 1):
                markup = types.InlineKeyboardMarkup()
                create_button = types.InlineKeyboardButton('Создать', callback_data='create_new')
                exit_button = types.InlineKeyboardButton('Выход', callback_data='exit')
                markup.row(create_button, exit_button)
                bot.send_message(callback.message.chat.id,
                                 'У вас еще нет списка\n\nХотите создать?', reply_markup=markup)

            else:
                markup = types.InlineKeyboardMarkup()
                add_elements = types.InlineKeyboardButton('Добавить элементы', callback_data='add_elems')
                delete_elems = types.InlineKeyboardButton('Удалить элементы', callback_data='delete_elems')
                hang_link_button = types.InlineKeyboardButton('Прикрепить ссылку', callback_data='hang_link')
                unhang_link_button = types.InlineKeyboardButton('Открепить ссылку', callback_data='unhang_link')
                change_private_button = types.InlineKeyboardButton('Изменить уровень доступа',
                                                                   callback_data='change_access')
                change_password_button = types.InlineKeyboardButton('Изменить пароль', callback_data='change_password')
                get_list_button = types.InlineKeyboardButton('Посмотреть свой список', callback_data='get_list')
                check_pass_button = types.InlineKeyboardButton('Посмотреть свой пароль', callback_data='print_pass')
                if private_exists[0][0] == 0:
                    markup.row(add_elements, delete_elems)
                    markup.row(hang_link_button, unhang_link_button)
                    markup.row(change_private_button)
                    markup.row(get_list_button)
                else:
                    markup.row(add_elements, delete_elems)
                    markup.row(hang_link_button, unhang_link_button)
                    markup.row(change_private_button, change_password_button)
                    markup.row(check_pass_button)
                    markup.row(get_list_button)

                bot.send_message(callback.message.chat.id,
                                 'У вас уже есть список\n\nЧто бы вы хотели с ним сделать?', reply_markup=markup)

        if callback.data == 'print_pass':
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            password = cur.execute(sql.select_pass % callback.message.chat.username).fetchall()[0][0]

            cur.close()
            conn.close()

            markup = types.InlineKeyboardMarkup()
            go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
            markup.row(go_back_button)
            bot.send_message(callback.message.chat.id, f'Имя пользователя: {callback.message.chat.username}\n'
                                                       f'Пароль: {password}', reply_markup=markup)

        if callback.data == 'change_password':
            bot.send_message(callback.message.chat.id, t.change_password)
            bot.register_next_step_handler(callback.message, final_password_creating)

        if callback.data == 'change_access':
            markup = types.InlineKeyboardMarkup()
            private_button = types.InlineKeyboardButton('Приватным', callback_data='change_private')
            public = types.InlineKeyboardButton('Публичным', callback_data='change_public')
            markup.row(private_button, public)

            bot.send_message(callback.message.chat.id, t.change_access, reply_markup=markup)

        if callback.data == 'change_private':
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            cur.execute(sql.private_insert % callback.message.chat.username)
            conn.commit()

            cur.close()
            conn.close()

            bot.send_message(callback.message.chat.id, t.private_access)
            bot.register_next_step_handler(callback.message, final_password_creating)

        if callback.data == 'change_public':
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            cur.execute(sql.non_private_insert % callback.message.chat.username)
            conn.commit()

            cur.close()
            conn.close()

            markup = types.InlineKeyboardMarkup()
            go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
            markup.row(go_back_button)
            bot.send_message(callback.message.chat.id, 'Отлично, ваш список теперь публичный', reply_markup=markup)

        if callback.data == 'unhang_link':
            links = []

            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            for it in cur.execute(sql.select_links % callback.message.chat.username).fetchall():
                links.append(it[0])

            if len(links) > 0:
                mess = 'Вот элемсенты списка с ссылками' + '\n'

                for item in links:
                    mess += "<a href='" + cur.execute(sql.catching_link %
                                                      (callback.message.chat.username, item)).fetchall()[0][0] \
                            + "'>" + item.capitalize() + "</a>" + '\n'

                cur.close()
                conn.close()

                bot.send_message(callback.message.chat.id, t.remove_link % mess, parse_mode='html')

                bot.register_next_step_handler(callback.message, rm_link)

            else:
                markup = types.InlineKeyboardMarkup()
                go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
                markup.row(go_back_button)

                bot.send_message(callback.message.chat.id, 'Вы еще не прикрепили ни одной ссылки', reply_markup=markup)

        if callback.data == 'delete_elems':
            wishlist = []
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            for it in cur.execute(sql.checking_if_in_wishlist % callback.message.chat.username).fetchall():
                wishlist.append(it[0])

            mess = 'Вот ваш список' + '\n'

            for item in wishlist:
                mess += "<a href='" + cur.execute(sql.catching_link %
                                                  (callback.message.chat.username, item)).fetchall()[0][0] \
                        + "'>" + item.capitalize() + "</a>" + '\n'

            cur.close()
            conn.close()

            bot.send_message(callback.message.chat.id, t.delete_elements % mess, parse_mode='html')

            bot.register_next_step_handler(callback.message, rm_elements)

        if callback.data == 'get_list':
            wishlist = []
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            for it in cur.execute(sql.checking_if_in_wishlist % callback.message.chat.username).fetchall():
                wishlist.append(it[0])

            mess = 'Вот ваш список' + '\n\n'

            for item in wishlist:
                mess += "<a href='" + cur.execute(sql.catching_link %
                                                  (callback.message.chat.username, item)).fetchall()[0][0] \
                        + "'>" + item.capitalize() + "</a>" + '\n'

            cur.close()
            conn.close()

            markup = types.InlineKeyboardMarkup()
            go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
            markup.row(go_back_button)
            bot.send_message(callback.message.chat.id, mess, parse_mode='html', reply_markup=markup)

        if callback.data == 'hang_link':
            wishlist = []
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            for it in cur.execute(sql.checking_if_in_wishlist % callback.message.chat.username).fetchall():
                wishlist.append(it[0])

            mess = 'Вот ваш список' + '\n\n'

            for item in wishlist:
                mess += "<a href='" + cur.execute(sql.catching_link %
                                                  (callback.message.chat.username, item)).fetchall()[0][0] \
                                                    + "'>" + item.capitalize() + "</a>" + '\n'

            cur.close()
            conn.close()

            bot.send_message(callback.message.chat.id, mess + '\nВведите к какому элементу вы хотите добавить ссылку',
                             parse_mode='html')
            bot.register_next_step_handler(callback.message, choosing_elem, wishlist)

        if callback.data == 'create_new':
            markup = types.InlineKeyboardMarkup()
            private_button = types.InlineKeyboardButton('Сделать приватным', callback_data='make_private')
            non_private_button = types.InlineKeyboardButton('Сделать открытым', callback_data='make_opened')
            markup.row(private_button, non_private_button)
            bot.send_message(callback.message.chat.id, t.private_choosing_text, reply_markup=markup)

        if callback.data == 'exit':
            bot.delete_message(callback.message.chat.id, callback.message.message_id)

        if callback.data == 'make_private':
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            cur.execute(sql.private_insert % callback.message.chat.username)
            conn.commit()

            cur.close()
            conn.close()

            markup = types.InlineKeyboardMarkup()
            create_password_button = types.InlineKeyboardButton('Создать пароль', callback_data='create_password')
            markup.row(create_password_button)
            bot.send_message(callback.message.chat.id, t.private_ready_text, reply_markup=markup)

        if callback.data == 'make_opened':
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            cur.execute(sql.non_private_insert % callback.message.chat.username)
            conn.commit()

            cur.close()
            conn.close()

            markup = types.InlineKeyboardMarkup()
            create_wishlist_button = types.InlineKeyboardButton('Создать список', callback_data='create_wishlist')
            markup.row(create_wishlist_button)
            bot.send_message(callback.message.chat.id, t.public_ready_text, reply_markup=markup)

        if callback.data == 'create_password':
            bot.send_message(callback.message.chat.id, t.password_choosing_text)
            bot.register_next_step_handler(callback.message, password_creating)

        if callback.data == 'create_wishlist' or callback.data == 'add_elems':
            bot.send_message(callback.message.chat.id, t.create_wishlist)

            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            cur.execute(sql.init_wishlist % callback.message.chat.username)
            conn.commit()

            cur.close()
            conn.close()

            bot.register_next_step_handler(callback.message, wishlist_creating)

        if callback.data == 'yes':
            bot.send_message(callback.message.chat.id, 'Что ж, попробуйте еще раз')
            bot.register_next_step_handler(callback.message, get_wishlist)

        if callback.data == 'no':
            bot.delete_messages(callback.message.chat.id,
                            [callback.message.message_id,
                             callback.message.message_id - 1, callback.message.message_id - 2])

        if callback.data == 'yes2':
            bot.send_message(callback.message.chat.id, 'Что ж, начнем сначала, введите имя пользователя')
            bot.register_next_step_handler(callback.message, get_wishlist)

        if callback.data == 'no2':
            markup = types.InlineKeyboardMarkup()
            go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
            markup.row(go_back_button)
            bot.send_message(callback.message.chat.id,
                             'Будте настойчивей когда спрашиваете пароль', reply_markup=markup)
    except Exception:
        markup = types.InlineKeyboardMarkup()
        go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
        markup.row(go_back_button)

        bot.send_message(callback.message.chat.id, 'Произошла ошибка', reply_markup=markup)


def hang_link(message):
    try:
        wishlist = []
        conn = sqlite3.connect('data.sqlite3')
        cur = conn.cursor()

        for it in cur.execute(sql.checking_if_in_wishlist % message.chat.username).fetchall():
            wishlist.append(it[0])

        mess = 'Вот ваш список' + '\n\n'

        for item in wishlist:
            mess += "<a href='" + cur.execute(sql.catching_link % (message.chat.username, item)).fetchall()[0][0]\
                    + "'>" + item.capitalize() + "</a>" + '\n'

        cur.close()
        conn.close()

        bot.send_message(message.chat.id, mess +
                         '\nВведите к какому элементу вы хотите добавить ссылку', parse_mode='html')
        bot.register_next_step_handler(message, choosing_elem, wishlist)
    except Exception:
        markup = types.InlineKeyboardMarkup()
        go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
        markup.row(go_back_button)

        bot.send_message(message.chat.id, 'Произошла ошибка', reply_markup=markup)


def choosing_elem(message, wishlist):
    try:
        if message.text.lower() in wishlist:
            bot.send_message(message.chat.id, f'Выбранный элемент: {message.text.lower().capitalize()}\nВведите ссылку')
            bot.register_next_step_handler(message, link_hanger, message.text.lower())

        else:
            bot.send_message(message.chat.id, 'Выбранного элемента нет в списке\nПопробуйте снова')
            bot.register_next_step_handler(message, choosing_elem, wishlist)
    except Exception:
        markup = types.InlineKeyboardMarkup()
        go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
        markup.row(go_back_button)

        bot.send_message(message.chat.id, 'Произошла ошибка', reply_markup=markup)


def link_hanger(message, elem):
    try:
        conn = sqlite3.connect('data.sqlite3')
        cur = conn.cursor()

        cur.execute(sql.adding_link % (message.chat.username, message.text, elem))
        conn.commit()

        cur.close()
        conn.close()

        markup = types.InlineKeyboardMarkup()
        go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
        markup.row(go_back_button)
        bot.send_message(message.chat.id, 'Готово', reply_markup=markup)
    except Exception:
        markup = types.InlineKeyboardMarkup()
        go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
        markup.row(go_back_button)

        bot.send_message(message.chat.id, 'Произошла ошибка', reply_markup=markup)


def password_creating(message):
    try:
        flag = True
        for elem in message.text:
            if elem in t.alph:
                flag = False

        if flag and len(message.text) == 9 and message.text[4] == '-' and message.text.count('-') == 1:
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            cur.execute(sql.password_insert % (message.text, message.chat.username))
            conn.commit()

            cur.close()
            conn.close()

            markup = types.InlineKeyboardMarkup()
            create_wishlist_button = types.InlineKeyboardButton('Создать список', callback_data='create_wishlist')
            markup.row(create_wishlist_button)

            bot.send_message(message.chat.id, t.password_great, reply_markup=markup)

        else:
            bot.reply_to(message, 'Вы ввели некорректный пароль, попробуйте еще раз')
            bot.register_next_step_handler(message, password_creating)
    except Exception:
        markup = types.InlineKeyboardMarkup()
        go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
        markup.row(go_back_button)

        bot.send_message(message.chat.id, 'Произошла ошибка', reply_markup=markup)


def final_password_creating(message):
    try:
        flag = True
        for elem in message.text:
            if elem in t.alph:
                flag = False

        if flag and len(message.text) == 9 and message.text[4] == '-' and message.text.count('-') == 1:
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            cur.execute(sql.password_insert % (message.text, message.chat.username))
            conn.commit()

            cur.close()
            conn.close()

            markup = types.InlineKeyboardMarkup()
            go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
            markup.row(go_back_button)
            bot.send_message(message.chat.id, 'Отлично, пароль создан', reply_markup=markup)

        else:
            bot.reply_to(message, 'Вы ввели некорректный пароль, попробуйте еще раз')
            bot.register_next_step_handler(message, final_password_creating)
    except Exception:
        markup = types.InlineKeyboardMarkup()
        go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
        markup.row(go_back_button)

        bot.send_message(message.chat.id, 'Произошла ошибка', reply_markup=markup)


def wishlist_creating(message):
    try:
        wishlist = []
        conn = sqlite3.connect('data.sqlite3')
        cur = conn.cursor()

        for it in cur.execute(sql.checking_if_in_wishlist % message.chat.username).fetchall():
            wishlist.append(it[0])

        cur.close()
        conn.close()

        if message.text.lower() in wishlist:
            bot.send_message(message.chat.id, 'Этот элемент уже есть в списке, введите новый')

            bot.register_next_step_handler(message, wishlist_creating)

        elif message.text.lower() not in ('стоп', 'stop'):
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            cur.execute(sql.wishlist_item_insert % (message.chat.username, message.text.lower()))
            conn.commit()

            cur.close()
            conn.close()

            bot.send_message(message.chat.id, 'Элемент добавлен')
            bot.register_next_step_handler(message, wishlist_creating)

        else:
            markup = types.InlineKeyboardMarkup()
            go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
            markup.row(go_back_button)

            bot.send_message(message.chat.id, 'Вы закончили', reply_markup=markup)
    except Exception:
        markup = types.InlineKeyboardMarkup()
        go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
        markup.row(go_back_button)

        bot.send_message(message.chat.id, 'Произошла ошибка', reply_markup=markup)


def rm_link(message):
    try:
        links = []

        conn = sqlite3.connect('data.sqlite3')
        cur = conn.cursor()

        for it in cur.execute(sql.select_links % message.chat.username).fetchall():
            links.append(it[0])

        cur.close()
        conn.close()

        if message.text.lower() in ('стоп', 'stop'):
            markup = types.InlineKeyboardMarkup()
            go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
            markup.row(go_back_button)

            bot.send_message(message.chat.id, 'Вы закончили', reply_markup=markup)

        elif message.text.lower() not in links:
            bot.send_message(message.chat.id, 'Этого элемента нет в списке предложенных')

            bot.register_next_step_handler(message, rm_link)

        elif message.text.lower() not in ('стоп', 'stop'):
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            cur.execute(sql.delete_links % (message.chat.username, message.text.lower()))
            conn.commit()

            cur.close()
            conn.close()

            bot.send_message(message.chat.id, 'Ссылка удалена')
            bot.register_next_step_handler(message, rm_link)
    except Exception:
        markup = types.InlineKeyboardMarkup()
        go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
        markup.row(go_back_button)

        bot.send_message(message.chat.id, 'Произошла ошибка', reply_markup=markup)


def rm_elements(message):
    try:
        wishlist = []
        conn = sqlite3.connect('data.sqlite3')
        cur = conn.cursor()

        for it in cur.execute(sql.checking_if_in_wishlist % message.chat.username).fetchall():
            wishlist.append(it[0])

        cur.close()
        conn.close()

        if len(wishlist) > 0:
            if message.text.lower() in ('стоп', 'stop'):
                markup = types.InlineKeyboardMarkup()
                go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
                markup.row(go_back_button)

                bot.send_message(message.chat.id, 'Вы закончили', reply_markup=markup)

            elif message.text.lower() not in wishlist:
                bot.send_message(message.chat.id, 'Этого элемента нет в списке, попробуйте другой')

                bot.register_next_step_handler(message, rm_elements)

            elif message.text.lower() not in ('стоп', 'stop'):
                conn = sqlite3.connect('data.sqlite3')
                cur = conn.cursor()

                cur.execute(sql.delete_elements % (message.chat.username, message.text.lower()))
                conn.commit()

                cur.close()
                conn.close()

                bot.send_message(message.chat.id, 'Элемент удален')
                bot.register_next_step_handler(message, rm_elements)

        else:
            markup = types.InlineKeyboardMarkup()
            go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
            markup.row(go_back_button)
            bot.send_message(message.chat.id, 'Список пуст', reply_markup=markup)
    except Exception:
        markup = types.InlineKeyboardMarkup()
        go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
        markup.row(go_back_button)

        bot.send_message(message.chat.id, 'Произошла ошибка', reply_markup=markup)


def get_wishlist(message):
    try:
        conn = sqlite3.connect('data.sqlite3')
        cur = conn.cursor()

        cur.execute(sql.checking_if_in_table)
        usernames = [item[0] for item in cur.fetchall()]

        cur.close()
        conn.close()

        if message.text not in usernames:
            markup = types.InlineKeyboardMarkup()
            yes_button = types.InlineKeyboardButton('Да', callback_data='yes')
            no_button = types.InlineKeyboardButton('Нет', callback_data='no')
            markup.row(yes_button, no_button)

            bot.send_message(message.chat.id, 'Имя пользователя не найдено, хотите попробовать еще раз?',
                             reply_markup=markup)

        else:
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            private_flag = cur.execute(sql.checking_if_private % message.text).fetchall()[0][0]

            cur.close()
            conn.close()

            if private_flag == 0:
                wishlist = []
                conn = sqlite3.connect('data.sqlite3')
                cur = conn.cursor()

                try:
                    for it in cur.execute(sql.checking_if_in_wishlist % message.text).fetchall():
                        wishlist.append(it[0])

                    if len(wishlist) > 0:
                        mess = 'Вот список пользователя ' + \
                               cur.execute(sql.catching_name % message.text).fetchall()[0][0] + '\n\n'

                        for item in wishlist:
                            mess += "<a href='" + \
                                    cur.execute(sql.catching_link % (message.text, item)).fetchall()[0][0]\
                                     + "'>" + item.capitalize() + "</a>" + '\n'

                        cur.close()
                        conn.close()

                        markup = types.InlineKeyboardMarkup()
                        go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
                        markup.row(go_back_button)
                        bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)

                    else:
                        markup = types.InlineKeyboardMarkup()
                        go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
                        markup.row(go_back_button)
                        bot.send_message(message.chat.id, 'Список вашего друга пуст', reply_markup=markup)

                except sqlite3.OperationalError:
                    markup = types.InlineKeyboardMarkup()
                    go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
                    markup.row(go_back_button)
                    bot.send_message(message.chat.id, 'Пользователь еще не создал список', reply_markup=markup)

            elif private_flag == 1:
                conn = sqlite3.connect('data.sqlite3')
                cur = conn.cursor()

                password = cur.execute(sql.catching_password % message.text).fetchall()[0][0]

                cur.close()
                conn.close()

                bot.send_message(message.chat.id, t.friends_private % message.text)
                bot.register_next_step_handler(message, check_pass, password, message.text)
    except Exception:
        markup = types.InlineKeyboardMarkup()
        go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
        markup.row(go_back_button)

        bot.send_message(message.chat.id, 'Произошла ошибка', reply_markup=markup)


def check_pass(message, password, username):
    try:
        if message.text == password:
            wishlist = []
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            try:
                for it in cur.execute(sql.checking_if_in_wishlist % username).fetchall():
                    wishlist.append(it[0])

                if len(wishlist) > 0:
                    mess = 'Вот список пользователя ' + \
                           cur.execute(sql.catching_name % username).fetchall()[0][0] + '\n\n'

                    for item in wishlist:
                        mess += "<a href='" + cur.execute(sql.catching_link % (username, item)).fetchall()[0][0]\
                                + "'>" + item.capitalize() + "</a>" + '\n'

                    cur.close()
                    conn.close()

                    markup = types.InlineKeyboardMarkup()
                    go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
                    markup.row(go_back_button)
                    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)

                else:
                    markup = types.InlineKeyboardMarkup()
                    go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
                    markup.row(go_back_button)

                    bot.send_message(message.chat.id, 'Список вашего друга пуст', reply_markup=markup)

            except sqlite3.OperationalError:
                markup = types.InlineKeyboardMarkup()
                go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
                markup.row(go_back_button)

                bot.send_message(message.chat.id, 'Пользователь еще не создал список', reply_markup=markup)

        else:
            markup = types.InlineKeyboardMarkup()
            yes_button = types.InlineKeyboardButton('Да', callback_data='yes2')
            no_button = types.InlineKeyboardButton('Нет', callback_data='no2')
            markup.row(yes_button, no_button)
            bot.send_message(message.chat.id, 'Пароль неверный или пользователь еще не создал его,'
                                              ' хотите попробовать снова?', reply_markup=markup)
    except Exception:
        markup = types.InlineKeyboardMarkup()
        go_back_button = types.InlineKeyboardButton('Вернуться в начало', callback_data='start')
        markup.row(go_back_button)

        bot.send_message(message.chat.id, 'Произошла ошибка', reply_markup=markup)


bot.polling(none_stop=True)
