import csv
import sys
from blaze import *
import pandas as pd
from bokeh.plotting import *
import numpy as np
import datetime as dt

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
        t = transform(t, harvest_rate=t.relevant_pages/r.downloaded_pages))

        relevant_pages = into(np.ndarray, t.relevant_pages)
        downloaded_pages = into(np.ndarray, t.downloaded_pages)
        harvest_rate = into(np.array, t.harvest_rate)
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

        figure(plot_width=800, plot_height=500, title="Harvest Plot", tools='resize, save', x_axis_type='datetime')
        hold()

        scatter(x="timestamp", y="relevant_pages", fill_alpha=0.6, color="red", width=0.2, source=source)
        line(x="timestamp", y="relevant_pages", fill_alpha=0.6, color="red", width=0.2, legend="relevant", source=source)
        scatter(x="timestamp", y="downloaded_pages", fill_alpha=0.6, color="blue", width=0.2, source=source)
        line(x="timestamp", y="downloaded_pages", fill_alpha=0.6, color="blue", width=0.2, legend="downloaded", source=source)

        hover = curplot().select(dict(type=HoverTool))
        hover.tooltips = OrderedDict([
            ("(x,y)", "($x, $y)"),
            ("fill color", "$color[hex, swatch]:colors"),
        ])

        legend().orientation = "top_left"
        show()

        return curplot()
