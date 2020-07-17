"""
@package mits.report
This module creates an HTML report from validated outputs.
"""
# TODO Make error highlighting in cooperation with validator
import os
from config import inv_testing_suites


class ResultsDirector(object):
    """ Decides which class to use to generate the report based on the suite.
    """
    @staticmethod
    def generate_results(results, outputs, outputs_denied, suite, path):
        """ Executes the generator function of the correct sublass based on the used suite.
        """
        if suite == 'do_tests':
            generator = SerialGenerator(results, outputs, outputs_denied, suite, path)
        elif suite == 'do_concurrent_tests':
            generator = ConcurrentGenerator(results, outputs, outputs_denied, suite, path)
        else:
            return
        generator.generate_results()


class Generator:
    """ Common generator class for both suites. Creates a new HTML file and prepares the beginning of it.
    Also provides methods for creating a new sub HTML file (used for detailed info on the output) and closing the HTML
    file.
    """
    def __init__(self, results, outputs, outputs_denied, suite, path):
        self.results = results
        self.outputs = outputs
        self.outputs_denied = outputs_denied
        self.suite = suite
        self.path = path
        self.file = None

    def create_file(self):
        if not os.path.exists(self.path + '/result_details'):
            os.mkdir(self.path + '/result_details')
        self.file = open(self.path + '/results_' + self.suite + '.html', 'w')

    def begin_html(self):
        """ Writes a beginning to the HTML file.
        """
        self.file.write("""\
    <!DOCTYPE html>
    <html>
    <head>
    <title>Medusa testing environment report</title>
    <style>
    .ok::after {content: " ✓"}
    .error::after {
        content: "✗";
        background-color: #e60a0a;
        padding: 1px 5px;
        margin: 10px 10px;
        color: white;
        font-weight: bold;
    }
    </style>
    <meta charset="utf-8">
    </head>
    <body>
    <h1>""" + inv_testing_suites[self.suite] + """ results</h1>
    <ul>
    """)

    @staticmethod
    def begin_sub_html(file):
        """ Writes a beginning to a specified HTML sub file.
        """
        file.write("""\
<!DOCTYPE html>
<html>
<head>
<title>Medusa testing environment report</title>
<meta charset="utf-8">
</head>
<body>
""")

    def end_html(self):
        self.file.write("</ul></body></html>")


class SerialGenerator(Generator):
    """ Reports generator used for creating report out of serial suite tests.
    """
    # def __init__(self, results, outputs, suite, path):
    #     super(SerialGenerator, self).__init__(results, outputs, suite, path)

    def generate_results(self):
        """
        Main report generation function for the serial suite. Creates a new HTML file, adds a row for each test
        and closes the file.
        """
        # Create a subfolder for detailed logs
        self.create_file()
        self.begin_html()
        for test in self.results:
            self.add_row(test)
        self.end_html()
        self.file.close()

    def add_row(self, test):
        """
        Creates a bullet point in the HTML for the test. It contains the dmesg, constable and command output along
        with a checkmark a cross to note if the test was successful.
        @param test: Name of the test, for which the row is created.
        """
        self.file.write("<li>" + test['test'] + "</li><ul>")
        # Create output file (not needed if output is none)
        if test['output_valid']:
            self.file.write('<li class="ok">output</li>')
        else:
            self.file.write('<li class="error"><a href="result_details/serial.' + test['test'] +
                            '.output.html">output</a></li>')
            # Create new html
            self.create_subpage(test, 'output')
        # Create dmesg file
        if test['dmesg_valid']:
            self.file.write('<li class="ok"><a href="result_details/serial.' + test['test'] +
                            '.system_log.html">dmesg</a></li>')
        else:
            self.file.write('<li class="error"><a href="result_details/serial.' + test['test'] +
                            '.system_log.html">dmesg</a></li>')
        self.create_subpage(test, 'system_log')
        # Create constable file
        if test['constable_valid']:
            self.file.write('<li class="ok"><a href="result_details/serial.' + test['test'] +
                            '.constable.html">constable</a></li>')
        else:
            self.file.write('<li class="error"><a href="result_details/serial.' + test['test'] +
                            '.constable.html">constable</a></li>')
        self.create_subpage(test, 'constable')

        if 'output_denied_valid' in test:
            # Output from the denied command
            if test['output_denied_valid']:
                self.file.write('<li class="ok"><a href="result_details/serial.' + test['test'] +
                                '.output_denied.html">denied output</a></li>')
            else:
                self.file.write('<li class="error"><a href="result_details/serial.' + test['test'] +
                                '.output_denied.html">denied output</a></li>')
                # Create new html
            self.create_subpage(test, 'output_denied')
            # Create dmesg file for the denied command
            if test['dmesg_denied_valid']:
                self.file.write('<li class="ok"><a href="result_details/serial.' + test['test'] +
                                '.system_log_denied.html">denied dmesg</a></li>')
            else:
                self.file.write('<li class="error"><a href="result_details/serial.' + test['test'] +
                                '.system_log_denied.html">denied dmesg</a></li>')
            self.create_subpage(test, 'system_log_denied')
            # Create constable file for the denied command
            if test['constable_denied_valid']:
                self.file.write('<li class="ok"><a href="result_details/serial.' + test['test'] +
                                '.constable_denied.html">denied constable</a></li>')
            else:
                self.file.write('<li class="error"><a href="result_details/serial.' + test['test'] +
                                '.constable_denied.html">denied constable</a></li>')
            self.create_subpage(test, 'constable_denied')
        self.file.write("</ul>")

    def create_subpage(self, test, log):
        """
        Creates new HTML file for a full output.
        @param test: Name of the test.
        @param log: Name of the output that is stored in this file.
        """
        file = open(self.path + '/result_details/serial.' + test['test'] + '.' + log + '.html', 'w')
        self.begin_sub_html(file)
        file.write('<p>' + test[log].replace('\n', '<br>\n'))
        file.write('</p></body></html>')
        file.close()


