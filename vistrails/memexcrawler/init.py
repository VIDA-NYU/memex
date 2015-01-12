from vistrails.core.modules.config import ModuleSettings
from vistrails.core.configuration import get_vistrails_configuration
from vistrails.core.modules.vistrails_module import Module, ModuleError, \
    ModuleSuspended, NotCacheable

import io
import os
import os.path
import scp
import time
# Assume server is running on a system using posixpath
import posixpath

import tej
from userpackages.tej.init import BaseSubmitJob, QueueCache, ServerLogger, \
    RemoteJob

class Crawler(Module):
    """ Crawler creates a dict with information about the crawler

    """
    _input_ports = [('queue', '(org.vistrails.extra.tej:Queue)'),
                    ('name', '(basic:String)',
                     {'optional': True, 'defaults': "['default']"}),
                    ('bin_path', '(basic:Path)'),
                    ]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)')]

    def compute(self):
        crawler = {'queue':self.get_input('queue'),
                   'name':self.get_input('name'),
                   'bin_path':self.get_input('bin_path').name
                   }
        crawler['long_name'] = crawler['name'] + '-achecrawler'
        crawler['crawler_dir'] = posixpath.join('~', '.crawler', crawler['name'])
        crawler['data_dir'] = posixpath.join(crawler['crawler_dir'], 'data')
        crawler['model_dir'] = posixpath.join(crawler['crawler_dir'], 'model')
        crawler['seeds_dir'] = posixpath.join(crawler['crawler_dir'], 'seeds')
        crawler['seeds_file'] = posixpath.join(crawler['seeds_dir'], 'seeds')
        crawler['url_examples_dir'] = posixpath.join(crawler['crawler_dir'], 'url_examples')
        crawler['examples_dir'] = posixpath.join(crawler['crawler_dir'], 'examples')
        # using default server conf for now
        # Later we may want to copy it to crawler dir and modify it
        crawler['conf_dir'] = posixpath.join(crawler['bin_path'], 'conf', 'conf_default')

        crawler['script_dir'] = posixpath.join(crawler['bin_path'], 'script')
        crawler['clean_data'] = posixpath.join(crawler['script_dir'], 'clean_data.sh')
        crawler['build_model'] = posixpath.join(crawler['script_dir'], 'build_model.sh')
        crawler['insert_seeds'] = posixpath.join(crawler['script_dir'], 'insert_seeds.sh')
        crawler['stop_crawler'] = posixpath.join(crawler['script_dir'], 'stop_crawler.sh')
        crawler['run_link_storage'] = posixpath.join(crawler['script_dir'], 'run_link_storage.sh')
        crawler['run_target_storage'] = posixpath.join(crawler['script_dir'], 'run_target_storage.sh')
        crawler['run_client'] = posixpath.join(crawler['script_dir'], 'run_client.sh')

        self.set_output('crawler', crawler)

class CreateCrawler(NotCacheable, Module):
    """ CreateCrawler creates the crawler dirs under ~/.crawler/CRAWLERNAME/

        Warning: This will delete the existing crawler
    """
    _settings = ModuleSettings(namespace='control')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)')]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)')]

    def compute(self):
        crawler = self.get_input('crawler')
        queue = crawler['queue']

        STEPS = 6

        cd = 'cd %s' % crawler['bin_path']

        # Remove directory if it exists
        queue.check_call('rm -rf %s' % crawler['crawler_dir'])
        self.logging.update_progress(self, 1.0/STEPS)
        # Create base directory
        queue.check_call('mkdir -p %s' % crawler['crawler_dir'])
        self.logging.update_progress(self, 2.0/STEPS)
        # Create conf directory (Not used right now?)
        queue.check_call('mkdir -p %s' % posixpath.join(crawler['crawler_dir'], 'conf'))
        self.logging.update_progress(self, 3.0/STEPS)
        # Create model directory
        queue.check_call('mkdir -p %s' % crawler['model_dir'])
        self.logging.update_progress(self, 4.0/STEPS)
        # Clean data directory
        queue.check_call('%s %s' % (crawler['clean_data'], crawler['data_dir']))
        self.logging.update_progress(self, 5.0/STEPS)

        self.logging.update_progress(self, 1.0)
        # done, ready to start
        self.set_output('crawler', crawler)

