import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QFrame, QMessageBox, QFormLayout
from PyQt5.QtWidgets import QScrollArea, QGridLayout, QTableView, QVBoxLayout, QHBoxLayout, QComboBox, QHeaderView, QSizePolicy
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt5.QtGui import QPainter, QIcon
from PyQt5.QtGui import QPixmap, QFont, QColor, QPainter, QBrush, QImage, QPalette, QLinearGradient


from PyQt5.QtGui import QFont
import psycopg2
import traceback







class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main")
        self.setGeometry(500, 200, 1000, 700)
        self.label = QLabel("Введите ваш логин и пароль", self)
        self.label.move(250, 175)
        self.label.resize(1000, 100)
        self.label.setFont(QFont("Timew New Roman", 25))

        self.write_login = QLineEdit(self)
        self.write_login.resize(400, 40)
        self.write_login.move(300, 300)

        self.write_password = QLineEdit(self)
        self.write_password.resize(400, 40)
        self.write_password.move(300, 350)
        self.write_password.setEchoMode(2)

        self.error_label = QLabel(self)
        self.error_label.move(300, 450)
        self.error_label.resize(400, 40)
        self.error_label.setStyleSheet("color: red; font-size: 14px;")
        self.error_label.hide()

        self.button = QPushButton("Войти", self)
        self.button.move(600, 400)
        self.button.resize(100, 40)
        self.button.clicked.connect(self.start_action)

        self.button.setDefault(True)
        self.button.setAutoDefault(True)

        self.button2 = QPushButton("Создать", self)
        self.button2.move(300, 400)
        self.button2.resize(100, 40)
        self.button2.clicked.connect(self.create_role)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.start_action()
        else:
            super().keyPressEvent(event)


    def start_action(self):
        self.log = self.write_login.text().strip()
        self.pas = self.write_password.text()

        self.error_label.hide()

        try:
            self.con = psycopg2.connect(
                dbname="Tickets",
                user=self.log,
                password=self.pas,
                host="localhost",
                port="5432"
            )
            self.cur = self.con.cursor()
            self.cur.execute("""
                            SELECT rolname FROM pg_roles 
                            WHERE pg_has_role(current_user, oid, 'member') 
                            OR rolname = current_user;
                            """)
            role = self.cur.fetchall()[0][0]
            print(role)
            if role == "customer":
                self.customer_layout = CustomerWindow(self.con, self.cur, self.log)
                self.customer_layout.show()
                self.hide()
            elif role == "admin" or role == "pg_database_owner":
                self.admin_layout = AdminWindow(self.cur)
                self.admin_layout.show()
                self.hide()
            elif role == "director":
                self.director_layout = DirectorWindow(self.cur)
                self.director_layout.show()
                self.hide()

        except psycopg2.OperationalError  as e:
            self.show_error(f"Ошибка входа: неправильный логин или пароль")
        except Exception as e:
            self.show_error(f"Неизвестная ошибка: {str(e)}")
            traceback.print_exc()

    def create_role(self):
        self.created = CreatedRole()
        self.created.show()



    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()
        self.error_label.setStyleSheet("""
            color: red; 
            font-size: 14px;
            background-color: #FFEBEE;
            padding: 5px;
            border-radius: 5px;
        """)
        QTimer.singleShot(3000, lambda: self.error_label.setStyleSheet("color: red; font-size: 14px;"))


