from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import os
import requests
import io
import shutil

app = Flask(__name__)

# AUTOMATIC FOLDER & FILE GENERATOR SETUP
def auto_setup():
    print("--- Gaurav Shopping Store Auto-Setup Started ---")
    
    # 1. Folders automatic banana
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    
    # 2. Photos ko automatic static folder me move aur rename karna
    possible_logos = ["file_00000000bb3871f88efc581b22f53120[1]_2.png", "logo.png"]
    possible_banners = ["file_0000000088ac720b867cec48d3e0e427[1]_2.png", "banner.png"]
    
    for logo in possible_logos:
        if os.path.exists(logo) and logo != "static/logo.png":
            shutil.copy(logo, "static/logo.png")
            
    for banner in possible_banners:
        if os.path.exists(banner) and banner != "static/banner.png":
            shutil.copy(banner, "static/banner.png")

    # 3. HTML File automatic create karna templates folder ke andar
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gaurav Shopping Store</title>
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 0; }
        body { background-color: #fcfbf7; color: #333; }
        .brand-banner { width: 100%; max-height: 400px; object-fit: cover; display: block; box-shadow: 0 4px 15px rgba(0,0,0,0.15); }
        header { background: #111; color: white; padding: 25px; text-align: center; display: flex; align-items: center; justify-content: center; gap: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        .brand-logo { height: 65px; width: auto; border-radius: 50%; border: 2px solid #e5a93c; }
        .container { max-width: 1200px; margin: 0 auto; padding: 30px 20px; }
        .seller-form { background: white; padding: 30px; border-radius: 12px; border: 1px solid #e5a93c; margin-bottom: 40px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: bold; color: #444; }
        .form-group input { width: 100%; padding: 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 14px; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); justify-content: center; align-items: center; z-index: 1000; }
        .modal-content { background: white; padding: 35px; border-radius: 12px; width: 90%; max-width: 500px; position: relative; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
        .close-btn { position: absolute; top: 12px; right: 20px; font-size: 28px; cursor: pointer; color: #aaa; }
        .search-box { width: 100%; padding: 15px 20px; border: 2px solid #e5a93c; border-radius: 30px; margin-bottom: 40px; font-size: 16px; outline: none; background: white; }
        .catalog { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 30px; }
        .product-card { border: 1px solid #eee; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 6px 15px rgba(0,0,0,0.05); background: white; transition: all 0.3s ease; }
        .product-card:hover { transform: translateY(-5px); box-shadow: 0 12px 25px rgba(0,0,0,0.12); border-color: #e5a93c; }
        .product-card img { width: 100%; height: 230px; object-fit: cover; border-radius: 8px; margin-bottom: 15px; }
        .price { color: #e5a93c; font-size: 22px; font-weight: bold; margin: 12px 0; }
        .btn { background: #e5a93c; color: black; border: none; padding: 14px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; font-size: 16px; }
        .btn:hover { background: #cca43b; color: white; }
        .btn-delete { background: #f44336; color: white; margin-top: 10px; }
    </style>
</head>
<body>
<img src="/static/banner.png" alt="Gaurav Shopping Store Banner" class="brand-banner" onerror="this.style.display='none'">
<header>
    <img src="/static/logo.png" alt="Logo" class="brand-logo" onerror="this.style.display='none'">
    <div>
        <h1 style="font-size: 28px; letter-spacing: 1px;">Gaurav Shopping Store</h1>
        <p style="color: #e5a93c; font-weight: bold; margin-top: 5px;">{{ 'SELLER MANAGEMENT PANEL' if mode == 'seller' else 'Your Beauty, Our Priority' }}</p>
    </div>
</header>
<div class="container">
    {% if mode == 'seller' %}
    <div class="seller-form">
        <h2>Upload New Catalog Item</h2>
        <form action="/add_product" method="POST">
            <div class="form-group"><label>Product Name:</label><input type="text" name="name" required></div>
            <div class="form-group"><label>Price (INR):</label><input type="number" name="price" required></div>
            <div class="form-group"><label>Image URL:</label><input type="url" name="image_url" required></div>
            <div class="form-group"><label>Category:</label><input type="text" name="category"></div>
            <button type="submit" class="btn">Upload & Live on Website</button>
        </form>
    </div>
    {% endif %}
    {% if mode == 'customer' %}
    <input type="text" id="searchBar" class="search-box" onkeyup="filterProducts()" placeholder="Search cosmetics...">
    {% endif %}
    <h2>Live Inventory ({{ products|length }} Items)</h2><br>
    <div class="catalog" id="catalogGrid">
        {% for product in products %}
        <div class="product-card" data-name="{{ product[1]|lower }}">
            <img src="{{ product[3] }}" alt="{{ product[1] }}" onerror="this.src='https://via.placeholder.com/250x230?text=No+Image'">
            <h3>{{ product[1] }}</h3><p class="price">₹{{ product[2] }}</p>
            {% if mode == 'customer' %}
                <button class="btn" onclick="openAddressModal('{{ product[1] }}', '{{ product[2] }}')">Buy Now</button>
            {% else %}
                <a href="/delete_product/{{ product[0] }}"><button class="btn btn-delete">Remove Item</button></a>
            {% endif %}
        </div>
        {% endfor %}
    </div>
</div>
<div id="addressModal" class="modal">
    <div class="modal-content">
        <span class="close-btn" onclick="closeModal()">&times;</span>
        <h2>Delivery Address</h2>
        <div class="form-group"><label>Full Name:</label><input type="text" id="c_name" required></div>
        <div class="form-group"><label>Phone Number:</label><input type="text" id="c_phone" required></div>
        <div class="form-group"><label>Complete Address:</label><input type="text" id="c_address" required></div>
        <div class="form-group"><label>City:</label><input type="text" id="c_city" required></div>
        <div class="form-group"><label>Pincode:</label><input type="text" id="c_pincode" required></div>
        <div class="form-group"><label>State:</label><input type="text" id="c_state" required></div>
        <button class="btn" onclick="payNow()">Proceed to Pay</button>
    </div>
</div>
<script>
    let currentProduct = "", currentPrice = "";
    function filterProducts() {
        let input = document.getElementById('searchBar').value.toLowerCase();
        let cards = document.getElementsByClassName('product-card');
        for (let i = 0; i < cards.length; i++) {
            let name = cards[i].getAttribute('data-name');
            cards[i].style.display = name.includes(input) ? "" : "none";
        }
    }
    function openAddressModal(name, price) { currentProduct = name; currentPrice = price; document.getElementById('addressModal').style.display = 'flex'; }
    function closeModal() { document.getElementById('addressModal').style.display = 'none'; }
    function payNow() {
        const c_name = document.getElementById('c_name').value;
        const c_phone = document.getElementById('c_phone').value;
        const c_address = document.getElementById('c_address').value;
        const c_city = document.getElementById('c_city').value;
        const c_pincode = document.getElementById('c_pincode').value;
        const c_state = document.getElementById('c_state').value;
        if(!c_name || !c_phone || !c_address || !c_city || !c_pincode || !c_state) { alert("Please fill all fields!"); return; }
        closeModal();
        var options = {
            "key": "{{ key_id }}", "amount": parseInt(currentPrice) * 100, "currency": "INR", "name": "Gaurav Shopping Store",
            "description": "Order for " + currentProduct,
            "handler": function (response){
                alert("Payment Successful! Downloading label...");
                fetch('/process_order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ product_name: currentProduct, product_price: currentPrice, c_name: c_name, c_phone: c_phone, c_address: c_address, c_city: c_city, c_pincode: c_pincode, c_state: c_state })
                }).then(res => res.json()).then(data => { if(data.status === 'success') { window.location.href = data.label_url; } else { alert(data.message); } });
            }, "theme": { "color": "#e5a93c" }
        };
        var rzp1 = new Razorpay(options); rzp1.open();
    }
</script>
</body>
</html>"""
    
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✓ Everything is setup perfectly automatically!")

# DATABASE INITIALIZATION
def init_db():
    conn = sqlite3.connect('store.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, price REAL NOT NULL, image_url TEXT, category TEXT)')
    conn.commit()
    conn.close()

RAZORPAY_KEY_ID = "rzp_live_T6gQmmJ8KCzf3b"
RAZORPAY_KEY_SECRET = "zkCC3zX2ijvblCab8Z0SKF8D"
SHIPROCKET_EMAIL = "YOUR_SHIPROCKET_EMAIL"  # <-- Yahan apna asli email dalo
SHIPROCKET_PASSWORD = "TABEyN7WZrsibu1VrrLoedBl41Ho#k84"

def get_shiprocket_token():
    url = "https://apiv2.shiprocket.in/v1/external/auth/login"
    try:
        res = requests.post(url, json={"email": SHIPROCKET_EMAIL, "password": SHIPROCKET_PASSWORD}).json()
        return res.get('token')
    except: return None

@app.route('/')
def customer_page():
    conn = sqlite3.connect('store.db')
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products, key_id=RAZORPAY_KEY_ID, mode="customer")

@app.route('/seller')
def seller_page():
    conn = sqlite3.connect('store.db')
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products, mode="seller")

@app.route('/add_product', methods=['POST'])
def add_product():
    conn = sqlite3.connect('store.db')
    conn.execute('INSERT INTO products (name, price, image_url, category) VALUES (?, ?, ?, ?)', (request.form['name'], request.form['price'], request.form['image_url'], request.form['category']))
    conn.commit()
    conn.close()
    return redirect(url_for('seller_page'))

@app.route('/delete_product/<int:id>')
def delete_product(id):
    conn = sqlite3.connect('store.db')
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('seller_page'))

@app.route('/process_order', methods=['POST'])
def process_order():
    data = request.json
    token = get_shiprocket_token()
    if not token: return {"status": "error", "message": "Token Failed"}, 400
    
    order_payload = {
        "order_id": "GSR_" + os.urandom(3).hex().upper(), "order_date": "2026-06-27", "pickup_location": "Primary",
        "billing_customer_name": data.get('c_name'), "billing_last_name": "", "billing_address": data.get('c_address'),
        "billing_city": data.get('c_city'), "billing_pincode": data.get('c_pincode'), "billing_state": data.get('c_state'),
        "billing_country": "India", "billing_email": "customer@gmail.com", "billing_phone": data.get('c_phone'),
        "shipping_is_billing": True, "order_items": [{"name": data.get('product_name'), "sku": "COSMETIC_SKU", "units": 1, "selling_price": float(data.get('product_price'))}],
        "payment_method": "Prepaid", "sub_total": float(data.get('product_price')), "length": 10, "breadth": 10, "height": 5, "weight": 0.2
    }
    
    res = requests.post("https://apiv2.shiprocket.in/v1/external/orders/create/adhoc", json=order_payload, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}).json()
    shipment_id = res.get('shipment_id')
    if shipment_id:
        lbl = requests.post("https://apiv2.shiprocket.in/v1/external/courier/generate/label", json={"shipment_id": [shipment_id]}, headers={"Authorization": f"Bearer {token}"}).json()
        if lbl.get('label_created') == 1: return {"status": "success", "label_url": lbl.get('label_url')}
    return {"status": "error", "message": "Label generation failed"}, 400

if __name__ == '__main__':
    auto_setup()
    init_db()
    app.run(debug=True, port=5000)