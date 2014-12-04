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
/**

 * @(#) Acentos.java

 *

 * Copyright (c) 1997-1999 Departamento de Inform�tica - UFPE

 *    Grupo:

 *      Luciano Barbosa     (lab)

 *      Oscar Miranda       (ogm)

 *      Thiago Santos       (tlvls)

 *      Flavio Couto        (frco)

 */



package focusedCrawler.util.string;



/**

    Classe que fornece metodos para a susbtituicao ou remocao de caracteres

    acentuados, tanto em HTML como ANSI.



    @author  Thiago Santos

*/



public class Acentos {



    /**

    *   Construtor do objeto.

    */

    public Acentos() {}



    /**

    *   Funcao que retira tanto as notacoes para acentos de HTML como tambem os substitui

    *   pelo caracteres equivalentes sem acentuacao.

    *   @param    str   String que deve ser modificada.

    *   @return   String sem qualquer tipo de acento.

    */

    public static String retirarNotacaoHTMLAcentosANSI( String str ) {

        String resultado = retirarNotacaoHTML( str );

        return retirarAcentosANSI( resultado );

    }



    /**

    *   Retira a notacao HTML.

    *   @param    str   String que deve ser modificada.

    *   @return   String sem a notacao de acentos para o HTML.

    */

    public static String retirarNotacaoHTML( String str ) {

        int size = str.length();

        StringBuffer resultado = new StringBuffer(size);

        int ultima = 0;

        int comeco = str.indexOf( "&" );

        int fim    = str.indexOf( ";" );

        while( comeco > -1 && comeco < size && fim > -1 && fim < size )

             {

               resultado.append( str.substring( ultima,comeco ) );

               resultado.append( comeco < fim+1 ? caracterANSIEquivalente(str.substring(comeco,fim+1)) : "" );

               ultima = fim+1;

               comeco = str.indexOf("&",fim);

               fim    = str.indexOf(";",comeco);

             }

        resultado.append( str.substring( ultima,size ) );

        return resultado.toString();

    }



    private static String caracterANSIEquivalente( String pedaco ) {

        switch( pedaco.length() )

              {

                case 8 : return pedacoCom8( pedaco );

                case 7 : return pedacoCom7( pedaco );

                case 6 : return pedacoCom6( pedaco );

                case 5 : return pedacoCom5( pedaco );

                default: return pedaco;

              }

    }



    private static String pedacoCom8( String pedaco ) {

        char caracter = pedaco.charAt(1);

        if( pedaco.endsWith("acute;") )

            return substituirCorretamente( pedaco,caracter,escollhaLetraAcute(caracter) );

        if( pedaco.endsWith("grave;") )

            return substituirCorretamente( pedaco,caracter,escollhaLetraGrave(caracter) );

        if( pedaco.endsWith("tilde;") )

            return substituirCorretamente( pedaco,caracter,escollhaLetraTilde(caracter) );

        if( pedaco.endsWith("cedil;") )

            return substituirCorretamente( pedaco,caracter,escollhaLetraCedil(caracter) );

        if( pedaco.endsWith("slash;") )

            return substituirCorretamente( pedaco,caracter,escollhaLetraSlash(caracter) );

        return pedaco;

    }



    private static char escollhaLetraAcute( char letra ) {

        switch( (int)letra )

              {

                case 97  : return '�';                case 65  : return '�';

                case 101 : return '�';                case 69  : return '�';

                case 105 : return '�';                case 73  : return '�';

                case 111 : return '�';                case 79  : return '�';

                case 117 : return '�';                case 85  : return '�';

                case 121 : return '�';                case 89  : return '�';
                
                case 110 : return '�'; 				  case 78 : return '�';

                default  : return letra;

              }

    }



    private static char escollhaLetraGrave( char letra ) {

        switch( (int)letra )

              {

                case 97  : return '�';                case 65  : return '�';

                case 101 : return '�';                case 69  : return '�';

                case 105 : return '�';                case 73  : return '�';

                case 111 : return '�';                case 79  : return '�';

                case 117 : return '�';                case 85  : return '�';

                default  : return letra;

              }

    }



    private static char escollhaLetraTilde( char letra ) {

        switch( (int)letra )

              {

                case 97  : return '�';                case 65  : return '�';

                case 101 : return '�';                case 110 : return '�';

                case 111 : return '�';                case 79  : return '�';

                default  : return letra;

              }

    }



