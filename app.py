import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

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
users = db["users"]


app = Flask(__name__)
app.secret_key = "super_key_987654321_fija"

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
    cart = session.get("cart", {})
    items = []

    for slug, data in cart.items():
        product = products.find_one({"slug": slug})
        if not product:
            continue

        items.append({
            "product": product,
            "quantity": data.get("quantity", 1)
        })

    return render_template("cart.html", items=items)


@app.route("/cart/add/<slug>", methods=["POST"])
def cart_add(slug):
    cart = get_cart()

    if slug not in cart:
        cart[slug] = {"quantity": 1}
    else:
        cart[slug]["quantity"] += 1

    session["cart"] = cart
    print(session["cart"])

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
    # 1. Validación de usuario
    if "user_id" not in session:
        flash("Debes iniciar sesión para continuar con la compra.", "error")
        return redirect(url_for("login_user"))

    cart = session.get("cart", {})

    # Calcular total
    total = 0
    items = []
    for slug, data in cart.items():
        product = products.find_one({"slug": slug})
        if product:
            qty = data["quantity"]
            items.append({"product": product, "quantity": qty})
            total += float(product["price"]) * qty

    if request.method == "POST":
        card_number = request.form.get("card_number")
        phone = request.form.get("phone")

        # Validaciones
        if not card_number or len(card_number) != 16 or not card_number.isdigit():
            flash("El número de tarjeta debe tener 16 dígitos.", "error")
            return redirect(url_for("checkout"))

        if not phone or len(phone) != 10 or not phone.isdigit():
            flash("El teléfono debe tener 10 dígitos.", "error")
            return redirect(url_for("checkout"))

        flash("Pago realizado con éxito.", "success")
        session["cart"] = {}
        return redirect(url_for("index"))

    return render_template("checkout.html", items=items, total=total)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # verificar si ya existe
        if users.find_one({"email": email}):
            flash("Este correo ya está registrado.")
            return redirect(url_for("register"))

        hashed_pass = generate_password_hash(password)

        users.insert_one({
            "email": email,
            "password": hashed_pass
        })

        flash("Registro exitoso. Ahora inicia sesión.")
        return redirect(url_for("login_user"))

    return render_template("register.html")


@app.route("/login_user", methods=["GET", "POST"])
def login_user():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = users.find_one({"email": email})

        if not user or not check_password_hash(user["password"], password):
            flash("Usuario o contraseña incorrectos.")
            return redirect(url_for("login_user"))

        session["user_id"] = str(user["_id"])
        session["user_email"] = user["email"]
        flash("Has iniciado sesión.")

        return redirect(url_for("index"))

    return render_template("login_user.html")


@app.route("/logout_user")
def logout_user():
    session.pop("user_id", None)
    session.pop("user_email", None)
    flash("Sesión cerrada.")
    return redirect(url_for("index"))


@app.route("/purchase_success")
def purchase_success():
    return render_template("purchase_success.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        flash("Inicia sesión para ver tu perfil.")
        return redirect(url_for("login_user"))

    user = users.find_one({"_id": ObjectId(session["user_id"])})

    if request.method == "POST":
        update = {
            "full_name": request.form["full_name"],
            "phone": request.form["phone"],
            "address": request.form["address"]
        }

        users.update_one({"_id": user["_id"]}, {"$set": update})
        flash("Perfil actualizado.")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)


if __name__ == "__main__":
    app.run(debug=True)
