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
        bot.clear_step_handler_by_chat_id(message.chat.id)

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

            if callback.message.chat.username.lower() not in usernames:
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

            private_exists = f.sql_without_commit(
                sql.checking_if_private_exists % callback.message.chat.username.lower())

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
                change_password_button = types.InlineKeyboardButton(t.buttons['change_password'],
                                                                    callback_data='change_password')
                get_list_button = types.InlineKeyboardButton(t.buttons['get_list'], callback_data='get_list')
                check_pass_button = types.InlineKeyboardButton(t.buttons['print_pass'], callback_data='print_pass')
                categories_button = types.InlineKeyboardButton(t.buttons['manage_cats'], callback_data='manage_cats')

                if private_exists[0][0] == 0:
                    change_private_button = types.InlineKeyboardButton(t.buttons['change_access'],
                                                                       callback_data='change_private')
                    markup.row(add_elements, delete_elems)
                    markup.row(hang_link_button, unhang_link_button)
                    markup.row(change_private_button)
                    markup.row(get_list_button)
                    markup.row(categories_button)

                else:
                    change_private_button = types.InlineKeyboardButton(t.buttons['change_access'],
                                                                       callback_data='change_public')
                    markup.row(add_elements, delete_elems)
                    markup.row(hang_link_button, unhang_link_button)
                    markup.row(change_private_button, change_password_button)
                    markup.row(check_pass_button)
                    markup.row(get_list_button)
                    markup.row(categories_button)

                bot.send_message(callback.message.chat.id, t.info['you_have_list'], reply_markup=markup)

        if callback.data == 'manage_cats':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)
            wishlist = f.form_list(sql.checking_if_in_wishlist % callback.message.chat.username.lower())
            if len(wishlist) > 0:
                f.form_buttons(bot, callback.message, t.cats_list, f.print_list(bot, callback.message,
                                                                                sql.catching_link,
                                                                                t.cats['start'],
                                                                                wishlist,
                                                                                callback.message.
                                                                                chat.username.lower(),
                                                                                1, 0))
                bot.register_next_step_handler(callback.message, choosing_elem, [], 1)

            else:
                f.go_to_the_start(bot, callback.message, t.cats['empty_list'])

        if callback.data == 'print_pass':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            password = f.sql_without_commit(sql.select_pass % callback.message.chat.username.lower())[0][0]
            private_exists = f.sql_without_commit(
                sql.checking_if_private_exists % callback.message.chat.username.lower())

            if private_exists[0][0] == 1:
                f.go_to_the_start(bot, callback.message, t.password['get_pass'] %
                                  (callback.message.chat.username.lower(), password))

            else:
                f.go_to_the_start(bot, callback.message, t.info['cant_use'])

        if callback.data == 'change_password':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            private_exists = f.sql_without_commit(
                sql.checking_if_private_exists % callback.message.chat.username.lower())

            if private_exists[0][0] == 1:
                bot.send_message(callback.message.chat.id, t.password['change_pass'])
                bot.register_next_step_handler(callback.message, password_creating, 1)

            else:
                f.go_to_the_start(bot, callback.message, t.info['cant_use'])

        if callback.data == 'change_private':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            f.sql_with_commit(sql.private_insert % callback.message.chat.username.lower())

            bot.send_message(callback.message.chat.id, t.access['to_private'])
            bot.register_next_step_handler(callback.message, password_creating, 1)

        if callback.data == 'change_public':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            f.sql_with_commit(sql.non_private_insert % callback.message.chat.username.lower())

            f.go_to_the_start(bot, callback.message, t.access['to_public'])

        if callback.data == 'unhang_link':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            links = f.form_list(sql.select_links % callback.message.chat.username.lower())

            if len(links) > 0:
                f.form_buttons(bot, callback.message, links, f.print_list(bot, callback.message, sql.catching_link,
                                                                          t.link['start_remove'], links,
                                                                          callback.message.chat.username.lower(), 1, 0))

                bot.register_next_step_handler(callback.message, rm_link)

            else:
                f.go_to_the_start(bot, callback.message, t.link['no_links'])

        if callback.data == 'delete_elems':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            wishlist = f.form_list(sql.checking_if_in_wishlist % callback.message.chat.username.lower())

            if len(wishlist) > 0:
                f.form_buttons(bot, callback.message, wishlist, f.print_list(bot, callback.message, sql.catching_link,
                                                                             t.elements['start_delete'], wishlist,
                                                                             callback.message.chat.username.lower(), 1,
                                                                             0))

                bot.register_next_step_handler(callback.message, rm_elements)

            else:
                f.go_to_the_start(bot, callback.message, t.elements['no_elems'])

        if callback.data == 'get_list':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            wishlist = f.form_list(sql.checking_if_in_wishlist % callback.message.chat.username.lower())

            if len(wishlist) > 0:
                f.go_to_the_start(bot, callback.message, f.print_list(bot, callback.message, sql.catching_link,
                                                                      t.info['get_list'], wishlist,
                                                                      callback.message.chat.username.lower(), 1, 0))

            else:
                f.go_to_the_start(bot, callback.message, t.elements['no_elems'])

        if callback.data == 'hang_link':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            wishlist = f.form_list(sql.checking_if_in_wishlist % callback.message.chat.username.lower())

            if len(wishlist) > 0:
                f.form_buttons(bot, callback.message, wishlist, f.print_list(bot, callback.message, sql.catching_link,
                                                                             t.link['start_hang'], wishlist,
                                                                             callback.message.chat.username.lower(), 1,
                                                                             0))

                bot.register_next_step_handler(callback.message, choosing_elem, wishlist, 0)

            else:
                f.go_to_the_start(bot, callback.message, t.elements['no_elems'])

        if callback.data == 'create_new':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)
            f.sql_with_commit(sql.init_wishlist % callback.message.chat.username.lower())

            markup = types.InlineKeyboardMarkup()
            private_button = types.InlineKeyboardButton(t.buttons['private'], callback_data='make_private')
            non_private_button = types.InlineKeyboardButton(t.buttons['public'], callback_data='make_opened')
            markup.row(private_button, non_private_button)
            bot.send_message(callback.message.chat.id, t.access['start_choosing'], reply_markup=markup)

        if callback.data == 'exit':
            bot.delete_message(callback.message.chat.id, callback.message.message_id)

        if callback.data == 'make_private':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            f.sql_with_commit(sql.private_insert % callback.message.chat.username.lower())
            bot.send_message(callback.message.chat.id, t.password['from_private'] + t.password['create_pass'])
            bot.register_next_step_handler(callback.message, password_creating, 0)

        if callback.data == 'make_opened':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)

            f.sql_with_commit(sql.non_private_insert % callback.message.chat.username.lower())
            f.form_buttons(bot, callback.message, [], t.info['from_public'] + t.elements['add_elements'])
            bot.register_next_step_handler(callback.message, wishlist_creating)

        if callback.data == 'add_elems':
            bot.clear_step_handler_by_chat_id(callback.message.chat.id)
            f.form_buttons(bot, callback.message, [], t.elements['add_elements'])

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