class AddSeed(NotCacheable, Module):
    """ AddSeed adds seeds from a file

    """
    _settings = ModuleSettings(namespace='modify')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                    ('seed_file', '(basic:File)')]
    _output_ports = []

    def compute(self):
        crawler = self.get_input('crawler')
        queue = crawler['queue']

        STEPS = 2

        cd = 'cd %s' % crawler['bin_path']

        queue.check_call('mkdir -p %s' % crawler['seeds_dir'])

        # Insert seeds
        scp_client = scp.SCPClient(queue.get_client().get_transport())
        scp_client.put(self.get_input('seed_file').name,
                       crawler['seeds_file'])
        self.logging.update_progress(self, 1.0/STEPS)
        queue.check_call('%s; %s %s %s %s' % (cd,
                                              crawler['insert_seeds'],
                                              crawler['conf_dir'],
                                              crawler['seeds_file'],
                                              crawler['data_dir']))
        self.logging.update_progress(self, 1.0)
        self.set_output('crawler', crawler)

class CreateModelFromUrls(BaseSubmitJob):
    """ rebuilds the model from a directory of examples

        Directory should contain directories "positive" and "negative"
        with files containing an url on each line

    """
    _settings = ModuleSettings(namespace='modify')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                    ('model_examples', '(basic:Directory)')]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)')]

    def job_read_inputs(self):
        """Reads the input ports.
        """
        crawler = self.get_input('crawler')
        return {'destination': crawler['queue'].destination_string,
                'queue': str(crawler['queue'].queue),
                'job_id': self.make_id(),
                'crawler': crawler,
                'model_examples': self.get_input('model_examples').name}

    def job_start(self, params):
        """Sends the directory and submits the job.
        """
        queue = QueueCache.get(params['destination'], params['queue'])

        # First, check if job already exists
        try:
            with ServerLogger.hide_output():
                queue.status(params['job_id'])
        except (tej.JobNotFound, tej.QueueDoesntExist):
            pass
        else:
            return params

        # Alright, submit a new job

        crawler = params['crawler']
        model_examples = params['model_examples']

        # Create script
        script = u''
        script += 'rm -rf %s\n' % crawler['examples_dir']
        script += 'rm -rf %s/*\n' % crawler['model_dir']
        # Fetch html
        scrap_dir = posixpath.join(crawler['bin_path'], '..', 'analytics',
                                   'escort', 'download', 'scrap.py')
        pos_dir = posixpath.join(crawler['examples_dir'], 'positive')
        script += 'mkdir -p %s\n' % pos_dir
        script += 'python %s %s html %s\n' % (scrap_dir, 'positive', pos_dir)
        neg_dir = posixpath.join(crawler['examples_dir'], 'negative')
        script += 'mkdir -p %s\n' % neg_dir
        script += 'python %s %s html %s\n' % (scrap_dir, 'negative', neg_dir)
        # Build model
        script += 'cd %s\n' % crawler['bin_path']
        script += '%s %s %s' % (crawler['build_model'],
                                crawler['examples_dir'],
                                crawler['model_dir'])

        kwargs = {'mode': 'w', 'newline': '\n'}
        with io.open(os.path.join(model_examples, 'vistrails_source.sh'),
                     **kwargs) as fp:
            fp.write(script)
        with io.open(os.path.join(model_examples, 'start.sh'), 'w',
                     newline='\n') as fp:
            fp.write(u'/bin/sh '
                     u'vistrails_source.sh '
                     u'>_stdout.txt '
                     u'2>_stderr.txt\n')

        queue.submit(params['job_id'], model_examples)

        # clean dir so that directory hash is unchanged
        os.remove(os.path.join(model_examples, 'vistrails_source.sh'))
        os.remove(os.path.join(model_examples, 'start.sh'))

        return params

    def job_set_results(self, params):
        """Sets the output ports once the job is finished.
        """
        queue = QueueCache.get(params['destination'], params['queue'])
        if params['exitcode']:

            temp_dir = self.interpreter.filePool.create_directory(
                    prefix='vt_tmp_shelljobout_').name
            queue.download(params['job_id'], ['_stderr.txt'],
                           directory=temp_dir)
            stderr = os.path.join(temp_dir, '_stderr.txt')
            raise ModuleError(self, 'Failed with exit code "%s"\n%s' % (params['exitcode'], stderr))

        self.set_output('crawler', params['crawler'])

        self.set_output('exitcode', params['exitcode'])
        self.set_output('job', RemoteJob(queue, params['job_id']))


