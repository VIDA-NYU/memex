import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.InputStream;
import java.io.StringReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Properties;
import java.util.ArrayList;
import org.apache.commons.codec.binary.Base64;
import org.xml.sax.InputSource;
import org.w3c.dom.*;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;

public class BingSearch {
    
  private String accountKey;
  private Properties prop; 

  public BingSearch(){
    try{
        prop = new Properties();
        prop.load(getClass().getClassLoader().getResourceAsStream("conf/config.properties"));
        //accountKey = "jgRfXs073p8B87c/TJamrnIDjbeyYtH5gAe7+TYvsIw";
        accountKey = prop.getProperty("ACCOUNTKEY");
    }   
    catch(Exception e){
        prop = null;
    }
  } 

  public ArrayList<String> read_input(String prefix, String filename){
    ArrayList<String> queries = new ArrayList<String>();
    try{
      File file = new File(filename);
      FileReader fileReader = new FileReader(file);
      BufferedReader bufferedReader = new BufferedReader(fileReader);
      String line;
      while ((line = bufferedReader.readLine()) != null) {
        queries.add(prefix + ":" + line);
      }
      fileReader.close();
    }
    catch(Exception e){
        e.printStackTrace();
    }
    return queries;
  }

  public ArrayList<String> search_manual(String filename, String top){
    ArrayList<String> queries = read_input(new String(""), filename);
    return search_multi_queries(queries, top);
  }

  public ArrayList<String> search_backlink(String filename, String top){
    ArrayList<String> queries = read_input(new String("link"), filename);
    return search_multi_queries(queries, top);
  }

  public ArrayList<String> search_related(String filename, String top){
    ArrayList<String> queries = read_input(new String("related"), filename);
    return search_multi_queries(queries, top);
  }

  public ArrayList<String> search_multi_queries(ArrayList<String> queries, String top){
    ArrayList<String> results = new ArrayList<String>();
    for(String query : queries){
      results.addAll(search(query, top));
    }
    return results;
  }

  public ArrayList<String> search(String query, String top){
    System.out.println("Query: " + query);
    if (this.prop == null){
        System.out.println("Error: config file is not loaded yet");
        return null;
    }
    ArrayList<String> results = new ArrayList<String>();
    query = query.replaceAll(" ", "%20");
    //String accountKey="jgRfXs073p8B87c/TJamrnIDjbeyYtH5gAe7+TYvsIw";
    byte[] accountKeyBytes = Base64.encodeBase64((this.accountKey + ":" + this.accountKey).getBytes());
    String accountKeyEnc = new String(accountKeyBytes);
    URL url;
    try {
      url = new URL("https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/Web?Query=%27" + query + "%27&$top="+ top);
      HttpURLConnection conn = (HttpURLConnection)url.openConnection();
      conn.setRequestMethod("GET");
      conn.setRequestProperty("Authorization", "Basic " + accountKeyEnc);

      BufferedReader br = new BufferedReader(new InputStreamReader((conn.getInputStream())));
      String output = "";
      String line;
      while ((line = br.readLine()) != null) {
          output = output + line;
      } 
      //System.out.println(output);
      conn.disconnect();

      DocumentBuilderFactory docBuilderFactory = DocumentBuilderFactory.newInstance();
      DocumentBuilder docBuilder = docBuilderFactory.newDocumentBuilder(); 
      InputSource is = new InputSource(new StringReader(output));
      Document doc = docBuilder.parse(is);
      NodeList urls = doc.getElementsByTagName("d:DisplayUrl");
      int totalUrls = urls.getLength();
      //System.out.println("Number of urls:" +  totalUrls);
      //System.out.println(urls);
      for (int i=0; i<urls.getLength(); i++){
        Element e = (Element)urls.item(i);
        NodeList nl = e.getChildNodes();
        results.add((nl.item(0).getNodeValue()));
      }
	} 
    catch (MalformedURLException e1) {
        e1.printStackTrace();
    } 
    catch (IOException e) {
        e.printStackTrace();
    }
    catch (Exception e){
        e.printStackTrace();
    }
    System.out.println("Number of results: " + String.valueOf(results.size()));
    return results;
  }

  public static void main(String[] args) {
    if (args.length != 4){
      System.out.println("Wrong arguments, see README");
      return;
    }

    String mode = args[0];
    String filename = args[1];
    String top = args[2];    
    String output = args[3];
    BingSearch bs = new BingSearch();
    ArrayList<String> results = null;
    
    if (mode.equals("m"))
      results = bs.search_manual(filename, top);
    else if (mode.equals("b"))
      results = bs.search_backlink(filename, top);
    else if (mode.equals("r"))
      results = bs.search_related(filename, top);
    try{
        PrintWriter writer = new PrintWriter(output, "UTF-8");
        for (String result : results){
            writer.println(result);
        }
        writer.close();
    }
    catch(Exception e){
        e.printStackTrace();
    }
  }        
}
