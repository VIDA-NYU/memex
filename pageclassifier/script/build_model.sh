#!/bin/bash
TRAINING_DATA_DIR=$1 #TRAINING_DATA_DIR that contain training examples. it should have two subdirectories: positive and negative
OUTPUT_DIR=$2 #OUTPUT_DIR directory
mkdir -p $OUTPUT_DIR
java -Xmx8g -cp class:libs/weka-stable-3.6.10.jar classifier.page.CreateWekaInput conf/ $TRAINING_DATA_DIR $OUTPUT_DIR
#./build/install/ache/bin/ache buildModel $TRAINING_DATA_DIR $OUTPUT_DIR
echo "CLASS_VALUES  S NS" > ${OUTPUT_DIR}/pageclassifier.features
echo -n "ATTRIBUTES " >> ${OUTPUT_DIR}/pageclassifier.features
cat ${TRAINING_DATA_DIR}/weka.arff | awk '{FS=" "; if (($1=="@ATTRIBUTE") && ($3=="REAL")) {print $2}}' | sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/ /g' >> ${OUTPUT_DIR}/pageclassifier.features
