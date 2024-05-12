from flask import Blueprint, render_template, abort

from .models import Post, Category, Tag

blog = Blueprint(
    'blog', __name__, template_folder='templates', url_prefix='/blog')


def custom_list_view(key):
    import os
    cd = os.path.dirname(os.path.abspath(__file__))
    lists_dir = os.path.join(cd, 'templates/blog/lists')

    result = None
    for (root, dir_names, file_names) in os.walk(lists_dir):
        for file_name in file_names:
            if key in file_name:
                result = file_name
                break
        if result:
            break

    if result:
        return 'blog/lists/' + file_name
    else:
        return 'blog/result_list.jinja2'


#    Blog Index -------------------------------------------------------------------------


@blog.route('/')
def index():
    """Display the ten most-recent posts."""

    categories = Category.query.all()
    posts = Post.query.filter_by(is_published=True) \
                    .order_by(Post.created_on.desc()).limit(10)
    return render_template(
        'blog/index.jinja2', categories=categories, posts=posts)


#    Post Details -----------------------------------------------------------------------


@blog.route('/<category_slug>/<post_slug>/')
def post_detail(category_slug, post_slug):
    """Display a single post.

    Args:
        category_slug (str): not required logically, but used for sanity checking.
        post_slug (str): key to search for post.
    """

    result = None

    posts = Post.query.all()
    for post in posts:
        if post.slug == post_slug:
            result = post
            break

    if not result:
        abort(404)

    # Although this _shouldn't_ do anything, it's here for my sanity. :)
    if result.category.slug != category_slug:
        abort(404)

    return render_template('blog/post_detail.jinja2', post=result)


#    Search Results ---------------------------------------------------------------------


@blog.route('/<slug>/')
def category_detail(slug):
    result = None

    categories = Category.query.all()
    for category in categories:
        if category.slug == slug:
            result = category
            break

    if not result:
        abort(404)

    template_file = custom_list_view(key=slug)
    return render_template(template_file, result=result)


@blog.route('/tag/<slug>/')
def tag_detail(slug):
    result = None

    tags = Tag.query.all()
    for tag in tags:
        if tag.slug == slug:
            result = tag
            break

    if not result:
        abort(404)

    template_file = custom_list_view(key=slug)
    return render_template(template_file, result=result)
