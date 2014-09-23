"""
Generate the domain plot.
"""
import csv
import datetime as dt
import unicodecsv
from cStringIO import StringIO
from blaze import *
import pandas as pd
from tld import get_tld
from bokeh.plotting import *
from bokeh.objects import ColumnDataSource

def group_by_minutes(d, minutes):
    k = d + dt.timedelta(minutes=-(d.minute % minutes)) 
    return dt.datetime(k.year, k.month, k.day, k.hour, k.minute, 0)

def generate_domain_data(minutes=5):
    """
    Generates the domain data
    """
    relevant_data = 'data_monitor/relevantpages.csv'
    crawled_data = 'data_monitor/crawledpages.csv'
    frontier_data = 'data_monitor/frontierpages.csv'

    # Transform the summary.txt file into a csv file with the purpose of inputing the file into Blaze-Bokeh for visualization.
    fmt ='%Y-%m-%d-%H-%M-%S-%f' 
    current_time = dt.datetime.now().strftime(fmt)
    #relevant_file = '%s_relevantpages.csv' % current_time
    relevant_file = 'relevantpages.csv'
    with open(relevant_file, 'wb') as outfile:
        writer = unicodecsv.writer(outfile, encoding='utf-8', delimiter='\t')
        with open(relevant_data, 'rb') as f:
            reader = unicodecsv.reader(f, encoding='utf-8', delimiter='\t')
            for row in reader:
                try:
                    url = row[0]
                    domain = get_tld(url, fail_silently=True)
                    #domain = url.split('/')[2]
                    timestamp = row[1]
                    timestamp_dt = dt.datetime.fromtimestamp(int(timestamp))
                    minute_gby = group_by_minutes(timestamp_dt, minutes)
                    minute = minute_gby.strftime('%Y-%m-%d %H:%M:%S')
                    #line = [url, domain, timestamp, minute]
                    line = [domain, timestamp, minute]
                    writer.writerow(line)
                except csv.Error as e:
                    print 'file %s, line %d: %s' % (input_summary, reader.line_num, e)
                    pass

    #crawled_file = '%s_crawledpages.csv' % current_time
    crawled_file = 'crawledpages.csv'
    with open(crawled_file, 'wb') as outfile:
        writer = unicodecsv.writer(outfile, encoding='utf-8', delimiter='\t')
        with open(crawled_data, 'rb') as f:
            reader = unicodecsv.reader(f, encoding='utf-8', delimiter='\t')
            for row in reader:
                try:
                    url = row[0]
                    domain = get_tld(url, fail_silently=True)
                    #domain = url.split('/')[2]
                    timestamp = row[1]
                    timestamp_dt = dt.datetime.fromtimestamp(int(timestamp))
                    minute_gby = group_by_minutes(timestamp_dt, minutes)
                    minute = minute_gby.strftime('%Y-%m-%d %H:%M:%S')
                    #line = [url, domain, timestamp, minute]
                    line = [domain, timestamp, minute]
                    writer.writerow(line)
                except csv.Error as e:
                    print 'file %s, line %d: %s' % (input_summary, reader.line_num, e)
                    pass

    #frontier_file = '%s_frontierpages.csv' % current_time
    frontier_file = 'frontierpages.csv'
    with open(frontier_file, 'wb') as outfile:
        writer = unicodecsv.writer(outfile, encoding='utf-8', delimiter='\t')
        with open(frontier_data, 'rb') as f:
            reader = unicodecsv.reader(f, encoding='utf-8', delimiter='\t')
            for row in reader:
                try:
                    url = row[0]
                    # Trying to clean the frontier list of urls in a very dirty way...
                    if (url.split('/')[0] == "http:" or url.split('/')[0] == "https:") and url != "http:/":
                        domain = get_tld(url, fail_silently=True)
                        #domain = url.split('/')[2]
                        #line = [url, domain]
                        line = [domain]
                        writer.writerow(line)
                    else:
                        pass
                        #print url.split('/')[0]
                    #domain = url.split('/')[2]
                    #timestamp = row[1]
                    #timestamp_dt = dt.datetime.fromtimestamp(int(timestamp))
                    #minute_gby = group_by_minutes(timestamp_dt, minutes)
                    #minute = minute_gby.strftime('%Y-%m-%d %H:%M:%S')
                    #line = [url, domain]
                    #writer.writerow(line)
                except csv.Error as e:
                    print 'file %s, line %d: %s' % (input_summary, reader.line_num, e)
                    pass

    frontier_file = "frontierpages.csv"
    crawled_file = "crawledpages.csv"
    relevant_file = "relevantpages.csv"
    #t_frontier = Table(CSV(frontier_file, columns=["url", "domain"], encoding='utf-8'), schema= "{url: string, domain:string}")
    #t_crawled = Table(CSV(crawled_file, columns=["url", "domain", "timestamp", "minute"], encoding='utf-8'), schema = "{url: string, domain:string, timestamp:datetime, minute:datetime}")
    #t_relevant = Table(CSV(relevant_file, columns=["url", "domain", "timestamp", "minute"], encoding='utf-8'), schema ="{url: string, domain:string, timestamp:datetime, minute:datetime}")
    df_frontier = pd.read_csv(frontier_file, names = ["domain"], delimiter='\t', encoding='utf-8', engine='c', error_bad_lines=False, squeeze=True)
    df_crawled = pd.read_csv(crawled_file, names = ["domain", "timestamp", "minute"], delimiter='\t', encoding='utf-8')
    df_relevant = pd.read_csv(relevant_file, names = ["domain", "timestamp", "minute"], delimiter='\t', encoding='utf-8')

    #grouped = df_frontier.groupby(by=['domain']).count()

    frontier_counts = df_frontier.value_counts()
    df_frontier_counts = pd.DataFrame(frontier_counts)
    df_frontier_counts.columns = ['frontier_count']

    df_crawled_counts = df_crawled[['domain', 'timestamp']].groupby(['domain']).count('timestamp').sort()
    df_crawled_counts.columns = ['crawled_count']

    df_relevant_counts = df_relevant[['domain', 'timestamp']].groupby(['domain']).count('timestamp').sort()
    df_relevant_counts.columns = ['relevant_count']

    df_crawled_time_evolution = df_crawled.groupby(['domain', 'minute']).count('timestamp').sort()
    df_crawled_time_evolution.columns = ['relevant_time_count']
    df_relevant_time_evolution = df_relevant.groupby(['domain', 'minute']).count('timestamp').sort()
    df_relevant_time_evolution.columns = ['relevant_time_count']

    # Join
    a = df_frontier_counts.join(df_crawled_counts, how='outer')
    joined = a.join(df_relevant_counts, how='outer').fillna(0)
    sort_relevant = joined.sort('relevant_count', ascending=False).head(15)
    sort_crawled = joined.sort('crawled_count', ascending=False).head(15)
    sort_frontier = joined.sort('frontier_count', ascending=False).head(15)

    return sort_relevant, sort_crawled, sort_frontier

