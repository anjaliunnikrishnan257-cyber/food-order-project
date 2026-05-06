from flask import Flask, render_template, request, redirect, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret123"   # required for cart

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",  # your password
    database="food_order"
)

# 🏠 Home Page
@app.route('/')
def home():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM restaurants")
    data = cursor.fetchall()
    return render_template('home.html', restaurants=data)

# 🍽️ Menu Page
@app.route('/menu/<int:id>')
def menu(id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM menu WHERE restaurant_id=%s", (id,))
    items = cursor.fetchall()
    return render_template('menu.html', items=items)

# 🛒 Add to Cart
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_name = request.form['item_name']
    price = float(request.form['price'])

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({'name': item_name, 'price': price})
    session.modified = True

    return redirect('/cart')

# 📦 Cart Page
@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum(item['price'] for item in cart)
    return render_template('cart.html', cart=cart, total=total)

# ✅ Place Order
@app.route('/place_order')
def place_order():
    cart = session.get('cart', [])
    cursor = db.cursor()

    total = sum(item['price'] for item in cart)

    cursor.execute("INSERT INTO orders (total_amount) VALUES (%s)", (total,))
    order_id = cursor.lastrowid

    for item in cart:
        cursor.execute(
            "INSERT INTO order_items (order_id, item_name, price, quantity) VALUES (%s, %s, %s, %s)",
            (order_id, item['name'], item['price'], 1)
        )

    db.commit()
    session['cart'] = []

    return "✅ Order Placed Successfully!"

if __name__ == '__main__':
    app.run(debug=True)