class CreatedRole(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create")
        self.setGeometry(500, 200, 1000, 700)

        self.label = QLabel("Введите данные для регистрации", self)
        self.label.move(250, 100)
        self.label.resize(1000, 100)
        self.label.setFont(QFont("Timew New Roman", 25))

        self.write_login = QLineEdit(self)
        self.write_login.setPlaceholderText("login")
        self.write_login.resize(400, 40)
        self.write_login.move(300, 200)

        self.write_password = QLineEdit(self)
        self.write_password.setPlaceholderText("password")
        self.write_password.resize(400, 40)
        self.write_password.move(300, 250)
        self.write_password.setEchoMode(2)

        self.write_email = QLineEdit(self)
        self.write_email.setPlaceholderText("email     (......@example.com)")
        self.write_email.resize(400, 40)
        self.write_email.move(300, 300)

        self.write_phone = QLineEdit(self)
        self.write_phone.setPlaceholderText("phone")
        self.write_phone.resize(400, 40)
        self.write_phone.move(300, 350)

        self.checkrole = QComboBox(self)
        self.checkrole.resize(400, 40)
        self.checkrole.move(300, 400)
        self.checkrole.addItems(["Customer", "Director", "Admin"])

        self.button = QPushButton("Создать", self)
        self.button.move(600, 450)
        self.button.resize(100, 40)
        self.button.clicked.connect(self.start_action)

        self.error_label = QLabel(self)
        self.error_label.move(300, 450)
        self.error_label.resize(290, 40)
        self.error_label.setStyleSheet("color: red; font-size: 14px;")
        self.error_label.hide()

    def start_action(self):
        try:
            con = psycopg2.connect(
                dbname="Tickets",
                user="kali",
                password="kalikali",
                host="localhost",
                port="5432"
            )
            self.cur = con.cursor()
            print(type(self.write_login.text()))
            if self.write_login.text().strip() and self.write_password.text():
                if self.checkrole.currentText() == "Customer":
                    login = self.write_login.text().strip()
                    password = self.write_password.text()
                    email = self.write_email.text().strip()
                    phone = self.write_phone.text().strip()

                    first_name, *last_name = login.split(" ")
                    last_name = " ".join(last_name) if last_name else ""

                    self.cur.execute(
                        """CALL public.create_role_with_sync_proc(
                            %s, %s, TRUE, %s, %s, %s, %s
                        )""",
                        (login, password, first_name, last_name, email, phone)
                    )
                    print("customer")

                else:
                    username = self.write_login.text().strip()
                    password = self.write_password.text()
                    role_type = self.checkrole.currentText()

                    print(f"Пытаемся создать роль: {username}, пароль: {password}, тип: {role_type}")
                    self.cur.execute(f"CREATE ROLE \"{username}\" WITH LOGIN PASSWORD '{password}' IN ROLE {role_type}")
                    #role = self.cur.fetchall()[0][0]
                    #print(role)
            else:
                self.show_error("Ошибка создания пользователя")

            con.commit()

        except Exception as e:
            print("Неизвестная ошибка")
            traceback.print_exc()


    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()
        self.error_label.setStyleSheet("""
            color: red; 
            font-size: 14px;
            background-color: #FFEBEE;
            padding: 5px;
            border-radius: 5px;
        """)
        QTimer.singleShot(3000, lambda: self.error_label.setStyleSheet("color: red; font-size: 14px;"))


class CustomerWindow(QWidget):
    def __init__(self, con, cur, log):
        super().__init__()
        self.setWindowTitle("Customer")
        self.setGeometry(500, 200, 1000, 700)
        self.con = con
        self.cur = cur
        self.log = log
        self.current_sort = "date"  # Текущий тип сортировки
        self.current_month = None  # Текущий выбранный месяц

        # Получаем ID пользователя
        try:
            name, surname = self.log.split(" ")[0], self.log.split(" ")[1]
            self.cur.execute(f"SELECT iduser FROM Users WHERE surname='{surname}' AND firstname='{name}';")
            self.id = self.cur.fetchall()[0][0]
        except Exception as e:
            print(f"Ошибка при получении ID пользователя: {e}")
            self.id = None

        self.setup_ui()
        self.load_events()

    def setup_ui(self):
        # Главный макет
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Верхняя панель с кнопками и поиском
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        top_layout.setSpacing(10)

        # Кнопки навигации
        self.search_btn = QPushButton("Поиск", self)
        self.search_btn.clicked.connect(self.show_search)
        self.search_btn.setFixedSize(100, 40)
        self.myorder_btn = QPushButton("Мои заказы", self)
        self.myorder_btn.clicked.connect(self.show_orders)
        self.myorder_btn.setFixedSize(100, 40)
        self.sort_btn = QPushButton("Сортировать", self)
        self.sort_btn.clicked.connect(self.show_sort_options)
        self.sort_btn.setFixedSize(100, 40)

        # Поле поиска (изначально скрыто)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название мероприятия...")
        self.search_input.setVisible(False)
        self.search_input.setFixedSize(200, 40)
        self.search_input.returnPressed.connect(self.apply_search)

        # Выпадающий список для сортировки (скрыт)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По дате", "По названию", "По популярности", "По цене"])
        self.sort_combo.setVisible(False)
        self.sort_combo.setFixedSize(100, 40)
        self.sort_combo.currentIndexChanged.connect(self.apply_sort)

        # Выпадающий список для фильтрации по месяцам
        self.month_combo = QComboBox()
        self.month_combo.addItems(["Все месяцы", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                                   "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"])
        self.month_combo.setVisible(False)
        self.month_combo.setFixedSize(100, 40)
        self.month_combo.currentIndexChanged.connect(self.apply_month_filter)

        # Добавляем элементы на верхнюю панель
        top_layout.addWidget(self.search_btn)
        top_layout.addWidget(self.myorder_btn)
        top_layout.addWidget(self.sort_btn)
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(QLabel("Сортировка:"))
        top_layout.addWidget(self.sort_combo)
        top_layout.addWidget(QLabel("Месяц:"))
        top_layout.addWidget(self.month_combo)
        top_layout.addStretch()

        main_layout.addWidget(top_panel)

        # Scroll area для мероприятий
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.events_container = QWidget()
        self.grid_layout = QGridLayout(self.events_container)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.events_container)
        main_layout.addWidget(self.scroll_area)

    def load_events(self, search_text=None, sort_by="date", month=None):
        """Загрузка мероприятий с возможностью поиска и сортировки"""
        # Очищаем предыдущие кнопки
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        self.buttons = []
        self.nameevents = []

        # Формируем SQL запрос с учетом параметров
        query = "SELECT idevent, eventname, date FROM Events WHERE 1=1"
        params = []

        # Поиск по названию
        if search_text:
            query += " AND eventname ILIKE %s"
            params.append(f"%{search_text}%")

        # Фильтрация по месяцу
        if month and month > 0:
            query += " AND EXTRACT(MONTH FROM date) = %s"
            params.append(month)

        # Сортировка
        if sort_by == "date":
            query += " ORDER BY date"
        elif sort_by == "name":
            query += " ORDER BY eventname"
        elif sort_by == "popularity":
            # query += " ORDER BY (SELECT COUNT(*) FROM Tickets WHERE eventId = Events.idevent) DESC"
            guery = "select * from events_by_ticket_count_view;"
        elif sort_by == "price":
            # query += " ORDER BY (SELECT MIN(price) FROM Tickets WHERE eventId = Events.idevent)"
            guery = "SELECT * FROM get_events_sorted_by_price;"

        try:
            self.cur.execute(query, params)
            events = self.cur.fetchall()


            for index, (event_id, event_name, event_date) in enumerate(events):
                btn = QPushButton()
                btn.setFixedSize(220, 170)
                btn.setStyleSheet("""
                    QPushButton {
                        border: 1px solid #ccc;
                        border-radius: 5px;
                        background: #f0f0f0;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background: #e0e0e0;
                    }
                """)

                # Добавляем информацию о мероприятии на кнопку
                btn.clicked.connect(self.go_to_info)
                btn.setProperty('event_id', event_id)
                btn.setProperty('event_name', event_name)
                btn.setStyleSheet(f"background-image : url(image_events/{event_id}.png);")


                self.nameevents.append(event_name)

                row = index // 4
                col = index % 4
                self.grid_layout.addWidget(btn, row, col)
                self.buttons.append(btn)

        except Exception as e:
            print(f"Ошибка при загрузке мероприятий: {e}")

    def show_search(self):
        """Показать/скрыть поле поиска"""
        if self.search_input.isVisible():
            self.search_input.setVisible(False)
            self.search_input.clear()
            self.load_events()  # Перезагружаем без фильтра
        else:
            self.search_input.setVisible(True)
            self.search_input.setFocus()
            self.sort_combo.setVisible(False)
            self.month_combo.setVisible(False)

    def apply_search(self):
        """Применить поиск по введенному тексту"""
        search_text = self.search_input.text()
        self.load_events(search_text=search_text, sort_by=self.current_sort, month=self.current_month)

    def show_sort_options(self):
        """Показать/скрыть варианты сортировки"""
        if self.sort_combo.isVisible():
            self.sort_combo.setVisible(False)
            self.month_combo.setVisible(False)
        else:
            self.sort_combo.setVisible(True)
            self.month_combo.setVisible(True)
            self.search_input.setVisible(False)

    def apply_sort(self, index):
        """Применить выбранную сортировку"""
        sort_options = ["date", "name", "popularity", "price"]
        self.current_sort = sort_options[index]
        self.load_events(search_text=self.search_input.text(),
                         sort_by=self.current_sort,
                         month=self.current_month)

    def apply_month_filter(self, index):
        """Применить фильтрацию по месяцам"""
        self.current_month = index if index > 0 else None
        self.load_events(search_text=self.search_input.text(),
                         sort_by=self.current_sort,
                         month=self.current_month)

    def show_orders(self):
        if self.id:
            self.orders_window = CheckOrder(self.cur, self.id)
            self.orders_window.show()
        else:
            print("Не удалось определить ID пользователя")

    def go_to_info(self):
        sender = self.sender()
        if sender:
            event_id = sender.property('event_id')
            event_name = sender.property('event_name')
            self.inform = InfoWidget(self.id, str(event_id), self.con, self.cur, event_name)
            self.inform.show()


