import telebot
from telebot import types
import text as t
import sqlite3
import sql
import funcs as f

bot = telebot.TeleBot('7613225662:AAH8CZOQBwZ6PWFLLyw2l3Pc7MHwL4uMNO8')


@bot.message_handler(commands=['start'])
def start(message):
    try:
        bot.clear_step_handler_by_chat_id(message.chat.id)

        markup = types.InlineKeyboardMarkup()
        start_button = types.InlineKeyboardButton(t.buttons['begin'], callback_data='start')
        markup.row(start_button)
        bot.send_message(message.chat.id, t.info['greeting'], reply_markup=markup)

    except Exception:
        f.exceptions(bot, message)


@bot.message_handler()
def all_messages(message):
    try:
        markup = types.InlineKeyboardMarkup()
        go_back_button = types.InlineKeyboardButton(t.buttons['begin_work'], callback_data='start')
        markup.row(go_back_button)

        bot.send_message(message.chat.id, t.info['not_a_command'], reply_markup=markup)

    except Exception:
        f.exceptions(bot, message)


@bot.callback_query_handler(func=lambda callback: True)
def callbacks(callback):
    try:
        if callback.data == 'start':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

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
            present_button = types.InlineKeyboardButton(t.buttons['present'], callback_data='present')
            make_list_button = types.InlineKeyboardButton(t.buttons['rule_list'], callback_data='make_list')
            info_button = types.InlineKeyboardButton(t.buttons['about'], callback_data='info')
            markup.row(present_button)
            markup.row(make_list_button)
            markup.row(info_button)

            bot.send_message(callback.message.chat.id, t.info['what_to_do'], reply_markup=markup)

        if callback.data == 'present':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            bot.send_message(callback.message.chat.id, t.info['enter_username'])
            bot.register_next_step_handler(callback.message, get_wishlist)

        if callback.data == 'make_list':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            private_exists = f.sql_without_commit(sql.checking_if_private_exists % callback.message.chat.username)

            if private_exists[0][0] not in (0, 1):
                markup = types.InlineKeyboardMarkup()
                create_button = types.InlineKeyboardButton(t.buttons['create'], callback_data='create_new')
                exit_button = types.InlineKeyboardButton(t.buttons['exit'], callback_data='exit')
                markup.row(create_button, exit_button)

                bot.send_message(callback.message.chat.id, t.info['you_dont_have_list'], reply_markup=markup)

            else:
                markup = types.InlineKeyboardMarkup()
                add_elements = types.InlineKeyboardButton(t.buttons['add_elems'], callback_data='add_elems')
                delete_elems = types.InlineKeyboardButton(t.buttons['delete_elems'], callback_data='delete_elems')
                hang_link_button = types.InlineKeyboardButton(t.buttons['hang_link'], callback_data='hang_link')
                unhang_link_button = types.InlineKeyboardButton(t.buttons['unhang_link'], callback_data='unhang_link')
                change_private_button = types.InlineKeyboardButton(t.buttons['change_access'],
                                                                   callback_data='change_access')
                change_password_button = types.InlineKeyboardButton(t.buttons['change_password'],
                                                                    callback_data='change_password')
                get_list_button = types.InlineKeyboardButton(t.buttons['get_list'], callback_data='get_list')
                check_pass_button = types.InlineKeyboardButton(t.buttons['print_pass'], callback_data='print_pass')

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

                bot.send_message(callback.message.chat.id, t.info['you_have_list'], reply_markup=markup)

        if callback.data == 'print_pass':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            password = f.sql_without_commit(sql.select_pass % callback.message.chat.username)[0][0]
            private_exists = f.sql_without_commit(sql.checking_if_private_exists % callback.message.chat.username)

            if private_exists[0][0] == 1:
                f.go_to_the_start(bot, callback.message, t.password['get_pass'] %
                              (callback.message.chat.username, password))

            else:
                f.go_to_the_start(bot, callback.message, t.info['cant_use'])

        if callback.data == 'change_password':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            private_exists = f.sql_without_commit(sql.checking_if_private_exists % callback.message.chat.username)

            if private_exists[0][0] == 1:
                bot.send_message(callback.message.chat.id, t.password['change_pass'])
                bot.register_next_step_handler(callback.message, final_password_creating)

            else:
                f.go_to_the_start(bot, callback.message, t.info['cant_use'])

        if callback.data == 'change_access':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            markup = types.InlineKeyboardMarkup()
            private_button = types.InlineKeyboardButton(t.buttons['private'], callback_data='change_private')
            public = types.InlineKeyboardButton(t.buttons['public'], callback_data='change_public')
            markup.row(private_button, public)

            bot.send_message(callback.message.chat.id, t.access['change_access'], reply_markup=markup)

        if callback.data == 'change_private':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            f.sql_with_commit(sql.private_insert % callback.message.chat.username)

            bot.send_message(callback.message.chat.id, t.access['to_private'])
            bot.register_next_step_handler(callback.message, final_password_creating)

        if callback.data == 'change_public':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            f.sql_with_commit(sql.non_private_insert % callback.message.chat.username)

            f.go_to_the_start(bot, callback.message, t.access['to_public'])

        if callback.data == 'unhang_link':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            links = f.form_list(sql.select_links % callback.message.chat.username)

            if len(links) > 0:
                f.print_list(bot, callback.message, sql.catching_link,
                             t.link['start_remove'], links, callback.message.chat.username)

                bot.register_next_step_handler(callback.message, rm_link)

            else:
                f.go_to_the_start(bot, callback.message, t.link['no_links'])

        if callback.data == 'delete_elems':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            wishlist = f.form_list(sql.checking_if_in_wishlist % callback.message.chat.username)

            if len(wishlist) > 0:
                f.print_list(bot, callback.message, sql.catching_link,
                             t.elements['start_delete'], wishlist, callback.message.chat.username)

                bot.register_next_step_handler(callback.message, rm_elements)

            else:
                f.go_to_the_start(bot, callback.message, t.elements['no_elems'])

        if callback.data == 'get_list':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            wishlist = f.form_list(sql.checking_if_in_wishlist % callback.message.chat.username)

            if len(wishlist) > 0:
                f.go_to_the_start(bot, callback.message, f.return_list(sql.catching_link,
                            t.info['get_list'], wishlist, callback.message.chat.username))

            else:
                f.go_to_the_start(bot, callback.message, t.elements['no_elems'])

        if callback.data == 'hang_link':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            wishlist = f.form_list(sql.checking_if_in_wishlist % callback.message.chat.username)

            if len(wishlist) > 0:
                f.print_list(bot, callback.message, sql.catching_link,
                             t.link['start_hang'], wishlist, callback.message.chat.username)

                bot.register_next_step_handler(callback.message, choosing_elem, wishlist)

            else:
                f.go_to_the_start(bot, callback.message, t.elements['no_elems'])

        if callback.data == 'create_new':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            markup = types.InlineKeyboardMarkup()
            private_button = types.InlineKeyboardButton(t.buttons['private'], callback_data='make_private')
            non_private_button = types.InlineKeyboardButton(t.buttons['public'], callback_data='make_opened')
            markup.row(private_button, non_private_button)
            bot.send_message(callback.message.chat.id, t.access['start_choosing'], reply_markup=markup)

        if callback.data == 'exit':
            bot.delete_message(callback.message.chat.id, callback.message.message_id)

        if callback.data == 'make_private':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            f.sql_with_commit(sql.private_insert % callback.message.chat.username)

            markup = types.InlineKeyboardMarkup()
            create_password_button = types.InlineKeyboardButton(t.buttons['create_password'],
                                                                callback_data='create_password')
            markup.row(create_password_button)
            bot.send_message(callback.message.chat.id, t.password['from_private'], reply_markup=markup)

        if callback.data == 'make_opened':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            f.sql_with_commit(sql.non_private_insert % callback.message.chat.username)

            markup = types.InlineKeyboardMarkup()
            create_wishlist_button = types.InlineKeyboardButton(t.buttons['create_list'],
                                                                callback_data='create_wishlist')
            markup.row(create_wishlist_button)
            bot.send_message(callback.message.chat.id, t.info['from_public'], reply_markup=markup)

        if callback.data == 'create_password':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            bot.send_message(callback.message.chat.id, t.password['create_pass'])
            bot.register_next_step_handler(callback.message, password_creating)

        if callback.data == 'create_wishlist' or callback.data == 'add_elems':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            bot.send_message(callback.message.chat.id, t.elements['add_elements'])

            f.sql_with_commit(sql.init_wishlist % callback.message.chat.username)

            bot.register_next_step_handler(callback.message, wishlist_creating)

        if callback.data == 'yes':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            bot.send_message(callback.message.chat.id, t.info['try_again'])
            bot.register_next_step_handler(callback.message, get_wishlist)

        if callback.data == 'no':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            bot.delete_messages(callback.message.chat.id,
                            [callback.message.message_id,
                             callback.message.message_id - 1, callback.message.message_id - 2])

        if callback.data == 'yes2':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            bot.send_message(callback.message.chat.id, t.password['incorrect_pass'])
            bot.register_next_step_handler(callback.message, get_wishlist)

        if callback.data == 'no2':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            f.go_to_the_start(bot, callback.message, t.info['stop_trying'])

    except Exception:
        f.exceptions(bot, callback.message)


