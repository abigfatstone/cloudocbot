#coding=utf-8

import argparse  # Command line parsing
import configparser  # Saving the models parameters
import datetime  # Chronometer
import os  # Files management
import pymysql

class Chatbot:

    class RunMode:
        """ Simple structure representing the different testing modes
        """
        INTERACTIVE = 'interactive'
        DAEMON ='daemon'


    def __init__(self):
        # Model/dataset parameters
        self.args = None
        
        self.CONFIG_FILENAME = 'params.ini'
        self.SENTENCES_PREFIX = ['AI: ', 'me: ']
        self.userID=''
        self.callbackKey = 'firstcall'

    @staticmethod
    def parseArgs(args):
        """
        Parse the arguments from the given command line
        Args:
            args (list<str>): List of arguments to parse. If None, the default sys.argv will be parsed
        """

        parser = argparse.ArgumentParser()

        # Global options
        globalArgs = parser.add_argument_group('Global options')
        globalArgs.add_argument('--runmode',
                                nargs='?',
                                choices=[Chatbot.RunMode.DAEMON,Chatbot.RunMode.INTERACTIVE],
                                const=Chatbot.RunMode.INTERACTIVE, 
                                default=None,
                                help='default is interactive model')
        globalArgs.add_argument('--rootDir', type=str, default=None, help='folder where to look for the models and data')

        return parser.parse_args(args)

    def main(self, args=None):#
        """
        Launch the training and/or the interactive mode
        """
        print('Welcome to cloudocBot v0.1 !')

        # General initialisation
        self.args = self.parseArgs(args)

        if not self.args.rootDir:
            self.args.rootDir = os.getcwd()  # Use the current working directory

        self.loadModelParams()

        if not self.args.rootDir:
            self.args.rootDir = os.getcwd()  # Use the current working directory

        if self.args.runmode == Chatbot.RunMode.INTERACTIVE:
            self.mainMedicalChat()


    def mainMedicalChat(self):
        """ Try predicting the sentences that the user will enter in the console
        Args:
            sess: The current running session
        """
        print('')

        if self.callbackKey == 'firstcall':
            self.getUserID()

        while True:
            answer = input(self.SENTENCES_PREFIX[1])
            if answer == 'exit':    
                break

            question = self.getNextQuestion(answer)
            print('{}{}'.format(self.SENTENCES_PREFIX[0],question))


    def getNextQuestion(self,answer):
        conn= pymysql.connect(host=self.mysqlHost , port = self.mysqlPort , user = self.mysqlUser , passwd=self.mysqlPassword , db =self.mysqlDB , charset=self.mysqlCharset)
        cur = conn.cursor()
        v_sql="call prc_main('"+self.userID+"','"+self.callbackKey+"','"+answer+"')"
        print(v_sql)
        cur.execute(v_sql)
        question=''
        for r in cur.fetchall():
            question = question+'\n'+r[2]
            self.callbackKey = r[1]
        conn.close()    
        return question

    def daemonPredict(self, sentence):
        """ Return the answer to a given sentence (same as singlePredict() but with additional cleaning)
        Args:
            sentence (str): the raw input sentence
        Return:
            str: the human readable sentence
        """
        return self.getNextQuestion( sentence )

    
    def daemonClose(self):
        """ A utility function to close the daemon when finish
        """
        print('Exiting the daemon mode...')
        self.sess.close()
        print('Daemon closed.')

    def getUserID(self):
        question='welcome! What is you name?'
        print('{}{}'.format(self.SENTENCES_PREFIX[0],question))
        self.userID = input(self.SENTENCES_PREFIX[1])
        question = self.getNextQuestion(self.userID)
        print('{}{}'.format(self.SENTENCES_PREFIX[0],question))



    def loadModelParams(self):
        """ Load the some values associated with the current model, like the current globStep value
        """

        configName = os.path.join(self.args.rootDir, self.CONFIG_FILENAME)

        if os.path.exists(configName):
            # Loading
            config = configparser.ConfigParser()
            config.read(configName)

            # Restoring the the parameters
            self.mysqlHost = config['dbConnection'].get('mysqlHost')
            self.mysqlPort = config['dbConnection'].getint('mysqlPort')
            self.mysqlUser = config['dbConnection'].get('mysqlUser')
            self.mysqlPassword = config['dbConnection'].get('mysqlPassword')
            self.mysqlDB = config['dbConnection'].get('mysqlDB')
            self.mysqlCharset = config['dbConnection'].get('mysqlCharset')
            