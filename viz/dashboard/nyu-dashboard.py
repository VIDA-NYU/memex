from __future__ import print_function

import time

from bokeh.objects import ColumnDataSource, Plot, DataRange1d, LinearAxis, Grid, Glyph, BoxSelectTool, BoxSelectionOverlay
from bokeh.glyphs import Circle
from bokeh.widgets import TableColumn, HandsonTable, Select, HBox, VBox
from bokeh.document import Document
from bokeh.session import Session

# Import plots
#from radialgraph import RadialGraph, get_radialgraph_data
from harvest import Harvest
from domain import Domain
from termite import Termite
#from handson import Handson

import requests
from requests.exceptions import ConnectionError

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

    def create_layout(self):

        top_panel = HBox(children=[self.harvest.plot, self.harvest.rate_plot])
        domains = VBox(children=[self.domain.sort_relevant_plot, self.domain.sort_crawled_plot, self.domain.sort_frontier_plot], width=200)   
        #middle_panel = HBox(children=[domains, handson.plot])
        middle_panel = HBox(children=[domains])
        layout = VBox(children=[top_panel, middle_panel, self.termite.plot])

        return layout

    def update_data(self):

        self.harvest.source = self.harvest.update_source()
        self.domain.sort_relevant_source, self.domain.sort_crawled_source, self.domain.sort_frontier_source = self.domain.update_source()
        self.termite.data, self.termite.source = self.termite.update_source()
        self.session.store_document(self.document)

    def run(self, poll_interval=0.5):
        link = self.session.object_link(self.document.context)
        print("Please visit %s to see the plots (press ctrl-C to exit)" % link)

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
    dashboard = DashBoard()
    dashboard.run(0)