def choosing_elem(message, wishlist, mode):
    try:
        if message.content_type == 'text':
            if message.text == t.buttons['exit']:
                bot.send_message(message.chat.id, t.info['great_choice'], reply_markup=types.ReplyKeyboardRemove())
                f.go_to_the_start(bot, message, t.info['ready'])

            else:
                if message.text[0] == '/':
                    bot.send_message(message.chat.id, t.info['cant_start'])
                    bot.register_next_step_handler(message, choosing_elem, wishlist, mode)

                elif (mode == 0 and message.text.lower() in wishlist) or (mode == 1 and message.text in t.cats_list):
                    if mode == 0:
                        bot.send_message(message.chat.id, t.elements['chosen_elem'] % message.text.lower().capitalize())
                        bot.register_next_step_handler(message, link_hanger, message.text.lower())

                    elif mode == 1:
                        index = t.cats_list.index(message.text) + 1
                        wishlist_1 = f.form_list(sql.gift_select_ct % (message.chat.username.lower(), index))

                        if len(wishlist_1) > 0:
                            f.form_buttons(bot, message, wishlist_1, t.cats['chosen'] % message.text)
                            bot.register_next_step_handler(message, cat_appender, message.text, wishlist_1)

                        else:
                            bot.send_message(message.chat.id, t.info['stop_joking'],
                                             reply_markup=types.ReplyKeyboardRemove())
                            f.go_to_the_start(bot, message, t.cats['all_in_one'] % message.text)

                else:
                    if mode == 0:
                        bot.send_message(message.chat.id, t.elements['no_elem_links'])
                        bot.register_next_step_handler(message, choosing_elem, wishlist, mode)

                    elif mode == 1:
                        bot.send_message(message.chat.id, t.cats['incorrect'])
                        bot.register_next_step_handler(message, choosing_elem, wishlist, mode)

        elif message.content_type != 'text':
            bot.send_message(message.chat.id, t.info['not_a_command'])
            bot.register_next_step_handler(message, choosing_elem, wishlist, mode)

    except Exception:
        f.exceptions(bot, message)


