import telebot
from telebot import types
import text as t
import sqlite3
import sql

bot = telebot.TeleBot('7613225662:AAH8CZOQBwZ6PWFLLyw2l3Pc7MHwL4uMNO8')


@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('data.sqlite3')
    cur = conn.cursor()
    cur.execute(sql.init_table)

    cur.execute(sql.checking_if_in_table)
    usernames = [item[0] for item in cur.fetchall()]

    if message.chat.username not in usernames:
        cur.execute(sql.insert_name_secondname_telegramid %
                    (message.chat.first_name, message.chat.last_name, message.chat.username.lower()))
    conn.commit()

    cur.close()
    conn.close()

    markup = types.InlineKeyboardMarkup()
    register_button = types.InlineKeyboardButton('Начать работу', callback_data='begin_work')
    about_button = types.InlineKeyboardButton('О боте', callback_data='about')
    get_list_button = types.InlineKeyboardButton('Узнать список друга', callback_data='get_list')
    markup.row(register_button, about_button)
    markup.row(get_list_button)

    bot.send_message(message.chat.id, t.greeting_text, reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callbacks(callback):
    if callback.data == 'get_list':
        bot.send_message(callback.message.chat.id, t.enter_username)
        bot.register_next_step_handler(callback.message, get_wishlist)

    if callback.data == 'begin_work':
        markup = types.InlineKeyboardMarkup()
        private_button = types.InlineKeyboardButton('Сделать приватным', callback_data='make_private')
        non_private_button = types.InlineKeyboardButton('Сделать открытым', callback_data='make_opened')
        markup.row(private_button, non_private_button)
        bot.send_message(callback.message.chat.id, t.private_choosing_text, reply_markup=markup)

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

    if callback.data == 'create_wishlist':
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
        bot.send_message(callback.message.chat.id, 'Жаль( заведите друзей')

    if callback.data == 'yes2':
        bot.send_message(callback.message.chat.id, 'Что ж, начнем сначала, введите имя пользователя')
        bot.register_next_step_handler(callback.message, get_wishlist)

    if callback.data == 'no2':
        bot.send_message(callback.message.chat.id, 'Будте настойчивей когда спрашиваете пароль')


def password_creating(message):
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


def wishlist_creating(message):
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

        bot.register_next_step_handler(message, wishlist_creating)

    else:
        bot.send_message(message.chat.id, 'Вы закончили')


def get_wishlist(message):
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

                mess = 'Вот список пользователя ' + cur.execute(sql.catching_name % message.text).fetchall()[0][
                    0] + '\n\n'

                cur.close()
                conn.close()

                for item in wishlist:
                    mess += item.capitalize() + '\n'

                bot.send_message(message.chat.id, mess)

            except sqlite3.OperationalError:
                bot.send_message(message.chat.id, 'Пользователь еще не создал список')

        elif private_flag == 1:
            conn = sqlite3.connect('data.sqlite3')
            cur = conn.cursor()

            password = cur.execute(sql.catching_password % message.text).fetchall()[0][0]

            cur.close()
            conn.close()

            bot.send_message(message.chat.id, t.friends_private % message.text)
            bot.register_next_step_handler(message, check_pass, password, message.text)


def check_pass(message, password, username):
    if message.text == password:
        wishlist = []
        conn = sqlite3.connect('data.sqlite3')
        cur = conn.cursor()

        try:
            for it in cur.execute(sql.checking_if_in_wishlist % username).fetchall():
                wishlist.append(it[0])

            mess = 'Вот список пользователя ' + cur.execute(sql.catching_name % username).fetchall()[0][0] + '\n\n'

            cur.close()
            conn.close()

            for item in wishlist:
                mess += item.capitalize() + '\n'

            bot.send_message(message.chat.id, mess)

        except sqlite3.OperationalError:
            bot.send_message(message.chat.id, 'Пользователь еще не создал список')

    else:
        markup = types.InlineKeyboardMarkup()
        yes_button = types.InlineKeyboardButton('Да', callback_data='yes2')
        no_button = types.InlineKeyboardButton('Нет', callback_data='no2')
        markup.row(yes_button, no_button)
        bot.send_message(message.chat.id, 'Пароль неверный или пользователь еще не создал его,'
                                          ' хотите попробовать снова?', reply_markup=markup)


bot.polling(none_stop=True)