class UpdateModelFromUrls(BaseSubmitJob):
    """ rebuilds the model from a directory of examples

        Directory should contain directories "positive" and "negative"
        with files containing an url on each line

    """
    _settings = ModuleSettings(namespace='modify')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                    ('model_examples', '(basic:Directory)')]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)')]

    def job_read_inputs(self):
        """Reads the input ports.
        """
        crawler = self.get_input('crawler')
        return {'destination': crawler['queue'].destination_string,
                'queue': str(crawler['queue'].queue),
                'job_id': self.make_id(),
                'crawler': crawler,
                'model_examples': self.get_input('model_examples').name}

    def job_start(self, params):
        """Sends the directory and submits the job.
        """
        queue = QueueCache.get(params['destination'], params['queue'])

        # First, check if job already exists
        try:
            with ServerLogger.hide_output():
                queue.status(params['job_id'])
        except (tej.JobNotFound, tej.QueueDoesntExist):
            pass
        else:
            return params

        # Alright, submit a new job

        crawler = params['crawler']
        model_examples = params['model_examples']

        # Create script
        script = u''
        #script += 'rm -rf %s\n' % crawler['examples_dir']
        script += 'rm -rf %s/*\n' % crawler['model_dir']
        # Fetch html
        scrap_dir = posixpath.join(crawler['bin_path'], '..', 'analytics',
                                   'escort', 'download', 'scrap.py')
        pos_dir = posixpath.join(crawler['examples_dir'], 'positive')
        script += 'mkdir -p %s\n' % pos_dir
        script += 'python %s %s html %s\n' % (scrap_dir, 'positive', pos_dir)
        neg_dir = posixpath.join(crawler['examples_dir'], 'negative')
        script += 'mkdir -p %s\n' % neg_dir
        script += 'python %s %s html %s\n' % (scrap_dir, 'negative', neg_dir)
        # Build model
        script += 'cd %s\n' % crawler['bin_path']
        script += '%s %s %s' % (crawler['build_model'],
                                crawler['examples_dir'],
                                crawler['model_dir'])

        kwargs = {'mode': 'w', 'newline': '\n'}
        with io.open(os.path.join(model_examples, 'vistrails_source.sh'),
                     **kwargs) as fp:
            fp.write(script)
        with io.open(os.path.join(model_examples, 'start.sh'), 'w',
                     newline='\n') as fp:
            fp.write(u'/bin/sh '
                     u'vistrails_source.sh '
                     u'>_stdout.txt '
                     u'2>_stderr.txt\n')

        queue.submit(params['job_id'], model_examples)

        # clean dir so that directory hash is unchanged
        os.remove(os.path.join(model_examples, 'vistrails_source.sh'))
        os.remove(os.path.join(model_examples, 'start.sh'))

        return params

    def job_set_results(self, params):
        """Sets the output ports once the job is finished.
        """
        queue = QueueCache.get(params['destination'], params['queue'])
        if params['exitcode']:

            temp_dir = self.interpreter.filePool.create_directory(
                    prefix='vt_tmp_shelljobout_').name
            queue.download(params['job_id'], ['_stderr.txt'],
                           directory=temp_dir)
            stderr = os.path.join(temp_dir, '_stderr.txt')
            raise ModuleError(self, 'Failed with exit code "%s"\n%s' % (params['exitcode'], stderr))

        self.set_output('crawler', params['crawler'])

        self.set_output('exitcode', params['exitcode'])
        self.set_output('job', RemoteJob(queue, params['job_id']))


