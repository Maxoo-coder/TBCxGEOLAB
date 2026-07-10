import os
from groq import Groq
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)

app.config["SECRET_KEY"] = "#!@$%^&*(9)maxo"


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "გასაგრძელებლად გთხოვთ გაიაროთ ავტორიზაცია."
login_manager.login_message_category = "warning"


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))