def choosing_elem(message, wishlist):
    try:
        if message.content_type == 'text':
            if message.text.lower() in wishlist:
                bot.send_message(message.chat.id, t.elements['chosen_elem'] % message.text.lower().capitalize())
                bot.register_next_step_handler(message, link_hanger, message.text.lower())

            else:
                bot.send_message(message.chat.id, t.elements['no_elem_links'])
                bot.register_next_step_handler(message, choosing_elem, wishlist)

        elif message.content_type != 'text':
            bot.send_message(message.chat.id, t.info['not_a_command'])
            bot.register_next_step_handler(message, choosing_elem, wishlist)

    except Exception:
        f.exceptions(bot, message)


def link_hanger(message, elem):
    try:
        if message.content_type == 'text':
            f.sql_with_commit(sql.adding_link % (message.chat.username, message.text, elem))
            f.go_to_the_start(bot, message, t.info['ready'])

        else:
            bot.send_message(message.chat.id, t.info['not_a_command'])
            bot.register_next_step_handler(message, link_hanger, elem)

    except Exception:
        f.exceptions(bot, message)


def password_creating(message):
    try:
        if message.content_type == 'text':
            flag = True
            for elem in message.text:
                if elem in t.info['alph']:
                    flag = False

            if flag and len(message.text) == 9 and message.text[4] == '-' and message.text.count('-') == 1:
                f.sql_with_commit(sql.password_insert % (message.text, message.chat.username))

                markup = types.InlineKeyboardMarkup()
                create_wishlist_button = types.InlineKeyboardButton(t.buttons['create_list'],
                                                                    callback_data='create_wishlist')
                markup.row(create_wishlist_button)

                bot.send_message(message.chat.id, t.password['pass_creating'], reply_markup=markup)

            else:
                bot.reply_to(message, t.password['out_format'])
                bot.register_next_step_handler(message, password_creating)

        elif message.content_type != 'text':
            bot.send_message(message.chat.id, t.info['not_a_command'])
            bot.register_next_step_handler(message, password_creating)

    except Exception:
        f.exceptions(bot, message)


