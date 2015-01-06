import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import org.apache.commons.codec.binary.Base64;

public class BingSearch {
  public static void main(String[] args) {
    String keyword = "Human Trafficking";
    String top = "50";
    if (args.length == 2){
      keyword = args[0];
      top = args[1];
    }
    keyword = keyword.replaceAll(" ", "%20");
    String accountKey="jgRfXs073p8B87c/TJamrnIDjbeyYtH5gAe7+TYvsIw";
    byte[] accountKeyBytes = Base64.encodeBase64((accountKey + ":" + accountKey).getBytes());
    String accountKeyEnc = new String(accountKeyBytes);
    URL url;
    try {
      url = new URL("https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/Web?Query=%27" + keyword + "%27&$top="+ top);
      HttpURLConnection conn = (HttpURLConnection)url.openConnection();
      conn.setRequestMethod("GET");
      conn.setRequestProperty("Authorization", "Basic " + accountKeyEnc);

      BufferedReader br = new BufferedReader(new InputStreamReader((conn.getInputStream())));
      String output = "";
      String line;
      while ((line = br.readLine()) != null) {
          output = output + line;
      } 
      System.out.println(output);
      conn.disconnect(); 
	  } catch (MalformedURLException e1) {
        e1.printStackTrace();
    } catch (IOException e) {
        e.printStackTrace();
    }
  }        
}
