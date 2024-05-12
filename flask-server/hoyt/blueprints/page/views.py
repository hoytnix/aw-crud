from flask import Blueprint, render_template, make_response

from lib.urls import all_urls

page = Blueprint('pages', __name__, template_folder='templates')


@page.route('/')
def index():
    return render_template('page/index.jinja2')


@page.route('/policy/terms/')
def terms():
    return render_template('page/terms.jinja2')


@page.route('/policy/privacy/')
def privacy():
    return render_template('page/privacy.jinja2')


@page.route('/sitemap.xml')
def sitemap():
    template = render_template('page/sitemap.jinja2', urls=all_urls())
    response = make_response(template)
    response.headers['Content-Type'] = 'application/xml'

    return response


#@page.route('/google36c6d388c4053b8a.html')
#def google_webmaster():
#    return render_template('page/google_webmaster.jinja2')
