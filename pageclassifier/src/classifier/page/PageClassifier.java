/*
############################################################################
##
## Copyright (C) 2006-2009 University of Utah. All rights reserved.
##
## This file is part of DeepPeep.
##
## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE.GPL included in the packaging of
## this file.  Please review the following to ensure GNU General Public
## Licensing requirements will be met:
## http://www.opensource.org/licenses/gpl-license.php
##
## If you are unsure which license is appropriate for your use (for
## instance, you are interested in developing a commercial derivative
## of DeepPeep), please contact us at deeppeep@sci.utah.edu.
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
############################################################################
*/
package classifier.page;

import classifier.util.Page;
import classifier.util.Target;
import weka.core.Instances;
import weka.classifiers.Classifier;
import classifier.util.ParameterFile;
import classifier.util.vsm.VSMElement;
import classifier.util.vsm.VSMVector;
import classifier.util.string.StopList;
import classifier.util.string.StopListArquivo;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.ObjectInputStream;
import java.net.URL;

import org.xml.sax.SAXException;

/**
 * <p> </p>
 *
 * <p>Description: </p>
 *
 * <p>Copyright: Copyright (c) 2004</p>
 *
 * <p> </p>
 *
 * @author Luciano Barbosa
 * @version 1.0
 */
public class PageClassifier {

	private Classifier classifier;
	private Instances instances;
	private String[] attributes;
	private StopList stoplist;
  
	public PageClassifier(Classifier classifier, Instances instances, String[] attributes, StopList stoplist){
		this.classifier = classifier;
		this.instances = instances;
		this.attributes = attributes;
		this.stoplist = stoplist;
	}

	public double[] classify(String target) throws Exception{
		double[] result = null;
		try{
			double[] values = getValues(new Page(null,target));
			weka.core.Instance instanceWeka = new weka.core.Instance(1, values);
			instanceWeka.setDataset(instances);
			result = classifier.distributionForInstance(instanceWeka);
		}catch(Exception ex){
			ex.printStackTrace();
	    }
		return result;
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

	public static PageClassifier loadClassifier(String cfgDir) throws IOException, ClassNotFoundException{
		String stoplistFile = cfgDir + "/stoplist.txt";
		String modelFile = cfgDir + "/pageclassifier.model";
        String featureFile = cfgDir + "/pageclassifier.features";

		StopList stoplist = new StopListArquivo(stoplistFile);
		InputStream is = new FileInputStream(modelFile);
		ObjectInputStream objectInputStream = new ObjectInputStream(is);
		Classifier classifier = (Classifier) objectInputStream.readObject();

		ParameterFile featureConfig = new ParameterFile(featureFile);
		String[] attributes = featureConfig.getParam("ATTRIBUTES", " ");
		weka.core.FastVector vectorAtt = new weka.core.FastVector();
		for (int i = 0; i < attributes.length; i++) {
			vectorAtt.addElement(new weka.core.Attribute(attributes[i]));
		}
		String[] classValues = featureConfig.getParam("CLASS_VALUES", " ");
		weka.core.FastVector classAtt = new weka.core.FastVector();
		for (int i = 0; i < classValues.length; i++) {
			classAtt.addElement(classValues[i]);
		}
		vectorAtt.addElement(new weka.core.Attribute("class", classAtt));
		Instances insts = new Instances("target_classification", vectorAtt, 1);
		insts.setClassIndex(attributes.length);
		return new PageClassifier(classifier, insts, attributes, stoplist);
	}
  
	public static void main(String[] args) {
  		try{
  			PageClassifier classifier = PageClassifier.loadClassifier(args[0]);
			long startTime = System.currentTimeMillis();
			for (int i = 0; i< 10; i++){
	        	File file = new File(args[1]);
   		    	FileInputStream fis = new FileInputStream(file);
        		byte[] data = new byte[(int)file.length()];
	        	fis.read(data);
    	    	fis.close();
        		String s = new String(data, "UTF-8");
	        	double prob = classifier.classify(s)[0];
				System.out.println("Prob = "  + String.valueOf(prob));        
			}
			long stopTime = System.currentTimeMillis();
			System.out.println("Total time to classify 10 documents: " + String.valueOf(stopTime-startTime) + " miliseconds");
  		}catch(Exception ex){
  			ex.printStackTrace();
  		}
	}
  
}
