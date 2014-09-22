# Memex-NYU visualizations


### Termite plot

The Termite plot is a visual analysis tool for assessing topic model quality. We'll use the Termite plot to visualize the output of the LDA model.

#### Instructions

- Get the output file "summary.txt" from applying LDA.

- Run:

    ```bash
    source termite.sh
    ```

Alternatively, if you don't want to create a conda environment and wish to install the requirements with other package managers, you can install yourself the packages under `requirements.txt` and run:


```bash
# Generate csv to preprocess data to visualize data.
python summary_to_csv.py

# Generate csv to preprocess data to visualize data. Get the topics relevance to order.
python summary_csv_topics.py

# Generate the Bokeh.plot Termite
python termite.py
```

#### Requirements

Requirements are available in requirements.txt.
    
#### Resources

- Stanford paper on Termite:

    + [http://vis.stanford.edu/papers/termite](http://vis.stanford.edu/papers/termite)
    + [http://vis.stanford.edu/files/2012-Termite-AVI.pdf](http://vis.stanford.edu/files/2012-Termite-AVI.pdf)

- Another Termite Visualization Project on GH:

    + [https://github.com/uwdata/termite-visualizations](https://github.com/uwdata/termite-visualizations)