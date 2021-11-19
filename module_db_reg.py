import os
import urllib.request
import pymysql
import pymysql.cursors
from config_con import *


REG_USER = 'u1488792_reg_db'
REG_PASS = ''
REG_DB = 'u1488792_sol_db'
REG_IP = '37.140.192.84'
REG_PORT = 3306


class MODULE_MYSQL(object):

    def __init__(self):
        self.item_id = None
        self.item_name = None
        self.item_description = None
        self.item_price = None
        self.item_stock_status = None
        self.item_sku = None
        self.item_link = None
        self.item_image = None
        self.item_stock_quantity = None
        self.table_name = 'FB15'
        self.name = 'XXX'



    def create_table(self):
        try:
            connection = pymysql.connect(user=REG_USER, password=REG_PASS, host=REG_IP, database=REG_DB, port=REG_PORT,
                                         cursorclass=pymysql.cursors.DictCursor)
            cursor = connection.cursor()
            cursor.execute(f"CREATE TABLE {self.table_name} (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), woo_id VARCHAR(255), price VARCHAR(255), url VARCHAR(255), image VARCHAR(255), stock_status VARCHAR(255))")
            result = cursor.fetchall()
            connection.close()
            return result
        except Exception as error:
            return error

    def insert_table_fb(self, product):
        name = product[0]
        woo_id = product[1]
        price = product[2]
        url = product[3]
        image = product[4]
        stock_status = product[5]
        try:
            connection = pymysql.connect(user=REG_USER, password=REG_PASS, host=REG_IP, database=REG_DB, port=REG_PORT,
                                         cursorclass=pymysql.cursors.DictCursor)
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE woo_id = %s", (str(woo_id)))
            result = cursor.fetchall()
            if result:
                print('Row exists')
            else:
                try:
                    connection = pymysql.connect(user=REG_USER, password=REG_PASS, host=REG_IP, database=REG_DB,
                                                 port=REG_PORT,
                                                 cursorclass=pymysql.cursors.DictCursor)
                    cursor = connection.cursor()
                    cursor.execute(
                        f"INSERT INTO {self.table_name} (name, woo_id, price, url, image, stock_status) VALUES (%s,%s,%s,%s,%s,%s)",
                        (name, woo_id, price, url, image, stock_status,))
                    connection.commit()
                    print(cursor.rowcount, "record(s) affected")
                    connection.close()
                    return cursor.rowcount
                except Exception as error:
                    print(error)
        except Exception as error:
            print(error)

    def select_table_fb(self):
        try:
            connection = pymysql.connect(user=REG_USER, password=REG_PASS, host=REG_IP, database=REG_DB, port=REG_PORT,
                                         cursorclass=pymysql.cursors.DictCursor)
            cursor = connection.cursor()
            cursor.execute(f"SELECT name, woo_id, price, url, image, stock_status FROM {self.table_name}")
            result = cursor.fetchall()
            connection.close()
            return result
        except Exception as error:
            return error

    def max_element(self):
        try:
            connection = pymysql.connect(user=REG_USER, password=REG_PASS, host=REG_IP, database=REG_DB, port=REG_PORT,
                                         cursorclass=pymysql.cursors.DictCursor)
            cursor = connection.cursor()
            cursor.execute(f"SELECT MAX(Id) FROM {self.table_name}")
            max = cursor.fetchall()
            result = max[0]['MAX(Id)']
            connection.close()
            return result
        except Exception as error:
            return error

