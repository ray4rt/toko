from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "ganti-dengan-secret-key-rahasia"  # ganti sebelum dipakai serius

# ------------------------------------------------------------------
# "Database" sederhana (list di memori). Untuk toko sungguhan,
# ganti bagian ini dengan database asli (SQLite/PostgreSQL, dll).
# ------------------------------------------------------------------
PRODUCTS = [
    {"id": 1, "name": "Kaos Polos Hitam", "price": 75000, "emoji": "👕",
     "description": "Kaos katun combed 30s, nyaman dipakai harian."},
    {"id": 2, "name": "Sepatu Sneakers Putih", "price": 250000, "emoji": "👟",
     "description": "Sneakers ringan, cocok untuk jalan-jalan atau olahraga ringan."},
    {"id": 3, "name": "Tas Ransel Laptop", "price": 180000, "emoji": "🎒",
     "description": "Ransel muat laptop 14 inci, tahan air, banyak kompartemen."},
    {"id": 4, "name": "Topi Baseball", "price": 45000, "emoji": "🧢",
     "description": "Topi adjustable, bahan adem, cocok untuk outdoor."},
    {"id": 5, "name": "Jam Tangan Analog", "price": 320000, "emoji": "⌚",
     "description": "Jam tangan tali kulit, tahan air ringan, desain minimalis."},
    {"id": 6, "name": "Botol Minum 1L", "price": 60000, "emoji": "🧴",
     "description": "Botol stainless steel, menjaga suhu dingin/panas lebih lama."},
]


def get_product(product_id):
    return next((p for p in PRODUCTS if p["id"] == product_id), None)


def get_cart():
    """Ambil keranjang dari session. Bentuk: {product_id_str: qty}"""
    return session.setdefault("cart", {})


def cart_items_detail():
    cart = get_cart()
    items = []
    total = 0
    for pid_str, qty in cart.items():
        product = get_product(int(pid_str))
        if not product:
            continue
        subtotal = product["price"] * qty
        total += subtotal
        items.append({**product, "qty": qty, "subtotal": subtotal})
    return items, total


def format_rupiah(value):
    return f"Rp{value:,.0f}".replace(",", ".")


app.jinja_env.filters["rupiah"] = format_rupiah


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", products=PRODUCTS)


@app.route("/produk/<int:product_id>")
def product_detail(product_id):
    product = get_product(product_id)
    if not product:
        flash("Produk tidak ditemukan.", "error")
        return redirect(url_for("index"))
    return render_template("product_detail.html", product=product)


@app.route("/keranjang/tambah/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = get_product(product_id)
    if not product:
        flash("Produk tidak ditemukan.", "error")
        return redirect(url_for("index"))

    qty = int(request.form.get("qty", 1))
    qty = max(1, qty)

    cart = get_cart()
    pid_str = str(product_id)
    cart[pid_str] = cart.get(pid_str, 0) + qty
    session.modified = True

    flash(f"{product['name']} ditambahkan ke keranjang.", "success")
    return redirect(url_for("index"))


@app.route("/keranjang")
def view_cart():
    items, total = cart_items_detail()
    return render_template("cart.html", items=items, total=total)


@app.route("/keranjang/update/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    qty = int(request.form.get("qty", 1))
    cart = get_cart()
    pid_str = str(product_id)

    if qty <= 0:
        cart.pop(pid_str, None)
    else:
        cart[pid_str] = qty

    session.modified = True
    return redirect(url_for("view_cart"))


@app.route("/keranjang/hapus/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    session.modified = True
    flash("Item dihapus dari keranjang.", "success")
    return redirect(url_for("view_cart"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    items, total = cart_items_detail()

    if not items:
        flash("Keranjang masih kosong.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        address = request.form.get("address", "").strip()

        if not name or not address:
            flash("Nama dan alamat wajib diisi.", "error")
            return render_template("checkout.html", items=items, total=total)

        # Di toko sungguhan: simpan order ke database, proses pembayaran, dll.
        session["cart"] = {}
        session.modified = True

        return render_template(
            "checkout_success.html", name=name, address=address, total=total
        )

    return render_template("checkout.html", items=items, total=total)


if __name__ == "__main__":
    app.run(debug=True)