def final_password_creating(message):
    try:
        if message.content_type == 'text':
            flag = True
            for elem in message.text:
                if elem in t.info['alph']:
                    flag = False

            if flag and len(message.text) == 9 and message.text[4] == '-' and message.text.count('-') == 1:
                f.sql_with_commit(sql.password_insert % (message.text, message.chat.username))
                f.go_to_the_start(bot, message, t.password['final_pass_creating'])

            else:
                bot.reply_to(message, t.password['out_format'])
                bot.register_next_step_handler(message, final_password_creating)

        elif message.content_type != 'text':
            bot.send_message(message.chat.id, t.info['not_a_command'])
            bot.register_next_step_handler(message, final_password_creating)

    except Exception:
        f.exceptions(bot, message)


def wishlist_creating(message):
    try:
        if message.content_type == 'text':
            wishlist = f.form_list(sql.checking_if_in_wishlist % message.chat.username)

            if message.text.lower() in wishlist:
                bot.send_message(message.chat.id, t.elements['exists'])

                bot.register_next_step_handler(message, wishlist_creating)

            elif message.text.lower() not in ('стоп', 'stop'):
                f.sql_with_commit(sql.wishlist_item_insert % (message.chat.username, message.text.lower()))

                bot.send_message(message.chat.id, t.elements['added'])
                bot.register_next_step_handler(message, wishlist_creating)

            else:
                f.go_to_the_start(bot, message, t.info['ready'])

        elif message.content_type != 'text':
            bot.send_message(message.chat.id, t.info['wrong_type'])
            bot.register_next_step_handler(message, wishlist_creating)

    except Exception:
        f.exceptions(bot, message)