class CreateModelFromExamples(BaseSubmitJob):
    """ rebuilds the model from a directory of examples

        Directory should contain directories "positive" and "negative"
        with files containing html pages

    """
    _settings = ModuleSettings(namespace='modify')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                    ('model_examples', '(basic:Directory)')]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)')]

    def job_read_inputs(self):
        """Reads the input ports.
        """
        crawler = self.get_input('crawler')
        return {'destination': crawler['queue'].destination_string,
                'queue': str(crawler['queue'].queue),
                'job_id': self.make_id(),
                'crawler': crawler,
                'model_examples': self.get_input('model_examples').name}

    def job_start(self, params):
        """Sends the directory and submits the job.
        """
        queue = QueueCache.get(params['destination'], params['queue'])

        # First, check if job already exists
        try:
            with ServerLogger.hide_output():
                queue.status(params['job_id'])
        except (tej.JobNotFound, tej.QueueDoesntExist):
            pass
        else:
            return params

        # Alright, submit a new job

        crawler = params['crawler']
        model_examples = params['model_examples']
        pos_dir = posixpath.join(crawler['examples_dir'], 'positive')
        neg_dir = posixpath.join(crawler['examples_dir'], 'negative')

        # Create script
        script = u''
        script += 'rm -rf %s\n' % crawler['examples_dir']
        script += 'cp -r positive %s\n' % pos_dir
        script += 'cp -r negative %s\n' % neg_dir
        script += 'rm -rf %s/*\n' % crawler['model_dir']

        # Build model
        script += 'cd %s\n' % crawler['bin_path']
        script += '%s %s %s' % (crawler['build_model'],
                                crawler['examples_dir'],
                                crawler['model_dir'])

        kwargs = {'mode': 'w', 'newline': '\n'}
        with io.open(os.path.join(model_examples, 'vistrails_source.sh'),
                     **kwargs) as fp:
            fp.write(script)
        with io.open(os.path.join(model_examples, 'start.sh'), 'w',
                     newline='\n') as fp:
            fp.write(u'/bin/sh '
                     u'vistrails_source.sh '
                     u'>_stdout.txt '
                     u'2>_stderr.txt\n')

        queue.submit(params['job_id'], model_examples)

        # clean dir so that directory hash is unchanged
        os.remove(os.path.join(model_examples, 'vistrails_source.sh'))
        os.remove(os.path.join(model_examples, 'start.sh'))

        return params

    def job_set_results(self, params):
        """Sets the output ports once the job is finished.
        """
        queue = QueueCache.get(params['destination'], params['queue'])
        if params['exitcode']:

            temp_dir = self.interpreter.filePool.create_directory(
                    prefix='vt_tmp_shelljobout_').name
            queue.download(params['job_id'], ['_stderr.txt'],
                           directory=temp_dir)
            stderr = os.path.join(temp_dir, '_stderr.txt')
            raise ModuleError(self, 'Failed with exit code "%s"\n%s' % (params['exitcode'], stderr))

        self.set_output('crawler', params['crawler'])

        self.set_output('exitcode', params['exitcode'])
        self.set_output('job', RemoteJob(queue, params['job_id']))

