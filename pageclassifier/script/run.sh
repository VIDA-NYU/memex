#!/bin/sh
java -Xmx8g -cp class:libs/weka-stable-3.6.10.jar classifier.page.PageClassifier conf $1
