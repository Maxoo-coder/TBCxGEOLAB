from functools import wraps
from flask import session
from ext import app, db, login_manager, client
from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_user, logout_user, login_required, current_user
from forms import BookForm, RegisterForm, LoginForm, ReviewForm, AskForm
import os
from collections import Counter
from models import Product, User, Review
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("გასაგრძელებლად გაიარეთ ავტორიზაცია.", "warning")
            return redirect(url_for("login"))
        if not current_user.is_admin:
            abort(403)
        return view_func(*args, **kwargs)
    return wrapper


@app.errorhandler(403)
def forbidden(e):
    flash("წვდომა შეზღუდულია — ეს ფუნქცია მხოლოდ ადმინისთვისაა ხელმისაწვდომი.", "danger")
    return redirect(url_for("home"))


@app.route("/")
@app.route("/main")
def home():
    role = 'user'
    cart_items = len(get_cart_items())
    books = Product.query.all()

    featured = Product.query.filter_by(is_featured=True).first()
    if not featured and books:
        featured = books[0]
    rest = [b for b in books if not featured or b.id != featured.id]

    return render_template("main.html", books=books, rest=rest, featured=featured, role=role, cart_items=cart_items)


@app.route("/about_us")
def about_us():
    return render_template("about_us.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            is_admin=False,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash("რეგისტრაცია წარმატებით დასრულდა!", "success")
        return redirect(url_for("home"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash(f"კეთილი იყოს თქვენი დაბრუნება, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("home"))
        flash("მომხმარებლის სახელი ან პაროლი არასწორია.", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("თქვენ გამოხვედით სისტემიდან.", "info")
    return redirect(url_for("home"))


@app.route('/book/<int:book_id>', methods=["GET", "POST"])
def book_detail(book_id):
    book = Product.query.get_or_404(book_id)
    form = ReviewForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("კომენტარის დასატებლად გაიარეთ ავტორიზაცია.", "warning")
            return redirect(url_for("login", next=request.path))

        review = Review(
            text=form.text.data,
            rating=form.rating.data,
            book_id=book.id,
            user_id=current_user.id,
        )
        db.session.add(review)
        db.session.commit()
        flash("თქვენი კომენტარი დაემატა!", "success")
        return redirect(url_for("book_detail", book_id=book.id))

    reviews = Review.query.filter_by(book_id=book.id).order_by(Review.created_at.desc()).all()
    return render_template("second.html", book=book, form=form, reviews=reviews)


@app.route("/add_book", methods=["GET", "POST"])
@admin_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        filename = None
        image = form.image.data
        if image:
            filename = secure_filename(image.filename)
            img_location = os.path.join(app.root_path, "static", "images", filename)
            image.save(img_location)

        new_book = Product(
            title=form.title.data,
            author=form.author.data,
            price=float(form.price.data.replace(' ₾', '').replace(',', '.')),
            desc=form.desc.data,
            image=filename,
            is_featured=form.is_featured.data,
        )
        if form.is_featured.data:
            Product.query.update({Product.is_featured: False})
        db.session.add(new_book)
        db.session.commit()
        flash("წიგნი წარმატებით დაემატა!", "success")
        return redirect(url_for("home"))

    return render_template('add_book.html', form=form)


@app.route('/delete_book/<int:book_id>')
@admin_required
def delete_book(book_id):
    book = Product.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash("წიგნი წაიშალა.", "info")
    return redirect(url_for('home'))


@app.route('/set_featured/<int:book_id>')
@admin_required
def set_featured(book_id):
    book = Product.query.get_or_404(book_id)
    Product.query.update({Product.is_featured: False})
    book.is_featured = True
    db.session.commit()
    flash(f'"{book.title}" დაყენდა რჩეულ წიგნად.', "success")
    return redirect(url_for('home'))


@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    book = Product.query.get_or_404(book_id)
    form = BookForm(obj=book)

    if form.validate_on_submit():
        book.title = form.title.data
        book.author = form.author.data
        book.price = float(form.price.data.replace(' ₾', '').replace(',', '.'))
        book.desc = form.desc.data

        if form.is_featured.data:
            Product.query.filter(Product.id != book.id).update({Product.is_featured: False})
        book.is_featured = form.is_featured.data

        if form.image.data and hasattr(form.image.data, 'filename'):
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.root_path, "static", "images", filename))
            book.image = filename

        db.session.commit()
        flash("წიგნი წარმატებით განახლდა!", "success")
        return redirect(url_for('home'))

    return render_template('add_book.html', form=form, book=book)


@app.route("/admin")
@admin_required
def admin_panel():
    users = User.query.all()
    books_count = Product.query.count()
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template("admin.html", users=users, books_count=books_count, reviews=reviews)


@app.route("/admin/delete_review/<int:review_id>")
@admin_required
def admin_delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    book_id = review.book_id
    db.session.delete(review)
    db.session.commit()
    flash("კომენტარი წაიშალა.", "info")
    return redirect(url_for("book_detail", book_id=book_id))


@app.route("/admin/toggle_admin/<int:user_id>")
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("საკუთარი ადმინის სტატუსის შეცვლა არ შეიძლება.", "warning")
        return redirect(url_for("admin_panel"))

    user.is_admin = not user.is_admin
    db.session.commit()
    flash(f"{user.username}-ის სტატუსი განახლდა.", "success")
    return redirect(url_for("admin_panel"))

def get_cart_items():
    return session.get("cart",[])

@app.route("/cart")
def cart():
    cart_product_ids = get_cart_items()
    length = len(cart_product_ids)
    quantities = Counter(cart_product_ids)
    if cart_product_ids:
        products = Product.query.filter(Product.id.in_(cart_product_ids)).all()
        total_price = sum(p.price * quantities[p.id] for p in products)
    else:
        products = []
        total_price = 0
    return render_template('cart.html', products=products, cart_items=length,
                            quantities=quantities, total_price=total_price)


@app.route('/add_to_cart/<int:item_id>', methods=['GET', 'POST'])
def add_to_cart(item_id):
    cart = session.get('cart', [])
    cart.append(item_id)

    session['cart'] = cart
    session.modified = True

    flash("პროდუქტი დაემატა კალათაში!", "success")
    return redirect("/")

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    session['cart'] = []
    session.modified = True
    flash("შეკვეთა წარმატებით გაფორმდა! მადლობა შეძენისთვის.", "success")
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    cart = session.get('cart', [])
    if item_id in cart:
        cart.remove(item_id)
        session['cart'] = cart

    return redirect("/cart")

@app.route('/ask_ai', methods=['GET', 'POST'])
def ai_page():
    form = AskForm()
    answer = None
    question = None

    if form.validate_on_submit():
        question = form.question.data

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": question,
                    }
                ],

                model="llama-3.3-70b-versatile",

            )
            answer = chat_completion.choices[0].message.content
        except Exception as e:
            answer = f"შეცდომა: {str(e)}"

        form.question.data = ""

    return render_template('ask_ai.html', form=form, answer=answer, question=question)