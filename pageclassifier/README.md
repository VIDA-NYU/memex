Page classifier
==============
Page classifier determines whether a html page is relevant to a particular topic

* Compile: 
	$sh script/compile.sh
* Build a model:
	$sh script/build_model.sh <config dir> <training data dir> <output dir>
* Classify a page: 
	$sh script/run.sh <path_to_html_file>
