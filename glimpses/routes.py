from datetime import datetime

from flask import redirect, render_template, request, url_for, make_response
from flask_login import login_required
from sqlalchemy import or_

from glimpses import app
from glimpses.model import Category, Post, db


@app.route("/")
@login_required
def home():
    view = request.args.get("show", "all")

    blank_msg = "No Posts"
    categories = Category.query.all()

    if view == "categories":
        posts = Post.query.order_by(Post.category.desc())
        title = "POSTS ARRANGED TO CATEGORIES"
    elif view == "all":
        posts = Post.query.order_by(Post.created_on.desc())
        title = "ALL POSTS"
    elif view == "starred":
        posts = Post.query.order_by(Post.created_on.desc()).filter_by(is_starred=True)
        title = "STARRED POSTS"
        blank_msg = "No starred Posts"
    elif view == "length":
        posts = Post.query.order_by(Post.length.desc())
        title = "POST SORTED BY LENGTH"

    return render_template(
        "home.html",
        title=title,
        posts=posts,
        categories=categories,
        view=view,
        blank_msg=blank_msg,
    )


@app.route("/<int:id>", methods=["GET", "POST"])
@login_required
def post(id):
    post = Post.query.get_or_404(id)
    if request.method == "POST":
        post.title = request.form["title"]
        post.content = request.form["content"]
        post.length = len(post.content.strip())
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("post.html", post=post, time=None)


@app.route("/new", methods=["GET", "POST"])
@login_required
def new_post():
    time = datetime.utcnow()
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        length = len(content.strip())
        post = Post(title=title, content=content, created_on=time, length=length)
        _all = Category.query.get_or_404(1)
        _all.posts.append(post)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("post.html", post=None, time=time)


@app.route("/tstar/<int:id>")
@login_required
def toggle_starring(id):
    post = Post.query.get_or_404(id)
    post.is_starred = not post.is_starred
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/search")
@login_required
def search():
    query = request.args.get("query", "").strip()
    posts = Post.query.filter(
        or_(Post.title.ilike(f"%{query}%"), Post.content.ilike(f"%{query}%"))
    ).all()
    categories = Category.query.all()

    return render_template(
        "home.html",
        title=f"search results for {query}".capitalize(),
        posts=posts,
        categories=categories,
        view="search results",
        blank_msg="No search results",
    )


@app.route("/category/<int:id>")
@login_required
def category(id):
    category = Category.query.get_or_404(id)
    posts = category.posts
    categories = Category.query.all()

    return render_template(
        "home.html",
        title=f"posts in category {category.name}",
        posts=posts,
        categories=categories,
        view="category",
        blank_msg="No posts in this category",
    )


@app.route("/del/<int:id>")
@login_required
def del_post(id):
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("home"))


@app.route("/change_cat/<int:post_id>/<int:cat_id>")
@login_required
def change_cat(post_id, cat_id):
    """
    if cat_id is 0, new category is created and post is added to it
    else post is added to category with id=catid
    """
    post = Post.query.get_or_404(post_id)
    if cat_id == 0:
        name = request.args.get("name", "").strip()
        category = Category(name=name)
        db.session.add(category)
        category.posts.append(post)
        db.session.commit()
    else:
        category = Category.query.get_or_404(cat_id)
        if category and post:
            post.category = category
            db.session.commit()
    return redirect(url_for("home"))


@app.route("/settings")
@login_required
def settings():
    categories = Category.query.all()
    return render_template("settings.html", categories=categories)


@app.route("/del_cat/<int:id>")
@login_required
def del_cat(id):
    if id > 1:
        category = Category.query.get_or_404(id)
        misc = Category.query.get_or_404(1)
        for post in category.posts:
            post.category = misc
            db.session.commit()
        db.session.delete(category)
        db.session.commit()
    return redirect(url_for("settings"))


@app.route("/rename_cat/<int:id>")
@login_required
def rename_cat(id):
    name = request.args.get("name", "Misc").strip()
    category = Category.query.get_or_404(id)
    category.name = name
    db.session.commit()

    return redirect(url_for("settings"))