def cat_appender(message, cat, wishlist):
    try:
        if message.content_type == 'text':
            index = t.cats_list.index(cat) + 1

            if len(wishlist) > 0:
                if message.text[0] == '/':
                    bot.send_message(message.chat.id, t.info['cant_start'])
                    bot.register_next_step_handler(message, cat_appender, cat, wishlist)

                elif message.text == t.buttons['exit']:
                    bot.send_message(message.chat.id, t.info['great_choice'], reply_markup=types.ReplyKeyboardRemove())
                    f.form_buttons(bot, message, t.cats_list, t.cats['created'] % cat)
                    bot.register_next_step_handler(message, choosing_elem, [], 1)

                elif message.text.lower() not in wishlist:
                    f.form_buttons(bot, message, wishlist, t.elements['no_elem_rm'])
                    bot.register_next_step_handler(message, cat_appender, cat, wishlist)

                else:
                    index_1 = f.sql_without_commit(sql.cat_select %
                                                   (message.chat.username.lower(), message.text.lower()))[0][0]
                    if index_1 == 0:
                        f.sql_with_commit(sql.cat_insert % (message.chat.username.lower(), index, message.text.lower()))
                        wishlist.remove(message.text.lower())
                        f.form_buttons(bot, message, wishlist, t.cats['added'] % cat)
                        bot.register_next_step_handler(message, cat_appender, cat, wishlist)
                    else:
                        f.sql_with_commit(sql.cat_insert % (message.chat.username.lower(), index, message.text.lower()))
                        wishlist.remove(message.text.lower())
                        f.form_buttons(bot, message, wishlist, t.cats['in_cat'] % (t.cats_list[index_1 - 1], cat))
                        bot.register_next_step_handler(message, cat_appender, cat, wishlist)

            else:
                bot.send_message(message.chat.id, t.info['great_choice'], reply_markup=types.ReplyKeyboardRemove())
                f.go_to_the_start(bot, message, t.cats['empty_list'] % cat)

        else:
            bot.send_message(message.chat.id, t.info['not_a_command'])
            bot.register_next_step_handler(message, cat_appender, cat, wishlist)

    except Exception:
        f.exceptions(bot, message)


def link_hanger(message, elem):
    try:
        if message.content_type == 'text':
            if message.text[0] == '/':
                bot.send_message(message.chat.id, t.info['cant_start'])
                bot.register_next_step_handler(message, link_hanger, elem)

            elif '//' in message.text:
                f.sql_with_commit(sql.adding_link % (message.chat.username.lower(), message.text, elem))
                bot.send_message(message.chat.id, t.info['great_choice'], reply_markup=types.ReplyKeyboardRemove())
                f.go_to_the_start(bot, message, t.info['ready'])

            else:
                bot.send_message(message.chat.id, t.info['not_a_link'])
                bot.register_next_step_handler(message, link_hanger, elem)

        else:
            bot.send_message(message.chat.id, t.info['not_a_command'])
            bot.register_next_step_handler(message, link_hanger, elem)

    except Exception:
        f.exceptions(bot, message)


def password_creating(message, mode):
    try:
        if message.content_type == 'text':
            flag = True
            for elem in message.text:
                if elem in t.info['alph']:
                    flag = False

            if message.text[0] == '/':
                bot.send_message(message.chat.id, t.info['cant_start'])
                bot.register_next_step_handler(message, password_creating, mode)

            elif flag and len(message.text) == 9 and message.text[4] == '-' and message.text.count('-') == 1:
                if mode == 0:
                    f.sql_with_commit(sql.password_insert % (message.text, message.chat.username.lower()))

                    f.form_buttons(bot, message, [], t.password['pass_creating'] + t.elements['add_elements'])
                    bot.register_next_step_handler(message, wishlist_creating)

                elif mode == 1:
                    f.sql_with_commit(sql.password_insert % (message.text, message.chat.username.lower()))
                    f.go_to_the_start(bot, message, t.password['final_pass_creating'])

            else:
                bot.reply_to(message, t.password['out_format'])
                bot.register_next_step_handler(message, password_creating, mode)

        elif message.content_type != 'text':
            bot.send_message(message.chat.id, t.info['not_a_command'])
            bot.register_next_step_handler(message, password_creating)

    except Exception:
        f.exceptions(bot, message)


