import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QFrame, QMessageBox, QFormLayout
from PyQt5.QtWidgets import QScrollArea, QGridLayout, QTableView, QVBoxLayout, QHBoxLayout, QComboBox, QHeaderView, QSizePolicy
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from PyQt5.QtGui import QColor, QPainter, QFont

import psycopg2
import traceback


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main")
        self.setGeometry(500, 200, 1000, 700)

        # Устанавливаем основной стиль для окна
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #333333;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #4d90fe;
            }
            QPushButton {
                background-color: #4a76a8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3a6690;
            }
            QPushButton:pressed {
                background-color: #2a5670;
            }
        """)

        self.label = QLabel("Введите ваш логин и пароль", self)
        self.label.move(275, 175)
        self.label.resize(1000, 100)
        self.label.setFont(QFont("Times New Roman", 25))
        self.label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }
        """)

        self.write_login = QLineEdit(self)
        self.write_login.resize(400, 40)
        self.write_login.move(300, 300)
        self.write_login.setPlaceholderText("Логин")

        self.write_password = QLineEdit(self)
        self.write_password.resize(400, 40)
        self.write_password.move(300, 350)
        self.write_password.setEchoMode(2)
        self.write_password.setPlaceholderText("Пароль")

        self.error_label = QLabel(self)
        self.error_label.move(300, 450)
        self.error_label.resize(400, 40)
        self.error_label.setStyleSheet("""
            color: #d32f2f; 
            font-size: 14px;
            background-color: #ffebee;
            padding: 5px;
            border-radius: 4px;
            border: 1px solid #ef9a9a;
        """)
        self.error_label.hide()

        self.button = QPushButton("Войти", self)
        self.button.move(590, 400)
        self.button.resize(100, 40)
        self.button.clicked.connect(self.start_action)
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)

        self.button.setDefault(True)
        self.button.setAutoDefault(True)

        self.button2 = QPushButton("Создать", self)
        self.button2.move(300, 400)
        self.button2.resize(100, 40)
        self.button2.clicked.connect(self.create_role)
        self.button2.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6da8;
            }
        """)

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

        except psycopg2.OperationalError as e:
            self.show_error(f"Ошибка входа: неправильный логин или пароль")
        except Exception as e:
            self.show_error(f"Неизвестная ошибка: {str(e)}")
            traceback.print_exc()

    def create_role(self):
        self.created = CreatedRole(self)
        self.created.show()
        self.hide()

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
    def __init__(self, mainwindow):
        super().__init__()
        self.setWindowTitle("Create")
        self.setGeometry(500, 200, 1000, 700)
        self.mainwindow = mainwindow

        # Основные стили для окна
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit, QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
                min-height: 20px;
            }
            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #4d90fe;
                outline: none;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 40px;
                border-left: 1px solid #d1d5db;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: white;
                selection-background-color: #e3f2fd;
                selection-color: black;
            }
            QPushButton {
                background-color: #4a76a8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                min-width: 100px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3a6690;
            }
            QPushButton:pressed {
                background-color: #2a5670;
            }
        """)

        self.label = QLabel("Введите данные для регистрации", self)
        self.label.move(250, 100)
        self.label.resize(1000, 100)
        self.label.setFont(QFont("Times New Roman", 25))
        self.label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }
        """)

        self.write_login = QLineEdit(self)
        self.write_login.setPlaceholderText("Логин")
        self.write_login.resize(400, 40)
        self.write_login.move(300, 200)
        self.write_login.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
            }
        """)

        self.write_password = QLineEdit(self)
        self.write_password.setPlaceholderText("Пароль")
        self.write_password.resize(400, 40)
        self.write_password.move(300, 250)
        self.write_password.setEchoMode(2)

        self.write_email = QLineEdit(self)
        self.write_email.setPlaceholderText("Email (example@domain.com)")
        self.write_email.resize(400, 40)
        self.write_email.move(300, 300)

        self.write_phone = QLineEdit(self)
        self.write_phone.setPlaceholderText("Телефон")
        self.write_phone.resize(400, 40)
        self.write_phone.move(300, 350)

        self.checkrole = QComboBox(self)
        self.checkrole.resize(400, 40)
        self.checkrole.move(300, 400)
        self.checkrole.addItems(["Customer", "Director", "Admin"])
        self.checkrole.setStyleSheet("""
            QComboBox {
                padding-right: 15px;
                border: 1px solid #d1d5db;
            }
            QComboBox::drop-down {
                width: 30px;
                border-left: 1px solid #d1d5db;
                border-radius: 0 6px 6px 0;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;

            }
        """)

        self.button = QPushButton("Создать", self)
        self.button.move(560, 450)
        self.button.resize(100, 40)
        self.button.clicked.connect(self.start_action)
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)

        self.button2 = QPushButton("Назад", self)
        self.button2.move(300, 450)
        self.button2.resize(100, 40)
        self.button2.clicked.connect(self.back_action)
        self.button2.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6da8;
            }
        """)

        self.error_label = QLabel(self)
        self.error_label.move(300, 450)
        self.error_label.resize(290, 40)
        self.error_label.setStyleSheet("""
            QLabel {
                color: #d32f2f;
                font-size: 14px;
                background-color: #ffebee;
                padding: 8px;
                border-radius: 4px;
                border: 1px solid #ef9a9a;
            }
        """)
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
            QLabel {
                color: #d32f2f;
                font-size: 14px;
                background-color: #ffebee;
                padding: 8px;
                border-radius: 4px;
                border: 1px solid #ef9a9a;
            }
        """)
        QTimer.singleShot(3000, lambda: self.error_label.setStyleSheet("""
            QLabel {
                color: #d32f2f;
                font-size: 14px;
                background-color: transparent;
                padding: 0;
                border: none;
            }
        """))

    def back_action(self):
        self.mainwindow.show()
        self.hide()


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

        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #4a76a8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #3a6690;
            }
            QPushButton:pressed {
                background-color: #2a5670;
            }
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #4d90fe;
            }
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
                min-height: 25px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                width: 20px;
                border-left: 1px solid #d1d5db;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background-color: white;
                selection-background-color: #e3f2fd;
                selection-color: black;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
        """)

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
        self.search_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
        self.myorder_btn = QPushButton("Мои заказы", self)
        self.myorder_btn.clicked.connect(self.show_orders)
        self.myorder_btn.setFixedSize(100, 40)
        self.myorder_btn.setStyleSheet("""
                   QPushButton {
                       background-color: #2ecc71;
                   }
                   QPushButton:hover {
                       background-color: #27ae60;
                   }
               """)
        self.sort_btn = QPushButton("Сортировать", self)
        self.sort_btn.clicked.connect(self.show_sort_options)
        self.sort_btn.setFixedSize(100, 40)
        self.sort_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #9b59b6;
                    }
                    QPushButton:hover {
                        background-color: #8e44ad;
                    }
                """)

        # Поле поиска (изначально скрыто)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите название мероприятия...")
        self.search_input.setVisible(False)
        self.search_input.setFixedSize(200, 40)
        self.search_input.returnPressed.connect(self.apply_search)
        self.search_input.setStyleSheet("""
                    QLineEdit {
                        background-color: white;
                        border: 1px solid #d1d5db;
                    }
                """)

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
            guery = "select * from events_by_ticket_count_view;"
        elif sort_by == "price":
            guery = "SELECT * FROM get_events_sorted_by_price;"

        try:
            self.cur.execute(query, params)
            events = self.cur.fetchall()


            for index, (event_id, event_name, event_date) in enumerate(events):
                btn = QPushButton()
                btn.setFixedSize(220, 170)
                btn.setStyleSheet("""
                    QPushButton {
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        background: #ffffff;
                        padding: 5px;
                        qproperty-iconSize: 100px;
                    }
                    QPushButton:hover {
                        border: 1px solid #4d90fe;
                        background: #f0f7ff;
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
        search_text = self.search_input.text()
        self.load_events(search_text=search_text, sort_by=self.current_sort, month=self.current_month)

    def show_sort_options(self):
        if self.sort_combo.isVisible():
            self.sort_combo.setVisible(False)
            self.month_combo.setVisible(False)
        else:
            self.sort_combo.setVisible(True)
            self.month_combo.setVisible(True)
            self.search_input.setVisible(False)

    def apply_sort(self, index):
        sort_options = ["date", "name", "popularity", "price"]
        self.current_sort = sort_options[index]
        self.load_events(search_text=self.search_input.text(),
                         sort_by=self.current_sort,
                         month=self.current_month)

    def apply_month_filter(self, index):
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
            self.inform = InfoWidget(self.id, str(event_id), self.con, self.cur, event_name, self)
            self.inform.show()
            self.hide()


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
                       background-color: #f8f9fa;
                       font-family: 'Segoe UI', Arial, sans-serif;
                   }
                   QLabel {
                       color: #343a40;
                       font-size: 16px;
                   }
                   QPushButton {
                       background-color: #28a745;
                       color: white;
                       border: none;
                       padding: 10px 20px;
                       font-size: 14px;
                       border-radius: 6px;
                       min-width: 120px;
                   }
                   QPushButton:hover {
                       background-color: #218838;
                   }
                   QPushButton:pressed {
                       background-color: #1e7e34;
                   }
                   QTableView {
                       background-color: white;
                       border: 1px solid #dee2e6;
                       border-radius: 6px;
                       alternate-background-color: #f8f9fa;
                       font-size: 14px;
                       selection-background-color: #e2f3e5;
                       selection-color: #212529;
                   }
                   QHeaderView::section {
                       background-color: #28a745;
                       color: white;
                       padding: 12px;
                       font-size: 14px;
                       font-weight: 500;
                       border: none;
                   }
                   QScrollArea {
                       border: none;
                       background: transparent;
                   }
                   QScrollBar:vertical {
                       border: none;
                       background: #f8f9fa;
                       width: 10px;
                       margin: 0px 0px 0px 0px;
                   }
                   QScrollBar::handle:vertical {
                       background: #ced4da;
                       min-height: 20px;
                       border-radius: 4px;
                   }
                   QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                       height: 0px;
                   }
               """)

        main_layout = QVBoxLayout(self)


        title_label = QLabel("История ваших заказов")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: 600;
                color: #212529;
                padding: 10px 0;
            }
        """)

        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.setFixedWidth(120)
        self.refresh_button.clicked.connect(self.start_table)
        self.refresh_button.setStyleSheet("""
                    QPushButton {
                        background-color: #17a2b8;
                    }
                    QPushButton:hover {
                        background-color: #138496;
                    }
                    QPushButton:pressed {
                        background-color: #117a8b;
                    }
                """)

        self.buy_button = QPushButton("Новая покупка")
        self.buy_button.setFixedWidth(150)
        self.buy_button.clicked.connect(self.go_to_add_card)
        self.buy_button.setStyleSheet("""
                    QPushButton {
                        background-color: #007bff;
                    }
                    QPushButton:hover {
                        background-color: #0069d9;
                    }
                    QPushButton:pressed {
                        background-color: #0062cc;
                    }
                """)

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
        self.table_view.setStyleSheet("""
                        QTableView {
                            font-size: 14px;
                            gridline-color: #dee2e6;
                        }
                        QTableView::item {
                            padding: 8px;
                        }
                    """)
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
            self.cur.execute(f'SELECT e.eventname, p.status, t.place, o.idorder, o.summ '
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
                    item.setTextAlignment(Qt.AlignCenter)


                    if col_num == 1:
                        if "Completed" in str(value):
                            item.setBackground(QColor(210, 255, 210))
                            item.setForeground(QColor(0, 100, 0))
                        elif "In process" in str(value):
                            item.setBackground(QColor(255, 255, 210))
                            item.setForeground(QColor(153, 102, 0))
                        elif "Cancelled" in str(value):
                            item.setBackground(QColor(255, 210, 210))
                            item.setForeground(QColor(139, 0, 0))

                    row_items.append(item)
                self.model.appendRow(row_items)

            self.table_view.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
            self.table_view.verticalHeader().setDefaultSectionSize(40)
            self.table_view.setShowGrid(False)

        except Exception as e:
            print(f"Ошибка при выполнении запроса: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {str(e)}")

    def on_row_selected(self, selected):
        if selected.indexes():
            row = selected.indexes()[0].row()
            self.selected_order_id = self.model.index(row, 3).data()

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

        self.cur.execute(f"""SELECT * FROM all_payments_view WHERE orderid = {order_id};""")
        answer = self.cur.fetchall()
        self.order_id = answer[0][0]
        self.summ = answer[0][1]
        self.status = answer[0][2]



        self.setWindowTitle("Добавление карты")
        self.setGeometry(800, 300, 500, 400)

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
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6da8;
            }
        """)

        self.add_btn.setObjectName("add_btn")
        self.cancel_btn.setObjectName("cancel_btn")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

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
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 16px;
                        padding: 8px;
                    }
                    #add_btn {
                        background-color: #4CAF50;  /* Зеленый для кнопки добавления */
                    }
                    #add_btn:hover {
                        background-color: #45a049;
                    }
                    #add_btn:pressed {
                        background-color: #3d8b40;
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
        if self.status == "Completed":
            QMessageBox.warning(self, "Ошибка", "Заказ уже оплачен")
            return

        try:
            # Обновляем платеж в базе данных
            self.cur.execute(f"""
                UPDATE payment
                SET card = pgp_sym_encrypt('{card_number}', 'your_secret_key'), 
                    status = 'In process' 
                WHERE orderId = {self.order_id}
                RETURNING Idpayment;
            """)

            result = self.cur.fetchone()
            if result:
                self.cur.connection.commit()
                QMessageBox.information(self, "Успех", "Карта успешно добавлена!\nПлатеж обрабатывается")
                self.hide()
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось обновить платеж")
                self.hide()

        except Exception as e:
            self.cur.connection.rollback()
            print("Ошибка", f"Произошла ошибка: {str(e)}")


