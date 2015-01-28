import pandas as pd
import bokeh.plotting as plt

# words = ['air', 'atm', 'atm', 'complexes', 'internal', 'oxidizer']
# topics = ['a', 'b', 'a', 'b', 'b', 'a']
# sizes = [0.17070214219087501,
#          0.20783267646346201,
#          0.17070214219087501,
#          0.20783267646346201,
#          0.20783267646346201,
#          0.17070214219087501]
#sizes = [a*100 for a in sizes]

sizes = [100, 39, 37]
words = [u'graphene', u'solar', u'devices']
topics = ['0', '0', '0']


plt.output_file('foo2.html')
p = plt.figure(x_range=list(set(topics)),
               y_range=list(set(words)),
               plot_width=800, plot_height=600,
               title="Plot", tools='resize, save')
#source = pd.DataFrame.from_dict({"words": words, "topics":topics, "sizes":sizes})
#source = plt.ColumnDataSource(source)
#plt.circle(x="topics", y="words", size="sizes", fill_alpha=0.6, source=source)
p.circle(x=topics, y=words, size=sizes, fill_alpha=0.6)
plt.show(p)
