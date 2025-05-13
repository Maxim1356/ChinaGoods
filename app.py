from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import sqlite3
import os
from functools import wraps
import asyncio
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['DATABASE'] = 'database.db'
app.config['SESSION_COOKIE_NAME'] = 'china2rus_session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = dict_factory
    return db


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()


def row_to_dict(row):
    if row is None:
        return None
    return dict(zip(row.keys(), row))

    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS users
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       password_hash
                       TEXT
                       NOT
                       NULL,
                       email
                       TEXT
                       UNIQUE,
                       created_at
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       last_login
                       TIMESTAMP
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS shipping_types
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       name
                       TEXT
                       NOT
                       NULL,
                       description
                       TEXT,
                       base_cost
                       REAL
                       NOT
                       NULL,
                       delivery_days_min
                       INTEGER,
                       delivery_days_max
                       INTEGER,
                       icon_name
                       TEXT
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS brands
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       name
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       description
                       TEXT,
                       logo_path
                       TEXT,
                       rating
                       REAL
                       DEFAULT
                       0.0,
                       is_featured
                       BOOLEAN
                       DEFAULT
                       FALSE
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS products
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       brand_id
                       INTEGER
                       NOT
                       NULL,
                       name
                       TEXT
                       NOT
                       NULL,
                       description
                       TEXT,
                       price
                       REAL
                       NOT
                       NULL,
                       image_path
                       TEXT,
                       category
                       TEXT,
                       stock_quantity
                       INTEGER
                       DEFAULT
                       0,
                       FOREIGN
                       KEY
                   (
                       brand_id
                   ) REFERENCES brands
                   (
                       id
                   )
                       )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS team_members
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       name
                       TEXT
                       NOT
                       NULL,
                       position
                       TEXT
                       NOT
                       NULL,
                       bio
                       TEXT,
                       image_path
                       TEXT,
                       join_date
                       TEXT
                   )
                   ''')

    db.commit()


@app.template_filter('number_format')
def number_format(value):
    return "{:,.0f}".format(value).replace(",", " ")


class DatabaseModel:
    @staticmethod
    def execute_query(query, args=(), fetch=False, commit=False):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, args)
        if commit:
            db.commit()
        if fetch:
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        return None


class User(DatabaseModel):
    @staticmethod
    def create(username, password, email=None):
        password_hash = generate_password_hash(password)
        try:
            User.execute_query(
                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password_hash, email),
                commit=True
            )
            return True
        except sqlite3.IntegrityError:
            return False

    @staticmethod
    def get_by_username(username):
        users = User.execute_query(
            "SELECT * FROM users WHERE username = ?",
            (username,),
            fetch=True
        )
        return users[0] if users else None

    @staticmethod
    def update_last_login(user_id):
        User.execute_query(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,),
            commit=True
        )


class ShippingType(DatabaseModel):
    @staticmethod
    def get_all():
        return ShippingType.execute_query(
            "SELECT * FROM shipping_types ORDER BY base_cost ASC",
            fetch=True
        )

    @staticmethod
    def get_by_name(name):
        types = ShippingType.execute_query(
            "SELECT * FROM shipping_types WHERE name = ?",
            (name,),
            fetch=True
        )
        return types[0] if types else None


@app.template_filter('int')
def format_int(value):
    return value


class Brand(DatabaseModel):
    @staticmethod
    def get_all():
        return Brand.execute_query(
            "SELECT * FROM brands ORDER BY name ASC",
            fetch=True
        )

    @staticmethod
    def get_featured():
        return Brand.execute_query(
            "SELECT * FROM brands WHERE is_featured = TRUE ORDER BY RANDOM() LIMIT 4",
            fetch=True
        )

    @staticmethod
    def get_by_name(name):
        brands = Brand.execute_query(
            "SELECT * FROM brands WHERE name = ?",
            (name,),
            fetch=True
        )
        return brands[0] if brands else None


class Product(DatabaseModel):
    @staticmethod
    def get_by_brand(brand_id):
        return Product.execute_query(
            "SELECT * FROM products WHERE brand_id = ?",
            (brand_id,),
            fetch=True
        )

    @staticmethod
    def get_featured(limit=6):
        return Product.execute_query(
            "SELECT * FROM products ORDER BY RANDOM() LIMIT ?",
            (limit,),
            fetch=True
        )


class TeamMember(DatabaseModel):
    @staticmethod
    def get_all():
        return TeamMember.execute_query(
            "SELECT * FROM team_members ORDER BY join_date DESC",
            fetch=True
        )


class AuthService:
    @staticmethod
    def login_user(username, password):
        user = User.get_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            User.update_last_login(user['id'])
            return True
        return False

    @staticmethod
    def logout_user():
        session.clear()

    @staticmethod
    def get_current_user():
        if 'user_id' in session:
            return User.get_by_username(session['username'])
        return None


class ShippingCalculator:
    BASE_RATE = 1.18
    EXCHANGE_RATE = 12.5

    @staticmethod
    def calculate(weight, volume, shipping_type_name, product_cost):
        shipping_type = ShippingType.get_by_name(shipping_type_name)
        if not shipping_type:
            return None
        dimensional_weight = (volume * 167) / 1000
        chargeable_weight = max(weight, dimensional_weight)

        base_cost = shipping_type['base_cost']
        shipping_cost = (
                base_cost *
                (chargeable_weight ** 0.9 + volume ** 1.1) *
                ShippingCalculator.BASE_RATE
        )

        total_cost = (
                product_cost * ShippingCalculator.EXCHANGE_RATE +
                shipping_cost
        )

        return {
            'shipping_type': dict(shipping_type),
            'weight': weight,
            'volume': volume,
            'product_cost': product_cost,
            'shipping_cost': round(shipping_cost, 2),
            'total_cost': round(total_cost, 2),
            'exchange_rate': ShippingCalculator.EXCHANGE_RATE,
            'delivery_days': (
                shipping_type['delivery_days_min'],
                shipping_type['delivery_days_max']
            )
        }


class DataInitializer:
    @staticmethod
    def initialize_sample_data():
        TeamMember.execute_query("DELETE FROM team_members", commit=True)
        team_data = [
            ("Кузьмичёв Максим", "Решала", "qwe", "team1.jpg", "2025-05-13"),
            ("Лукин Александр", "Логист", "qwe", "team1.jpg", "2025-05-13"),
            ("Кабанов Сергей", "Логист", "qwe", "team1.jpg", "2025-05-13")
        ]
        for name, pos, bio, img, date in team_data:
            TeamMember.execute_query(
                "INSERT INTO team_members (name, position, bio, image_path, join_date) VALUES (?, ?, ?, ?, ?)",
                (name, pos, bio, img, date),
                commit=True
            )
            Brand.execute_query("DELETE FROM brands", commit=True)
            Product.execute_query("DELETE FROM products", commit=True)
            brands = [
                {"name": "Nike", "description": "Мировой лидер в производстве спортивной одежды",
                 "logo_path": "nike.jpg"},
                {"name": "Adidas", "description": "Немецкий производитель спортивной экипировки",
                 "logo_path": "adidas.jpg"},
                {"name": "Zara", "description": "Испанский бренд модной одежды", "logo_path": "zara.jpg"},
                {"name": "H&M", "description": "Шведский ритейлер одежды", "logo_path": "hm.jpg"}
            ]

            for brand in brands:
                existing = Brand.execute_query(
                    "SELECT 1 FROM brands WHERE name = ?",
                    (brand["name"],),
                    fetch=True
                )
                if not existing:
                    Brand.execute_query(
                        "INSERT INTO brands (name, description, logo_path) VALUES (?, ?, ?)",
                        (brand["name"], brand["description"], brand["logo_path"]),
                        commit=True
                    )
            products = [
                {"brand": "Nike", "name": "Кроссовки Air Max", "price": 8990, "image_path": "nike_air_max.jpg",
                 "category": "Обувь"},
                {"brand": "Adidas", "name": "Кроссовки Ultraboost", "price": 10990,
                 "image_path": "adidas_ultraboost.jpg", "category": "Обувь"},
                {"brand": "Zara", "name": "Джинсы Slim Fit", "price": 3990, "image_path": "zara_jeans.jpg",
                 "category": "Одежда"},
                {"brand": "H&M", "name": "Футболка Basic", "price": 1290, "image_path": "hm_tshirt.jpg",
                 "category": "Одежда"}
            ]

            for product in products:
                brand = Brand.get_by_name(product["brand"])
                if brand:
                    Product.execute_query(
                        "INSERT INTO products (brand_id, name, price, image_path, category) VALUES (?, ?, ?, ?, ?)",
                        (brand["id"], product["name"], product["price"], product["image_path"], product["category"]),
                        commit=True
                    )

    @staticmethod
    def calculate(weight, volume, shipping_type, product_cost):
        if weight > shipping_type['max_weight']:
            raise ValueError(f"Вес превышает максимальный для {shipping_type['name']}")
        if volume > shipping_type['max_volume']:
            raise ValueError(f"Объем превышает максимальный для {shipping_type['name']}")
        dimensional_weight = (volume * 167) / 1000
        chargeable_weight = max(weight, dimensional_weight)

        base_cost = shipping_type['base_cost']
        shipping_cost = (
                base_cost *
                (chargeable_weight ** 0.9 + volume ** 1.1) *
                1.18
        )
        insurance = product_cost * shipping_type['insurance_rate']

        total_cost = (
                product_cost * 12.5 +
                shipping_cost +
                insurance
        )

        return {
            'shipping_type': shipping_type,
            'weight': weight,
            'volume': volume,
            'product_cost': product_cost,
            'base_cost': base_cost,
            'shipping_cost': round(shipping_cost, 2),
            'insurance_cost': round(insurance, 2),
            'total_cost': round(total_cost, 2),
            'exchange_rate': 12.5,
            'delivery_days': (
                shipping_type['delivery_days_min'],
                shipping_type['delivery_days_max']
            )
        }


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите для доступа к этой странице', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


def inject_global_data():
    current_user = AuthService.get_current_user()
    return {
        'current_user': current_user,
        'current_year': datetime.now().year,
        'is_authenticated': current_user is not None
    }


@app.route('/')
def home():
    shipping_types = [
        {"name": 'ЖД грузоперевозки', 'base_cost': '500 за кг', 'delivery_days_min': '2 недели',
         'delivery_days_max': '3 недели'},
        {"name": 'Авиа перевозки', 'base_cost': '1000 за кг', 'delivery_days_min': '3 дня',
         'delivery_days_max': '7 дней'},
        {"name": 'По морю', 'base_cost': '300 за кг', 'delivery_days_min': '3 недели', 'delivery_days_max': '5 недель'}]
    return render_template('index.html', shipping_types=shipping_types)


@app.route('/brands')
def brands():
    all_brands = Brand.get_all()
    return render_template('brands.html', brands=all_brands)


@app.route('/brand/<brand_name>')
def brand_main(brand_name):
    brand = Brand.get_by_name(brand_name)
    if not brand:
        abort(404)
    return render_template('brand_main.html', brand=brand)


@app.route('/brand/<brand_name>/products')
def brand_products(brand_name):
    brand = Brand.get_by_name(brand_name)
    if not brand:
        abort(404)
    products = Product.get_by_brand(brand['id'])
    return render_template('brand_products.html',
                           brand=brand,
                           products=products)


@app.route('/calculator')
def calculator():
    shipping_types = [
        {"name": 'ЖД грузоперевозки', 'base_cost': '500', 'delivery_days_min': '2 недели',
         'delivery_days_max': '3 недели'},
        {"name": 'Авиа перевозки', 'base_cost': '1000', 'delivery_days_min': '3 дня', 'delivery_days_max': '7 дней'},
        {"name": 'По морю', 'base_cost': '300', 'delivery_days_min': '3 недели', 'delivery_days_max': '5 недель'}]
    for st in shipping_types:
        if not isinstance(st['base_cost'], int):
            st['base_cost'] = st['base_cost']
    return render_template('calculator_form.html', shipping_types=shipping_types)


@app.route('/team')
def team():
    team_members = [{'name': 'Максим', 'position': 'Кузьмичёв'},
                    {'name': 'Александр', 'position': 'Лукин'},
                    {'name': 'Сергей', 'position': 'Кабанов'}]
    return render_template('team.html', team=team_members)


def _render_brand_page(brand_name):
    brand = Brand.get_by_name(brand_name)
    if not brand:
        abort(404)
    products = Product.get_by_brand(brand['id'])
    return render_template('brand_detail.html', brand=brand, products=products)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if AuthService.login_user(username, password):
            flash('Вы успешно вошли в систему', 'success')
            return redirect(url_for('home'))

        flash('Неверный логин или пароль', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        if User.create(username, password, email):
            flash('Регистрация успешна. Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))

        flash('Пользователь с таким именем уже существует', 'danger')

    return render_template('register.html')


@app.route('/logout')
def logout():
    AuthService.logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500



if __name__ == '__main__':
    get_db()
    DataInitializer.initialize_sample_data()
    app.context_processor(inject_global_data)
    app.run(debug=True)