class InfoWidget(QWidget):
    def __init__(self, id, index, con, cur, event_name, afisha):
        super().__init__()
        self.setWindowTitle("Zal")
        self.setGeometry(500, 200, 1000, 700)
        self.id = id
        self.index = int(index)
        self.con = con
        self.cur = cur
        self.event_name = event_name
        self.buttons = []

        self.afisha = afisha

        self.scrollarea = QScrollArea(self)
        self.scrollarea.setWidgetResizable(True)

        self.hor = QHBoxLayout()

        self.button = QPushButton("Оформить заказ", self)
        self.button.setFixedSize(200, 40)
        self.button.clicked.connect(self.finish_buy)

        self.button2 = QPushButton("Назад", self)
        self.button2.setFixedSize(200, 40)
        self.button2.clicked.connect(self.back_activity)
        self.button2.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                    QPushButton:pressed {
                        background-color: #1c6da8;
                    }
                """)

        self.hor.addWidget(self.button2)
        self.hor.addWidget(self.button)


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
        self.main_layout.addLayout(self.hor)
        self.title.setFixedSize(1000, 50)

        self.checkbtnforbuy = []

        self.title.setObjectName("title")
        self.title2.setObjectName("selected_seats")
        self.button.setObjectName("order_button")
        self.w.setObjectName("seats_widget")

        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            QLabel#title {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #4a76a8;
                color: white;
                border-radius: 5px;
                qproperty-alignment: AlignCenter;
            }

            QLabel#selected_seats {
                font-size: 18px;
                color: #34495e;
                padding: 10px;
                qproperty-alignment: AlignCenter;
            }

            QPushButton#order_button {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 500;
            }
            QPushButton#order_button:hover {
                background-color: #2ecc71;
            }
            QPushButton#order_button:pressed {
                background-color: #219653;
            }

            QScrollArea {
                border: none;
                background: transparent;
            }

            QWidget#seats_widget {
                background-color: #ecf0f1;
                border-radius: 8px;
                padding: 15px;
            }

            QScrollBar:vertical {
                border: none;
                background: #dfe6e9;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #b2bec3;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    def load_seats(self):
        try:
            self.cur.execute(f"""SELECT place, price FROM tickets_by_event_view WHERE eventid = {self.index+1};""")

            seats = self.cur.fetchall()
            seat_style = """
                            QPushButton {
                                border: none;
                                border-radius: 4px;
                                background: %s;
                                color: #2c3e50;
                                font-weight: 500;
                                min-width: 40px;
                                min-height: 40px;
                                margin: 2px;
                            }
                            QPushButton:hover {
                                opacity: 0.9;
                                transform: scale(1.05);
                            }
                            QPushButton:pressed {
                                opacity: 0.8;
                            }
                            QPushButton:checked {
                                background: #e74c3c;
                                color: white;
                            }
                        """

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
            seats_numbers = ", ".join(i[0] for i in self.checkbtnforbuy)
            self.title2.setText(f"Выбраны места: {seats_numbers}")

    def finish_buy(self):
        self.byuticket = BuyTicket(self.id, self.index, self.con, self.cur, self.event_name, self.checkbtnforbuy, self, self.afisha)
        self.byuticket.show()

    def back_activity(self):
        self.afisha.show()
        self.close()


class BuyTicket(QWidget):
    def __init__(self, id, index, con, cur, event_name, placeAndPrice, zal, afisha):
        super().__init__()
        self.setWindowTitle("Оформление билета")
        self.setGeometry(700, 250, 500, 500)
        self.setMinimumSize(600, 400)

        # Основные данные
        self.eventid = int(index)+1
        self.userid = id
        self.con = con
        self.cur = cur
        self.places = [item[0] for item in placeAndPrice]
        self.prices = [item[1] for item in placeAndPrice]
        self.total_price = sum(self.prices)

        self.zal = zal
        self.afisha = afisha

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
                padding: 15px;
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
                padding: 0px 0;
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
                padding: 0px 0;
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
        self.zal.close()
        self.afisha.show()




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
        table_font.setPointSize(12)

        self.setStyleSheet("""
           QWidget {
               background-color: #f5f7fa;
               font-family: 'Segoe UI', Arial, sans-serif;
           }

           QComboBox {
               border: 1px solid #ced4da;
               border-radius: 6px;
               padding: 8px 12px;
               font-size: 14px;
               background-color: white;
               min-height: 25px;
           }
           QComboBox::drop-down {
               width: 30px;
               border-left: 1px solid #ced4da;
           }
           QComboBox QAbstractItemView {
            border: 1px solid #d1d5db;
            border-radius: 6px;
            background-color: white;
            selection-background-color: #e3f2fd;
            selection-color: black;
           }

           QPushButton {
               background-color: #4a76a8;
               color: white;
               border: none;
               border-radius: 6px;
               padding: 8px 16px;
               font-size: 14px;
               min-width: 100px;
           }
           QPushButton:hover {
               background-color: #3a6690;
           }
           QPushButton:pressed {
               background-color: #2a5670;
           }

           QTableView {
               background-color: white;
               border: 1px solid #dee2e6;
               alternate-background-color: #f8f9fa;
               gridline-color: #dee2e6;
               font-size: 14px;
           }
           QHeaderView::section {
               background-color: #4a76a8;
               color: white;
               padding: 8px;
               font-weight: 500;
               border: none;
           }
           QTableView::item {
               padding: 6px;
           }
           QTableView::item:selected {
               background-color: #c3e6cb;
               color: black;
           }

           QScrollBar:vertical {
               border: none;
               background: #f1f1f1;
               width: 10px;
               margin: 0px 0px 0px 0px;
           }
           QScrollBar::handle:vertical {
               background: #b2bec3;
               min-height: 20px;
               border-radius: 4px;
           }
       """)


        self.refresh_btn = QPushButton("Обновить список таблиц")
        self.refresh_btn.setFixedSize(250, 40)
        self.refresh_btn.clicked.connect(self.load_tables)
        self.refresh_btn.setFont(button_font)
        control_layout.addWidget(self.refresh_btn)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)

        self.loadtab = QPushButton("Загрузить таблицу")
        self.loadtab.setFixedSize(200, 40)
        self.loadtab.clicked.connect(self.start_table)
        self.loadtab.setFont(button_font)
        control_layout.addWidget(self.loadtab)
        self.loadtab.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)

        main_layout.addLayout(control_layout)

        self.table_view = QTableView()
        self.table_view.setFont(table_font)
        main_layout.addWidget(self.table_view)

        edit_layout = QHBoxLayout()

        self.add_row_btn = QPushButton("Добавить строку")
        self.add_row_btn.setFixedSize(150, 40)
        self.add_row_btn.clicked.connect(self.add_row)
        self.add_row_btn.setFont(button_font)
        edit_layout.addWidget(self.add_row_btn)

        self.delete_row_btn = QPushButton("Удалить строку")
        self.delete_row_btn.setFixedSize(150, 40)
        self.delete_row_btn.clicked.connect(self.delete_row)
        self.delete_row_btn.setFont(button_font)
        edit_layout.addWidget(self.delete_row_btn)

        self.save_changes_btn = QPushButton("Сохранить изменения")
        self.save_changes_btn.setFixedSize(200, 40)
        self.save_changes_btn.clicked.connect(self.save_changes)
        self.save_changes_btn.setFont(button_font)
        edit_layout.addWidget(self.save_changes_btn)

        main_layout.addLayout(edit_layout)

        self.table_view.setEditTriggers(QTableView.DoubleClicked | QTableView.EditKeyPressed)

        self.primary_keys = {}

        self.start_table()

        self.checktable.setObjectName("tables_combo")
        self.refresh_btn.setObjectName("refresh_button")
        self.loadtab.setObjectName("load_button")
        self.table_view.setObjectName("data_table")

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
            self.cur.execute(f"""
                            SELECT a.attname
                            FROM pg_index i
                            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                            WHERE i.indrelid = '{self.selected_table}'::regclass
                            AND i.indisprimary;
                        """)
            self.primary_keys[self.selected_table] = [pk[0] for pk in self.cur.fetchall()]


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

    def add_row(self):
        model = self.table_view.model()
        if not model:
            return

        row_items = [QStandardItem("") for _ in range(model.columnCount())]
        model.appendRow(row_items)

        self.table_view.scrollToBottom()

    def delete_row(self):
        model = self.table_view.model()
        if not model:
            return

        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для удаления")
            return

        for index in sorted(selected, key=lambda x: x.row(), reverse=True):
            model.removeRow(index.row())

    def save_changes(self):
        model = self.table_view.model()
        if not model:
            QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения")
            return

        try:
            # Получаем информацию о столбцах таблицы, включая identity-столбцы
            self.cur.execute(f"""
                SELECT column_name, 
                       is_identity = 'YES' OR column_default LIKE 'nextval%' AS is_identity
                FROM information_schema.columns 
                WHERE table_name = '{self.selected_table}';
            """)
            columns_info = self.cur.fetchall()
            identity_columns = [col[0] for col in columns_info if col[1]]

            # Получаем текущие данные из БД для сравнения
            self.cur.execute(f"SELECT * FROM {self.selected_table};")
            db_data = self.cur.fetchall()
            db_columns = [desc[0] for desc in self.cur.description]

            # Подготовка данных для обработки
            model_data = []
            for row in range(model.rowCount()):
                row_data = []
                for col in range(model.columnCount()):
                    item = model.item(row, col)
                    row_data.append(item.text() if item else "")
                model_data.append(row_data)

            # Определяем, какие строки были добавлены, изменены или удалены
            added_rows = []
            updated_rows = []
            deleted_rows = []

            # Проверяем удаленные строки (есть в БД, но нет в модели)
            for db_row in db_data:
                pk_values = []
                for pk in self.primary_keys.get(self.selected_table, []):
                    pk_index = db_columns.index(pk)
                    pk_values.append(str(db_row[pk_index]))

                # Ищем строку с такими же первичными ключами в модели
                found = False
                for model_row in model_data:
                    model_pk_values = []
                    for pk in self.primary_keys.get(self.selected_table, []):
                        pk_index = db_columns.index(pk)
                        model_pk_values.append(model_row[pk_index])

                    if pk_values == model_pk_values:
                        found = True
                        # Проверяем, были ли изменения в строке
                        for i in range(len(db_row)):
                            if str(db_row[i]) != model_row[i]:
                                updated_rows.append((pk_values, model_row))
                                break
                        break

                if not found:
                    deleted_rows.append(pk_values)

            # Проверяем добавленные строки (есть в модели, но нет в БД)
            for model_row in model_data:
                if not self.primary_keys.get(self.selected_table):
                    added_rows.append(model_row)
                    continue

                pk_values = []
                for pk in self.primary_keys.get(self.selected_table, []):
                    pk_index = db_columns.index(pk)
                    pk_values.append(model_row[pk_index])

                # Если первичный ключ пустой или содержит NULL, считаем строку новой
                if any(pk == "" or pk.lower() == "null" for pk in pk_values):
                    added_rows.append(model_row)
                    continue

                # Ищем строку с такими же первичными ключами в БД
                found = False
                for db_row in db_data:
                    db_pk_values = []
                    for pk in self.primary_keys.get(self.selected_table, []):
                        pk_index = db_columns.index(pk)
                        db_pk_values.append(str(db_row[pk_index]))

                    if pk_values == db_pk_values:
                        found = True
                        break

                if not found:
                    added_rows.append(model_row)

            # Выполняем SQL-запросы для каждого типа изменений
            with self.cur.connection.cursor() as temp_cur:
                # Удаление строк
                for pk_values in deleted_rows:
                    where_parts = []
                    for pk, pk_value in zip(self.primary_keys[self.selected_table], pk_values):
                        where_parts.append(f"{pk} = %s")

                    query = f"DELETE FROM {self.selected_table} WHERE {' AND '.join(where_parts)};"
                    temp_cur.execute(query, pk_values)

                # Обновление строк
                for pk_values, row_data in updated_rows:
                    set_parts = []
                    values = []
                    for col_name, value in zip(db_columns, row_data):
                        if (col_name not in self.primary_keys[self.selected_table] and
                                col_name not in identity_columns):
                            set_parts.append(f"{col_name} = %s")
                            values.append(None if value.lower() == 'null' or value == '' else value)

                    where_parts = []
                    for pk, pk_value in zip(self.primary_keys[self.selected_table], pk_values):
                        where_parts.append(f"{pk} = %s")
                        values.append(pk_value)

                    if set_parts:  # Проверяем, есть ли что обновлять
                        query = f"UPDATE {self.selected_table} SET {', '.join(set_parts)} WHERE {' AND '.join(where_parts)};"
                        temp_cur.execute(query, values)

                # Добавление строк
                for row_data in added_rows:
                    columns = []
                    placeholders = []
                    values = []
                    for col_name, value in zip(db_columns, row_data):
                        if col_name not in identity_columns:  # Пропускаем identity-столбцы
                            columns.append(col_name)
                            placeholders.append("%s")
                            values.append(None if value.lower() == 'null' or value == '' else value)

                    if columns:  # Проверяем, есть ли столбцы для вставки
                        query = f"INSERT INTO {self.selected_table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                        temp_cur.execute(query, values)

                # Фиксируем изменения
                self.cur.connection.commit()

            QMessageBox.information(self, "Успех", "Изменения успешно сохранены")
            self.start_table()  # Обновляем таблицу

        except Exception as e:
            self.cur.connection.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения: {str(e)}")
            print(f"Ошибка при сохранении изменений: {e}")
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

        self.allinfo.setObjectName("all_info_btn")
        self.button1.setObjectName("events_btn")
        self.button2.setObjectName("payments_btn")
        self.button3.setObjectName("profitability_btn")
        self.button4.setObjectName("orders_payments_btn")

        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
    
            QPushButton {
                background-color: #4a76a8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: 500;
                text-align: left;
                min-width: 250px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #3a6690;
            }
            QPushButton:pressed {
                background-color: #2a5670;
            }
    
            QPushButton#all_info_btn {
                background-color: #28a745;
            }
            QPushButton#all_info_btn:hover {
                background-color: #218838;
            }
    
            QPushButton#events_btn {
                background-color: #6f42c1;
            }
            QPushButton#events_btn:hover {
                background-color: #5e32b1;
            }
    
            QPushButton#payments_btn {
                background-color: #fd7e14;
            }
            QPushButton#payments_btn:hover {
                background-color: #e66a00;
            }
    
            QPushButton#profitability_btn {
                background-color: #17a2b8;
            }
            QPushButton#profitability_btn:hover {
                background-color: #138496;
            }
    
            QPushButton#orders_payments_btn {
                background-color: #dc3545;
            }
            QPushButton#orders_payments_btn:hover {
                background-color: #c82333;
            }
        """)
        self.go_to_evnt = EventForDirector(self.cur)
        self.go_to_payment = PaymentForDirector(self.cur)
        self.go_to_allTables = AllTablesDirector(self.cur)
        self.ocypaemost = Ocypaemost(self.cur)
        self.union = Union(self.cur)

        self.windows = [
            self.go_to_allTables, self.go_to_payment, self.go_to_evnt, self.ocypaemost,  self.union]

        self.hide_all_windows()

    def event_action(self):
        self.hide_all_windows()
        self.go_to_evnt.show()

    def payment_action(self):
        self.hide_all_windows()
        self.go_to_payment.show()

    def view_all_tables(self):
        self.hide_all_windows()
        self.go_to_allTables.show()

    def ocypaemost_action(self):
        self.hide_all_windows()
        self.ocypaemost.show()

    def union_action(self):
        self.hide_all_windows()
        self.union.show()

    def hide_all_windows(self):
        for window in self.windows:
            if window is not None:
                window.hide()


