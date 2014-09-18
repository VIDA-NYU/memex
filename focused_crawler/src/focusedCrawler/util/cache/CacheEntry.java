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
package focusedCrawler.util.cache;



import focusedCrawler.util.*;



/**

 * Tupla de dado de uma cache com a chave e o dado associado

 * a chave.

 *

 * @author Oscar Miranda

 * @version %I%, %G%

 * @see focusedCrawler.util.cache.CacheFIFO

 */

public class CacheEntry {

    CacheKey key;

    Object   dado;

    int      hits;

    long     init_time;

    long     timestamp;

    int      index;



    // global init

    { clear(); }



    public int getHits() {

        return hits;

    }



    public void incHits() {

        hits++;

    }



    public void incHits(int inc) {

        hits+= inc;

    }



    public void setHits(int val) {

        hits = val;

    }



    public long getTimestamp() {

        return timestamp;

    }



    public void setTimestamp() {

        timestamp = System.currentTimeMillis();

    }



    public void hit() {

        hits++;

        timestamp = System.currentTimeMillis();

    }



    public void clear() {

        index = 0;

        hits = 0;

        init_time = System.currentTimeMillis();

        timestamp = init_time;

        key = null;

        dado = null;

    }



    /**

     * Modifica o valor da chave

     *

     *

     * @param key a nova chave

     *

     * @see focusedCrawler.util.cache.CacheKey

     */

    public void setKey(CacheKey key) {

        this.key = key;

    }



    /**

     * retorna a chave desta entry.

     *

     *

     * @return a chave desta entry

     *

     * @see focusedCrawler.util.cache.CacheKey

     */

    public CacheKey getKey() {

        return key;

    } 



    /**

     * modifica o valor do dado

     *

     *

     * @param data o novo dado

     *

     */

    public void setData(Object data) {

        this.dado = data;

    }



    /**

     * retorna o dado desta entry

     *

     *

     * @return o dado

     *

     */

    public Object getData() {

        return dado;

    }

    

    public long tempo_de_vida() {

        return System.currentTimeMillis() - init_time;

    }



    /**

     * retorna uma representacao String da chave.

     *

     *

     * @return representacao em String desta entry

     *

     */

    public String toString() {

        return "[" + key + "=" + dado + ", hits=" + hits + ", idx="+index

                + ", TS=" + timestamp + ", INIT=" + init_time

                + ", lifetime=" + Timer.toString(tempo_de_vida())+ "]";



    } 



}