# -------------------------------- OLD ----------------------------------------------------

    def select_products(table_name, stockstatus):
        db_user = "gmw0tdz26q0z5457"
        db_pass = "ty6ija59lc028qqe"
        db_host = "vkh7buea61avxg07.cbetxkdyhwsb.us-east-1.rds.amazonaws.com"
        db_port = 3306
        db_database = "lq32alymdi5j9q8v"
        conn = pymysql.connect(user=db_user, password=db_pass, host=db_host, database=db_database, port=db_port,
                               cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()

        try:
            if stockstatus == 'instock':
                cur.execute(
                    f"SELECT id, item_id, item_name, item_description, item_price, item_stock_status, item_sku, item_link, item_image, item_stock_quantity "
                    f"FROM {table_name} WHERE item_stock_status = 'instock' ORDER BY item_id", )
                myresult = cur.fetchall()
                return myresult
            elif stockstatus == 'outofstock':
                cur.execute(
                    f"SELECT id, item_id, item_name, item_description, item_price, item_stock_status, item_sku, item_link, item_image, item_stock_quantity "
                    f"FROM {table_name} WHERE item_stock_status = 'outofstock' ORDER BY item_id", )
                myresult = cur.fetchall()
                return myresult
            elif stockstatus == 'all':
                cur.execute(
                    f"SELECT id, item_id, item_name, item_description, item_price, item_stock_status, item_sku, item_link, item_image, item_stock_quantity "
                    f"FROM {table_name} ORDER BY item_id", )
                myresult = cur.fetchall()
                return myresult
        except Exception as error:
            return error
        finally:
            conn.close()

    def delete_allfrom_table(self):
        cur = self.conn.cursor()
        try:
            cur.execute(f"DELETE FROM {self.table_name}", )
            self.conn.commit()
            result = cur.fetchall()
            return result
        except Exception as error:
            return error


    def select_product_param(table_name):
        db_user = "gmw0tdz26q0z5457"
        db_pass = "ty6ija59lc028qqe"
        db_host = "vkh7buea61avxg07.cbetxkdyhwsb.us-east-1.rds.amazonaws.com"
        db_port = 3306
        db_database = "lq32alymdi5j9q8v"
        conn = pymysql.connect(user=db_user, password=db_pass, host=db_host, database=db_database, port=db_port,
                               cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()

        try:
            cur.execute(
                f"SELECT * "
                f"FROM {table_name} WHERE item_name = '*NOT FOR SALE* Test jewelry'", )
            myresult = cur.fetchall()
            return myresult
        except Exception as error:
            return error
        finally:
            conn.close()


    def count(table_name, stockstatus):
        db_user = "gmw0tdz26q0z5457"
        db_pass = "ty6ija59lc028qqe"
        db_host = "vkh7buea61avxg07.cbetxkdyhwsb.us-east-1.rds.amazonaws.com"
        db_port = 3306
        db_database = "lq32alymdi5j9q8v"
        conn = pymysql.connect(user=db_user, password=db_pass, host=db_host, database=db_database, port=db_port,
                               cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()

        try:
            if stockstatus == 'instock':
                cur.execute(f"SELECT count(*) FROM {table_name} WHERE item_stock_status = 'instock'")
                rows = cur.fetchall()[0].get('count(*)')
                return rows
            elif stockstatus == 'outofstock':
                cur.execute(f"SELECT count(*) FROM {table_name} WHERE item_stock_status = 'outofstock'")
                rows = cur.fetchall()[0].get('count(*)')
                return rows
            elif stockstatus == 'all':
                cur.execute(f"SELECT count(*) FROM {table_name}")
                rows = cur.fetchall()[0].get('count(*)')
                return rows
        except Exception as error:
            return error
        finally:
            conn.close()

    def last(table_name):
        db_user = "gmw0tdz26q0z5457"
        db_pass = "ty6ija59lc028qqe"
        db_host = "vkh7buea61avxg07.cbetxkdyhwsb.us-east-1.rds.amazonaws.com"
        db_port = 3306
        db_database = "lq32alymdi5j9q8v"
        conn = pymysql.connect(user=db_user, password=db_pass, host=db_host, database=db_database, port=db_port,
                               cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()

        cur.execute(f"SELECT * FROM {table_name} ORDER BY ID DESC LIMIT 1")
        last = cur.fetchall()[0].get('item_sku')

        conn.close()

        return last

    def insert_products_simple(pr):
        table_name = 'simple2'

        db_user = config.REG_USER
        db_pass = config.REG_PASS
        db_host = config.REG_IP
        db_port = config.REG_PORT
        db_database = config.REG_DB
        conn = pymysql.connect(user=db_user, password=db_pass, host=db_host, database=db_database, port=db_port,
                               cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()

        cur.execute(f"SELECT * FROM {table_name} WHERE sku = %s", (str(id)))
        myresult = cur.fetchall()
        if myresult:
            print('Row exists')
        else:
            cur.execute(
                f"INSERT INTO {table_name} (sku, name, permalink, regular_price, short_description, image) VALUES (%s,%s,%s,%s,%s,%s)",
                (pr[0], pr[1], pr[2], pr[3], pr[4], pr[5]))
            conn.commit()
            print(cur.rowcount, "record(s) affected")
            conn.close()

    def insert_products(table_name, item_id, item_name, item_description, item_price, item_stock_status, item_sku,
                        item_link, item_image, item_stock_quantity):

        db_user = "gmw0tdz26q0z5457"
        db_pass = "ty6ija59lc028qqe"
        db_host = "vkh7buea61avxg07.cbetxkdyhwsb.us-east-1.rds.amazonaws.com"
        db_port = 3306
        db_database = "lq32alymdi5j9q8v"

        conn = pymysql.connect(user=db_user, password=db_pass, host=db_host, database=db_database, port=db_port,
                               cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()

        cur.execute(f"SELECT * FROM {table_name} WHERE item_id = %s", (str(item_id)))
        myresult = cur.fetchall()
        if myresult:
            # for i in myresult:
            #     print(i)
            print('Row exists')
        else:
            cur.execute(
                f"INSERT INTO {table_name} (item_id, item_name, item_description, item_price, item_stock_status, item_sku, item_link, item_image, item_stock_quantity) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (item_id, item_name, item_description, item_price, item_stock_status, item_sku, item_link, item_image,
                 item_stock_quantity,))
            conn.commit()
            print(cur.rowcount, "record(s) affected")
            conn.close()

    def insert_guests(guest_id, guest_name, guest_firstname, guest_lastname):
        table_name = 'karenka_guests1'

        db_user = "gmw0tdz26q0z5457"
        db_pass = "ty6ija59lc028qqe"
        db_host = "vkh7buea61avxg07.cbetxkdyhwsb.us-east-1.rds.amazonaws.com"
        db_port = 3306
        db_database = "lq32alymdi5j9q8v"

        conn = pymysql.connect(user=db_user, password=db_pass, host=db_host, database=db_database, port=db_port,
                               cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()

        cur.execute(f"SELECT * FROM {table_name} WHERE item_id = %s", (str(item_id)))
        myresult = cur.fetchall()
        if myresult:
            # for i in myresult:
            #     print(i)
            print('Row exists')
        else:
            cur.execute(
                f"INSERT INTO {table_name} (guest_id, guest_name, guest_firstname, guest_lastname) VALUES (%s,%s,%s,%s)",
                (item_id, item_name, item_description, item_price, item_stock_status, item_sku, item_link, item_image,
                 item_stock_quantity,))
            conn.commit()
            print(cur.rowcount, "record(s) affected")
            conn.close()

    def insert_user(fbid):
        # print(f' DB1 {fbid}')
        db_user = "gmw0tdz26q0z5457"
        db_pass = "ty6ija59lc028qqe"
        db_host = "vkh7buea61avxg07.cbetxkdyhwsb.us-east-1.rds.amazonaws.com"
        db_port = 3306
        db_database = "lq32alymdi5j9q8v"
        conn = pymysql.connect(user=db_user, password=db_pass, host=db_host, database=db_database, port=db_port,
                               cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute("SELECT * FROM karenka WHERE fbid = %s", (str(fbid)))
        myresult = cur.fetchall()
        if myresult:
            # print('User exists')
            conn.close()
        else:
            cur.execute("INSERT INTO karenka (fbid) VALUES (%s)", (str(fbid)))
            conn.commit()
            # print(cur.rowcount, "record(s) affected")
            conn.close()
            return "Success"

    def convertToBinaryData(item_image):
        image_url = item_image
        response = urllib.request.urlopen(image_url)
        image = response.read()
        with open("image.png", "wb") as file:
            file.write(image)
        with open('image.png', "rb") as file:
            binaryData = file.read()
        os.remove('image.png')
        return binaryData

    def write_file(data, filename):
        with open(filename, 'wb') as file:
            file.write(data)

    def convert_to_image():
        cur.execute("SELECT item_name, item_image from test2")
        myresult = cur.fetchall()
        for data in myresult:
            item_name = data.get('item_name')
            im = data.get('item_image')
            filename = f'{item_name}.png'
            write_file(im, filename)

    def convert_to_blob():
        for i in [0, 1, 2, 3]:
            i = str(i)
            item_name = 'name' + i
            item_description = 'description' + i
            item_price = 'price' + i
            i = int(i)
            item_image = items[i]
            print(f'{item_name} + {item_description} + {item_price} + {item_image}')
            print(db_host)
            empPicture = write_file(item_image)
            cur.execute("INSERT INTO test2 (item_name, item_description, item_price, item_image) VALUES (%s,%s,%s,%s)",
                        (item_name, item_description, item_price, empPicture,))
            conn.commit()

    def create_table_product(self, table_name):
        cur = self.conn.cursor()
        try:
            cur.execute(f"CREATE TABLE {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, "
                        f"id VARCHAR(255), "
                        f"name VARCHAR(255),"
                        f"slug VARCHAR(255), "
                        f"permalink VARCHAR(255),"
                        f"type VARCHAR(255),"
                        f"status VARCHAR(255),"
                        f"catalog_visibility VARCHAR(255),"
                        f"description VARCHAR(255),"
                        f"short_description VARCHAR(255),"
                        f"sku VARCHAR(255),"
                        f"regular_price VARCHAR(255),"
                        f"sale_price VARCHAR(255),"
                        f"tax_status VARCHAR(255),"
                        f"manage_stock VARCHAR(255),"
                        f"stock_quantity VARCHAR(255),"
                        f"shipping_required VARCHAR(255),"
                        f"shipping_taxable VARCHAR(255),"
                        f"shipping_class VARCHAR(255),"
                        f"shipping_class_id VARCHAR(255),"
                        f"categories VARCHAR(255),"
                        f"tags VARCHAR(255),"
                        f"images VARCHAR(255),"
                        f"attributes VARCHAR(255),"
                        f"stock_status VARCHAR(255)))")
            result = cur.fetchall()
        except Exception as error:
            return error
        else:
            return result
        finally:
            self.conn.close()

    def create_table_test(self):
        try:
            connection = pymysql.connect(user=REG_USER, password=REG_PASS, host=REG_IP, database=REG_DB, port=REG_PORT,
                                         cursorclass=pymysql.cursors.DictCursor)
            cursor = connection.cursor()
            cursor.execute(f"CREATE TABLE TEST2 (id INT AUTO_INCREMENT PRIMARY KEY, "
                           f"name VARCHAR(255), "
                           f"age VARCHAR(255))")
            result = cursor.fetchall()
            connection.close()
            return result
        except Exception as error:
            return error


    # create_table_product(config.SQL_TABLE_PRODUCTS)
    #
    # x1 = create_table()
    # x2 = delete_allfrom_table()
    # x3 = select_products(0, 100, 'instock')
    # x4 = max()
    # x5 = count()
    # x6 = last()
    # x7 = insert_products()
    # x8 = insert_user()
    #
    # table_name = 'simple2'
    # create_table_product_simple(table_name)


# db1 = MODULE_MYSQL()
# r = db1.create_table_test()
# print(r)
# print(db1.create_table_test2())

# wcapi1 = WOO_API()
#
# print(db1.max_element())
#
# print(db1.create_table_fb())
#
# all_products = wcapi1.get_all_products()
# for i in all_products:
#     all_products_list2 = []
#     name = str(i.get('name'))
#     all_products_list2.append(name)
#     woo_id = str(i.get('id'))
#     all_products_list2.append(woo_id)
#     price = str(i.get('regular_price'))
#     all_products_list2.append(price)
#     url = str(i.get('permalink'))
#     all_products_list2.append(url)
#     image2 = i['images'][0]
#     image = str(image2.get('src'))
#     all_products_list2.append(image)
#     stock_status = str(i.get('stock_status'))
#     all_products_list2.append(stock_status)
#     db1.insert_table_fb(all_products_list2)
#
#
# all_products = db1.select_table_fb()
# k = 0
# for i in all_products:
#     k = k + 1
#     print(i)
# print(k)
#
# list_len = len(all_products)
# print(f'list_len {list_len }')
# list = []
# counter = 0
# for index, item in enumerate(all_products):
#     print(index, item)
#     list.append(item)
#     list_len = list_len - 1
#     counter = counter + 1
#     if list_len == 0:
#
#         print('All!')
#         counter = 0
#         list = []
#         break
#     if counter == 5:
#
#         print(f'counter is 5!')
#         counter = 0
#         list = []




