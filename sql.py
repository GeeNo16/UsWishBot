init_table = 'CREATE TABLE IF NOT EXISTS users (id auto_increment primary key, ' \
             'name varchar(50), second_name varchar(50), pass varchar(50), ' \
             'username varchar(50), private boolean)'

insert_name_secondname_telegramid = "INSERT INTO users (name, second_name, username) VALUES ('%s', '%s', '%s')"

checking_if_in_table = 'SELECT username FROM users'

private_insert = "UPDATE users SET private=1 WHERE username='%s'"

non_private_insert = "UPDATE users SET private=0 WHERE username='%s'"

password_insert = "UPDATE users SET pass='%s' WHERE username='%s'"

init_wishlist = "CREATE TABLE IF NOT EXISTS '%s' (id auto_increment primary key, gift varchar, link varchar)"

wishlist_item_insert = "INSERT INTO '%s' (gift) VALUES ('%s')"

checking_if_in_wishlist = "SELECT gift FROM '%s'"

checking_if_private = "SELECT private FROM users WHERE username='%s'"

catching_name = "SELECT name FROM users WHERE username='%s'"
