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
                    (message.chat.first_name, message.chat.last_name, message.chat.username))

    conn.commit()
    cur.close()
    conn.close()

    markup = types.ReplyKeyboardMarkup()
    register_button = types.KeyboardButton('Начать работу')
    about_button = types.KeyboardButton('О боте')
    markup.row(register_button, about_button)

    bot.send_message(message.chat.id, t.greeting_text, reply_markup=markup)
    bot.register_next_step_handler(message, menu)


def menu(message):
    if message.text == 'Начать работу':
        markup = types.InlineKeyboardMarkup()
        private_button = types.InlineKeyboardButton('Сделать приватным', callback_data='make_private')
        non_private_button = types.InlineKeyboardButton('Сделать открытым', callback_data='make_opened')
        markup.row(private_button)
        markup.row(non_private_button)
        bot.send_message(message.chat.id, t.private_choosing_text, reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def callback_from_private(callback):
    conn = sqlite3.connect('data.sqlite3')
    cur = conn.cursor()
    if callback.data == 'make_private':
        cur.execute(sql.private_insert + "='%s'" % callback.message.chat.username)
        conn.commit()
        markup = types.InlineKeyboardMarkup()
        create_password_button = types.InlineKeyboardButton('Создать пароль', callback_data='create_password')
        markup.row(create_password_button)
        bot.send_message(callback.message.chat.id, t.private_ready_text, reply_markup=markup)
    if callback.data == 'make_opened':
        cur.execute(sql.non_private_insert + "='%s'" % callback.message.chat.username)
        conn.commit()
    cur.close()
    conn.close()


@bot.callback_query_handler(func=lambda callback: True)
def callback_from_password():
    pass


bot.polling(none_stop=True)
