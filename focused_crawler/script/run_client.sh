#!/bin/sh
cd .;
# java -Xmx1g -cp class focusedCrawler.crawler.CrawlerManager conf/crawler/crawler.cfg > log/crawler.log 2>&1 &
java -Xmx1g -cp build/classes/main focusedCrawler.crawler.CrawlerManager conf/crawler/crawler.cfg > log/crawler.log 2>&1 &