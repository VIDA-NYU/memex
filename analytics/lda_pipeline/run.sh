sh compile_Extract.sh
mkdir -r data
LDADATA="data/lda_input.csv"
java -cp .:lib/boilerpipe-1.2.0.jar:lib/nekohtml-1.9.13.jar:lib/xerces-2.9.1.jar Extract ../focused_crawler/data/data_target/ focused_crawler/data/data_monitor/relevantpages.csv  | python concat_nltk.py $LDADATA
echo "Done Preproccessing"
echo "Running LDA..."
java -jar lib/tmt-0.4.0.jar ht.scala
