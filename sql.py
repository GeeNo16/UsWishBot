init_table = 'CREATE TABLE IF NOT EXISTS users (id auto_increment primary key, ' \
             'name varchar(50), second_name varchar(50), pass varchar(50), ' \
             'username varchar(50), wishlist varchar, private boolean)'

insert_name_secondname_telegramid = "INSERT INTO users (name, second_name, username) VALUES ('%s', '%s', '%s')"

checking_if_in_table = 'SELECT username FROM users'

private_insert = "UPDATE users SET private=1 WHERE username"

non_private_insert = "UPDATE users SET private=0 WHERE username"
