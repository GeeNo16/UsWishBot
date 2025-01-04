from telebot import types

import sql
import text as t
import sqlite3


def exceptions(bot, message):
    markup = types.InlineKeyboardMarkup()
    go_back_button = types.InlineKeyboardButton(t.buttons['go_to_the_start'], callback_data='start')
    markup.row(go_back_button)

    bot.send_message(message.chat.id, t.buttons['error'], reply_markup=markup)


def go_to_the_start(bot, message, text):
    markup = types.InlineKeyboardMarkup()
    go_back_button = types.InlineKeyboardButton(t.buttons['go_to_the_start'], callback_data='start')
    markup.row(go_back_button)

    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='html')


def form_list(request):
    result = []

    conn = sqlite3.connect('data.sqlite3')
    cur = conn.cursor()

    for it in cur.execute(request).fetchall():
        result.append(it[0])

    cur.close()
    conn.close()

    return result


def sql_with_commit(request):
    conn = sqlite3.connect('data.sqlite3')
    cur = conn.cursor()

    cur.execute(request)
    conn.commit()

    cur.close()
    conn.close()


def sql_without_commit(request):
    conn = sqlite3.connect('data.sqlite3')
    cur = conn.cursor()

    result = cur.execute(request).fetchall()

    cur.close()
    conn.close()

    return result


def print_list(bot, message, request, insert_text, init_list, insert_item, mode, observer):
    mess = ''

    conn = sqlite3.connect('data.sqlite3')
    cur = conn.cursor()
    number = 1

    for item in init_list:
        if observer == 0:
            mess += str(number) + ". <a href='" + cur.execute(request % (insert_item, item)).fetchall()[0][0] \
                    + "'>" + item.capitalize() + "</a>" + '\n'
            number += 1

        elif observer == 1:
            pres_flag = sql_without_commit(sql.prepare_crossing % (insert_item, item))[0][0]
            if pres_flag == 1:
                mess += str(number) + ". <s><a href='" + cur.execute(request % (insert_item, item)).fetchall()[0][0] \
                        + "'>" + item.capitalize() + "</a></s>" + '\n'
                number += 1
            else:
                mess += str(number) + ". <a href='" + cur.execute(request % (insert_item, item)).fetchall()[0][0] \
                        + "'>" + item.capitalize() + "</a>" + '\n'
                number += 1

    cur.close()
    conn.close()

    if mode == 0:
        bot.send_message(message.chat.id, insert_text % mess, parse_mode='html')

    elif mode == 1:
        result = insert_text % mess

        return result


def form_buttons(bot, message, init_list, text, mode):
    markup = types.ReplyKeyboardMarkup()

    for item in init_list:
        mid_button = types.KeyboardButton(item.capitalize())
        markup.row(mid_button)

    finish_button = types.KeyboardButton(t.buttons['do_nothing'])
    markup.row(finish_button)

    if mode == 1:
        stop_button = types.KeyboardButton('Стоп')
        markup.row(stop_button)

    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='html')
