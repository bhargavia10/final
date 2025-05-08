from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_required, login_user, logout_user
import base64
from io import BytesIO
from .. import bcrypt
from werkzeug.utils import secure_filename
from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm, UpdateProfilePicForm
from ..models import User, Review
from ..client import BookClient


users = Blueprint("users", __name__)

""" ************ User Management views ************ """


# TODO: implement
@users.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("books.index"))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        user.save()
        return redirect(url_for("users.login"))
    return render_template("register.html", form=form)


# TODO: implement
@users.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("books.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            return redirect(url_for("users.account"))
        flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)


# TODO: implement
@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("books.index"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    update_username_form = UpdateUsernameForm()
    update_profile_pic_form = UpdateProfilePicForm()

    if request.method == "POST":
        if update_username_form.submit_username.data and update_username_form.validate():
            # TODO: handle update username form submit
            new_username = update_username_form.username.data
            existing_user = User.objects(username=new_username).first()
            if existing_user:
                return redirect(url_for("users.account"))
            current_user.modify(username=new_username)
            current_user.save()
            return redirect(url_for("users.account"))

        if update_profile_pic_form.submit_picture.data and update_profile_pic_form.validate():
            # TODO: handle update profile pic form submit
            picture = update_profile_pic_form.picture.data
            filename = secure_filename(picture.filename)
            content_type = f'images/{filename[-3:]}'

            if not current_user.profile_pic:
                current_user.profile_pic.put(picture.stream, content_type=content_type)
            else:
                current_user.profile_pic.replace(picture.stream, content_type=content_type)
            current_user.save()
            return redirect(url_for("users.account"))
    
    profile_pic_data = None
    if current_user.profile_pic:
        profile_pic_binary = current_user.profile_pic.read()
        profile_pic_data = base64.b64encode(profile_pic_binary).decode("utf-8")
    # TODO: handle get requests
    return render_template(
        "account.html",
        update_username_form = update_username_form,
        update_profile_pic_form = update_profile_pic_form,
        profile_pic = profile_pic_data
    )

@users.route("/user/<username>")
@login_required
def user_detail(username):
    user = User.objects(username=username).first()

    if not user:
        return render_template("user_detail.html", error="User not found")

    reviews = Review.objects(commenter=user)
    profile_pic_data = None
    if user.profile_pic:
        profile_pic_binary = user.profile_pic.read()
        profile_pic_data = base64.b64encode(profile_pic_binary).decode("utf-8")

    book_client = BookClient()
    reading_list = []
    for book_id in user.reading_list:
        try:
            book_data = book_client.retrieve_book_by_id(book_id)
            info = book_data.get("volumeInfo", {})
            reading_list.append({
                "id": book_id,
                "title": info.get("title", "No Title"),
                "author": ", ".join(info.get("authors", ["Unknown Author"])),
                "cover_url": info.get("imageLinks", {}).get("thumbnail", url_for("static", filename="no_cover.png")),
            })
        except Exception:
            continue

    return render_template("user_detail.html", user=user, reviews=reviews, profile_pic=profile_pic_data, reading_list=reading_list)

@users.route("/add-to-reading-list/<book_id>", methods=["POST"])
@login_required
def add_to_reading_list(book_id):
    user = User.objects(username=current_user.username).first()
    if user:
        if book_id not in user.reading_list:
            user.reading_list.append(book_id)
            user.save()
    return redirect(url_for("books.book_detail", book_id=book_id))