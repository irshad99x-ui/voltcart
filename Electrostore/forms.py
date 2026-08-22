from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    TextAreaField, FloatField, IntegerField, SelectField
)
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from models import User, Category, Product

class LoginForm(FlaskForm):
    login_id = StringField('Email or Username', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=40)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.strip()).first()
        if user:
            raise ValidationError('This username is already taken. Please choose another.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.strip().lower()).first()
        if user:
            raise ValidationError('An account with this email address already exists.')


class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=30)])
    address = StringField('Street Address', validators=[Optional(), Length(max=255)])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    state = StringField('State / Province', validators=[Optional(), Length(max=100)])
    postal_code = StringField('Postal / ZIP Code', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Save Profile')


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long.')
    ])
    confirm_new_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match.')
    ])
    submit = SubmitField('Update Password')


class CheckoutForm(FlaskForm):
    customer_name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=7, max=30)])
    shipping_address = StringField('Street Address', validators=[DataRequired(), Length(max=255)])
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
    state = StringField('State / Province', validators=[DataRequired(), Length(max=100)])
    postal_code = StringField('Postal / ZIP Code', validators=[DataRequired(), Length(max=20)])
    notes = TextAreaField('Order Notes (Optional)', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Confirm & Place Order')


class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        ('5', '★★★★★ (5 - Excellent)'),
        ('4', '★★★★☆ (4 - Very Good)'),
        ('3', '★★★☆☆ (3 - Average)'),
        ('2', '★★☆☆☆ (2 - Poor)'),
        ('1', '★☆☆☆☆ (1 - Terrible)')
    ], default='5', validators=[DataRequired()])
    title = StringField('Review Title', validators=[DataRequired(), Length(min=3, max=120)])
    comment = TextAreaField('Review Content', validators=[DataRequired(), Length(min=10, max=1500)])
    submit = SubmitField('Submit Review')


class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=255)])
    brand = StringField('Brand', validators=[DataRequired(), Length(max=100)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    price = FloatField('Price ($)', validators=[DataRequired(), NumberRange(min=0.01)])
    original_price = FloatField('Original Price ($) (Optional)', validators=[Optional(), NumberRange(min=0)])
    stock_quantity = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0)])
    sku = StringField('SKU / Product Code', validators=[DataRequired(), Length(max=64)])
    short_description = TextAreaField('Short Summary', validators=[Optional(), Length(max=350)])
    description = TextAreaField('Full Description', validators=[Optional()])
    specs_json = TextAreaField('Specs (JSON Format: {"Display": "6.7 inch", "RAM": "12GB"})', validators=[Optional()])
    is_featured = BooleanField('Featured Product')
    is_trending = BooleanField('Trending Item')
    is_on_sale = BooleanField('On Sale')
    primary_image_url = StringField('Primary Image URL', validators=[DataRequired(), Length(max=500)])
    extra_images = TextAreaField('Additional Image URLs (One URL per line)', validators=[Optional()])
    submit = SubmitField('Save Product')


class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(max=100)])
    slug = StringField('Slug (Optional - auto generated if empty)', validators=[Optional(), Length(max=120)])
    description = TextAreaField('Description', validators=[Optional()])
    icon_class = StringField('FontAwesome Icon Class (e.g. fa-solid fa-laptop)', validators=[Optional(), Length(max=100)])
    image_url = StringField('Category Image URL', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Category')


class CouponForm(FlaskForm):
    code = StringField('Promo Code', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Apply')