# ---------------------------------- IMPORTS ----------------------------------
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from sqlalchemy import exc
import blog_timing


# ---------------------------------- SERVER -----------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)


# ---------------------------------- DATABASE ---------------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ---------------------------------- CLASSES ----------------------------------
class BlogPost(db.Model):
    # Database Table
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


class CreatePostForm(FlaskForm):
    # Form
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    # body = StringField("Blog Content", validators=[DataRequired()])
    body = CKEditorField('Body')
    submit = SubmitField("Submit Post")


# --------------------------------- FUNCTIONS ---------------------------------
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return posts


# ---------------------------------- ROUTING ----------------------------------
@app.route('/')
def home():
    # Default Home routing. This function renders the homepage of the blog.
    posts = get_all_posts()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    # Show Post routing, this is the function activated when the user wants
    # to open a specific blog post.
    posts = db.session.query(BlogPost).all()
    requested_post = posts[index-1]

    for blog_post in posts:
        # +1 because for index correction
        if posts.index(blog_post) + 1 == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


@app.route("/new-post", methods=["GET", "POST"])
def create_post():
    # Create post routing, for when the client wants to create a new post.
    create_post_form = CreatePostForm()
    posts = db.session.query(BlogPost).all()

    if create_post_form.validate_on_submit():

        new_post = BlogPost(
            title=create_post_form.title.data,
            subtitle=create_post_form.subtitle.data,
            date=blog_timing.get_post_timing(),
            body=create_post_form.body.data,
            author=create_post_form.author.data,
            img_url=create_post_form.img_url.data,
        )

        try:
            # Creating a new Cafe to the Database.
            db.session.add(new_post)  # Adding the Post
            db.session.commit()  # Commiting the Change.

        except exc.IntegrityError:
            # If Post already exists, the code returns an error message.
            print("Error! Post already exists!")

        posts = get_all_posts()
        return render_template("index.html", all_posts=posts)

    posts = get_all_posts()
    return render_template("make-post.html", all_posts=posts, form=create_post_form)


@app.route("/edit")
def edit_post():
    # Edit post routing, for when the client wants to change post info.
    posts = db.session.query(BlogPost).all()
    return render_template("make-post.html", all_posts=posts)


@app.route("/about")
def about():
    # About routing, for when the client clicks "About"
    return render_template("about.html")


@app.route("/contact")
def contact():
    # Contact routing, for when the client clicks "contact"
    return render_template("contact.html")


# ---------------------------------- RUNNING ----------------------------------
if __name__ == "__main__":
    app.run(debug=True)