def rm_link(message):
    try:
        if message.content_type == 'text':
            links = f.form_list(sql.select_links % message.chat.username)

            if message.text.lower() in ('стоп', 'stop'):
                f.go_to_the_start(bot, message, t.info['ready'])

            elif message.text.lower() not in links:
                bot.send_message(message.chat.id, t.link['no_link_in_offered'])

                bot.register_next_step_handler(message, rm_link)

            elif message.text.lower() not in ('стоп', 'stop'):
                f.sql_with_commit(sql.delete_links % (message.chat.username, message.text.lower()))

                bot.send_message(message.chat.id, t.link['deleted'])
                bot.register_next_step_handler(message, rm_link)

        elif message.content_type != 'text':
            bot.send_message(message.chat.id, t.info['not_a_command'])
            bot.register_next_step_handler(message, rm_link)

    except Exception:
        f.exceptions(bot, message)


def rm_elements(message):
    try:
        if message.content_type == 'text':
            wishlist = f.form_list(sql.checking_if_in_wishlist % message.chat.username)

            if len(wishlist) > 0:
                if message.text.lower() not in wishlist:
                    bot.send_message(message.chat.id, t.elements['no_elem_rm'])

                    bot.register_next_step_handler(message, rm_elements)

                elif message.text.lower() in ('стоп', 'stop'):
                    f.go_to_the_start(bot, message, t.info['ready'])

                elif message.text.lower() not in ('стоп', 'stop'):
                    f.sql_with_commit(sql.delete_elements % (message.chat.username, message.text.lower()))

                    bot.send_message(message.chat.id, t.elements['deleted'])
                    bot.register_next_step_handler(message, rm_elements)

            else:
                f.go_to_the_start(bot, message, t.elements['no_elems'])

        elif message.content_type != 'text':
            bot.send_message(message.chat.id, t.info['wrong_type'])
            bot.register_next_step_handler(message, rm_elements)

    except Exception:
        f.exceptions(bot, message)


def get_wishlist(message):
    try:
        usernames = f.form_list(sql.checking_if_in_table)

        if message.content_type == 'text':
            if message.text not in usernames:
                markup = types.InlineKeyboardMarkup()
                yes_button = types.InlineKeyboardButton(t.buttons['yes'], callback_data='yes')
                no_button = types.InlineKeyboardButton(t.buttons['no'], callback_data='no')
                markup.row(yes_button, no_button)

                bot.send_message(message.chat.id, t.info['no_username'], reply_markup=markup)
            else:
                private_flag = f.sql_without_commit(sql.checking_if_private % message.text)[0][0]

                if private_flag == 0:
                    try:
                        wishlist = f.form_list(sql.checking_if_in_wishlist % message.text)

                        if len(wishlist) > 0:
                            f.go_to_the_start(bot, message, f.return_list(sql.catching_link,
                                                            t.elements['friends_hat'], wishlist, message.text))

                        else:
                            f.go_to_the_start(bot, message, t.elements['empty_fr_list'])

                    except sqlite3.OperationalError:
                        f.go_to_the_start(bot, message, t.info['didnt_create'])

                elif private_flag == 1:
                    password = f.sql_without_commit(sql.catching_password % message.text)[0][0]

                    bot.send_message(message.chat.id, t.access['is_private'] % message.text)
                    bot.register_next_step_handler(message, check_pass, password, message.text)

        elif message.content_type != 'text':
            bot.send_message(message.chat.id, t.info['not_a_command'])
            bot.register_next_step_handler(message, get_wishlist)

    except Exception:
        f.exceptions(bot, message)


def check_pass(message, password, username):
    try:
        if message.content_type == 'text':
            if message.text == password:
                try:
                    wishlist = f.form_list(sql.checking_if_in_wishlist % username)

                    if len(wishlist) > 0:
                        f.go_to_the_start(bot, message, f.return_list(sql.catching_link,
                                                        t.elements['friends_hat'], wishlist, username))

                    else:
                        f.go_to_the_start(bot, message, t.elements['empty_fr_list'])

                except sqlite3.OperationalError:
                    f.go_to_the_start(bot, message, t.info['didnt_create'])

            else:
                markup = types.InlineKeyboardMarkup()
                yes_button = types.InlineKeyboardButton('Да', callback_data='yes2')
                no_button = types.InlineKeyboardButton('Нет', callback_data='no2')
                markup.row(yes_button, no_button)
                bot.send_message(message.chat.id, t.password['incorrect_vars'], reply_markup=markup)

        elif message.content_type != 'text':
            bot.send_message(message.chat.id, t.info['not_a_command'])
            bot.register_next_step_handler(message, check_pass)

    except Exception:
        f.exceptions(bot, message)


bot.polling(none_stop=True)
