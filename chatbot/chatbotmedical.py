#coding=utf-8

import argparse  # Command line parsing
import configparser  # Saving the models parameters
import datetime  # Chronometer
import os  # Files management
import pymysql

from chatbot.symptomModel import SymptomModel
from chatbot.mainModel import MainModel

class Chatbot:

    class RunMode:
        INTERACTIVE = 'interactive'
        DAEMON ='daemon'


    def __init__(self):
        # Model/dataset parameters
        self.args = None
        self.symptomModel = None  # Dataset

        self.callbackKey = {}
        self.CONFIG_FILENAME = 'params.ini'
        self.SENTENCES_PREFIX = ['AI: ', 'me: ']


    @staticmethod
    def parseArgs(args):


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

        print('Welcome to cloudocBot v0.1 !')

        # General initialisation
        self.args = self.parseArgs(args)

        if not self.args.rootDir:
            self.args.rootDir = os.getcwd()  # Use the current working directory

        self.loadModelParams()

        self.symptomModel = SymptomModel(self.args)
        self.mainModel = MainModel(self.args)

        if not self.args.rootDir:
            self.args.rootDir = os.getcwd()  # Use the current working directory

        if self.args.runmode == Chatbot.RunMode.INTERACTIVE:
            self.chatInteractive()


    def chatInteractive(self):
        print('')

        p_userid = self.getUserID()
        p_callbackKey = 'firstcall'

        sysSaid = self.daemonPredict(p_userid,p_callbackKey ,p_userid)
        p_callbackKey = sysSaid[1]
        print('{}{}'.format(self.SENTENCES_PREFIX[0],sysSaid[2]))

        while True:
            userSaid = input(self.SENTENCES_PREFIX[1])
            if userSaid == 'exit':    
                break

            sysSaid = self.daemonPredict(p_userid,p_callbackKey,userSaid)
            p_callbackKey = sysSaid[1]
            print('{}{}'.format(self.SENTENCES_PREFIX[0],sysSaid[2]))


    def daemonPredict(self, in_userID,in_callbackKey,in_sentence):

        p_callbackKey = in_callbackKey

        print('input callbackKey is ' + p_callbackKey )
        #===============================
        #get callback key from database
        #===============================
        if in_callbackKey != 'firstcall':
            p_callbackKey = self.mainModel.getCallbackKeyfromDB(in_userID,p_callbackKey,in_sentence) 

        print('callbackKey from db is ' + p_callbackKey )

        sysSaid=self.mainPredict(in_userID,p_callbackKey,in_sentence) 

        #===============================
        # set back callback key to database
        #===============================
        self.mainModel.setCallbackKeytoDB(in_userID,sysSaid[1],in_sentence)
        print('callbackKey after mainPredict is ' + sysSaid[1])  

        return sysSaid


    def mainPredict(self, in_userID,in_callbackKey,in_sentence):
        sysSaid = ['','','','']
        p_callbackKey = in_callbackKey
        p_sentence = in_sentence
        print('#=====================================')
        print('call mainPredict('+in_userID+','+in_callbackKey+','+in_sentence+')')
        print('#=====================================')

        conn= pymysql.connect(host=self.args.mysqlHost , port = self.args.mysqlPort , user = self.args.mysqlUser , passwd=self.args.mysqlPassword , db =self.args.mysqlDB , charset=self.args.mysqlCharset)
        cur = conn.cursor()


        v_sql="select count(1) from chatbot_symptom where symptom_name like \'%"+ in_sentence+"%\'"
        cur.execute(v_sql)
        p_hit_cnt = cur.fetchone()
        if (p_hit_cnt[0] > 0) :
            in_callbackKey = 'ask_symptom'
            sysSaid = self.symptomModel.prc_ask_symptom(in_userID,in_callbackKey,in_sentence)
            p_callbackKey = sysSaid[1]
            p_sentence =sysSaid[2]

        print('callback key after check symptom is ' + p_callbackKey)

        if in_sentence.lower() == 'cleanup':
            sysSaid = self.mainModel.cleanup(in_userID,p_callbackKey,p_sentence)

        elif p_callbackKey == 'firstcall':  
            sysSaid = self.mainModel.firstcall(in_userID,p_callbackKey,p_sentence)

        elif p_callbackKey == 'set_symptom':
            sysSaid = self.symptomModel.prc_set_symptom(in_userID,p_callbackKey,p_sentence)
     
        elif p_callbackKey == 'set_symptom':
            sysSaid = self.symptomModel.prc_set_symptom(in_userID,p_callbackKey,p_sentence) 
        else:  
             sysSaid = [in_userID,'auto','undefine function','text'] 

        return sysSaid

        
    def daemonClose(self):
        print('Exiting the daemon mode...')
        self.sess.close()
        print('Daemon closed.')

    def getUserID(self):
        sysSaid=['welcome! What is you name?']
        print('{}{}'.format(self.SENTENCES_PREFIX[0],sysSaid[0]))
        return input(self.SENTENCES_PREFIX[1])


    def loadModelParams(self):
        configName = os.path.join(self.args.rootDir, self.CONFIG_FILENAME)
        if os.path.exists(configName):
            # Loading
            config = configparser.ConfigParser()
            config.read(configName)

            # Restoring the the parameters
            self.args.mysqlHost = config['dbConnection'].get('mysqlHost')
            self.args.mysqlPort = config['dbConnection'].getint('mysqlPort')
            self.args.mysqlUser = config['dbConnection'].get('mysqlUser')
            self.args.mysqlPassword = config['dbConnection'].get('mysqlPassword')
            self.args.mysqlDB = config['dbConnection'].get('mysqlDB')
            self.args.mysqlCharset = config['dbConnection'].get('mysqlCharset')
            