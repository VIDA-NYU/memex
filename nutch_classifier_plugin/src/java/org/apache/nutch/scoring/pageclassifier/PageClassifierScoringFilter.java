/**
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


package org.apache.nutch.scoring.pageclassifier;

import java.util.Collection;
import java.util.List;
import java.util.Map.Entry;

//Slf4j Logging imports
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.io.Text;
import org.apache.nutch.crawl.CrawlDatum;
import org.apache.nutch.crawl.Inlinks;
import org.apache.nutch.indexer.NutchDocument;
import org.apache.nutch.metadata.Nutch;
import org.apache.nutch.parse.Parse;
import org.apache.nutch.parse.ParseData;
import org.apache.nutch.protocol.Content;
import org.apache.nutch.scoring.ScoringFilter;
import org.apache.nutch.scoring.ScoringFilterException;
import org.apache.nutch.scoring.pageclassifier.PageClassifier;


/*
 * Goal:
 * author:
 */
public class PageClassifierScoringFilter implements ScoringFilter {
	
	private final static Logger LOG = LoggerFactory.getLogger(PageClassifierScoringFilter.class);

	private Configuration conf;
	private PageClassifier pc;
	
	public Configuration getConf() {
		return conf;
	}

	public void setConf(Configuration conf) {
		this.conf = conf;
		pc = new PageClassifier(conf);
	}
	
	public float classify(String text){
		return (float)pc.classify(text);
	}

	@Override
	public void injectedScore(Text url, CrawlDatum datum)
			throws ScoringFilterException {
		// TODO Auto-generated method stub

	}

	@Override
	public void initialScore(Text url, CrawlDatum datum)
			throws ScoringFilterException {
		datum.setScore(0.0f);
	}

	@Override
	public float generatorSortValue(Text url, CrawlDatum datum, float initSort)
			throws ScoringFilterException {
		// TODO Auto-generated method stub
		return datum.getScore() * initSort;
	}

	@Override
	public void passScoreBeforeParsing(Text url, CrawlDatum datum,
			Content content) throws ScoringFilterException {
		// TODO Auto-generated method stub

	}

	public void passScoreAfterParsing(Text url, Content content, Parse parse)
			throws ScoringFilterException {
		Float score = classify(parse.getText());
		parse.getData().getContentMeta().set(Nutch.SCORE_KEY, Float.toString(score));
	}

	/*
	 * outlinks are assigned the same score as the source page.
	 * Therefore, outlinks will be fetch if they come from high score page and vice versa.
	 * When using this filter, we need to set the threshold in nutch configuration so that it won't fetch links with low scores.
	 */
	public CrawlDatum distributeScoreToOutlinks(Text fromUrl,
			ParseData parseData, Collection<Entry<Text, CrawlDatum>> targets,
			CrawlDatum adjust, int allCount) throws ScoringFilterException {
		float score = 0.0f;
	    String scoreString = parseData.getContentMeta().get(Nutch.SCORE_KEY);
	    if (scoreString != null) {
	      try {
	        score = Float.parseFloat(scoreString);
	      } catch (Exception e) {
	        LOG.error("Error: ", e);
	      }
	    }
		for (Entry<Text, CrawlDatum> target : targets) {
			target.getValue().setScore(score);
		}
		return adjust;
	}

	@Override
	public void updateDbScore(Text url, CrawlDatum old, CrawlDatum datum,
			List<CrawlDatum> inlinked) throws ScoringFilterException {
		// TODO Auto-generated method stub

	}

	@Override
	public float indexerScore(Text url, NutchDocument doc, CrawlDatum dbDatum,
			CrawlDatum fetchDatum, Parse parse, Inlinks inlinks, float initScore)
			throws ScoringFilterException {
		// TODO Auto-generated method stub
		return initScore;
	}

}
