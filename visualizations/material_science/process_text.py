"""Visualizations of the material science research files"""

import json
import os
import random

import numpy as np
import pandas as pd
import pattern.vector as pv
from wordcloud import WordCloud

import bokeh.plotting as plt


FONT_PATH = "/Users/aterrel/Library/Fonts/DejaVuSans.ttf"
DATA_FILE = "msr-data.json"
STOPWORD_FILE = "stopwords_wordnet.txt"


def make_output_dir(dir_name="output"):
    try:
        os.mkdir(dir_name)
    except OSError:
        pass


def read_file():
    list_of_dicts = []
    with open(DATA_FILE, 'r') as fp:
        for line in fp.readlines():
            try:
                list_of_dicts.append(json.loads(line))
            except ValueError:
                print("Unable to process line:\n\t", line)
    return pd.DataFrame(list_of_dicts)


def read_sample(n=10):
    df = read_file()
    rows = random.sample(df.index, n)
    return df.ix[rows]


def get_abstracts_by_year(df):
    abstracts = {}
    grouped = df.groupby('year')
    for year, pks in grouped.groups.iteritems():
        abstracts[year] = df.loc[pks]
    return abstracts


def create_models(group):
    docs = [pv.Document(item, threshold=1) for item in group]
    return pv.Model(docs, weight=pv.TFIDF)


def get_models_by_year(df):
    return df[['year', 'abstract']].groupby('year').apply(create_models)


def get_clusters_by_year(df, k=5):
    return get_models_by_year(df).apply(lambda x: x.cluster(pv.KMEANS, k=k))


def lsa_apply(df):
    m = pv.Model([pv.Document(a) for a in df['abstract']], weight=pv.TFIDF)
    return m.reduce(2)


def get_lsa_by_year(df):
    return df[['year', 'abstract']].groupby('year').apply(lsa_apply)


def generate_annual_wordclouds(df, field):
    abstract_series = df[["year", field]].groupby("year").agg(np.sum)
    wordclouds = []
    for year in abstract_series.index:
        abstract = abstract_series.ix[year][field]
        wordclouds.append((year, WordCloud(font_path=FONT_PATH).generate(abstract)))
    return wordclouds


def generate_word_cloud_image(text, filename="output/wordcloud.jpg"):
    wordcloud = WordCloud(font_path=FONT_PATH).generate(text)
    wordcloud.to_image().save(filename, "JPEG")


def generate_annual_wordcloud_images(df, field):
    make_output_dir(os.path.join("output", field))
    wcs = generate_annual_wordclouds(df, field)
    for year, wordcloud in wcs:
        wordcloud.to_image().save(os.path.join("output", field, year+".jpg"), "JPEG")


def wordclouds_to_bokeh(wordclouds):
    plt.output_file("wordclouds.html", title="Wordclouds of Abstracts 1by Year")
    images = [w.to_image() for y, w in wordclouds]
    p = plt.figure(x_range=[0, 10], y_range=[0, 10])
    # XXX: Need to figure out how to put images in
    p.image(image=images, x=range(len(images)), y=[0]*len(images), dw=[10]*len(images), dh=[10]*len(images), palette="Spectral11")

    plt.show(p)


def remove_stopwords(text):
    pass

if __name__ == "__main__":
    pass
    #df = read_file()
    # generate_annual_wordcloud_images(df, "abstract")
    #generate_annual_wordcloud_images(df, "title")
