from flask import Flask, render_template, request, redirect, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = "secret123"

# 🔗 Connect to PostgreSQL (Render)
DATABASE_URL = os.environ.get("DATABASE_URL")

try:
    db = psycopg2.connect(DATABASE_URL)
    print("✅ Database Connected")
except Exception as e:
    print("❌ DB Error:", e)

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

    # 🔥 IMPORTANT: PostgreSQL insert fix
    cursor.execute(
        "INSERT INTO orders (total_amount) VALUES (%s) RETURNING order_id",
        (total,)
    )
    order_id = cursor.fetchone()[0]

    for item in cart:
        cursor.execute(
            "INSERT INTO order_items (order_id, item_name, price, quantity) VALUES (%s, %s, %s, %s)",
            (order_id, item['name'], item['price'], 1)
        )

    db.commit()
    session['cart'] = []

    return "✅ Order Placed Successfully!"

# 🚀 Run app (Render compatible)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)