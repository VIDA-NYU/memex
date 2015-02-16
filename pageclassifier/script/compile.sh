mkdir -p class
find ./src/ -name "*.java" > sources.txt
javac -d class -encoding ISO-8859-1 -cp .:libs/weka-stable-3.6.10.jar:libs/nekohtml-1.9.20.jar:libs/xercesImpl-2.11.0.jar @sources.txt
rm -rf sources.txt
