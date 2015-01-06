"""
Draw a termite plot to visualize topics and words from an LDA.
"""

from blaze import *
import pandas as pd
from bokeh.plotting import *
import numpy as np

t = Table(CSV('termite_data.csv', columns=['topic', 'word', 'result']))
df = into(DataFrame, t)

top = Table(CSV('topics_data.csv', columns=['topic', 'word', 'result']))
topics_df = into(DataFrame, top)

topics_df = topics_df[["topic", "result"]]
topics_df.sort('result', ascending=False)

gby_df = df.groupby('topic')

gby_df.describe()

t_by = by(t.topic, max=t.result.max(), min=t.result.min())

# size proportional to result in Karan's example 0-10 range.
MAX = compute(t.result.max())
MIN = compute(t.result.min())

# Create a size variable to define the size of the the circle for the plot.
t = transform(t, size=sqrt((t.result - MIN)/(MAX - MIN))*50)

data = t

WORDS = data['word'].distinct()
WORDS = into(list, WORDS)

TOPICS = data['topic'].distinct()
TOPICS = into(list, TOPICS)

output_file('termite.html')

data_source = into(ColumnDataSource, data)

figure(x_range=TOPICS, y_range=WORDS,
       plot_width=1000, plot_height=1700,
       title="Termite Plot", tools='resize, save')

circle(x="topic", y="word", size="size", fill_alpha=0.6, source=data_source)
xaxis().major_label_orientation = np.pi/3
show()