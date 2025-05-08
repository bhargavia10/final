from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager
from wtforms import StringField



# TODO: implement
@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first() 

# TODO: implement fields
class User(db.Document, UserMixin):
    username = db.StringField(required=True, unique=True, min_length=1, max_length=40)
    email = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)
    profile_pic = db.ImageField()
    reviews = db.ListField(db.ReferenceField('Review'))
    reading_list = db.ListField(db.StringField())

    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Returns unique string identifying our object
    def get_id(self):
        # TODO: implement
        return str(self.username)


# TODO: implement fields
class Review(db.Document):
    commenter = db.ReferenceField('User', required=True)  
    book_id = db.StringField(required=True)
    book_title = db.StringField()
    content = db.StringField(required=True)
    date = db.StringField(required=True, default=datetime.now().strftime("%B %d, %Y at %H:%M:%S"))
    image = db.StringField()
