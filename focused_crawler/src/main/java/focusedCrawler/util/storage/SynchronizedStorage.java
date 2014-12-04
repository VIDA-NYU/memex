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
 package focusedCrawler.util.storage;



import java.util.Enumeration;

import java.util.Vector;

import focusedCrawler.util.DataNotFoundException;
import focusedCrawler.util.distribution.CommunicationException;


public class SynchronizedStorage implements Storage  {



    private Object mutex;

    private Storage storage;



    /**

     * Contrutor

     */

    public SynchronizedStorage(Storage storage) {

        this.storage = storage;

        this.mutex = this;

    }



    /**

     * Contrutor

     */

    public SynchronizedStorage(Storage storage, Object mutex) {

        this.storage = storage;

        this.mutex = mutex;

    }



    public Object insert(Object obj) throws StorageException, CommunicationException {

        synchronized(mutex) {

            return storage.insert(obj);

        }

    }



    public Object[] insertArray(Object[] objs) throws StorageException, CommunicationException {

        synchronized(mutex) {

            return storage.insertArray(objs);

        }

    }



    public Object select(Object obj) throws StorageException, DataNotFoundException, CommunicationException {

        synchronized(mutex) {

            return storage.select(obj);

        }

    }

    public Object[] selectArray(Object[] objs) throws StorageException, DataNotFoundException, CommunicationException {

        synchronized(mutex) {

            return storage.selectArray(objs);

        }

    }

    public Enumeration selectEnumeration(Object obj) throws StorageException, DataNotFoundException, CommunicationException {

        synchronized(mutex) {

            return storage.selectEnumeration(obj);

        }

    }

    public Object update(Object obj) throws StorageException, CommunicationException {

        synchronized(mutex) {

            return storage.update(obj);

        }

    }

    public Object[] updateArray(Object[] objs) throws StorageException, CommunicationException {

        synchronized(mutex) {

            return storage.updateArray(objs);

        }

    }

    public Object remove(Object obj) throws StorageException, CommunicationException {

        synchronized(mutex) {

            return storage.remove(obj);

        }

    }

    public Object[] removeArray(Object[] objs) throws StorageException, CommunicationException {

        synchronized(mutex) {

            return storage.removeArray(objs);

        }

    }

    public Object addResource(Object obj) throws StorageException, CommunicationException {

        synchronized(mutex) {

            return storage.addResource(obj);

        }

    }

    public Object[] addResourceArray(Object[] objs) throws StorageException, CommunicationException {

        synchronized(mutex) {

            return storage.addResourceArray(objs);

        }

    }

    public Object removeResource(Object obj) throws StorageException, CommunicationException {

        synchronized(mutex) {

            return storage.removeResource(obj);

        }

    }

    public Object[] removeResourceArray(Object[] objs) throws StorageException, CommunicationException {

        synchronized(mutex) {

            return storage.removeResourceArray(objs);

        }

    }

    public Object commit(Object obj) throws StorageException, CommunicationException {

        synchronized(mutex) {

            return storage.commit(obj);

        }

    }

    public Object rollback(Object obj) throws StorageException, CommunicationException {

        synchronized(mutex) {

            return storage.rollback(obj);

        }

    }

    public Object finalize(Object obj) throws StorageException, CommunicationException {

        synchronized(mutex) {

            return storage.finalize(obj);

        }

    }

    public Object ping(Object obj) throws StorageException, CommunicationException {

        return storage.ping(obj);

    }





}