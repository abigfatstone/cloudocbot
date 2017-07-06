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
            self.chatInteractive()


    def chatInteractive(self):
        """ Try predicting the sentences that the user will enter in the console
        Args:
            sess: The current running session
        """
        print('')

        p_userid = self.getUserID()
        p_callbackKey  ='firstcall'

        sysSaid = self.daemonPredict(p_userid,p_callbackKey ,p_userid)
        p_callbackKey =sysSaid[1]
        print('{}{}'.format(self.SENTENCES_PREFIX[0],sysSaid[2]))

        while True:
            userSaid = input(self.SENTENCES_PREFIX[1])
            if userSaid == 'exit':    
                break

            sysSaid = self.daemonPredict(p_userid,p_callbackKey,userSaid)
            p_callbackKey = sysSaid[1]
            print('{}{}'.format(self.SENTENCES_PREFIX[0],sysSaid[2]))


    def daemonPredict(self, in_userID,in_callbackKey,in_sentence):

        conn= pymysql.connect(host=self.mysqlHost , port = self.mysqlPort , user = self.mysqlUser , passwd=self.mysqlPassword , db =self.mysqlDB , charset=self.mysqlCharset)
        cur = conn.cursor()

        p_callbackKey=in_callbackKey
        
        ''' get last call back key from server
        ''' 
        
        v_sql='select callback_key from t_user_callback where user_id=\''+in_userID+'\''
        cur.execute(v_sql)
        if (cur.rowcount>0):
            for r in cur.fetchall():
                p_callbackKey = r[0]
            else:
                p_callbackKey == 'firstcall'
        

        v_sql="call prc_main('"+in_userID+"','"+p_callbackKey+"','"+in_sentence+"')"
        print(v_sql)
        cur.execute(v_sql)
        sysSaid=['','','']
        if (cur.rowcount>0):
            for r in cur.fetchall():
                sysSaid[0]  = r[0]
                sysSaid[1]  = r[1]
                sysSaid[2] = sysSaid[2]+'\n'+r[2]


        #insert callback key back to server    
        v_sql='insert into t_user_callback(user_id,callback_key) select \''+in_userID+'\',\''+p_callbackKey+'\' ON DUPLICATE KEY UPDATE callback_key=\''+p_callbackKey+'\''
        print(v_sql)
        cur.execute(v_sql)  
        conn.commit()
        
        # close connection
        conn.close()    

        return sysSaid

    
    def daemonClose(self):
        """ A utility function to close the daemon when finish
        """
        print('Exiting the daemon mode...')
        self.sess.close()
        print('Daemon closed.')

    def getUserID(self):
        sysSaid=['welcome! What is you name?']
        print('{}{}'.format(self.SENTENCES_PREFIX[0],sysSaid[0]))
        return input(self.SENTENCES_PREFIX[1])


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
            