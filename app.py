from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "demo-secret-key"

PRODUCTS = [
    {"id": 1, "name": "iPhone 15 Pro", "price": 28990000, "category": "Điện thoại",
     "image": "https://via.placeholder.com/300x300/2563eb/ffffff?text=iPhone+15+Pro",
     "description": "iPhone 15 Pro với chip A17 Pro mạnh mẽ, camera 48MP, titanium design.", "stock": 10},
    {"id": 2, "name": "Samsung Galaxy S24", "price": 22990000, "category": "Điện thoại",
     "image": "https://via.placeholder.com/300x300/16a34a/ffffff?text=Galaxy+S24",
     "description": "Samsung Galaxy S24 với AI tích hợp, màn hình Dynamic AMOLED 2X.", "stock": 15},
    {"id": 3, "name": "MacBook Air M3", "price": 32990000, "category": "Laptop",
     "image": "https://via.placeholder.com/300x300/9333ea/ffffff?text=MacBook+Air",
     "description": "MacBook Air M3 siêu mỏng nhẹ, pin 18 giờ, hiệu năng vượt trội.", "stock": 5},
    {"id": 4, "name": "Dell XPS 15", "price": 45990000, "category": "Laptop",
     "image": "https://via.placeholder.com/300x300/dc2626/ffffff?text=Dell+XPS+15",
     "description": "Dell XPS 15 OLED, Intel Core i9, RTX 4070, màn hình 4K.", "stock": 3},
    {"id": 5, "name": "AirPods Pro 2", "price": 6490000, "category": "Phụ kiện",
     "image": "https://via.placeholder.com/300x300/0891b2/ffffff?text=AirPods+Pro",
     "description": "AirPods Pro 2 với chống ồn chủ động, Adaptive Audio, USB-C.", "stock": 20},
    {"id": 6, "name": "iPad Pro M4", "price": 26990000, "category": "Máy tính bảng",
     "image": "https://via.placeholder.com/300x300/d97706/ffffff?text=iPad+Pro+M4",
     "description": "iPad Pro M4 màn hình OLED 13 inch, chip M4, mỏng nhất từ trước đến nay.", "stock": 8},
    {"id": 7, "name": "Sony WH-1000XM5", "price": 8990000, "category": "Phụ kiện",
     "image": "https://via.placeholder.com/300x300/be185d/ffffff?text=Sony+WH1000",
     "description": "Tai nghe Sony WH-1000XM5, chống ồn hàng đầu, pin 30 giờ.", "stock": 12},
    {"id": 8, "name": "Apple Watch Series 9", "price": 11990000, "category": "Phụ kiện",
     "image": "https://via.placeholder.com/300x300/065f46/ffffff?text=Apple+Watch",
     "description": "Apple Watch Series 9 với Double Tap, sáng nhất từ trước tới nay.", "stock": 7},
]


def get_product(pid):
    return next((p for p in PRODUCTS if p["id"] == pid), None)


def get_cart():
    return session.get("cart", {})


def cart_count():
    return sum(get_cart().values())


def cart_total():
    cart = get_cart()
    total = 0
    for pid, qty in cart.items():
        p = get_product(int(pid))
        if p:
            total += p["price"] * qty
    return total


@app.context_processor
def inject_cart():
    return {"cart_count": cart_count()}


@app.route("/")
def index():
    category = request.args.get("category", "")
    search = request.args.get("search", "").lower()
    products = PRODUCTS
    if category:
        products = [p for p in products if p["category"] == category]
    if search:
        products = [p for p in products if search in p["name"].lower() or search in p["description"].lower()]
    categories = sorted(set(p["category"] for p in PRODUCTS))
    return render_template("index.html", products=products, categories=categories,
                           selected_category=category, search=search)


@app.route("/product/<int:pid>")
def product(pid):
    p = get_product(pid)
    if not p:
        return redirect(url_for("index"))
    related = [x for x in PRODUCTS if x["category"] == p["category"] and x["id"] != pid][:3]
    return render_template("product.html", product=p, related=related)


@app.route("/cart")
def cart():
    cart = get_cart()
    items = []
    for pid, qty in cart.items():
        p = get_product(int(pid))
        if p:
            items.append({**p, "qty": qty, "subtotal": p["price"] * qty})
    return render_template("cart.html", items=items, total=cart_total())


@app.route("/cart/add/<int:pid>", methods=["POST"])
def add_to_cart(pid):
    qty = int(request.form.get("qty", 1))
    cart = get_cart()
    key = str(pid)
    cart[key] = cart.get(key, 0) + qty
    session["cart"] = cart
    return redirect(request.referrer or url_for("index"))


@app.route("/cart/update/<int:pid>", methods=["POST"])
def update_cart(pid):
    qty = int(request.form.get("qty", 1))
    cart = get_cart()
    key = str(pid)
    if qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = qty
    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/cart/remove/<int:pid>", methods=["POST"])
def remove_from_cart(pid):
    cart = get_cart()
    cart.pop(str(pid), None)
    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/cart/clear", methods=["POST"])
def clear_cart():
    session["cart"] = {}
    return redirect(url_for("cart"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        session["cart"] = {}
        return render_template("success.html")
    cart = get_cart()
    items = []
    for pid, qty in cart.items():
        p = get_product(int(pid))
        if p:
            items.append({**p, "qty": qty, "subtotal": p["price"] * qty})
    return render_template("checkout.html", items=items, total=cart_total())


@app.route("/about")
def about():
    return render_template("about.html")


@app.template_filter("vnd")
def vnd_format(value):
    return f"{value:,.0f}₫"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