class ConcurrentGenerator(Generator):
    """ Report generator used for creating report out of concurrent suite tests.
    """
    # def __init__(self, results, outputs, suite, path):
    #     super(ConcurrentGenerator, self).__init__(results, outputs, suite, path)

    def generate_results(self):
        """ Main generator function used to generate report of a concurrent testing suite.
        """
        # Create a subfolder for detailed logs
        self.create_file()
        self.begin_html()
        for test in self.outputs:
            self.add_row(test)
        for test in self.outputs_denied:
            self.add_row(test, denied=True)
        self.file.write('<li><a href="result_details/concurrent.system_log.html">dmesg</a></li>')
        self.file.write('<li><a href="result_details/concurrent.constable.html">constable</a></li>')
        self.create_subpage(self.results, 'system_log')
        self.create_subpage(self.results, 'constable')
        self.end_html()
        self.file.close()

    def add_row(self, test, denied=False):
        """ Creates a new bullet point for a test containing the validated outputs.
        """
        self.file.write("<li>" + 'denied' if denied else '' + test['test'] + "</li><ul>")
        # Create output file (not needed if output is none)
        if test['output_valid']:
            self.file.write('<li class="ok">output</li>')
        else:
            self.file.write('<li class="error"><a href="result_details/concurrent.' + test['test'] +
                            '.output.html">output</a></li>')
            # Create new html
            self.create_subpage(test, 'output', True)
        # Create dmesg file
        if test['dmesg_valid']:
            self.file.write('<li class="ok">dmesg</li>')
        else:
            self.file.write('<li class="error">dmesg</li>')
        # Create constable file
        if test['constable_valid']:
            self.file.write('<li class="ok">constable</li>')
        else:
            self.file.write('<li class="error">constable</li>')
        self.file.write("</ul>")

    def create_subpage(self, test, log, output=False):
        """ Creates HTML sub file for constable or dmesg outputs, since they are separatly grouped together.
        It can also be used to create subpage for a command output - parameter output has to be set to True
        """
        if output:
            file = open(self.path + '/result_details/concurrent.' + test['test'] + '.' + log + '.html', 'w')
        else:
            file = open(self.path + '/result_details/concurrent.' + log + '.html', 'w')
        self.begin_sub_html(file)
        file.write('<p>' + test[log].replace('\n', '<br>\n'))
        file.write('</p></body></html>')
        file.close()
