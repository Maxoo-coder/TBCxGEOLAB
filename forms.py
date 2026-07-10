from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField, IntegerField, BooleanField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError, length
from models import User

class BookForm(FlaskForm):
    title = StringField('სათაური', validators=[DataRequired()])
    author = StringField('ავტორი', validators=[DataRequired()])
    price = StringField('ფასი', validators=[DataRequired()])
    image = FileField('სურათი', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'webp'])])
    desc = TextAreaField('აღწერა', validators=[DataRequired()])
    is_featured = BooleanField('დააყენე რჩეულ წიგნად მთავარ გვერდზე')
    submit = SubmitField('დამატება')


class RegisterForm(FlaskForm):
    username = StringField('მომხმარებლის სახელი', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('ელ-ფოსტა', validators=[DataRequired(), Email()])
    password = PasswordField('პაროლი', validators=[DataRequired(), Length(min=6, message="პაროლი უნდა შედგებოდეს მინიმუმ 6 სიმბოლოსგან")])
    confirm_password = PasswordField('გაიმეორეთ პაროლი', validators=[DataRequired(), EqualTo('password', message="პაროლები არ ემთხვევა")])
    submit = SubmitField('რეგისტრაცია')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError('ეს მომხმარებლის სახელი დაკავებულია.')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('ამ ელ-ფოსტით მომხმარებელი უკვე არსებობს.')


class LoginForm(FlaskForm):
    username = StringField('მომხმარებლის სახელი', validators=[DataRequired()])
    password = PasswordField('პაროლი', validators=[DataRequired()])
    submit = SubmitField('შესვლა')


class ReviewForm(FlaskForm):
    text = TextAreaField('კომენტარი', validators=[DataRequired(), Length(min=2, max=500)])
    rating = IntegerField('შეფასება (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5, message="შეფასება უნდა იყოს 1-დან 5-მდე")])
    submit = SubmitField('გამოქვეყნება')

class AskForm(FlaskForm):
    question = StringField("Ask AI", validators=[DataRequired(), length(max=200, message="Maximum 200 characters allowed.")])
    submit = SubmitField("Send")