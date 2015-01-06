mkdir -p class
find ./src/ -name "*.java" > sources.txt
javac -d class -encoding ISO-8859-1 -cp .:libs/weka.jar:libs/nekohtml.jar:libs/xercesImpl.jar @sources.txt
rm -rf sources.txt