def wishlist_creating(message):
    try:
        if message.content_type == 'text':
            wishlist = f.form_list(sql.checking_if_in_wishlist % message.chat.username.lower())

            if message.text[0] == '/':
                bot.send_message(message.chat.id, t.info['cant_start'])
                bot.register_next_step_handler(message, wishlist_creating)

            elif message.text.lower() in wishlist:
                bot.send_message(message.chat.id, t.elements['exists'])

                bot.register_next_step_handler(message, wishlist_creating)

            elif message.text != t.buttons['exit']:
                f.sql_with_commit(sql.wishlist_item_insert % (message.chat.username.lower(), message.text.lower()))

                bot.send_message(message.chat.id, t.elements['added'])
                bot.register_next_step_handler(message, wishlist_creating)

            else:
                flag = False
                cats = f.form_list(sql.cat_select_all % message.chat.username.lower())
                for item in cats:
                    if item != 0:
                        flag = True

                bot.send_message(message.chat.id, t.info['great_choice'], reply_markup=types.ReplyKeyboardRemove())

                if flag:
                    markup = types.InlineKeyboardMarkup()
                    yes_button = types.InlineKeyboardButton(t.buttons['yes'], callback_data='manage_cats')
                    no_button = types.InlineKeyboardButton(t.buttons['no'], callback_data='make_list')
                    markup.row(yes_button, no_button)
                    bot.send_message(message.chat.id, t.cats['after_adding'], reply_markup=markup)
                    bot.register_next_step_handler(message, choosing_elem, [], 1)

                else:
                    f.form_buttons(bot, message, t.cats_list, f.print_list(bot, message,
                                                                           sql.catching_link,
                                                                           t.cats['start'],
                                                                           wishlist,
                                                                           message.
                                                                           chat.username.lower(),
                                                                           1, 0))
                    bot.register_next_step_handler(message, choosing_elem, [], 1)

        elif message.content_type != 'text':
            bot.send_message(message.chat.id, t.info['wrong_type'])
            bot.register_next_step_handler(message, wishlist_creating)

    except Exception:
        f.exceptions(bot, message)


def rm_link(message):
    try:
        if message.content_type == 'text':
            links = f.form_list(sql.select_links % message.chat.username.lower())

            if message.text[0] == '/':
                bot.send_message(message.chat.id, t.info['cant_start'])
                bot.register_next_step_handler(message, rm_link)

            elif message.text == t.buttons['exit']:
                bot.send_message(message.chat.id, t.info['great_choice'], reply_markup=types.ReplyKeyboardRemove())
                f.go_to_the_start(bot, message, t.info['ready'])

            elif message.text.lower() not in links:
                bot.send_message(message.chat.id, t.link['no_link_in_offered'])

                bot.register_next_step_handler(message, rm_link)

            elif message.text.lower() != t.buttons['exit']:
                f.sql_with_commit(sql.delete_links % (message.chat.username.lower(), message.text.lower()))
                links.remove(message.text.lower())
                f.form_buttons(bot, message, links, t.link['deleted'])
                bot.register_next_step_handler(message, rm_link)

        elif message.content_type != 'text':
            bot.send_message(message.chat.id, t.info['not_a_command'])
            bot.register_next_step_handler(message, rm_link)

    except Exception:
        f.exceptions(bot, message)


