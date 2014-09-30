from __future__ import print_function

import time
import os
import os.path as op
from threading import Thread
import unicodecsv

from bokeh.objects import ColumnDataSource, Plot, DataRange1d, LinearAxis, Grid, Glyph, BoxSelectTool, BoxSelectionOverlay
from bokeh.glyphs import Circle
from bokeh.widgets import TableColumn, HandsonTable, Select, HBox, VBox
#from bokeh.widgets import TableColumn, HandsonTable, Select, HBox, VBox, Button
from bokeh.document import Document
from bokeh.session import Session
from bokeh.embed import autoload_server
# Import plots
#from radialgraph import RadialGraph, get_radialgraph_data
from harvest import Harvest
from domain import Domain
from termite import Termite
#from table_urls. import Handson

import requests
from requests.exceptions import ConnectionError
from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla import filters, ModelView

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

# Create admin
admin = admin.Admin(app, 'FocusCrawlerVIz')

# Add views
admin.add_view(UrlView(db.session))

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

@app.route('/')
def render_index():
    return render_template('index.html')

@app.route('/dashboard')
def render_dashboard():
    #dashboard = DashBoard()
    #tag = autoload_server(dashboard.layout, dashboard.session)
    tag = autoload_server(dashboard.layout, dashboard.session)

    html = """
    <html>
    <head></head>
    <body>
    %s
    </body>
    </html>
    """
    html = html % (tag)
    #render_template('demo.html', tag=tag)

    return render_template('demo.html', tag=tag)

def make_snippet(kind, plot, session=None, target=None):
    if kind == "plot":
        tag = autoload_server(plot, session)
        thread = Thread()
        thread.start()
    if kind == "animated":
        tag = autoload_server(plot, session)
        thread = Thread(target=target, args=(plot, session))
        thread.start()
    elif kind == "widget":
        tag = autoload_server(plot, session)
        thread = Thread(target=target, args=(pop,))
        thread.start()

    return tag, plot._id

class DashBoard(object):

    def __init__(self):
        self.document = Document()
        self.session = Session()
        self.session.use_doc('crawler_dashboard')
        self.session.load_document(self.document)

        #self.harvest_source = ColumnDataSource(data=dict())
        #self.domain_relevant_source = ColumnDataSource(data=dict())
        #self.domain_crawled_source = ColumnDataSource(data=dict())
        #self.domain_frontier_source = ColumnDataSource(data=dict())
        #self.handson_source = ColumnDataSource(data=dict())
        #self.termite_source = ColumnDataSource(data=dict())

        self.harvest = Harvest()
        self.domain = Domain()
        #handson = Handson()
        self.termite = Termite()

        self.document.add(self.create_layout())
        self.session.store_document(self.document)

    def render(self):
        self.create_layout()
        self.document.add(self.layout)
        self.update_data()

    def create_layout(self):

        #button = Button(label="Randomize data", type="success")
        #button.on_click(update_data)
        #top_panel = HBox(children=[button, self.harvest.plot, self.harvest.rate_plot])
        top_panel = HBox(children=[self.harvest.plot, self.harvest.rate_plot])
        domains = VBox(children=[self.domain.sort_relevant_plot, self.domain.sort_crawled_plot, self.domain.sort_frontier_plot], width=200)   
        #middle_panel = HBox(children=[domains, handson.plot])
        middle_panel = HBox(children=[domains])
        layout = VBox(children=[top_panel, middle_panel, self.termite.plot])
        self.layout = layout
        return layout

    def update_data(self):

        self.harvest.source = self.harvest.update_source()
        self.domain.sort_relevant_source, self.domain.sort_crawled_source, self.domain.sort_frontier_source = self.domain.update_source()
        self.termite.data, self.termite.source = self.termite.update_source()
        #self.session.store_objects(ds)
        self.session.store_document(self.document)

        
    def run(self, poll_interval=0.5):
        #link = self.session.object_link(self.document.context)
        #print("Please visit %s to see the plots (press ctrl-C to exit)" % link)

        try:
            while True:
                self.update_data()
                self.session.load_document(self.document)
                time.sleep(poll_interval)
        except KeyboardInterrupt:
            print()
        except ConnectionError:
            print("Connection to bokeh-server was terminated")


if __name__ == "__main__":
    # Build a sample db on the fly, if one does not exist yet.
    app_dir = op.realpath(os.path.dirname(__file__))
    database_path = op.join(app_dir, app.config['DATABASE_FILE'])
    build_db()
    dashboard = DashBoard()
    dashboard.render()
    app.run(debug=True)