class StartCrawler(NotCacheable, Module):
    """ StartCrawler starts the crawler at ~/.crawler/CRAWLERNAME/

    """
    _settings = ModuleSettings(namespace='control')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                    ('num_crawlers', '(basic:Integer)',
                     {'optional': True, 'defaults': "['4']"})]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)')]

    def compute(self):
        crawler = self.get_input('crawler')
        queue = crawler['queue']

        cd = 'cd %s' % crawler['bin_path']

        crawlers = self.get_input('num_crawlers')
        STEPS = 3 + crawlers

        # Stop crawler first
        # We remove the process itself by looking for 'kill'
        print queue._call("kill $(ps aux | grep %s | grep -v 'grep' "
                          "| grep -v 'kill' | awk '{print $2}')" %
                          crawler['long_name'], True)
        # make sure it stops
        time.sleep(1)
        _, output = queue._call('ps aux | grep %s | grep -v "grep" | grep -v "sh -c"' %
                                crawler['long_name'], True)
        if output.strip():
            raise ModuleError(self, 'Some instances are still running, wait a'
                                    'few seconds and try again.\n%s' % output)
        self.logging.update_progress(self, 1.0/STEPS)

        # Run link storage
        queue.check_call('%s; %s %s %s %s %s' % (cd,
                                           crawler['run_link_storage'],
                                           crawler['conf_dir'],
                                           crawler['seeds_file'],
                                           crawler['data_dir'],
                                           crawler['long_name']))
        self.logging.update_progress(self, 2.0/STEPS)

        # Run target storage
        queue.check_call('%s; %s %s %s %s %s' % (cd,
                                           crawler['run_target_storage'],
                                           crawler['conf_dir'],
                                           crawler['model_dir'],
                                           crawler['data_dir'],
                                           crawler['long_name']))
        self.logging.update_progress(self, 3.0/STEPS)

        # Run clients
        for i in xrange(crawlers):
            queue.check_call('%s; %s %s %s' % (cd,
                                               crawler['run_client'],
                                               crawler['conf_dir'],
                                               crawler['long_name']))
            self.logging.update_progress(self, (4.0+i)/STEPS)


        self.logging.update_progress(self, 1.0)
        self.set_output('crawler', crawler)

class StopCrawler(NotCacheable, Module):
    """ StopCrawler stops the crawler at ~/.crawler/CRAWLERNAME/

    """
    _settings = ModuleSettings(namespace='control')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)')]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)')]

    def compute(self):
        crawler = self.get_input('crawler')
        queue = crawler['queue']

        # Stop crawler
        # We remove the process itself with 'sh -c'
        print queue._call("kill $(ps aux | grep %s | grep -v 'grep' "
                          "| grep -v 'kill' | awk '{print $2}')" %
                          crawler['long_name'], True)
        # make sure it stops
        time.sleep(1)
        _, output = queue._call('ps aux | grep %s | grep -v "grep" | grep -v "sh -c"' %
                                crawler['long_name'], True)
        if output.strip():
            raise ModuleError(self, 'Some instances are still running, wait a'
                                    'while and try again.\n%s' % output)

        self.set_output('crawler', crawler)

class CrawlerStatus(NotCacheable, Module):
    """ CheckCrawler checks the crawler at ~/.crawler/CRAWLERNAME/ using ps

        Just a ps printout for now
    """
    _settings = ModuleSettings(namespace='control')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)')]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                     ('status', '(basic:String)')]

    def compute(self):
        crawler = self.get_input('crawler')
        self.set_output('crawler', crawler)
        queue = crawler['queue']
        _, output = queue._call("ps aux | awk 'NR == 1 || (/%s/ && !/ps aux/) {print}'" %
                                crawler['long_name'], True)
        self.logging.annotate(self, {'status': output})
        self.set_output('status', output)

class CrawledPages(NotCacheable, Module):
    """ CrawledPages reads the status file at
        ~/.crawler/CRAWLERNAME/data/data_monitor/crawledpages.csv

    """
    _settings = ModuleSettings(namespace='monitor')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                    ('lines', '(basic:Integer)',
                     {'optional': True, 'defaults': "['20']"})]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                     ('result', '(basic:String)')]

    def compute(self):
        crawler = self.get_input('crawler')
        self.set_output('crawler', crawler)
        queue = crawler['queue']
        lines = self.get_input('lines')
        fname = posixpath.join(crawler['data_dir'], 'data_monitor',
                               'crawledpages.csv')
        _, output = queue._call("tail -n %s %s" % (lines, fname), True)
        self.logging.annotate(self, {'result': output})
        self.set_output('result', output)

class FrontierPages(NotCacheable, Module):
    """ FrontierPages reads the status file at
        ~/.crawler/CRAWLERNAME/data/data_monitor/frontierpages.csv

    """
    _settings = ModuleSettings(namespace='monitor')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                    ('lines', '(basic:Integer)',
                     {'optional': True, 'defaults': "['20']"})]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                     ('result', '(basic:String)')]

    def compute(self):
        crawler = self.get_input('crawler')
        self.set_output('crawler', crawler)
        queue = crawler['queue']
        lines = self.get_input('lines')
        fname = posixpath.join(crawler['data_dir'], 'data_monitor',
                               'frontierpages.csv')
        _, output = queue._call("tail -n %s %s" % (lines, fname), True)
        self.logging.annotate(self, {'result': output})
        self.set_output('result', output)

