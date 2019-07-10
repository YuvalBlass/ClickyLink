from datetime import datetime

from flask import Blueprint, render_template, request, redirect

from .extensions import db
from .models import Link
from .auth import requires_auth

page = Blueprint('page', __name__)


@page.route('/<short_url>')
def redirect_to_url(short_url):
    link = Link.query.filter_by(short_url=short_url).first_or_404()
    if link.check_password(""):
        return redirect(link.original_url)
    return render_template('redirect.html', short_url=link.short_url, wrong_password=False)


@page.route('/get_link/<short_url>', methods=['POST'])
@requires_auth
def get_link(short_url):
    password = request.form['password']
    link = Link.query.filter_by(short_url=short_url).first_or_404()
    if (link.check_password(password)):
        link.visits += 1
        db.session.commit()
        return redirect(link.original_url)
    else:
        return render_template('redirect.html', short_url=link.short_url, wrong_password=True)

@page.route('/')
@requires_auth
def index():
    users = Link.query.all()
    return render_template('index.html', remove_records=False)


@page.route('/remove_all')
@requires_auth
def remove_all():
    users = Link.query.all()
    for u in users:
        db.session.delete(u)
    db.session.commit()
    return render_template('index.html', remove_records=True)


@page.route('/add_link', methods=['POST'])
@requires_auth
def add_link():
    original_url = request.form['original_url']
    requested_url = request.form['requested_url']
    password = request.form['password']
    date = request.form['date']
    print(datetime.strptime(date,"%Y-%m-%d"))
    link = Link(original_url=original_url)
    temp = link.generate_short_link(requested_url)
    link.set_password(password)
    db.session.add(link)
    db.session.commit()

    return render_template('link_added.html', 
        new_link=link.short_url, approved=(not temp[1]), original_url=link.original_url)


@page.route('/info')
@requires_auth
def stats():
    links = Link.query.all()

    return render_template('info.html', links=links)


@page.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404