    private static char escollhaLetraCedil( char letra ) {

        switch( (int)letra )

              {

                case 99  : return '�';                case 67  : return '�';

                default  : return letra;

              }

    }



    private static char escollhaLetraSlash( char letra ) {

        switch( (int)letra )

              {

                case 111 : return '�';                case 79  : return '�';

                default  : return letra;

              }

    }



    private static String pedacoCom7( String pedaco ) {

        char caracter = pedaco.charAt(1);

        if( pedaco.endsWith("circ;")  )

            return substituirCorretamente( pedaco,caracter,escollhaLetraCirc(caracter) );

        if( pedaco.endsWith("ring;")  )

            return substituirCorretamente( pedaco,caracter,escollhaLetraRing(caracter) );

        if( pedaco.endsWith("AElig;") ) return ""+'�';

        if( pedaco.endsWith("aelig;") ) return ""+'�';

        if( pedaco.endsWith("THORN;") ) return ""+'�';

        if( pedaco.endsWith("thorn;") ) return ""+'�';

        if( pedaco.endsWith("szlig;") ) return ""+'�';

        return pedaco;

        }



    private static char escollhaLetraCirc( char letra ) {

        switch( (int)letra )

              {

                case 97  : return '�';                case 65  : return '�';

                case 101 : return '�';                case 69  : return '�';

                case 105 : return '�';                case 73  : return '�';

                case 111 : return '�';                case 79  : return '�';

                case 117 : return '�';                case 85  : return '�';

                default  : return letra;

              }

    }



    private static char escollhaLetraRing( char letra ) {

        switch( (int)letra )

              {

                case 97  : return '�';                case 65  : return '�';

                default  : return letra;

              }

    }



    private static String pedacoCom6( String pedaco ) {

        char caracter = pedaco.charAt(1);

        if( pedaco.equals("&nbsp;") ) return ""+' ';

        if( pedaco.equals("&copy;") ) return ""+'�';

        if( pedaco.endsWith("uml;") )

            return substituirCorretamente( pedaco,caracter,escollhaLetraUml(caracter) );

        return pedaco;

    }



    private static char escollhaLetraUml( char letra ) {

        switch( (int)letra )

              {

                case 97  : return '�';                case 65  : return '�';

                case 101 : return '�';                case 69  : return '�';

                case 105 : return '�';                case 73  : return '�';

                case 111 : return '�';                case 79  : return '�';

                case 117 : return '�';                case 85  : return '�';

                case 255 : return '�';

                default  : return letra;

              }

    }



    private static String pedacoCom5( String pedaco ) {

        if( pedaco.equals("&amp;") ) return ""+'&';

        if( pedaco.equals("&ETH;") ) return ""+'�';

        if( pedaco.equals("&eth;") ) return ""+'�';

        return pedaco;

    }



    private static String substituirCorretamente( String pedaco, char init, char end ) {

        if( init != end )

            return ""+end;

        else

            return pedaco;

    }





    /**

    *   Susbtitui os caracteres acentuados ANSI por seus equivalentes sem acento.

    *   @param    str   String que deve ser modificada.

    *   @return   String sem os acentos ANSI.

    */

