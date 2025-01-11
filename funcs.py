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
    cats = [cur.execute(sql.cat_select % (insert_item, item)).fetchall()[0][0] for item in init_list]
    working_wishlist = sorted([(cats[i], init_list[i]) for i in range(len(init_list))])
    count = [i - i for i in range(7)]

    for item in working_wishlist:
        if observer == 0:
            if item[0] == 0:
                if count[0] == 0:
                    mess += str(number) + '. Без категории' + '\n'
                    number += 1
                    count[0] += 1

            elif item[0] == 1:
                if count[1] == 0:
                    mess += str(number) + '. ' + t.cats_list[item[0] - 1] + '\n'
                    number += 1
                    count[1] += 1

            elif item[0] == 2:
                if count[2] == 0:
                    mess += str(number) + '. ' + t.cats_list[item[0] - 1] + '\n'
                    number += 1
                    count[2] += 1

            elif item[0] == 3:
                if count[3] == 0:
                    mess += str(number) + '. ' + t.cats_list[item[0] - 1] + '\n'
                    number += 1
                    count[3] += 1

            elif item[0] == 4:
                if count[4] == 0:
                    mess += str(number) + '. ' + t.cats_list[item[0] - 1] + '\n'
                    number += 1
                    count[4] += 1

            elif item[0] == 5:
                if count[5] == 0:
                    mess += str(number) + '. ' + t.cats_list[item[0] - 1] + '\n'
                    number += 1
                    count[5] += 1

            elif item[0] == 6:
                if count[6] == 0:
                    mess += str(number) + '. ' + t.cats_list[item[0] - 1] + '\n'
                    number += 1
                    count[6] += 1

            mess += "\t\t- <a href='" + cur.execute(request % (insert_item, item[1])).fetchall()[0][0] \
                    + "'>" + item[1].capitalize() + "</a>" + '\n'

        elif observer == 1:
            pres_flag = sql_without_commit(sql.prepare_crossing % (insert_item, item[1]))[0][0]
            if item[0] == 0:
                if count[0] == 0:
                    mess += str(number) + '. Без категории' + '\n'
                    number += 1
                    count[0] += 1

            elif item[0] == 1:
                if count[1] == 0:
                    mess += str(number) + '. ' + t.cats_list[item[0] - 1] + '\n'
                    number += 1
                    count[1] += 1

            elif item[0] == 2:
                if count[2] == 0:
                    mess += str(number) + '. ' + t.cats_list[item[0] - 1] + '\n'
                    number += 1
                    count[2] += 1

            elif item[0] == 3:
                if count[3] == 0:
                    mess += str(number) + '. ' + t.cats_list[item[0] - 1] + '\n'
                    number += 1
                    count[3] += 1

            elif item[0] == 4:
                if count[4] == 0:
                    mess += str(number) + '. ' + t.cats_list[item[0] - 1] + '\n'
                    number += 1
                    count[4] += 1

            elif item[0] == 5:
                if count[5] == 0:
                    mess += str(number) + '. ' + t.cats_list[item[0] - 1] + '\n'
                    number += 1
                    count[5] += 1

            elif item[0] == 6:
                if count[6] == 0:
                    mess += str(number) + '. ' + t.cats_list[item[0] - 1] + '\n'
                    number += 1
                    count[6] += 1

            if pres_flag == 1:
                mess += "\t\t- <s><a href='" + cur.execute(request % (insert_item, item[1])).fetchall()[0][0] \
                        + "'>" + item[1].capitalize() + "</a></s>" + '\n'

            else:
                mess += "\t\t- <a href='" + cur.execute(request % (insert_item, item[1])).fetchall()[0][0] \
                        + "'>" + item[1].capitalize() + "</a>" + '\n'

    cur.close()
    conn.close()

    if mode == 0:
        bot.send_message(message.chat.id, insert_text % mess, parse_mode='html')

    elif mode == 1:
        result = insert_text % mess

        return result


def form_buttons(bot, message, init_list, text):
    markup = types.ReplyKeyboardMarkup()

    for item in init_list:
        mid_button = types.KeyboardButton(item.capitalize())
        markup.row(mid_button)

    finish_button = types.KeyboardButton(t.buttons['exit'])
    markup.row(finish_button)

    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='html')