class HarvestInfo(NotCacheable, Module):
    """ HarvestInfo reads the status file at
        ~/.crawler/CRAWLERNAME/data/data_monitor/harvestinfo.csv

    """
    _settings = ModuleSettings(namespace='monitor')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                    ('lines', '(basic:Integer)',
                     {'optional': True, 'defaults': "['20']"})]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                     ('result', '(basic:String)')]

    def compute(self):
        crawler = self.get_input('crawler')
        self.set_output('crawler', crawler)
        queue = crawler['queue']
        lines = self.get_input('lines')
        fname = posixpath.join(crawler['data_dir'], 'data_monitor',
                               'harvestinfo.csv')
        _, output = queue._call("tail -n %s %s" % (lines, fname), True)
        self.logging.annotate(self, {'result': output})
        self.set_output('result', output)

class NonRelevantPages(NotCacheable, Module):
    """ NonRelevantPages reads the status file at
        ~/.crawler/CRAWLERNAME/data/data_monitor/nonrelevantpages.csv

    """
    _settings = ModuleSettings(namespace='monitor')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                    ('lines', '(basic:Integer)',
                     {'optional': True, 'defaults': "['20']"})]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                     ('result', '(basic:String)')]

    def compute(self):
        crawler = self.get_input('crawler')
        self.set_output('crawler', crawler)
        queue = crawler['queue']
        lines = self.get_input('lines')
        fname = posixpath.join(crawler['data_dir'], 'data_monitor',
                            'nonrelevantpages.csv')
        _, output = queue._call("tail -n %s %s" % (lines, fname), True)
        self.logging.annotate(self, {'result': output})
        self.set_output('result', output)

class OutLinks(NotCacheable, Module):
    """ OutLinks reads the status file at
        ~/.crawler/CRAWLERNAME/data/data_monitor/outlinks.csv

    """
    _settings = ModuleSettings(namespace='monitor')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                    ('lines', '(basic:Integer)',
                     {'optional': True, 'defaults': "['20']"})]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                     ('result', '(basic:String)')]

    def compute(self):
        crawler = self.get_input('crawler')
        self.set_output('crawler', crawler)
        queue = crawler['queue']
        lines = self.get_input('lines')
        fname = posixpath.join(crawler['data_dir'], 'data_monitor',
                               'outlinks.csv')
        _, output = queue._call("tail -n %s %s" % (lines, fname), True)
        self.logging.annotate(self, {'result': output})
        self.set_output('result', output)

class RelevantPages(NotCacheable, Module):
    """ RelevantPages reads the status file at
        ~/.crawler/CRAWLERNAME/data/data_monitor/relevantpages.csv

    """
    _settings = ModuleSettings(namespace='monitor')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                    ('lines', '(basic:Integer)',
                     {'optional': True, 'defaults': "['20']"})]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                     ('result', '(basic:String)')]

    def compute(self):
        crawler = self.get_input('crawler')
        self.set_output('crawler', crawler)
        queue = crawler['queue']
        lines = self.get_input('lines')
        fname = posixpath.join(crawler['data_dir'], 'data_monitor',
                               'relevantpages.csv')
        _, output = queue._call("tail -n %s %s" % (lines, fname), True)
        self.logging.annotate(self, {'result': output})
        self.set_output('result', output)

class CrawlerLog(NotCacheable, Module):
    """ CrawlerLog reads the status file at
        log/crawler.log

    """
    _settings = ModuleSettings(namespace='log')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                    ('lines', '(basic:Integer)',
                     {'optional': True, 'defaults': "['100']"})]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                     ('result', '(basic:String)')]

    def compute(self):
        crawler = self.get_input('crawler')
        self.set_output('crawler', crawler)
        queue = crawler['queue']
        lines = self.get_input('lines')
        fname = posixpath.join(crawler['bin_path'], 'log', 'crawler.log')
        _, output = queue._call("tail -n %s %s" % (lines, fname), True)
        self.logging.annotate(self, {'result': output})
        self.set_output('result', output)