sort_relevant, sort_crawled, sort_frontier = generate_domain_data()

# Sorted by Relevance
sort_relevant['relevant_rect'] = sort_relevant['relevant_count'].map(lambda x: x/2)
sort_relevant['frontier_rect'] = sort_relevant['frontier_count'].map(lambda x: x/2)
sort_relevant['crawled_rect'] = sort_relevant['crawled_count'].map(lambda x: x/2)
sort_relevant_source = ColumnDataSource(sort_relevant)
output_file('domain.html')
y_range= sort_relevant_source.data['index']

figure(plot_width=800, plot_height=500, title="Domains Sorted by Relevance", y_range = y_range, tools='pan, wheel_zoom, box_zoom, reset, resize, save, hover')

hold()

rect(y=y_range, x='frontier_rect', height=0.4, width='frontier_count', color="grey", fill_color="grey", source = sort_relevant_source, legend="frontier")
rect(y=y_range, x='crawled_rect', height=0.4, width='crawled_count', color="blue", fill_color="blue", source = sort_relevant_source, legend="crawled")
rect(y=y_range, x='relevant_rect', height=0.4, width='relevant_count', color="red", fill_color="red", source = sort_relevant_source, legend="relevant")

axis().major_label_text_font_size = "8pt"

# Sorted by Frontier
sort_frontier['relevant_rect'] = sort_frontier['relevant_count'].map(lambda x: x/2)
sort_frontier['frontier_rect'] = sort_frontier['frontier_count'].map(lambda x: x/2)
sort_frontier['crawled_rect'] = sort_frontier['crawled_count'].map(lambda x: x/2)
sort_frontier_source = ColumnDataSource(sort_frontier)
output_file('domain.html')
y_range= sort_frontier.data['index']

