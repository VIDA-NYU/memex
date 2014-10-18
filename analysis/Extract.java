import java.io.*;
import de.l3s.boilerpipe.extractors.ArticleExtractor;
import java.net.URL;
import java.util.*;
import java.util.HashMap;
import java.lang.String;
import java.net.URLDecoder;

public class Extract {
  private HashMap<String, String> m;
  private HashMap<String, ArrayList<String>> contentMap; //keeps file paths for documents with same content

  public Extract()
  {
    m = new HashMap<String, String>();
    contentMap = new HashMap<String, ArrayList<String>>();
  }  
  private String readFile(String pathname) throws IOException {
    File file = new File(pathname);
    StringBuilder fileContents = new StringBuilder((int)file.length());
    Scanner scanner = new Scanner(file);
    String lineSeparator = System.getProperty("line.separator");
    try {
        while(scanner.hasNextLine()) {        
            fileContents.append(scanner.nextLine() + lineSeparator);
        }
        return fileContents.toString();
    } finally {
        scanner.close();
    }
  }

  private void deduplicateContent() {
    try {
      Runtime r = Runtime.getRuntime();
      Process p;
      for(String c: contentMap.keySet()) {
        List<String> tmp = contentMap.get(c);
        if(tmp.size() > 1) {
          int size = tmp.size();
          for(String s: tmp) {
            if(size == 1) break;
            p = r.exec("rm " + s);
            p.waitFor();
            size--;
          }
          System.out.println("**");
        }
      }
    } 
    catch(IOException e1) {}
    catch(InterruptedException e2) {}	
  }

  public  void  process(File f, String url)
  {
    try{
          //System.out.println(f.getPath());
          String content = readFile(f.getPath());
          content = ArticleExtractor.INSTANCE.getText(content);
          content = content.trim().replaceAll(" +", " ");
          content = content.replaceAll("[\n\"\t]", " ").toLowerCase();

          //the if below helps to identify false positives by printing them so one can analyse them manually
          if(!content.matches("(.*)sex(.*)") && !content.matches("(.*)traffick(.*)") && !content.matches("(.*)exploitation(.*)") && !content.matches("(.*)slave(.*)") && !content.matches("(.*)prostitution(.*)") && !content.matches("(.*)labor(.*)") && !content.matches("(.*)organ(.*)") && !content.matches("(.*)forced marriage(.*)")) {
            System.out.println(f.getPath() + "\n" + content + "\n");
          }

          if(contentMap.containsKey(content)) {
	    contentMap.get(content).add(f.getPath());
          } else {
            contentMap.put(content, new ArrayList<String>());
            contentMap.get(content).add(f.getPath());
          }
	  deduplicateContent();
          //System.out.println(url + "\t" + m.get(url) + "\t" + content);
    }
    catch(Exception e){
      System.out.println("process Exception");
    }
     
  }
  public void listFiles(final File folder) {
    for (final File fileEntry : folder.listFiles()) {
        if (fileEntry.isDirectory()) {
            listFiles(fileEntry);
        } else {
            process(fileEntry, URLDecoder.decode(fileEntry.getName()));
        }
    }
  }

  public void getTimestamp(String filename)
  {
    try
    {
      BufferedReader br = new BufferedReader(new FileReader(filename));
      String line;
      while ((line = br.readLine()) != null) 
      {
        try
        {
          String[] url_tp = line.replace("\n", "").split("\t");
          m.put(url_tp[0], url_tp[1]);
        }
        catch(Exception ex)
        {
          ex.printStackTrace();
        }
      }
      br.close();
    }
    catch(Exception ex)
    {
      ex.printStackTrace();
    }
  }  

  public static void main(String[] args) {
    try{
          String inputpath = args[0];
          File folder = new File(inputpath);
          Extract e = new Extract();
          e.listFiles(folder);
    } catch(Exception e){
      System.out.println("Exception");
    }
  }
}
