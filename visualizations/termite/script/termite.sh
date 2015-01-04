#!/usr/bin/env bash

# Install conda if not available
OS_TYPE=`uname`
if [ ! `which conda` ]; then
    if [ $OS_TYPE == "Darwin" ]; then
    wget -P /tmp http://repo.continuum.io/miniconda/Miniconda-3.6.0-MacOSX-x86_64.sh 
    /bin/bash /tmp/Miniconda-3.6.0-MacOSX-x86_64.sh -b
    elif [ $OS_TYPE == "Linux" ]; then
    wget -P http://repo.continuum.io/miniconda/Miniconda-3.6.0-Linux-x86_64.sh
    /bin/bash /tmp/Miniconda-3.6.0-Linux-x86_64.sh -b
    else
    echo "Please install conda from Miniconda first: http://conda.pydata.org/miniconda.html"
    exit 1
    fi
    printf "Adding conda to .bash_profile. Please either start a new terminal or execute\n\tPATH=$HOME/miniconda/bin:$PATH"
    echo 'PATH=$HOME/miniconda/bin:$PATH' >> $HOME/.bash_profile
    export PATH=$HOME/miniconda/bin:$PATH
fi

# Create the required conda environment
conda create --name memex --file environment.txt

# Activate the environment
source activate memex

# Convert the output file `summary.txt` to a csv file with relevance per word and topic.
python summary_to_csv.py

# Convert the output file `summary.txt` to a csv file with relevance per topic.
python summary_csv_topics.py

# Create the bokeh termite plot.
python termite.py