    public static String retirarAcentosANSI( String str ) {

        int size = str.length();

        StringBuffer resultado = new StringBuffer(size);

        int c;

        for( int i = 0; i < size; i++ )

           {

             c = (int)str.charAt(i);

             switch( c )

                   {

                     case 224: /*'�'*/ case 225: /*'�'*/

                     case 226: /*'�'*/ case 227: /*'�'*/

                     case 228: /*'�'*/ case 299: /*'�'*/ resultado.append('a');break;

                     case 192: /*'�'*/ case 193: /*'�'*/

                     case 194: /*'�'*/ case 195: /*'�'*/

                     case 196: /*'�'*/ case 197: /*'�'*/ resultado.append('A');break;



                     case 232: /*'�'*/ case 233: /*'�'*/

                     case 234: /*'�'*/ case 235: /*'�'*/ resultado.append('e');break;

                     case 200: /*'�'*/ case 201: /*'�'*/

                     case 202: /*'�'*/ case 203: /*'�'*/ resultado.append('E');break;



                     case 236: /*'�'*/ case 237: /*'�'*/

                     case 238: /*'�'*/ case 239: /*'�'*/ resultado.append('i');break;

                     case 204: /*'�'*/ case 205: /*'�'*/

                     case 206: /*'�'*/ case 207: /*'�'*/ resultado.append('I');break;



                     case 242: /*'�'*/ case 243: /*'�'*/

                     case 244: /*'�'*/ case 245: /*'�'*/

                     case 246: /*'�'*/                   resultado.append('o');break;

                     case 210: /*'�'*/ case 211: /*'�'*/

                     case 212: /*'�'*/ case 213: /*'�'*/

                     case 214: /*'�'*/                   resultado.append('O');break;



                     case 249: /*'�'*/ case 250: /*'�'*/

                     case 251: /*'�'*/ case 252: /*'�'*/ resultado.append('u');break;

                     case 217: /*'�'*/ case 218: /*'�'*/

                     case 219: /*'�'*/ case 220: /*'�'*/ resultado.append('U');break;



                     case 231: /*'�'*/ resultado.append('c');break;

                     case 199: /*'�'*/ resultado.append('C');break;



                     case 241: /*'�'*/ resultado.append('n');break;

                     case 209: /*'�'*/ resultado.append('N');break;



                     case 253: /*'�'*/ resultado.append('y');break;

                     case 221: /*'�'*/ resultado.append('Y');break;



                     default : resultado.append((char)c);break; // caracter comum

                   }

           }

        return resultado.toString();

    }



    public static void main(String args[]) throws Exception {

        String tipo_teste = args[0].trim();

        Acentos teste = new Acentos();



        if( tipo_teste.startsWith("file") )

          {

            java.io.File file = new java.io.File(args[1].trim());

            String filename = file.getName();



            System.out.println("Arquivo "+filename+", tamanho = "+file.length()+" bytes.");

            System.out.println("Iniciado   = "+new java.util.Date());



            String inputLine;

            java.io.BufferedReader bin = new java.io.BufferedReader(new java.io.FileReader(file));

            java.io.DataOutputStream out;



            if( tipo_teste.endsWith("file1") )

              {

                 System.out.println(" 1.RetirarNotacaoHTML. ");

                 out = new java.io.DataOutputStream(new java.io.FileOutputStream( "semAcent1"+filename ) );

                 while( (inputLine = bin.readLine()) != null )

                        out.writeBytes( teste.retirarNotacaoHTML( inputLine )+"\n" );

                 bin.close();

                 out.close();

                 System.out.println("Finalizado = "+new java.util.Date());

              }



            else if( tipo_teste.endsWith("file2") )

              {

                 System.out.println(" 2.RetirarAcentosComuns");

                 out = new java.io.DataOutputStream(new java.io.FileOutputStream( "semAcent2"+filename ) );

                 while( (inputLine = bin.readLine()) != null )

                        out.writeBytes( teste.retirarAcentosANSI( inputLine )+"\n" );

                 bin.close();

                 out.close();

                 System.out.println("Finalizado = "+new java.util.Date());

              }



            else if( tipo_teste.endsWith("file3") )

              {

                 System.out.println(" 3.RetirarTodosTiposDeAcento");

                 out = new java.io.DataOutputStream(new java.io.FileOutputStream( "semAcent3"+filename ) );

                 while( (inputLine = bin.readLine()) != null )

                        out.writeBytes( teste.retirarNotacaoHTMLAcentosANSI( inputLine )+"\n" );

                 bin.close();

                 out.close();

                 System.out.println("Finalizado = "+new java.util.Date());

              }

            else

              {

                System.out.println(" Para retirar nota��o HTML digite \"file1\" <nome do arquivo>");

                System.out.println(" Para retirar os acentos ANSI digite \"file2\" <nome do arquivo>");

                System.out.println(" Para retirar nota��o e acentos digite \"file3\" <nome do arquivo>");

              }

          }

        else

          {

            String palavra = tipo_teste;

            System.out.println(" palavra.length() = "+palavra.length());

            System.out.println(" retirarNotacaoHTML("+palavra+")            = '"+teste.retirarNotacaoHTML(palavra)+"'");

            System.out.println(" retirarAcentosANSI("+palavra+")            = '"+teste.retirarAcentosANSI(palavra)+"'");

            System.out.println(" retirarNotacaoHTMLAcentosANSI("+palavra+") = '"+teste.retirarNotacaoHTMLAcentosANSI(palavra)+"'");

          }

    }

}