class AllTablesDirector(QWidget):
    def __init__(self, cur):
        super().__init__()
        self.setGeometry(800, 200, 1000, 700)
        self.cur = cur

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        self.table_view = QTableView()
        self.table_view.setObjectName("data_table")
        self.main_layout.addWidget(self.table_view)
        self.start_table()

        self.setStyleSheet("""
           QWidget {
               background-color: #f5f7fa;
               font-family: 'Segoe UI', Arial, sans-serif;
           }

           QTableView {
               background-color: white;
               border: 1px solid #dee2e6;
               alternate-background-color: #f8f9fa;
               gridline-color: #dee2e6;
               font-size: 14px;
           }
           QHeaderView::section {
               background-color: #4a76a8;
               color: white;
               padding: 8px;
               font-weight: 500;
               border: none;
           }
           QTableView::item {
               padding: 6px;
           }
           QTableView::item:selected {
               background-color: #c3e6cb;
               color: black;
           }

           QScrollBar:vertical {
               border: none;
               background: #f1f1f1;
               width: 10px;
               margin: 0px 0px 0px 0px;
           }
           QScrollBar::handle:vertical {
               background: #b2bec3;
               min-height: 20px;
               border-radius: 4px;
           }
       """)

    def start_table(self):
        try:
            title_label = QLabel("Полная информация о пользователях и заказах")
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2c3e50;
                    padding: 10px;
                    qproperty-alignment: AlignCenter;
                }
            """)
            self.main_layout.addWidget(title_label)

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
        self.count_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
            }
        """)

        self.sort_on_month = QLabel("По месяцам: ", self.scroll_area)
        self.sort_on_month.setGeometry(20, 60, 700, 40)
        self.sort_on_month.setFont(label_font)
        self.sort_on_month.setStyleSheet("""
           QLabel {
               font-size: 16px;
               font-weight: bold;
               padding: 5px;
           }
       """)

        self.chart_view = QChartView(self.scroll_area)
        self.chart_view.setGeometry(20, 120, 680, 400)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        self.chart_view.setStyleSheet("""
            QChartView {
                background: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        self.load_data()

        self.setStyleSheet("""
             QWidget {
                 background-color: #f5f7fa;
                 font-family: 'Segoe UI', Arial, sans-serif;
             }

             QLabel {
                 color: #2c3e50;
                 font-size: 14px;
                 font-weight: 500;
             }
             QScrollArea {
                 border: none;
                 background: transparent;
             }
             QChartView {
                 background-color: white;
                 border: 1px solid #d1d5db;
                 border-radius: 8px;
             }
             QScrollBar:vertical {
                 border: none;
                 background: #f1f1f1;
                 width: 10px;
                 margin: 0px 0px 0px 0px;
             }
             QScrollBar::handle:vertical {
                 background: #b2bec3;
                 min-height: 20px;
                 border-radius: 4px;
             }
         """)

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

        main_layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        label_font = QFont()
        label_font.setPointSize(12)

        self.count_label = QLabel()
        self.count_label.setFont(label_font)
        self.scroll_layout.addWidget(self.count_label)
        self.get_count()
        self.count_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px 0;
            }
        """)

        self.sort_on_month = QLabel("Выберите мероприятие:")
        self.sort_on_month.setFont(label_font)
        self.scroll_layout.addWidget(self.sort_on_month)
        self.sort_on_month.setStyleSheet("""
                    QLabel {
                        font-size: 16px;
                        font-weight: bold;
                        padding: 10px 0;
                    }
                """)

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
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                margin-top: 10px;
                margin-bottom: 10px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)

        self.table_view = QTableView()
        self.scroll_layout.addWidget(self.table_view)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        self.setStyleSheet("""
             QWidget {
                 background-color: #f5f7fa;
                 font-family: 'Segoe UI', Arial, sans-serif;
             }

             QLabel {
                 color: #2c3e50;
                 font-size: 14px;
                 font-weight: 500;
                 padding: 5px 0;
             }

             QComboBox {
                 border: 1px solid #ced4da;
                 border-radius: 6px;
                 padding: 8px 8px;
                 font-size: 14px;
                 background-color: white;
                 min-height: 25px;
             }
             QComboBox::drop-down {
                 width: 30px;
                 border-left: 1px solid #ced4da;
             }
             QComboBox QAbstractItemView {
                 border: 1px solid #d1d5db;
                 border-radius: 6px;
                 background-color: white;
                 selection-background-color: #e3f2fd;
                 selection-color: black;
             }

             QPushButton {
                 background-color: #4a76a8;
                 color: white;
                 border: none;
                 border-radius: 6px;
                 padding: 0px;
                 font-size: 14px;
                 font-weight: 500;
                 min-height: 10px
             }
             QPushButton:hover {
                 background-color: #3a6690;
             }
             QPushButton:pressed {
                 background-color: #2a5670;
             }

             QTableView {
                 background-color: white;
                 border: 1px solid #dee2e6;
                 alternate-background-color: #f8f9fa;
                 gridline-color: #dee2e6;
                 font-size: 14px;
             }
             QHeaderView::section {
                 background-color: #4a76a8;
                 color: white;
                 padding: 8px;
                 font-weight: 500;
                 border: none;
             }
             QTableView::item {
                 padding: 6px;
             }
             QTableView::item:selected {
                 background-color: #c3e6cb;
                 color: black;
             }

             QScrollArea {
                 border: none;
                 background: transparent;
             }

             QScrollBar:vertical {
                 border: none;
                 background: #f1f1f1;
                 width: 10px;
                 margin: 0px 0px 0px 0px;
             }
             QScrollBar::handle:vertical {
                 background: #b2bec3;
                 min-height: 20px;
                 border-radius: 4px;
             }
         """)

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


