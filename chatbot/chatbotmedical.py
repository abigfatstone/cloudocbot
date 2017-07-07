#coding=utf-8

import argparse  # Command line parsing
import configparser  # Saving the models parameters
import datetime  # Chronometer
import os  # Files management
import pymysql

class Chatbot:

    class RunMode:
        INTERACTIVE = 'interactive'
        DAEMON ='daemon'


    def __init__(self):
        # Model/dataset parameters
        self.args = None
        
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

        p_callbackKey = ''
        conn= pymysql.connect(host=self.mysqlHost , port = self.mysqlPort , user = self.mysqlUser , passwd=self.mysqlPassword , db =self.mysqlDB , charset=self.mysqlCharset)
        cur = conn.cursor()
        
        #get last call back key from server 
        v_sql='select callback_key from t_user_callback where user_id=\''+in_userID+'\''
        print(v_sql)
        cur.execute(v_sql)
        for r in cur.fetchall():
            p_callbackKey  = r[0]

        print('0.'+p_callbackKey)
        
        if p_callbackKey == '':
            p_callbackKey = 'firstcall'

        sysSaid=self.mainPredict(in_userID,p_callbackKey,in_sentence) 
        p_callbackKey=sysSaid[1]
        print('1.'+p_callbackKey)


        v_sql='insert into t_user_callback(user_id,callback_key) select \''+in_userID+'\',\''+p_callbackKey+'\' ON DUPLICATE KEY UPDATE callback_key=\''+p_callbackKey+'\''
        cur.execute(v_sql)  
        conn.commit()
        conn.close()    

        return sysSaid


    def mainPredict(self, in_userID,in_callbackKey,in_sentence):
        sysSaid = ['','','','']

        print('#=====================================')
        print('call mainPredict('+in_userID+','+in_callbackKey+','+in_sentence+')')
        print('#=====================================')

        conn= pymysql.connect(host=self.mysqlHost , port = self.mysqlPort , user = self.mysqlUser , passwd=self.mysqlPassword , db =self.mysqlDB , charset=self.mysqlCharset)
        cur = conn.cursor()

        
        v_sql="select count(1) from chatbot_symptom where symptom_name like \'%"+ in_sentence+"%\'"
        print(v_sql)
        cur.execute(v_sql)
        p_hit_cnt = 0
        for r in cur.fetchall():
            p_hit_cnt  = r[0]

        if (p_hit_cnt > 0) :
            in_callbackKey = 'ask_symptom'
        
        if in_callbackKey == 'firstcall':  
            sysSaid = [in_userID,'ask_symptom','欢迎使用小i，这是您第一次使用小，请问您的主症状？','text'] 

        elif in_callbackKey == 'ask_symptom':
            sysSaid = self.prc_get_main_symptom(in_userID,in_callbackKey,in_sentence);


        elif in_sentence == 'cleanup':
            cur.execute('DELETE FROM t_patient_symptom')  
            conn.commit()
            cur.execute('DELETE FROM t_user_callback')  
            conn.commit()
            sysSaid = [in_userID,in_callbackKey,'cleanup is done','text'] 
     
        elif in_callbackKey == 'auto' :  
             sysSaid = [in_userID,'auto','undefine function','text'] 

        return sysSaid

    def prc_get_main_symptom(self,in_userID,in_callbackKey,in_sentence):
        sysSaid  = ['','','','']
        print('===============================')
        print('         start ask symptom     ')
        print('===============================')
        conn= pymysql.connect(host=self.mysqlHost , port = self.mysqlPort , user = self.mysqlUser , passwd=self.mysqlPassword , db =self.mysqlDB , charset=self.mysqlCharset)
        cur = conn.cursor()

        return_list = ''
        v_sql = 'select distinct disease_name from chatbot_symptom where symptom_name like \'%'+in_sentence+'%\' and note is null'
        row_count = cur.execute(v_sql)
        if row_count >0 :

            return_list = '根据您所描述的症状提示您可能存在以下疾病：'
            r1 = cur.fetchone()
            return_list = return_list + '@L2@' + r1[0]
            for r0 in cur.fetchall():
                return_list  =  return_list + '@L2@' + r0[0] 

            return_list = return_list + '@L2@为更好的服务您，我们需要进一步了解您是否还具有以下其他症状：@L1@'

            v_sql = 'select distinct disease_name ,symptom_name ,rank rank1,note from chatbot_symptom '+  \
                    ' where disease_name in ('+ \
                            ' select disease_name from chatbot_symptom where symptom_name like \'%'+in_sentence+'%\' and note is null '+ \
                             ' group by disease_name,rank,symptom_name order by disease_name,rank desc,symptom_name'+ \
                    ') limit 3'
            print(v_sql)

            row_count = cur.execute(v_sql)
            r1 = cur.fetchone()
            return_list = return_list + r1[1]
            for r0 in cur.fetchall():
                return_list  =  return_list + '@L2@' + r0[1] 

            sysSaid = [in_userID,'ask_symptom',return_list,'checkbox']

        else:
            sysSaid = [in_userID,'ask_symptom','无法找打相关的疾病，请重新输入','text']

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
            self.mysqlHost = config['dbConnection'].get('mysqlHost')
            self.mysqlPort = config['dbConnection'].getint('mysqlPort')
            self.mysqlUser = config['dbConnection'].get('mysqlUser')
            self.mysqlPassword = config['dbConnection'].get('mysqlPassword')
            self.mysqlDB = config['dbConnection'].get('mysqlDB')
            self.mysqlCharset = config['dbConnection'].get('mysqlCharset')
            