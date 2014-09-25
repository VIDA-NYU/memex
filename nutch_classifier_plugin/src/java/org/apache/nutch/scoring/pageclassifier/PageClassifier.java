package org.apache.nutch.scoring.pageclassifier;

import org.apache.nutch.scoring.pageclassifier.Page;
import org.apache.nutch.scoring.pageclassifier.Target;

import weka.core.Instances;
import weka.classifiers.Classifier;

import org.apache.nutch.scoring.pageclassifier.ParameterFile;
import org.apache.nutch.scoring.pageclassifier.VSMElement;
import org.apache.nutch.scoring.pageclassifier.VSMVector;
import org.apache.nutch.scoring.pageclassifier.StopList;
import org.apache.nutch.scoring.pageclassifier.StopListArquivo;

import org.xml.sax.SAXException;

import org.apache.hadoop.conf.Configuration;

public class PageClassifier {
	
	//private String modelFile;
	//private String stopwordFile;
	//private String[] attributes;
	private String confFile;
	private Classifier classifier;
	private Instances instances;
	private String[] attributes;
	private StopList stoplist;
	private Instances insts;
	
	
	
	public PageClassifier(Configuration conf){
		try{
			confFile = conf.get("scoring.conf.filename");
			initClassifier(conf, confFile);
		//modelFile = conf.get("scoring.model.filename");
		//stopwordFile = conf.get("scoring.stopword.filename");
		}
		catch(Exception ex){
			ex.printStackTrace();
		}
	}
	
	private void initClassifier(Configuration conf, String confFile) throws Exception
	{
		ParameterFile config = new ParameterFile(confFile);
		String stoplistfile = config.getParam("STOPLIST_FILES");
		this.stoplist = new StopListArquivo(stoplistfile);
		String classifierfile = config.getParam("FILE_CLASSIFIER");
		/*
		InputStream is = new FileInputStream(classifierfile);
		ObjectInputStream objectInputStream = new ObjectInputStream(is);
		this.classifier = (Classifier) objectInputStream.readObject();
		*/
		this.classifier = (Classifier) weka.core.SerializationHelper.read(classifierfile);
		this.attributes = config.getParam("ATTRIBUTES", " ");
		weka.core.FastVector vectorAtt = new weka.core.FastVector();
		for (int i = 0; i < attributes.length; i++) {
			vectorAtt.addElement(new weka.core.Attribute(attributes[i]));
		}
		String[] classValues = config.getParam("CLASS_VALUES", " ");
		weka.core.FastVector classAtt = new weka.core.FastVector();
		for (int i = 0; i < classValues.length; i++) {
			classAtt.addElement(classValues[i]);
		}
		vectorAtt.addElement(new weka.core.Attribute("class", classAtt));
		this.insts = new Instances("target_classification", vectorAtt, 1);
		this.insts.setClassIndex(attributes.length);
	}
	
	public double classify(String text){
		double[] result = null;
		try{
			double[] values = getValues(new Page(null, text));
			weka.core.Instance instanceWeka = new weka.core.Instance(1, values);
			instanceWeka.setDataset(instances);
			result = this.classifier.distributionForInstance(instanceWeka);
		}catch(Exception ex){
			ex.printStackTrace();
	    }
		return result[0];
	}
	
	private double[] getValues(Target target) throws IOException, SAXException {
		VSMVector vsm = null;
		vsm = new VSMVector(target.getSource(),stoplist,true);

		double[] values = new double[attributes.length];
		for (int i = 0; i < attributes.length; i++) {
			VSMElement elem = vsm.getElement(attributes[i]);
			if (elem == null) {
				values[i] = 0;
			}else{
				values[i] = elem.getWeight();
			}
		}
		return values;
	}

}
