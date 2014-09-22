import csv
import sys
from blaze import *
import pandas as pd
from bokeh.plotting import *
from bokeh.objects import HoverTool
from collections import OrderedDict
import numpy as np
import datetime as dt
from __future__ import division

def generate_harvest():
    """
    Generates a fake_harvest_data
    """
    harvest_data = 'data_monitor/harvestinfo.csv'
    return harvest_data


class Harvest(object):

    def __init__(self, input_data='harvest.csv'):
        self.harvest_data = generate_harvest()

    def create(self, output_html='harvest.html'):
        t = Table(CSV(self.harvest_data, columns=['relevant_pages', 'downloaded_pages', 'timestamp']))
        t = transform(t, timestamp=t.timestamp.map(dt.datetime.fromtimestamp, schema='{timestamp: datetime}'))
        t = transform(t, date=t.timestamp.map(lambda x: x.date(), schema='{date: date}'))
        #t = transform(t, harvest_rate=t.relevant_pages/t.downloaded_pages)

        relevant_pages = into(np.ndarray, t.relevant_pages)
        downloaded_pages = into(np.ndarray, t.downloaded_pages)
        harvest_rate = relevant_pages/downloaded_pages
        timestamp = into(np.ndarray, t.timestamp)

        source = ColumnDataSource(
            data=dict(
                relevant_pages = relevant_pages,
                downloaded_pages = downloaded_pages,
                harvest_rate = harvest_rate,
                timestamp = timestamp
            )
        )

        output_file(output_html)

        #data_source = into(ColumnDataSource, data)

        figure(plot_width=800, plot_height=500, title="Harvest Plot", tools='pan, wheel_zoom, box_zoom, reset, resize, save, hover', x_axis_type='datetime')
        hold()

        scatter(x="timestamp", y="relevant_pages", fill_alpha=0.6, color="red", source=source)
        line(x="timestamp", y="relevant_pages", color="red", width=0.2, legend="relevant", source=source)
        scatter(x="timestamp", y="downloaded_pages", fill_alpha=0.6, color="blue", source=source)
        line(x="timestamp", y="downloaded_pages", color="blue", width=0.2, legend="downloaded", source=source)

        hover = curplot().select(dict(type=HoverTool))
        hover.tooltips = OrderedDict([
            ("harvest_rate", "@harvest_rate"),
        ])

        legend().orientation = "top_left"
        show()

        figure(plot_width=800, plot_height=500, title="Harvest Rate", x_axis_type='datetime', tools='pan, wheel_zoom, box_zoom, reset, resize, save, hover')
        line(x="timestamp", y="harvest_rate", fill_alpha=0.6, color="blue", width=0.2, legend="harvest_rate", source=source)
        scatter(x="timestamp", y="harvest_rate", alpha=0, color="blue", legend="harvest_rate", source=source)

        hover = curplot().select(dict(type=HoverTool))
        hover.tooltips = OrderedDict([
            ("harvest_rate", "@harvest_rate"),
        ])

        show()

        return curplot()
