from __future__ import division

from decimal import *

import os
import os.path as op
from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
import unicodecsv

from wtforms import validators

from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla import filters, ModelView

import pprint
import sqlite3 as lite

from os import listdir

# Create application
app = Flask(__name__)

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
app.config['DATABASE_FILE'] = 'UrlTable.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class CrawledUrl(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(140))
    domain = db.Column(db.String(140))
    datetime = db.Column(db.String(140))

    def __unicode__(self):
        return self.url


class UrlView(ModelView):
    #column_select_related_list = ('primary_term', 'secondary_term', 'ratio')

    column_searchable_list = ("url","domain")
    column_filters = ('url','domain')

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(UrlView, self).__init__(CrawledUrl, session, **kwargs)


# Flask views
@app.route('/')
def index():
    return render_template("index.html")


# Create admin
admin = admin.Admin(app, 'CrawledUrls')

# Add views
admin.add_view(UrlView(db.session))
# admin.add_view(PercentagesView(db.session))

def build_db():
    db.drop_all()
    db.create_all()

    csvfile = "/Users/cdoig/memexcrawler/viz/app/data_preprocessed/crawledpages.csv"
    with open(csvfile, 'rb') as f:
        reader = unicodecsv.reader(f, encoding='utf-8', delimiter='\t')
        for row in reader:
            crawledurl = CrawledUrl()
            crawledurl.url = row[0]
            #crawledurl.url = '<a href="%s">%s</a><div class="box"><iframe src="%s" width = "500px" height = "500px"></iframe></div>' % (url, url, url)
            crawledurl.domain = row[1]
            crawledurl.datetime = row[3]
            db.session.add(crawledurl)
    db.session.commit()



if __name__ == '__main__':
    # Build a sample db on the fly, if one does not exist yet.
    app_dir = op.realpath(os.path.dirname(__file__))
    database_path = op.join(app_dir, app.config['DATABASE_FILE'])
    build_db()

    # Start app
    app.run(debug=True)
