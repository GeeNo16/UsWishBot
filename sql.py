init_table = 'CREATE TABLE IF NOT EXISTS users (id auto_increment primary key, ' \
             'name varchar(50), second_name varchar(50), pass varchar(50),' \
             'username varchar(50), private boolean)'

insert_name_secondname_telegramid = "INSERT INTO users (name, second_name, username) VALUES ('%s', '%s', '%s')"

checking_if_in_table = 'SELECT username FROM users'

private_insert = "UPDATE users SET private=1 WHERE username='%s'"

non_private_insert = "UPDATE users SET private=0 WHERE username='%s'"

password_insert = "UPDATE users SET pass='%s' WHERE username='%s'"

init_wishlist = "CREATE TABLE IF NOT EXISTS '%s' (id auto_increment primary key, gift varchar, " \
                "link varchar DEFAULT '', gets_presented boolean DEFAULT 0, cat int DEFAULT 0)"

wishlist_item_insert = "INSERT INTO '%s' (gift) VALUES ('%s')"

checking_if_in_wishlist = "SELECT gift FROM '%s'"

checking_if_private = "SELECT private FROM users WHERE username='%s'"

catching_name = "SELECT name FROM users WHERE username='%s'"

catching_password = "SELECT pass FROM users WHERE username='%s'"

adding_link = "UPDATE '%s' SET link='%s' WHERE gift='%s'"

catching_link = "SELECT link FROM '%s' WHERE gift='%s'"

checking_if_private_exists = "SELECT private FROM users WHERE username='%s'"

delete_elements = "DELETE FROM '%s' WHERE gift='%s'"

select_links = "SELECT gift FROM '%s' WHERE link <>''"

delete_links = "UPDATE '%s' SET link='' WHERE gift='%s'"

select_pass = "SELECT pass FROM users WHERE username='%s'"

gets_presented = "UPDATE '%s' SET gets_presented=1 WHERE gift='%s'"

prepare_crossing = "SELECT gets_presented FROM '%s' WHERE gift='%s'"

select_not_crossed = "SELECT gift FROM '%s' WHERE gets_presented<>1"

cat_insert = "UPDATE '%s' SET cat='%s' WHERE gift='%s'"

cat_select = "SELECT cat FROM '%s' WHERE gift='%s'"

gift_select_ct = "SELECT gift FROM '%s' WHERE cat<>'%s'"

gift_select_cat_0 = "SELECT gift FROM '%s' WHERE cat=0"

cat_select_all = "SELECT cat FROM '%s'"
