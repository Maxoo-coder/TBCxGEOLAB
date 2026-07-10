from werkzeug.security import generate_password_hash

from ext import db, app
from models import Product, User


with app.app_context():

    db.drop_all()
    db.create_all()

    admin = User(
        username="admin",
        email="admin@bookverse.ge",
        password_hash=generate_password_hash("admin123"),
        is_admin=True,
    )
    db.session.add(admin)
    db.session.commit()

    print("ბაზა წარმატებით შეიქმნა")
    print("ადმინის მონაცემები -> მომხმარებელი: admin | პაროლი: admin123 (გთხოვთ შეცვალოთ პაროლი production-ში)")