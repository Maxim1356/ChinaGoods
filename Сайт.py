# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nike.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TELEGRAM_BOT_LINK'] = 'https://t.me/your_nike_bot'  # Ваша ссылка на бота

# Инициализация расширений
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Модели данных
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    telegram_chat_id = db.Column(db.String(50))  # Для уведомлений через бота


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    description = db.Column(db.Text)
    image = db.Column(db.String(100))
    category = db.Column(db.String(50))
    stock = db.Column(db.Integer)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, default=1)


# Загрузчик пользователя
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Главная страница
@app.route('/')
def home():
    products = Product.query.limit(8).all()
    return render_template('home.html', products=products)


# Страница продукта
@app.route('/product/<int:id>')
def product(id):
    product = Product.query.get_or_404(id)
    return render_template('product.html', product=product)


# Корзина
@app.route('/cart')
@login_required
def cart():
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)


# Добавление в корзину
@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product.id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=current_user.id, product_id=product.id)
        db.session.add(cart_item)

    db.session.commit()
    flash('Товар добавлен в корзину', 'success')
    return redirect(request.referrer)


# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        telegram_chat_id = request.form.get('telegram_chat_id')

        if User.query.filter_by(username=username).first():
            flash('Имя пользователя занято', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email уже используется', 'error')
        else:
            user = User(username=username, email=email, password=password, telegram_chat_id=telegram_chat_id)
            db.session.add(user)
            db.session.commit()
            flash('Регистрация успешна!', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')


# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Неверные данные', 'error')

    return render_template('login.html')


# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# API для Telegram бота (упрощенное)
@app.route('/api/telegram', methods=['POST'])
def telegram_webhook():
    data = request.json
    # Здесь обработка команд от бота
    return {'status': 'ok'}


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)