class LinkStorageLog(NotCacheable, Module):
    """ LinkStorageLog reads the status file at
        log/link_storage.log

    """
    _settings = ModuleSettings(namespace='log')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                    ('lines', '(basic:Integer)',
                     {'optional': True, 'defaults': "['100']"})]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                     ('result', '(basic:String)')]

    def compute(self):
        crawler = self.get_input('crawler')
        self.set_output('crawler', crawler)
        queue = crawler['queue']
        lines = self.get_input('lines')
        fname = posixpath.join(crawler['bin_path'], 'log', 'link_storage.log')
        _, output = queue._call("tail -n %s %s" % (lines, fname), True)
        self.logging.annotate(self, {'result': output})
        self.set_output('result', output)

class TargetStorageLog(NotCacheable, Module):
    """ TargetStorageLog reads the status file at
        log/target_storage.log

    """
    _settings = ModuleSettings(namespace='log')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                    ('lines', '(basic:Integer)',
                     {'optional': True, 'defaults': "['100']"})]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                     ('result', '(basic:String)')]

    def compute(self):
        crawler = self.get_input('crawler')
        self.set_output('crawler', crawler)
        queue = crawler['queue']
        lines = self.get_input('lines')
        fname = posixpath.join(crawler['bin_path'], 'log', 'target_storage.log')
        _, output = queue._call("tail -n %s %s" % (lines, fname), True)
        self.logging.annotate(self, {'result': output})
        self.set_output('result', output)

class RunLDA(NotCacheable, Module):
    """ RunLDA computes LDA and returns summary
    """
    _settings = ModuleSettings(namespace='analysis')
    _input_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)')]
    _output_ports = [('crawler', '(edu.nyu.vistrails.memexcrawler:Crawler)'),
                     ('summary', '(basic:String)')]

    def compute(self):
        crawler = self.get_input('crawler')
        self.set_output('crawler', crawler)
        queue = crawler['queue']

        lda_dir = posixpath.join(crawler['bin_path'], '..', 'analytics', 'lda_pipeline')

        cd = "cd %s" % lda_dir

        # remove old lda_input.csv*
        queue.check_output("%s; rm -rf %s*" % (cd,
                           posixpath.join(crawler['data_dir'], 'lda_input.csv')))

        # remove old result
        queue.check_output("%s; rm -rf %s" % (cd,
                            posixpath.join('lda-result')))

        STEPS = 4

        queue.check_output("%s; sh compile_Extract.sh" % cd)
        self.logging.update_progress(self, 1.0/STEPS)


        output = queue.check_output("%s; java -cp .:lib/boilerpipe-1.2.0.jar:lib/nekohtml-1.9.13.jar:lib/xerces-2.9.1.jar Extract %s %s | python concat_nltk.py %s" %
                                (cd,
                                 posixpath.join(crawler['data_dir'], 'data_target'),
                                 posixpath.join(crawler['data_dir'], 'data_monitor', 'relevantpages.csv'),
                                 posixpath.join(crawler['data_dir'], 'lda_input.csv')))
        self.logging.update_progress(self, 2.0/STEPS)

        output = queue.check_output("%s; java -jar lib/tmt-0.4.0.jar ht.scala %s" %
                                       (cd, posixpath.join(crawler['data_dir'], 'lda_input.csv')))
        self.logging.update_progress(self, 3.0/STEPS)

        output = queue.check_output("%s; cat %s" %
                                       (cd, posixpath.join('lda-result', '00500', 'summary.txt')))
        self.logging.update_progress(self, 1.0)

        self.logging.annotate(self, {'summary': output})
        self.set_output('summary', output)

_modules = [Crawler, CreateCrawler, StartCrawler, StopCrawler, CrawlerStatus,
            CrawledPages, FrontierPages, HarvestInfo, NonRelevantPages,
            OutLinks, RelevantPages, CrawlerLog, LinkStorageLog,
            TargetStorageLog, RunLDA, AddSeed, CreateModelFromUrls,
            UpdateModelFromUrls, CreateModelFromExamples]
