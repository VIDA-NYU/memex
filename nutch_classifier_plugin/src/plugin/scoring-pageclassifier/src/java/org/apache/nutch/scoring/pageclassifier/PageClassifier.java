package org.apache.nutch.scoring.pageclassifier;

import java.net.MalformedURLException;



import weka.core.Instances;
import weka.classifiers.Classifier;

import org.apache.nutch.scoring.pageclassifier.VSMElement;
import org.apache.nutch.scoring.pageclassifier.VSMVector;
import org.apache.nutch.scoring.pageclassifier.StopList;
import org.apache.nutch.scoring.pageclassifier.StopListArquivo;
import org.apache.nutch.scoring.pageclassifier.Page;
import org.apache.nutch.scoring.pageclassifier.Target;
import org.apache.hadoop.conf.Configuration;

import org.xml.sax.SAXException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.io.IOException;
import java.util.List;

//Slf4j Logging imports
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PageClassifier {
	private Classifier classifier;
	private Instances instances;
	private String[] features;
	private StopList stoplist;
	private Instances insts;
	private final static Logger LOG = LoggerFactory.getLogger(PageClassifierScoringFilter.class);
	
	public PageClassifier(Configuration conf){
		try{
			initClassifier(conf);
		}
		catch(Exception e){
			LOG.error("Error: ", e);
		}
	}
	
	private String[] readFeatureFile(String featureFile){
		String features = "";
		String[] featureList = null;
        try {
            List<String> lines = Files.readAllLines(Paths.get(featureFile), Charset.defaultCharset());
            for (String line : lines) {
                features += line;
            }
            featureList = features.split(" ");
        } catch (IOException e) {
        	LOG.error("Error: ", e);
        }
		return featureList;
	}
	
	private void initClassifier(Configuration conf) throws Exception
	{
		String modelFile = conf.get("scoring.model.filename");
		String stoplistFile = conf.get("scoring.stoplist.filename");
		String featureFile = conf.get("scoring.feature.filename");
		String[] classValues = conf.get("scoring.class.values").split(" ");
		
		this.stoplist = new StopListArquivo(stoplistFile);
		this.classifier = (Classifier) weka.core.SerializationHelper.read(modelFile);
		this.features = readFeatureFile(featureFile);
		
		weka.core.FastVector vectorAtt = new weka.core.FastVector();
		for (int i = 0; i < features.length; i++) {
			vectorAtt.addElement(new weka.core.Attribute(features[i]));
		}
		
		weka.core.FastVector classAtt = new weka.core.FastVector();
		for (int i = 0; i < classValues.length; i++) {
			classAtt.addElement(classValues[i]);
		}
		vectorAtt.addElement(new weka.core.Attribute("class", classAtt));
		this.insts = new Instances("target_classification", vectorAtt, 1);
		this.insts.setClassIndex(features.length);
	}
	
	public double classify(String text){
		double[] result = null;
		try{
			double[] values = getValues(new Page(null, text));
			weka.core.Instance instanceWeka = new weka.core.Instance(1, values);
			instanceWeka.setDataset(instances);
			result = this.classifier.distributionForInstance(instanceWeka);
		}catch(Exception e){
			LOG.error("Error: ", e);
			return 0.0f;
	    }
		return result[0];
	}
	
	private double[] getValues(Target target) throws MalformedURLException, SAXException {
		VSMVector vsm = null;
		vsm = new VSMVector(target.getSource(),stoplist,true);

		double[] values = new double[features.length];
		for (int i = 0; i < features.length; i++) {
			VSMElement elem = vsm.getElement(features[i]);
			if (elem == null) {
				values[i] = 0;
			}else{
				values[i] = elem.getWeight();
			}
		}
		return values;
	}

}