def rm_elements(message):
    try:
        if message.content_type == 'text':
            wishlist = f.form_list(sql.checking_if_in_wishlist % message.chat.username.lower())

            if len(wishlist) > 0:
                if message.text[0] == '/':
                    bot.send_message(message.chat.id, t.info['cant_start'])
                    bot.register_next_step_handler(message, rm_elements)

                elif message.text == t.buttons['exit']:
                    bot.send_message(message.chat.id, t.info['great_choice'], reply_markup=types.ReplyKeyboardRemove())
                    f.go_to_the_start(bot, message, t.info['ready'])

                elif message.text.lower() not in wishlist:
                    f.form_buttons(bot, message, wishlist, t.elements['no_elem_rm'])

                    bot.register_next_step_handler(message, rm_elements)

                elif message.text != t.buttons['exit']:
                    f.sql_with_commit(sql.delete_elements % (message.chat.username.lower(), message.text.lower()))
                    wishlist.remove(message.text.lower())

                    f.form_buttons(bot, message, wishlist, t.elements['deleted'])
                    bot.register_next_step_handler(message, rm_elements)

            else:
                bot.send_message(message.chat.id, t.info['great_choice'], reply_markup=types.ReplyKeyboardRemove())
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
            if message.text.lower()[0] == '@':
                username = message.text.lower()[1:]
            else:
                username = message.text.lower()

            if message.chat.username.lower() != username:
                if message.text[0] == '/':
                    bot.send_message(message.chat.id, t.info['cant_start'])
                    bot.register_next_step_handler(message, get_wishlist)

                elif username not in usernames:
                    markup = types.InlineKeyboardMarkup()
                    yes_button = types.InlineKeyboardButton(t.buttons['yes'], callback_data='yes')
                    no_button = types.InlineKeyboardButton(t.buttons['no'], callback_data='no')
                    markup.row(yes_button, no_button)

                    bot.send_message(message.chat.id, t.info['no_username'], reply_markup=markup)
                else:
                    private_flag = f.sql_without_commit(sql.checking_if_private % username)[0][0]

                    if private_flag == 0:
                        try:
                            wishlist = f.form_list(sql.checking_if_in_wishlist % username)
                            but_els = f.form_list(sql.select_not_crossed % username)

                            if len(wishlist) > 0:
                                f.form_buttons(bot, message, but_els, f.print_list(bot, message, sql.catching_link,
                                                                                   t.elements['friends_hat'], wishlist,
                                                                                   username, 1,
                                                                                   1))

                                bot.register_next_step_handler(message, elem_crosser, username)

                            else:
                                f.go_to_the_start(bot, message, t.elements['empty_fr_list'])

                        except sqlite3.OperationalError:
                            f.go_to_the_start(bot, message, t.info['didnt_create'])

                    elif private_flag == 1:
                        password = f.sql_without_commit(sql.catching_password % username)[0][0]

                        bot.send_message(message.chat.id, t.access['is_private'])
                        bot.register_next_step_handler(message, check_pass, password, username)

            else:
                f.go_to_the_start(bot, message, t.info['incorrect_mode'])

        elif message.content_type != 'text':
            bot.send_message(message.chat.id, t.info['not_a_command'])
            bot.register_next_step_handler(message, get_wishlist)

    except Exception:
        f.exceptions(bot, message)


def check_pass(message, password, username):
    try:
        if message.content_type == 'text':
            if message.text[0] == '/':
                bot.send_message(message.chat.id, t.info['cant_start'])
                bot.register_next_step_handler(message, elem_crosser, username)

            elif message.text == password:
                try:
                    wishlist = f.form_list(sql.checking_if_in_wishlist % username)
                    but_els = f.form_list(sql.select_not_crossed % username)

                    if len(wishlist) > 0:
                        f.form_buttons(bot, message, but_els, f.print_list(bot, message, sql.catching_link,
                                                                           t.elements['friends_hat'], wishlist,
                                                                           username.lower(), 1,
                                                                           1))

                        bot.register_next_step_handler(message, elem_crosser, username)

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


def elem_crosser(message, username):
    if message.content_type == 'text':
        if message.text != t.buttons['exit']:
            if message.text[0] == '/':
                bot.send_message(message.chat.id, t.info['cant_start'])
                bot.register_next_step_handler(message, elem_crosser, username)

            f.sql_with_commit(sql.gets_presented % (username, message.text.lower()))
            bot.send_message(message.chat.id, t.info['great_choice'], reply_markup=types.ReplyKeyboardRemove())
            f.go_to_the_start(bot, message, t.info['ready'])
        else:
            bot.send_message(message.chat.id, t.info['great_choice'], reply_markup=types.ReplyKeyboardRemove())
            f.go_to_the_start(bot, message, t.info['ready'])

    elif message.content_type != 'text':
        bot.send_message(message.chat.id, t.info['not_a_command'])
        bot.register_next_step_handler(message, check_pass)


bot.polling(none_stop=True)