class CheckOrder(QWidget):
    def __init__(self, cur, id):
        super().__init__()
        self.setWindowTitle("My orders")
        self.setGeometry(700, 300, 700, 400)
        self.cur = cur
        self.id = id
        self.selected_order_id = None

        table_font = QFont()
        table_font.setPointSize(15)

        self.setStyleSheet("""
            QWidget {
                font-family: Arial;
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QTableView {
                background-color: white;
                border: 1px solid #ddd;
                selection-background-color: #e0f7fa;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)

        main_layout = QVBoxLayout(self)


        title_label = QLabel("История ваших заказов")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.setFixedWidth(120)
        self.refresh_button.clicked.connect(self.start_table)

        self.buy_button = QPushButton("Новая покупка")
        self.buy_button.setFixedWidth(150)
        self.buy_button.clicked.connect(self.go_to_add_card)

        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        button_layout.addWidget(self.buy_button)
        main_layout.addLayout(button_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.table_container = QWidget()
        self.table_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.table_view = QTableView()
        self.table_view.setStyleSheet("font-size: 14px;")
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setAlternatingRowColors(True)

        container_layout = QVBoxLayout(self.table_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.table_view)

        self.scroll_area.setWidget(self.table_container)
        main_layout.addWidget(self.scroll_area)

        # Инициализируем пустую модель
        self.model = QStandardItemModel()
        self.table_view.setModel(self.model)

        # Теперь можно подключить сигнал
        self.table_view.selectionModel().selectionChanged.connect(self.on_row_selected)

        self.start_table()

    def start_table(self):
        try:
            self.cur.execute(f'SELECT e.eventname, p.status, o.idorder, o.summ '
                             f'FROM "orders" as o '
                             f'JOIN payment p ON o.idorder = p.orderId '
                             f'JOIN detalization d ON o.idorder = d.orderid '
                             f'JOIN tickets t ON d.ticketid = t.idticket '
                             f'JOIN events e ON t.eventId = e.Idevent '
                             f'WHERE o.userid = {self.id};')
            data = self.cur.fetchall()

            columns = [desc[0] for desc in self.cur.description]

            self.model.clear()
            self.model.setHorizontalHeaderLabels(columns)

            for row_num, row_data in enumerate(data):
                row_items = []
                for col_num, value in enumerate(row_data):
                    item = QStandardItem(str(value))

                    if col_num == 1:  # Столбец статуса
                        if "Completed" in str(value):
                            item.setBackground(QColor(200, 255, 200))
                        elif "In process" in str(value):
                            item.setBackground(QColor(255, 255, 200))
                        elif "Cancelled" in str(value):
                            item.setBackground(QColor(255, 200, 200))

                    row_items.append(item)
                self.model.appendRow(row_items)

            self.table_view.resizeColumnsToContents()

        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {str(e)}")

    def on_row_selected(self, selected):
        if selected.indexes():
            row = selected.indexes()[0].row()
            self.selected_order_id = self.model.index(row, 2).data()  # 2 - индекс столбца с ID заказа

    def go_to_add_card(self):
        if not self.selected_order_id:
            QMessageBox.warning(self, "Предупреждение", "Пожалуйста, выберите заказ из таблицы")
            return

        # Передаем order_id в AddCard
        self.buy = AddCard(self.cur, self.id, self.selected_order_id)
        self.buy.show()




class AddCard(QWidget):
    def __init__(self, cur, id, order_id):
        super().__init__()
        self.cur = cur
        self.order_id = order_id

        # self.cur.execute(f"Select orderid, summ, status From payment where orderid = {order_id}")
        self.cur.execute(f"""SELECT * FROM all_payments_view WHERE orderid = {order_id};""")
        answer = self.cur.fetchall()
        self.order_id = answer[0][0]
        self.summ = answer[0][1]
        self.status = answer[0][2]



        self.setWindowTitle("Добавление карты")
        self.setGeometry(600, 200, 500, 400)

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)

        # Заголовок
        title = QLabel("Добавление платежной карты")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        main_layout.addWidget(title)

        # Информация о заказе
        info_frame = QWidget()
        info_layout = QVBoxLayout(info_frame)

        order_label = QLabel(f"Номер заказа: {self.order_id}")
        amount_label = QLabel(f"Сумма к оплате: {self.summ} руб.")
        status_label = QLabel(f"Статус платежа: {self.status}")

        for label in [order_label, amount_label, status_label]:
            label.setFont(QFont("Arial", 14))
            info_layout.addWidget(label)

        main_layout.addWidget(info_frame)

        # Форма для ввода карты
        form_frame = QWidget()
        form_layout = QFormLayout(form_frame)

        self.card_number = QLineEdit()
        self.card_number.setPlaceholderText("XXXX XXXX XXXX XXXX")
        self.card_number.setMaxLength(19)  # 16 цифр + 3 пробела


        form_layout.addRow("Номер карты:", self.card_number)


        main_layout.addWidget(form_frame)

        # Кнопки
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(15)

        self.add_btn = QPushButton("Добавить карту")
        self.add_btn.setFixedHeight(40)
        self.add_btn.clicked.connect(self.add_card)

        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.clicked.connect(self.close)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        # Стилизация
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: Arial;
            }
            QLabel {
                color: #333;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            #cancel_btn {
                background-color: #f44336;
            }
            #cancel_btn:hover {
                background-color: #d32f2f;
            }
        """)

    def add_card(self):
        card_number = self.card_number.text().replace(" ", "")

        # Простая валидация
        if not all([card_number]):
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены")
            return

        if len(card_number) != 16 or not card_number.isdigit():
            QMessageBox.warning(self, "Ошибка", "Некорректный номер карты")
            return

        try:
            # Обновляем платеж в базе данных
            self.cur.execute(f"""
                UPDATE payment
                SET card = '{card_number}', status = 'In process' 
                WHERE orderId = {self.order_id}
                RETURNING Idpayment;""")

            result = self.cur.fetchone()
            if result:
                self.cur.connection.commit()
                QMessageBox.information(self, "Успех", "Карта успешно добавлена!\nПлатеж обрабатывается")
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось обновить платеж")

        except Exception as e:
            self.cur.connection.rollback()
            print("Ошибка", f"Произошла ошибка: {str(e)}")



