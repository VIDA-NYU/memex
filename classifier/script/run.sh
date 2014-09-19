#!/bin/sh
java -Xmx8g -cp class:libs/weka.jar classifier.page.TargetClassifierImpl conf/topic.cfg $1
