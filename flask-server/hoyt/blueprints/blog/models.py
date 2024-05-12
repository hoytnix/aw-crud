import os
import datetime
import hashlib

import pytz
from flask import url_for
from sqlalchemy import or_

from hoyt.extensions import db
from lib.urls import slugify
from lib.util_sqlalchemy import ResourceMixin

# Many-to-many relationships.
tags = db.Table('tags',
                db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
                db.Column('post_id', db.Integer, db.ForeignKey('posts.id')))


class Post(ResourceMixin, db.Model):
    __tablename__ = 'posts'  # plural lower-case
    id = db.Column(db.Integer, primary_key=True)

    # Relationships.
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    tags = db.relationship(
        'Tag', secondary=tags, backref='posts', lazy='dynamic')

    # Details
    title = db.Column(db.String(128))
    body = db.Column(db.Text)
    comments_enabled = db.Column(db.Boolean, default=True)
    is_published = db.Column(db.Boolean, default=False)
    preview_paragraphs = db.Column(db.Integer, default=2)
    file_hash = db.Column(db.String(128))

    @classmethod
    def search(cls, query):
        """
        Search a resource by 1 or more fields.

        :param query: Search query
        :type query: str
        :return: SQLAlchemy filter
        """
        if not query:
            return ''

        search_query = '%{0}%'.format(query)
        search_chain = (Post.title.ilike(search_query), )

        return or_(*search_chain)

    @property
    def next_post(self):
        minimum = self.id
        current = None

        posts = Post.query.all()
        for post in posts:
            if not post.id > minimum:
                continue
            if not current:
                current = post
                continue
            if post.id < current.id:
                current = post
        return current

    @property
    def previous_post(self):
        maximum = self.id
        current = None

        posts = Post.query.all()
        for post in posts:
            if not post.id < maximum:
                continue
            if not current:
                current = post
                continue
            if post.id > current.id:
                current = post
        return current

    @property
    def preview_text(self):
        """Return so many paragraphs of the body, as specified by `preview_paragraphs`.

        Returns: str
        """

        text = self.body
        if not text or text == '':
            return ''

        paragraphs = text.split('\r\n\r\n')
        return '\r\n\r\n'.join(paragraphs[:self.preview_paragraphs])
        #return '%r' % text

    @property
    def category(self):
        return Category.query.get(self.category_id)

    @property
    def href(self):
        return '<a href="{}">{}</a>'.format(self.url_for, self.title)

    @property
    def url_for(self):
        return url_for(
            'blog.post_detail',
            category_slug=self.category.slug,
            post_slug=self.slug)

    @property
    def slug(self):
        return slugify(self.title)

    def __str__(self):
        return self.title


class Category(db.Model):
    __tablename__ = 'categories'  # plural lower-case
    id = db.Column(db.Integer, primary_key=True)

    # Relationships.
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    # Details
    title = db.Column(db.String(128), nullable=False)

    @property
    def most_recent_posts(self):
        return Post.query.filter_by(category_id=self.id) \
                        .filter_by(is_published=True) \
                        .order_by(Post.created_on.desc()).all()

    @property
    def href(self):
        return '<a href="{}">{}</a>'.format(self.url_for, self.title)

    @property
    def url_for(self):
        return url_for('blog.category_detail', slug=self.slug)

    @property
    def slug(self):
        return slugify(self.title)

    def __str__(self):
        return self.title


class Tag(db.Model):
    #__tablename__ = 'tags'  # plural lower-case
    id = db.Column(db.Integer, primary_key=True)

    # Details
    title = db.Column(db.String(128), nullable=False)

    @classmethod
    def tag_cloud(cls):
        count = {}
        posts = Post.query.all()
        for post in posts:
            tags = post.tags
            for tag in tags:
                if tag not in count:
                    count[tag] = 1
                else:
                    count[tag] += 1

        return sorted(
            [{
                "tag": tag,
                "count": count[tag]
            } for tag in count],
            key=lambda k: k['tag'].title)

    @property
    def most_recent_posts(self):
        return Post.query.filter(Post.tags.any(Tag.title == self.title)) \
                        .filter_by(is_published=True) \
                        .order_by(Post.created_on.desc()).all()

    @property
    def href(self):
        return '<a href="{}">{}</a>'.format(self.url_for, self.title)

    @property
    def url_for(self):
        return url_for('blog.tag_detail', slug=self.slug)

    @property
    def slug(self):
        return slugify(self.title)

    def __str__(self):
        return self.title