figure(plot_width=800, plot_height=500, title="Domains Sorted by urls in Frontier", y_range = y_range, tools='pan, wheel_zoom, box_zoom, reset, resize, save, hover')

hold()

rect(y=y_range, x='frontier_rect', height=0.4, width='frontier_count', color="grey", fill_color="grey", source = sort_frontier_source, legend="frontier")
rect(y=y_range, x='crawled_rect', height=0.4, width='crawled_count', color="blue", fill_color="blue", source = sort_frontier_source, legend="crawled")
rect(y=y_range, x='relevant_rect', height=0.4, width='relevant_count', color="red", fill_color="red", source = sort_frontier_source, legend="relevant")

axis().major_label_text_font_size = "8pt"

# Sorted by Crawled
sort_crawled['relevant_rect'] = sort_crawled['relevant_count'].map(lambda x: x/2)
sort_crawled['frontier_rect'] = sort_crawled['frontier_count'].map(lambda x: x/2)
sort_crawled['crawled_rect'] = sort_crawled['crawled_count'].map(lambda x: x/2)
sort_crawled_source = ColumnDataSource(sort_crawled)

y_range= sort_crawled_source.data['index']

figure(plot_width=800, plot_height=500, title="Domains Sorted by Crawled urls", y_range = y_range, tools='pan, wheel_zoom, box_zoom, reset, resize, save, hover')

hold()

rect(y=y_range, x='frontier_rect', height=0.4, width='frontier_count', color="grey", fill_color="grey", source = sort_crawled_source, legend="frontier")
rect(y=y_range, x='crawled_rect', height=0.4, width='crawled_count', color="blue", fill_color="blue", source = sort_crawled_source, legend="crawled")
rect(y=y_range, x='relevant_rect', height=0.4, width='relevant_count', color="red", fill_color="red", source = sort_crawled_source, legend="relevant")

axis().major_label_text_font_size = "8pt"

show()

class Domain(object):

    def __init__(self):
        self.sort_relevant, self.sort_crawled, self.sort_frontier = generate_domain_data()

    def create(self, output_html='domain.html'):

        sort_relevant_source = ColumnDataSource(self.sort_relevant)
        sort_crawled_source = ColumnDataSource(self.sort_crawled)
        sort_frontier_source = ColumnDataSource(self.sort_frontier)

        output_file(output_html)

        figure(plot_width=800, plot_height=500, title="Domain by Frontier", tools='pan, wheel_zoom, box_zoom, reset, resize, save, hover', x_axis_type='categorical')
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

        harvest_plot = curplot()

        figure(plot_width=800, plot_height=500, title="Harvest Rate", x_axis_type='datetime', tools='pan, wheel_zoom, box_zoom, reset, resize, save, hover')
        line(x="timestamp", y="harvest_rate", fill_alpha=0.6, color="blue", width=0.2, legend="harvest_rate", source=source)
        scatter(x="timestamp", y="harvest_rate", alpha=0, color="blue", legend="harvest_rate", source=source)

        hover = curplot().select(dict(type=HoverTool))
        hover.tooltips = OrderedDict([
            ("harvest_rate", "@harvest_rate"),
        ])
        show()

        harvest_rate_plot = curplot()

        return harvest_plot, harvest_rate_plot

