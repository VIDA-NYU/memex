from __future__ import print_function
import sys
import time
from threading import Thread

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
#from handson import Handson

import requests
from requests.exceptions import ConnectionError
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def render_dashboard():
    #dashboard = DashBoard()
    #tag = autoload_server(dashboard.layout, dashboard.session)
    tag1, id1 = make_snippet("animated", dashboard.layout, dashboard.session, dashboard.run)

    html = """
    <html>
    <head></head>
    <body>
    %s
    </body>
    </html>
    """
    html = html % (tag1)

    return html

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

    def __init__(self, path, url):
        self.document = Document()
        self.session = Session(name=url, root_url=url)
        #self.session = Session('load_from_config=False')
        self.session.use_doc('crawler_dashboard')
        self.session.load_document(self.document)

        #self.harvest_source = ColumnDataSource(data=dict())
        #self.domain_relevant_source = ColumnDataSource(data=dict())
        #self.domain_crawled_source = ColumnDataSource(data=dict())
        #self.domain_frontier_source = ColumnDataSource(data=dict())
        #self.handson_source = ColumnDataSource(data=dict())
        #self.termite_source = ColumnDataSource(data=dict())
        self.harvest = Harvest(path)
        self.domain = Domain(path)
        #handson = Handson()
        #self.termite = Termite()

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
        layout = VBox(children=[top_panel, middle_panel])
        self.layout = layout
        return layout

    def update_data(self):

        self.harvest.source = self.harvest.update_source()
        self.domain.sort_relevant_source, self.domain.sort_crawled_source, self.domain.sort_frontier_source = self.domain.update_source()
        #self.termite.data, self.termite.source = self.termite.update_source()
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
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if len(sys.argv) > 2:
          url = sys.argv[2]
        else:
          url = "http://localhost:5006" #default host port
    else:
        path = "data_monitor/" #default path
        
    dashboard = DashBoard(path, url)
    dashboard.render()
    app.run(debug=True)
    #app.run(debug=True, host='http://128.238.182.77', port=5006)
    #app.run(debug=True, host='128.238.182.77', port=5006)
