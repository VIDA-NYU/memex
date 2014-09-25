from __future__ import absolute_import, division, print_function

import pickle
import time
import pandas as pd
import numpy as np
from random import random
from collections import Counter
import itertools
import requests
from requests.exceptions import ConnectionError

from bokeh.plotting import *

from bokeh.objects import (ColumnDataSource, Plot, DataRange1d, Range1d,
       LinearAxis, Grid, Glyph, ClickTool)
from bokeh.glyphs import Circle
from bokeh.widgets import TableColumn, HandsonTable, HBox, VBox, TextInput
from bokeh.document import Document
from bokeh.session import Session

from data_generator import fake_data
from seabornify import seabornify
from termite import Termite

class Dashboard(object):

    def __init__(self):
        self.document = Document()
        self.session = Session()
        self.session.use_doc('data_tables_server')
        self.session.load_document(self.document)

        COLORS = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00"]
        self.colors = itertools.cycle(COLORS)

        data = fake_data(n=1000, uniques=80)
        # data = get_data_files()
        # data = get_data_remote()

        df = pd.DataFrame(columns=data[0].keys())
        df = df.append(data)

        urls = list(df.url)
        c = Counter(urls)
        url_data = {'url':[], 'count':[], 'color': [],
                    'rank': [], 'relevance': []}

        for k, v in c.iteritems():
            rank = random()
            relevance = random()

            url_data['url'].append(k)
            url_data['count'].append(v)
            url_data['rank'].append(rank)
            url_data['relevance'].append(relevance)
            url_data['color'].append(self.colors.next())

        self.data = data
        self.url_data = url_data

        self.url_source = ColumnDataSource(data=url_data)

        self.document.add(self.create())
        self.session.store_document(self.document)

    def create_pie1(self):
        df = pd.DataFrame(columns=self.data[0].keys())
        df = df.append(self.data)

        total = len(df)
        c = Counter(tuple(x) for x in df.type)
        theta = 0

        figure(plot_width=400, plot_height=400,
               x_range=(-4, 4), y_range=(-4, 4),
               x_axis_type=None, y_axis_type=None, 
               title="Content-Type Distribution")
        hold()

        for c_type in c.keys():
            
            percent = c[c_type]/total
            theta_2 = percent*2*np.pi + theta
            
            annular_wedge([0], [0],
                          [0], [2],
                          theta, theta_2,
                          color=self.colors.next(), legend=c_type[0])
            
            theta = theta_2
            
        seabornify(curplot())

        p = curplot()

        c = Counter(x for x in df.contentLength)

        figure(plot_width=400, plot_height=400,
               x_range=(-4, 4), y_range=(-4, 4),
               x_axis_type=None, y_axis_type=None, 
               title="Content-Length Distribution?", tools="click")
        hold()

        for c_len in c.keys():
            
            percent = c[c_len]/total
            theta_2 = percent*2*np.pi + theta
            
            annular_wedge([0], [0],
                          [0], [2],
                          theta, theta_2, name="c_len",
                          color=self.colors.next(), legend=c_len)
            
            theta = theta_2
            
            
        seabornify(curplot())

        termite = Termite()

        return HBox(children=[p, curplot()])


    def create(self):

        # Hands On Table Widget
        columns = [
            TableColumn(field="url", header="URL"),
            TableColumn(field="count", header="Count"),
            TableColumn(field="rank", header="Rank", type="numeric", format="0.00"),
            TableColumn(field="relevance", header="Relevance", type="numeric", format="0.00")
        ]

        handson_table = HandsonTable(source=self.url_source, columns=columns, sorting=True)

        # Plot
        plot = Plot(title="Rank-Relevance",
                    x_range=Range1d(start=0, end=1), y_range=Range1d(start=0, end=1),
                    plot_width=600, plot_height=400)

        # Axes and Grids
        xaxis = LinearAxis(plot=plot, axis_label="Rank")
        xgrid = Grid(plot=plot, dimension=1, ticker=xaxis.ticker)
        plot.below.append(xaxis)

        yaxis = LinearAxis(plot=plot, axis_label="Relevance")
        ygrid = Grid(plot=plot, dimension=1, ticker=yaxis.ticker)
        plot.left.append(yaxis)

        # Renderer
        points = Glyph(data_source=self.url_source,
                    glyph=Circle(x="rank", y="relevance",
                    line_color="color", fill_color="color",
                    size=6,
                    line_alpha=0.7, fill_alpha=0.7))

        # Dump renderers into plot, return layout
        plot.renderers.extend([points, xgrid, ygrid])
        seabornify(plot)

        layout = VBox(children=[plot, handson_table,
                                # self.create_sparkline(),
                                self.create_pie1()])
        return layout


    def run(self, poll_interval=0.5):
        link = self.session.object_link(self.document.context)
        # print("Please visit %s to see the plots (press ctrl-C to exit)" % link)
        import webbrowser
        webbrowser.open(link)

        try:
            while True:
                self.session.load_document(self.document)
                time.sleep(poll_interval)
        except KeyboardInterrupt:
            print()
        except ConnectionError:
            print("Connection to bokeh-server was terminated")

if __name__ == "__main__":
    data_tables = Dashboard()
    data_tables.run()