class InfoWidget(QWidget):
    def __init__(self, id, index, con, cur, event_name):
        super().__init__()
        self.setWindowTitle("Zal")
        self.setGeometry(500, 200, 1000, 700)
        self.id = id
        self.index = int(index)
        self.con = con
        self.cur = cur
        self.event_name = event_name
        self.buttons = []

        self.scrollarea = QScrollArea(self)
        self.scrollarea.setWidgetResizable(True)

        self.button = QPushButton("Оформить заказ", self)
        self.button.setFixedSize(200, 40)
        self.button.clicked.connect(self.finish_buy)

        self.w = QWidget()
        self.grid_layout = QGridLayout(self.w)
        self.grid_layout.setSpacing(5)
        self.w.setStyleSheet("background-color: #d3d3d3;")

        self.scrollarea.setWidget(self.w)

        self.w.setLayout(self.grid_layout)
        self.scrollarea.setWidget(self.w)



        label_font = QFont()
        label_font.setPointSize(20)
        self.title = QLabel(event_name, self)
        self.title.setFont(label_font)
        self.title.setFixedSize(600, 50)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.scrollarea)


        self.load_seats()

        self.title2 = QLabel(self)
        self.title2.setFont(label_font)
        self.main_layout.addWidget(self.title2)
        self.main_layout.addWidget(self.button)
        self.title.setFixedSize(1000, 50)

        self.checkbtnforbuy = []

    def load_seats(self):
        try:
            self.cur.execute(f"""SELECT place, price FROM tickets_by_event_view WHERE eventid = {self.index+1};""")

            seats = self.cur.fetchall()
            print(seats)

            btn_font = QFont()
            btn_font.setPointSize(8)

            row_colors = [
                "#FFCDD2",  # светло-красный (самый дорогой)
                "#F8BBD0",  # светло-розовый
                "#E1BEE7",  # светло-фиолетовый
                "#C5CAE9",  # светло-индиго
                "#BBDEFB",  # светло-голубой
                "#B2DFDB",  # светло-бирюзовый
                "#DCEDC8"  # светло-зеленый (самый дешевый)
            ]

            max_rows = 7


            for place, price in seats:
                row = ''.join([c for c in place if not c.isdigit()])
                seat_num = ''.join([c for c in place if c.isdigit()])

                try:
                    # Преобразуем букву ряда в число (A->0, B->1 и т.д.)
                    row = ord(row.upper()) - ord('A')
                    col = int(seat_num) - 1  # Нумерация с 0

                    color_index = min(row, max_rows - 1)
                    row_color = row_colors[color_index]
                except (ValueError, TypeError):
                    continue  # Пропускаем некорректные места


                btn = QPushButton(place)
                btn.setFixedSize(42, 40)
                btn.setProperty('place', place)
                btn.setProperty('price', price)
                btn.setFont(btn_font)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {row_color};  
                        border: none;            
                        background-image: url(seat.png);
                        background-repeat: no-repeat;
                        background-position: center;
                        padding: 0px;
                        margin: 0px;

                    }}
                    QPushButton:hover {{
                        opacity: 0.8;
                    }}
                    QPushButton:pressed {{
                        opacity: 0.6;
                    }}
                        """)
                btn.clicked.connect(self.go_to_info)

                self.grid_layout.addWidget(btn, row, col)
                self.buttons.append(btn)

            self.w.setLayout(self.grid_layout)


        except Exception as e:
            print(f"Ошибка при загрузке событий: {e}")

    def go_to_info(self):
        sender = self.sender()
        place = sender.property('place')
        price = sender.property('price')

        if [place, price] not in self.checkbtnforbuy:
            self.checkbtnforbuy.append([place, price])
            self.title2.setText(f"Выбраны места: {[i[0] for i in self.checkbtnforbuy]}")

    def finish_buy(self):
        self.byuticket = BuyTicket(self.id, self.index, self.con, self.cur, self.event_name, self.checkbtnforbuy)
        self.byuticket.show()


class BuyTicket(QWidget):
    def __init__(self, id, index, con, cur, event_name, placeAndPrice):
        super().__init__()
        self.setWindowTitle("Оформление билета")
        self.setGeometry(700, 250, 800, 600)
        self.setMinimumSize(600, 400)

        # Основные данные
        self.eventid = int(index)+1
        self.userid = id
        self.con = con
        self.cur = cur
        self.places = [item[0] for item in placeAndPrice]
        self.prices = [item[1] for item in placeAndPrice]
        self.total_price = sum(self.prices)

        # Главный layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 20, 30, 30)
        self.main_layout.setSpacing(25)

        # Заголовок
        self.title = QLabel(f"Оформление билета\n{event_name}")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """)
        self.main_layout.addWidget(self.title)

        # Информационный блок
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        info_layout = QVBoxLayout(info_frame)
        info_layout.setSpacing(15)

        # Места
        places_label = QLabel("Выбранные места:")
        places_label.setStyleSheet("font-size: 16px; color: #495057;")

        places_list = QLabel(", ".join(self.places))
        places_list.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 5px 0;
            }
        """)

        # Цена
        price_label = QLabel("Общая стоимость:")
        price_label.setStyleSheet("font-size: 16px; color: #495057;")

        price_value = QLabel(f"{self.total_price} руб.")
        price_value.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #27ae60;
                padding: 5px 0;
            }
        """)

        # Добавляем элементы в инфоблок
        info_layout.addWidget(places_label)
        info_layout.addWidget(places_list)
        info_layout.addSpacing(10)
        info_layout.addWidget(price_label)
        info_layout.addWidget(price_value)

        self.main_layout.addWidget(info_frame)

        # Кнопка оформления
        self.buy_button = QPushButton("Оформить заказ")
        self.buy_button.setFixedHeight(50)
        self.buy_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 18px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1a6ea0;
            }
        """)
        self.buy_button.clicked.connect(self.process_payment)

        self.main_layout.addWidget(self.buy_button)
        self.main_layout.addStretch()

        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                font-family: 'Arial';
            }
        """)

    def process_payment(self):
        self.cur.execute("""
                    SELECT idticket, place
                    FROM tickets 
                    WHERE place = ANY(%s) AND eventId = %s;
                """, (self.places, self.eventid))
        self.array_id_ticket = [i[0] for i in self.cur.fetchall()]
        #print([i[0] for i in self.array_id_ticket])
        self.cur.execute(f"SELECT create_order({self.userid}, ARRAY{self.array_id_ticket});")
        self.createorder = QLabel("Заказ создан!")
        self.createorder.setAlignment(Qt.AlignCenter)
        self.createorder.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #27ae60;
                padding: 10px;
            }
        """)
        self.main_layout.addWidget(self.createorder)
        self.con.commit()
        self.close()






class AdminWindow(QWidget):
    def __init__(self, cur):
        super().__init__()
        self.setWindowTitle("Admin")
        self.setGeometry(500, 200, 1000, 700)
        self.cur = cur

        main_layout = QVBoxLayout(self)
        control_layout = QHBoxLayout()
        self.selected_table = "detalization"

        button_font = QFont()
        button_font.setPointSize(12)

        self.checktable = QComboBox()
        self.checktable.setFixedSize(400, 40)
        self.checktable.setFont(button_font)
        control_layout.addWidget(self.checktable)


        self.load_tables()
        table_font = QFont()
        table_font.setPointSize(15)


        self.refresh_btn = QPushButton("Обновить список таблиц")
        self.refresh_btn.setFixedSize(250, 40)
        self.refresh_btn.clicked.connect(self.load_tables)
        self.refresh_btn.setFont(button_font)
        control_layout.addWidget(self.refresh_btn)

        self.loadtab = QPushButton("Загрузить таблицу")
        self.loadtab.setFixedSize(200, 40)
        self.loadtab.clicked.connect(self.start_table)
        self.loadtab.setFont(button_font)
        control_layout.addWidget(self.loadtab)

        main_layout.addLayout(control_layout)

        self.table_view = QTableView()
        self.table_view.setFont(table_font)
        main_layout.addWidget(self.table_view)

        self.start_table()

    def load_tables(self):
        try:
            self.cur.execute("""SELECT * FROM public_tables_list_view;""")
            tables = self.cur.fetchall()

            self.checktable.clear()
            for table in tables:
                self.checktable.addItem(table[0])

        except Exception as e:
            print(f"Ошибка при загрузке таблиц: {e}")

    def start_table(self):
        self.selected_table = self.checktable.currentText()
        if not self.selected_table:
            return
        try:
            self.cur.execute(f"SELECT * FROM {self.selected_table};")
            data = self.cur.fetchall()

            self.cur.execute(f"""
                       SELECT column_name
                       FROM information_schema.columns
                       WHERE table_name = '{self.selected_table}';
                   """)
            columns = [col[0] for col in self.cur.fetchall()]

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(columns)

            for row_num, row_data in enumerate(data):
                row_items = []
                for col_num, value in enumerate(row_data):
                    item = QStandardItem(str(value))
                    row_items.append(item)
                model.appendRow(row_items)

            self.table_view.setModel(model)
            self.table_view.resizeColumnsToContents()

        except Exception as e:
            print(f"Ошибка при загрузке данных таблицы: {e}")
            traceback.print_exc()


class DirectorWindow(QWidget):
    def __init__(self, cur):
        super().__init__()
        self.setWindowTitle("Director")
        self.setGeometry(500, 200, 1000, 700)
        self.cur = cur

        self.allinfo = QPushButton("Пoлная информация", self)
        self.allinfo.setGeometry(20, 20, 250, 40)
        self.allinfo.clicked.connect(self.view_all_tables)

        self.button1 = QPushButton("Мероприятия", self)
        self.button1.setGeometry(20, 80, 250, 40)
        self.button1.clicked.connect(self.event_action)

        self.button2 = QPushButton("Покупки", self)
        self.button2.setGeometry(20, 140, 250, 40)
        self.button2.clicked.connect(self.payment_action)

        self.button3 = QPushButton("Окупаемость", self)
        self.button3.setGeometry(20, 200, 250, 40)
        self.button3.clicked.connect(self.ocypaemost_action)

        self.button4 = QPushButton("Связь заказов и платежей", self)
        self.button4.setGeometry(20, 260, 250, 40)
        self.button4.clicked.connect(self.union_action)

    def event_action(self):
        self.go_to_evnt = EventForDirector(self.cur)
        self.go_to_evnt.show()

    def payment_action(self):
        self.go_to_payment = PaymentForDirector(self.cur)
        self.go_to_payment.show()

    def view_all_tables(self):
        self.go_to_allTables = AllTablesDirector(self.cur)
        self.go_to_allTables.show()

    def ocypaemost_action(self):
        self.ocypaemost = Ocypaemost(self.cur)
        self.ocypaemost.show()

    def union_action(self):
        self.union = Union(self.cur)
        self.union.show()




class EventForDirector(QWidget):
    def __init__(self, cur):
        super().__init__()
        self.setGeometry(800, 200, 700, 700)
        self.cur = cur

        label_font = QFont()
        label_font.setPointSize(12)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(0, 0, 700, 700)

        self.count_label = QLabel(self.scroll_area)
        self.count_label.setGeometry(20, 20, 700, 40)
        self.count_label.setFont(label_font)
        self.get_count()

        self.sort_on_month = QLabel("По месяцам: ", self.scroll_area)
        self.sort_on_month.setGeometry(20, 60, 700, 40)
        self.sort_on_month.setFont(label_font)

        self.chart_view = QChartView(self.scroll_area)
        self.chart_view.setGeometry(20, 120, 680, 400)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.load_data()

    def get_count(self):
        self.cur.execute("""SELECT * FROM events_count_view;""")
        self.count = self.cur.fetchall()[0][0]
        self.count_label.setText(f"Количство мероприяти: {self.count}")

    def load_data(self):
        try:
            self.cur.execute("""
                SELECT 
                    TO_CHAR(date, 'MM') AS month,
                    COUNT(*) AS events_count
                FROM events
                GROUP BY TO_CHAR(date, 'MM')
                ORDER BY month;
            """)

            data = self.cur.fetchall()

            if not data:
                print("Нет данных для отображения")
                return

            chart = QChart()
            chart.setAnimationOptions(QChart.SeriesAnimations)

            bar_set = QBarSet("Количество мероприятий")
            months = []

            for month, count in data:
                bar_set.append(count)
                months.append(month)

            series = QBarSeries()
            series.append(bar_set)
            chart.addSeries(series)

            axis_x = QBarCategoryAxis()
            axis_x.append(months)
            chart.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)

            axis_y = QValueAxis()
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)

            self.chart_view.setChart(chart)

        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")


class PaymentForDirector(QWidget):
    def __init__(self, cur):
        super().__init__()
        self.setGeometry(800, 200, 700, 700)
        self.cur = cur

        # Основной layout
        main_layout = QVBoxLayout(self)

        # Создаем scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Контейнер для содержимого scroll area
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        label_font = QFont()
        label_font.setPointSize(12)

        self.count_label = QLabel()
        self.count_label.setFont(label_font)
        self.scroll_layout.addWidget(self.count_label)
        self.get_count()

        self.sort_on_month = QLabel("Выберите мероприятие:")
        self.sort_on_month.setFont(label_font)
        self.scroll_layout.addWidget(self.sort_on_month)

        self.checkevents = QComboBox()
        self.checkevents.setFont(label_font)
        self.checkevents.setFixedSize(650, 40)
        self.scroll_layout.addWidget(self.checkevents)
        self.load_events()

        self.load_btn = QPushButton("Показать ")
        self.load_btn.setFont(label_font)
        self.load_btn.setFixedSize(650, 40)
        self.load_btn.clicked.connect(self.show_orders)
        self.scroll_layout.addWidget(self.load_btn)

        self.table_view = QTableView()
        self.scroll_layout.addWidget(self.table_view)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

    def get_count(self):
        self.cur.execute("SELECT COUNT(*) FROM payment;")
        self.count = self.cur.fetchall()[0][0]
        self.count_label.setText(f"Количество покупок: {self.count}")

    def load_events(self):
        try:
            self.cur.execute(" SELECT idevent, eventname FROM events ORDER BY idevent;")
            events = self.cur.fetchall()

            self.checkevents.clear()
            for event_id, event_name in events:
                self.checkevents.addItem(event_name, event_id)

        except Exception as e:
            print(f"Ошибка при загрузке мероприятий: {e}")

    def show_orders(self):
        event_name = self.checkevents.currentText()
        if not event_name:
            return

        try:
            self.cur.execute("""
                SELECT p.* FROM payment AS p
                INNER JOIN orders AS o ON o.idorder = p.orderid
                INNER JOIN detalization AS d ON d.orderid=o.idorder
                INNER JOIN tickets AS t ON t.idticket=d.ticketid
                INNER JOIN events AS e ON e.idevent = t.eventid
                WHERE e.eventname LIKE %s
            """, (event_name,))

            orders = self.cur.fetchall()

            column_names = [desc[0] for desc in self.cur.description]

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(column_names)

            for order in orders:
                row_items = []
                for value in order:
                    item = QStandardItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    row_items.append(item)
                model.appendRow(row_items)

            self.table_view.setModel(model)
            self.table_view.resizeColumnsToContents()

        except Exception as e:
            print(f"Ошибка при загрузке покупок: {e}")
            traceback.print_exc()


class AllTablesDirector(QWidget):
    def __init__(self, cur):
        super().__init__()
        self.setGeometry(800, 200, 1000, 700)
        self.cur = cur

        table_font = QFont()
        table_font.setPointSize(15)

        self.table_view = QTableView(self)
        self.table_view.setFont(table_font)
        self.table_view.setGeometry(20, 20, 960, 660)
        self.start_table()

    def start_table(self):
        try:
            self.cur.execute("""select * from user_orders_details_view;""")
            data = self.cur.fetchall()

            columns = [desc[0] for desc in self.cur.description]

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(columns)

            for row_num, row_data in enumerate(data):
                row_items = []
                for col_num, value in enumerate(row_data):
                    item = QStandardItem(str(value))
                    row_items.append(item)
                model.appendRow(row_items)

            self.table_view.setModel(model)
            self.table_view.resizeColumnsToContents()

        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            traceback.print_exc()


class Ocypaemost(QWidget):
    def __init__(self, cur):
        super().__init__()
        self.setGeometry(800, 200, 1000, 700)
        self.cur = cur

        table_font = QFont()
        table_font.setPointSize(15)

        self.table_view = QTableView(self)
        self.table_view.setFont(table_font)
        self.table_view.setGeometry(20, 20, 960, 660)
        self.start_table()


    def start_table(self):
        try:
            self.cur.execute("""    
            SELECT 
                e.IdEvent,
                e.EventName,
                e.Date,
                e.Place,
                e.Capacity,
                COUNT(t.IdTicket) AS SoldTickets,
                e.Capacity - COUNT(t.IdTicket) AS FreeSeats,
                CASE 
                    WHEN e.Capacity > 0 THEN ROUND((COUNT(t.IdTicket)::NUMERIC / e.Capacity * 100), 2)
                    ELSE 0 
                END AS OccupancyPercentage,
                CASE
                    WHEN COUNT(t.IdTicket)::NUMERIC / NULLIF(e.Capacity, 0) > 0.9 THEN 'High Occupancy (90%+)'
                    WHEN COUNT(t.IdTicket) = 0 THEN 'No Tickets Sold'
                    ELSE 'Normal Occupancy'
                END AS Status
            FROM 
                Events AS e
            LEFT JOIN 
                Tickets AS t ON e.IdEvent = t.EventId
            GROUP BY 
                e.IdEvent
            ORDER BY 
                CASE 
                    WHEN COUNT(t.IdTicket) = 0 THEN 0
                    ELSE (COUNT(t.IdTicket)::NUMERIC / NULLIF(e.Capacity, 0))
                END DESC;
                """)
            data = self.cur.fetchall()

            columns = [desc[0] for desc in self.cur.description]

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(columns)

            for row_num, row_data in enumerate(data):
                row_items = []
                for col_num, value in enumerate(row_data):
                    item = QStandardItem(str(value))
                    row_items.append(item)
                model.appendRow(row_items)

            self.table_view.setModel(model)
            self.table_view.resizeColumnsToContents()

        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            traceback.print_exc()


class Union(QWidget):
    def __init__(self, cur):
        super().__init__()
        self.setGeometry(800, 200, 1000, 700)
        self.cur = cur

        table_font = QFont()
        table_font.setPointSize(15)

        self.table_view = QTableView(self)
        self.table_view.setFont(table_font)
        self.table_view.setGeometry(20, 20, 960, 660)
        self.start_table()


    def start_table(self):
        try:
            self.cur.execute("SELECT * FROM combined_tickets_payments_view;")
            data = self.cur.fetchall()

            columns = [desc[0] for desc in self.cur.description]

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(columns)

            for row_num, row_data in enumerate(data):
                row_items = []
                for col_num, value in enumerate(row_data):
                    item = QStandardItem(str(value))
                    row_items.append(item)
                model.appendRow(row_items)

            self.table_view.setModel(model)
            self.table_view.resizeColumnsToContents()

        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            traceback.print_exc()


def expert_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.excepthook = expert_hook
    sys.exit(app.exec())