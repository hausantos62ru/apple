import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("ARCHIVOS EN EL DIRECTORIO:", os.listdir())
print("MONGO_URI CARGADO:", os.getenv("MONGO_URI"))

MONGO_URI = os.getenv("MONGO_URI")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

if not MONGO_URI:
    raise Exception("Debes definir la variable de entorno MONGO_URI")

client = MongoClient(MONGO_URI)

# Obtener base de datos definida en la URI
default_db = client.get_default_database()

# Si la URI no trae nombre de BD, usar apple_store
db = default_db if default_db is not None else client["apple_store"]

products = db["products"]

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Rutas principales


@app.route("/")
def index():
    all_products = list(products.find())
    return render_template("index.html", products=all_products)


@app.route("/product/<slug>")
def product_detail(slug):
    product = products.find_one({"slug": slug})

    if not product:
        return "Producto no encontrado", 404

    return render_template("product_detail.html", product=product)


# Admin


@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    all_products = list(products.find())
    return render_template("admin.html", products=all_products)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("admin"))
        else:
            flash("Contraseña incorrecta")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# CRUD


@app.route("/admin/add", methods=["GET", "POST"])
@app.route("/admin/add", methods=["GET", "POST"])
def admin_add():
    if request.method == "POST":
        new_product = {
            "title": request.form["title"],
            "slug": request.form.get("slug", ""),
            "price": float(request.form["price"]),
            "description": request.form["description"],
            "image_url": request.form.get("image_url", "")
        }

        products.insert_one(new_product)
        return redirect(url_for("admin"))

    return render_template("admin_add.html")


@app.route("/admin/edit/<id>", methods=["GET", "POST"])
def edit_product(id):
    product = products.find_one({"_id": ObjectId(id)})

    if request.method == "POST":
        update = {
            "title": request.form["title"],
            "slug": request.form.get("slug", ""),
            "price": float(request.form["price"]),
            "description": request.form["description"],
            "image_url": request.form["image_url"]
        }

        products.update_one({"_id": ObjectId(id)}, {"$set": update})
        return redirect(url_for("admin"))

    return render_template("edit_product.html", product=product)


@app.route("/admin/delete/<id>")
def delete_product(id):
    products.delete_one({"_id": ObjectId(id)})
    return redirect(url_for("admin"))


def get_cart():
    return session.get("cart", {})


@app.route("/cart")
def cart_view():
    cart = get_cart()
    cart_items = []

    for slug, item in cart.items():
        product = products.find_one({"slug": slug})
        if product:
            cart_items.append({
                "product": product,
                "quantity": item["quantity"]
            })

    return render_template("cart.html", items=cart_items)


@app.route("/cart/add/<slug>", methods=["POST"])
def cart_add(slug):
    cart = get_cart()

    if slug not in cart:
        cart[slug] = {"quantity": 1}
    else:
        cart[slug]["quantity"] += 1

    session["cart"] = cart
    return redirect(url_for("cart_view"))


@app.route("/cart/remove/<slug>")
def cart_remove(slug):
    cart = get_cart()

    if slug in cart:
        del cart[slug]

    session["cart"] = cart
    return redirect(url_for("cart_view"))


@app.route("/cart/update/<slug>/<action>")
def cart_update(slug, action):
    cart = get_cart()

    if slug in cart:
        if action == "plus":
            cart[slug]["quantity"] += 1
        elif action == "minus":
            cart[slug]["quantity"] -= 1
            if cart[slug]["quantity"] <= 0:
                del cart[slug]

    session["cart"] = cart
    return redirect(url_for("cart_view"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        # Aquí simulas el pago exitoso
        session["cart"] = {}  # Vacía el carrito tras pagar
        flash("Pago procesado correctamente. ¡Gracias por tu compra!", "success")
        return redirect(url_for("index"))

    return render_template("checkout.html")


if __name__ == "__main__":
    app.run(debug=True)
