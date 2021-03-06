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
app = Flask(__name__)                                               # Flask Server Creation
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'       # Secret key example
ckeditor = CKEditor(app)                                            # CKE Editor for blog content.
Bootstrap(app)                                                      # Implementing bootstrap


# ---------------------------------- DATABASE ---------------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'        # Database Link
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False                # Disabling outdated config
db = SQLAlchemy(app)                                                # Creating the App


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
    # Form Structure
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField('Body')
    submit = SubmitField("Submit Post")


# --------------------------------- FUNCTIONS ---------------------------------
def get_all_posts():
    # This function returns all posts from the DB
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

    if create_post_form.validate_on_submit():
        # If the user is submitting the form (POST Method),
        # a new BlogPost object is created with the submitted info:
        new_post = BlogPost(
            title=create_post_form.title.data,
            subtitle=create_post_form.subtitle.data,
            date=blog_timing.get_post_timing(),         # Date comes from datetime python module.
            body=create_post_form.body.data,
            author=create_post_form.author.data,
            img_url=create_post_form.img_url.data,
        )

        try:
            # Creating a new Post in the Database.
            db.session.add(new_post)    # Adding the Post
            db.session.commit()         # Commiting the Change.

        except exc.IntegrityError:
            # If Post already exists, the code returns an error message.
            print("Error! Post already exists!")

        # Finally, the index page is rendered with the new post!
        posts = get_all_posts()
        return render_template("index.html", all_posts=posts)

    # If the user is first accessing the New Post page
    # (GET Method), the form is loaded.
    posts = get_all_posts()
    return render_template("make-post.html", all_posts=posts, form=create_post_form, page_header="New Post")


@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit_post(index):
    # Edit post routing, for when the client wants to change post info.
    posts = db.session.query(BlogPost).all()
    requested_post = posts[index - 1]

    for blog_post in posts:
        # +1 because for index correction
        if posts.index(blog_post) + 1 == index:
            requested_post = blog_post

    # Creating a form with the existing object so that all the info
    # is displayed to the user.
    edit_post_form = CreatePostForm(
        title=requested_post.title,
        subtitle=requested_post.subtitle,
        img_url=requested_post.img_url,
        author=requested_post.author,
        body=requested_post.body
    )

    # If the user is submitting the form (POST Method),
    # the existing BlogPost object is updated with the new data:
    if edit_post_form.validate_on_submit():

        # Finding the correct post to edit
        post_to_edit = db.session.query(BlogPost).filter_by(id=index).first()

        # Updating every field from form info (date remains the same)
        post_to_edit.title = edit_post_form.title.data
        post_to_edit.subtitle = edit_post_form.subtitle.data
        post_to_edit.body = edit_post_form.body.data
        post_to_edit.author = edit_post_form.author.data
        post_to_edit.img_url = edit_post_form.img_url.data

        # Commiting the changes
        db.session.commit()

        # Finally, the index page is rendered with the edited post!
        posts = get_all_posts()
        return render_template("index.html", all_posts=posts)

    # If the user is first accessing the Edit Post page
    # (GET Method), the form is loaded with existing info.
    return render_template("make-post.html", all_posts=posts, form=edit_post_form, page_header="Edit Post")


@app.route("/delete/<int:index>", methods=["GET", "POST"])
def delete_post(index):
    # Delete post routing, for when user wants to delete a post and clicks on
    # its respective "x" mark by the date information.

    post_to_delete = db.session.query(BlogPost).filter_by(id=index).first()     # Filters the post by ID
    db.session.delete(post_to_delete)                                           # Deletes the post
    db.session.commit()                                                         # Commits the change
    posts = get_all_posts()
    return render_template("index.html", all_posts=posts)


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