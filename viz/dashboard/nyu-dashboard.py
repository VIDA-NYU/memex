from __future__ import print_function

import time

from bokeh.objects import ColumnDataSource, Plot, DataRange1d, LinearAxis, Grid, Glyph, BoxSelectTool, BoxSelectionOverlay
from bokeh.glyphs import Circle
from bokeh.widgets import TableColumn, HandsonTable, Select, HBox, VBox
from bokeh.document import Document
from bokeh.session import Session

# Import plots
from radialgraph import RadialGraph, get_radialgraph_data
from harvest_rate import Harvest, get_har
from domain import Domain
from termite import Termite

import requests
from requests.exceptions import ConnectionError

class DashBoard(object):

    def __init__(self):
        self.document = Document()
        self.session = Session()
        self.session.use_doc('crawler_dashboard')
        self.session.load_document(self.document)

        self.termite_source = ColumnDataSource()
        self.radial_source = ColumnDataSource()
        self.domain_source = ColumnDataSource()
        self.harvest_source = ColumnDataSource()

        self.update_data()

        self.document.add(self.create_plots())

        self.session.store_document(self.document)

    def create_plots(self):

        domain_relevant_plot, domain_crawled_plot, domain_frontier_plot = Domain()
        harvest_plot, harvest_rate_plot = Harvest()
        termite_plot = Termite()

        controls = VBox(children=[manufacturer_select, model_select, transmission_select, drive_select, class_select], width=200)
        top_panel = HBox(children=[controls, plot])
        layout = VBox(children=[top_panel, handson_table])

        return layout

    def update_data(self):

        self.source.data = ColumnDataSource.from_df(df)

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
    dashboard.run(0.3)