class Ocypaemost(QWidget):
    def __init__(self, cur):
        super().__init__()
        self.setGeometry(800, 200, 2000, 700)
        self.cur = cur

        table_font = QFont()
        table_font.setPointSize(15)

        self.table_view = QTableView(self)
        self.table_view.setFont(table_font)
        self.table_view.setGeometry(20, 20, 1960, 660)

        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.table_view.verticalHeader().setVisible(False)

        self.start_table()

        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }

            QTableView {
                background-color: white;
                border: 1px solid #dee2e6;
                alternate-background-color: #f8f9fa;
                gridline-color: #dee2e6;
                font-size: 14px;
                selection-background-color: #e2f3e5;
                selection-color: black;
            }
            QHeaderView::section {
                background-color: #4a76a8;
                color: white;
                padding: 5px;
                font-size: 14px;
                font-weight: 500;
                border: none;
            }
            QTableView::item {
                padding: 8px;
            }

            QScrollBar:vertical {
                border: none;
                background: #f1f1f1;
                width: 12px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #b2bec3;
                min-height: 30px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)



    def start_table(self):
        try:
            self.cur.execute("""SELECT * FROM event_occupancy_with_detail_view;""")
            data = self.cur.fetchall()

            columns = [desc[0] for desc in self.cur.description]

            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(columns)

            for row_num, row_data in enumerate(data):
                row_items = []
                for col_num, value in enumerate(row_data):
                    item = QStandardItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)

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

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        self.setStyleSheet("""
                   QWidget {
                       background-color: #f5f7fa;
                       font-family: 'Segoe UI', Arial, sans-serif;
                   }

                   QTableView {
                       background-color: white;
                       border: 1px solid #dee2e6;
                       border-radius: 4px;
                       alternate-background-color: #f8f9fa;
                       gridline-color: #dee2e6;
                       font-size: 14px;
                       selection-background-color: #e2f3e5;
                       selection-color: black;
                   }
                   QHeaderView::section {
                       background-color: #4a76a8;
                       color: white;
                       padding: 10px;
                       font-size: 14px;
                       font-weight: 500;
                       border: none;
                   }
                   QTableView::item {
                       padding: 8px;
                   }

                   QScrollBar:vertical {
                       border: none;
                       background: #f1f1f1;
                       width: 12px;
                       margin: 0;
                   }
                   QScrollBar::handle:vertical {
                       background: #b2bec3;
                       min-height: 30px;
                       border-radius: 6px;
                   }
                   QScrollBar::add-line:vertical, 
                   QScrollBar::sub-line:vertical {
                       height: 0;
                   }
               """)

        title_label = QLabel("Связь заказов и платежей")
        title_label.setStyleSheet("""
                   QLabel {
                       font-size: 18px;
                       font-weight: bold;
                       color: #2c3e50;
                       padding: 10px;
                       qproperty-alignment: AlignCenter;
                   }
               """)
        main_layout.addWidget(title_label)

        self.table_view = QTableView()
        self.table_view.setObjectName("dataTable")

        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setSortingEnabled(True)

        main_layout.addWidget(self.table_view)

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