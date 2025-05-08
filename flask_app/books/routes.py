import base64,io
from io import BytesIO
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user
from PIL import Image
from ..client import BookClient
from ..forms import BookReviewForm, SearchForm
from ..models import User, Review
from ..utils import current_time

books = Blueprint("books", __name__)
book_client = BookClient()

""" ************ Helper for pictures uses username to get their profile picture************ """
def get_b64_img(username):
    user = User.objects(username=username).first()
    if user and user.profile_pic:
        image = Image.open(user.profile_pic)
    else:
        image = Image.open("static/images/default.jpg")
    
    image = image.resize((80, 80))

    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


""" ************ View functions ************ """


@books.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for("books.query_results", query=form.search_query.data))

    return render_template("index.html", form=form)


@books.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    try:
        raw_books = book_client.search_books(query)
    except ValueError as e:
        return render_template("query.html", error_msg=str(e), results=[])

    results = []
    for book in raw_books:
        info = book.get("volumeInfo", {})
        book_id = book.get("id", "")
        results.append({
            "id": book_id,
            "title": info.get("title", "No Title"),
            "author": ", ".join(info.get("authors", ["Unknown Author"])),
            "cover_url": info.get("imageLinks", {}).get("thumbnail", url_for("static", filename="no_cover.png")),
        })
    return render_template("query.html", results=results)


@books.route("/books/<book_id>", methods=["GET", "POST"])
def book_detail(book_id):
    try:
        result = book_client.retrieve_book_by_id(book_id)
    except ValueError as e:
        return render_template("book_detail.html", error_msg=str(e))

    form = BookReviewForm()
    if form.validate_on_submit():
        review = Review(
            commenter=current_user._get_current_object(),
            content=form.text.data,
            date=current_time(),
            book_id=book_id,
            book_title=result.get("volumeInfo", {}).get("title", "Unknown Title"),
        )
        review.save()
        return redirect(request.path)

    reviews = Review.objects(book_id=book_id)
    for review in reviews:
        review.image = get_b64_img(review.commenter.username)
        
    volume_info = result.get("volumeInfo", {})
    book = {
        "title": volume_info.get("title", "No Title"),
        "year": volume_info.get("publishedDate", "Unknown Year")[:4],
        "author": ", ".join(volume_info.get("authors", ["Unknown Author"])),
        "genres": ", ".join(volume_info.get("categories", ["Unknown Genre"])),
        "publisher": volume_info.get("publisher", "Unknown Publisher"),
        "cover_url": volume_info.get("imageLinks", {}).get("thumbnail", url_for("static", filename="no_cover.png")),
    }

    return render_template("book_detail.html", form=form, book=book, reviews=reviews)


@books.route("/user/<username>", methods=["GET", "POST"])
def user_detail(username):
    user = User.objects(username=username).first()
    img = get_b64_img(user.username)
    return render_template("user_detail.html", user=user, img=img)




