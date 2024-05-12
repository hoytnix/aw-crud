from flask import (Blueprint, redirect, request, flash, url_for,
                   render_template)
from sqlalchemy import text

from .forms import (SearchForm, BulkDeleteForm, PostForm)

from hoyt.blueprints.blog import Post, Category, Tag

dashboard = Blueprint(
    'dashboard',
    __name__,
    template_folder='templates',
    url_prefix='/dashboard')


@dashboard.route('/')
def index():
    """Display the ten most-recent posts."""
    return render_template('dashboard/index.jinja2')


# Posts ---------------------------------------------------------------------
@dashboard.route('/posts', defaults={'page': 1})
@dashboard.route('/posts/page/<int:page>')
def posts(page):
    search_form = SearchForm()
    bulk_form = BulkDeleteForm()

    sort_by = Post.sort_by(
        request.args.get('sort', 'created_on'),
        request.args.get('direction', 'desc'))
    order_values = '{0} {1}'.format(sort_by[0], sort_by[1])

    paginated_posts = Post.query \
        .filter(Post.search(request.args.get('q', ''))) \
        .order_by(text(order_values)) \
        .paginate(page, 50, True)

    return render_template(
        'dashboard/post/index.jinja2',
        form=search_form,
        bulk_form=bulk_form,
        posts=paginated_posts)


@dashboard.route('/posts/new', methods=['GET', 'POST'])
def posts_new():
    post = Post()
    form = PostForm(obj=post)

    if form.validate_on_submit():
        form.populate_obj(post)

        params = {
            'code': post.code,
            'duration': post.duration,
            'percent_off': post.percent_off,
            'amount_off': post.amount_off,
            'currency': post.currency,
            'redeem_by': post.redeem_by,
            'max_redemptions': post.max_redemptions,
            'duration_in_months': post.duration_in_months,
        }

        if Post.create(params):
            flash('Post has been created successfully.', 'success')
            return redirect(url_for('dashboard.posts'))

    return render_template('dashboard/post/new.jinja2', form=form, post=post)


@dashboard.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
def posts_edit(id):
    post = Post.query.get(id)
    form = PostForm(obj=post)

    if form.validate_on_submit():
        form.populate_obj(post)
        post.save()

        flash('Post has been saved successfully.', 'success')
        return redirect(url_for('dashboard.posts'))

    return render_template('dashboard/post/edit.jinja2', form=form, post=post)


@dashboard.route('/posts/bulk_delete', methods=['POST'])
def posts_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = Post.get_bulk_action_ids(
            request.form.get('scope'),
            request.form.getlist('bulk_ids'),
            query=request.args.get('q', ''))

        # Prevent circular imports.
        from snakeeyes.blueprints.billing.tasks import delete_posts

        delete_posts.delay(ids)

        flash('{0} posts(s) were scheduled to be deleted.'.format(len(ids)),
              'success')
    else:
        flash('No posts were deleted, something went wrong.', 'error')

    return redirect(url_for('dashboard.posts'))
