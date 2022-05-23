from datetime import datetime
from distutils.log import debug
from sqlite3 import IntegrityError
from nfc_module import nfc_module
from database import database
from cryptolib import cryptolib

class command:
    def __init__(self, dbname) -> None:
        self.dbname = dbname
        self.nfc_controller = nfc_module()

    def start(self):
        switcher = {"1": self.purchase, "2": self.register, "3": self.show, "99": self.debug}
        command = input("Command Select[1: Purchase, 2: Register, 3: Show]: ")

        if command in list(switcher.keys()):
            switcher.get(command)()

    def purchase(self):
        database_controller = database(self.dbname)

        self.nfc_controller.connection()
        discover_tag = self.nfc_controller.discover_tag

        find_cur = database_controller.db_execute('SELECT * FROM users WHERE tag = ?', discover_tag.idm)
        find_tag = find_cur.fetchone()
        if find_tag:
            print("Student name: ", find_tag[3])
            print("Student number: ", find_tag[2])
            print("Usage Amount: ", find_tag[4])
            food_ids = []
            raw_foods = database_controller.db_execute('SELECT * FROM foods')
            foods = raw_foods.fetchall()
            print("id, name, price")
            for food in foods:
                food_ids.append(str(food[0]))
                print(food)
            select = input("Select food id: ")
            if select in food_ids:
                select_food = foods[int(select)-1]
                price = select_food[2]
                try:
                    now_time = int(datetime.now().timestamp())
                    database_controller.db_execute('INSERT INTO history(user_id, food_id, datetime) values(?, ?, ?)', int(find_tag[0]), int(select), now_time)
                    database_controller.db_execute('UPDATE users SET usage_amount = usage_amount + ? WHERE tag = ?', price, discover_tag.idm)
                    database_controller.db_commit()
                except Exception as e:
                    print(e)
                else:
                    print("Purchase has been completed")
            else:
                print("Processing did not complete")
        else:
            print("This tag is not already registered")

    def register(self):
        def register_id_card():
            database_controller = database(self.dbname)

            self.nfc_controller.connection()
            discover_tag = self.nfc_controller.discover_tag
            exist_check = database_controller.db_execute('SELECT * FROM users WHERE tag = ?', discover_tag.idm)
            if exist_check.fetchone():
                print("Already register")
                return
            student_info = self.nfc_controller.student_info(discover_tag)
            if student_info is None:
                return
            student_number, student_name = student_info.values()
            salt = cryptolib.salt_generate()
            crypt = cryptolib(salt)
            password = crypt.enter_password()
            try:
                database_controller.db_execute('INSERT INTO users(tag, student_number, student_name, usage_amount, password, salt) values(?, ?, ?, 0, ?, ?)', discover_tag.idm, student_number, student_name, password, salt)
                database_controller.db_commit()
            except Exception as e:
                print(e)
            else:
                print("Registration has benn completed")

        def register_food():
            database_controller = database(self.dbname)

            food_name = input("Food name is ")
            if not food_name:
                print("Processing did not complete")
                return
            food_price = input("Food price is ")

            try:
                food_price = int(food_price)
            except ValueError:
                print("Price is not numeric")
                print("Processing did not complete")
            else:
                try:
                    database_controller.db_execute('INSERT INTO foods(name, price) values(?, ?)', food_name, food_price)
                    database_controller.db_commit()
                except IntegrityError:
                    print("This name is duplicate name")
                else:
                    print("Registration has been completed")

        switcher = {"1": register_id_card, "2": register_food}
        command = input("Command Select[1: users, 2: foods]: ")
        if command in list(switcher.keys()):
            switcher.get(command)()

    def show(self):
        def show_users():
            self.reload_usage_amount()
            database_controller = database(self.dbname)
            find_users = database_controller.db_execute('SELECT id, student_number, student_name, usage_amount FROM users')
            print("id, student_number, student_name, usage_amount")
            for row in find_users:
                print(row)

        def show_foods():
            database_controller = database(self.dbname)
            find_foods = database_controller.db_execute('SELECT * FROM foods')
            print("id, food_name, food_price")
            for row in find_foods:
                print(row)

        def show_history():
            database_controller = database(self.dbname)
            history = database_controller.db_execute('SELECT history.id, users.student_number, users.student_name, foods.name, history.datetime FROM history INNER JOIN users ON history.user_id = users.id INNER JOIN foods ON history.food_id = foods.id')
            print("id, student_number, student_name, food_name, purchase_datetime")
            for row in history:
                list_history = list(row)
                list_history[4] = datetime.fromtimestamp(list_history[4]).strftime('%Y/%m/%d %H:%M:%S')
                print(list_history)

        switcher = {"1": show_users, "2": show_foods, "3": show_history}
        command = input("Command Select[1: users, 2: foods, 3: purchase_history]: ")
        if command in list(switcher.keys()):
            switcher.get(command)()

    def debug(self):
        def delete_history(student_number):
            database_controller = database(self.dbname)
            raw_history = database_controller.db_execute('SELECT history.id, users.student_number, users.student_name, foods.name, history.datetime FROM history INNER JOIN users ON history.user_id = users.id INNER JOIN foods ON history.food_id = foods.id')
            history = raw_history.fetchall()
            history_ids = []
            print("id, student_number, student_name, food_name, purchase_datetime")
            for row in history:
                history_ids.append(str(row[0]))
                list_history = list(row)
                list_history[4] = datetime.fromtimestamp(list_history[4]).strftime('%Y/%m/%d %H:%M:%S')
                print(list_history)
            select = input("Select history id: ")
            if select in history_ids:
                select_history = [x for x in history if x[0] == int(select)][0]
                print(select_history)
                if select_history[1] == student_number:
                    print("Not Available(retry other user)")
                else:
                    command = input("Command Select[1: Delete]: ")
                    if command == "1":
                        try:
                            database_controller.db_execute('DELETE FROM history WHERE id = ?', int(select))
                            database_controller.db_commit()
                        except Exception as e:
                            print(e)
                        else:
                            print("The following history has been deleted by", student_number)
                            print(select_history)
                    else:
                        print("Proccessing did not complete")
            else:
                print("Proccessing did not complete")
            self.reload_usage_amount()

        database_controller = database(self.dbname)
        self.nfc_controller.connection()
        discover_tag = self.nfc_controller.discover_tag
        exist_check = database_controller.db_execute('SELECT * FROM users WHERE tag = ?', discover_tag.idm)
        user = exist_check.fetchone()
        if not user:
            print("This operation is not available")
        else:
            student_number = user[2]
            salt = user[6]
            stretching_password = user[5]
            crypt = cryptolib(salt)
            if crypt.correct_check(stretching_password):
                print("delete operate")
                delete_history(student_number)
            else:
                print("Incorrect password")
                self.reload_usage_amount()

    def reload_usage_amount(self):
        database_controller = database(self.dbname)
        raw_history = database_controller.db_execute('SELECT history.id, users.student_number, users.student_name, foods.price, history.datetime FROM history INNER JOIN users ON history.user_id = users.id INNER JOIN foods ON history.food_id = foods.id')
        history = raw_history.fetchall()
        raw_users = database_controller.db_execute('SELECT student_number FROM users')
        users = raw_users.fetchall()
        student_list = []
        for u in users:
            student_list.append(u[0])
        usage_amount_list = [{"usage_amount": 0, "student_number": student_number} for student_number in student_list ]
        for row in history:
            if row[1] in student_list:
                target = list(filter(lambda item: item['student_number'] == row[1], usage_amount_list))[0]
                target['usage_amount'] += row[3]
        update_list = list(map(lambda x: tuple(x.values()), usage_amount_list))
        try:
            database_controller.db_execute_many('UPDATE users SET usage_amount = ? WHERE student_number = ?', update_list)
            database_controller.db_commit()
        except Exception as e:
            print(e)
