#!/bin/sh
java -Xmx8g -cp class:libs/weka.jar classifier.page.PageClassifier conf/topic.cfg $1
