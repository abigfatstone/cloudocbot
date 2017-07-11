import pymysql
import os

class MainModel:
    def __init__(self, args):
        self.args = args
        self.speechcraft = {}
        self.SPEECHCRAFT_FILENAME = 'speechcraft.ini'
        self.speechcraft = self.loadSpeechcraft()

    def cleanup(self,in_userID,in_callbackKey,in_sentence):

        conn= pymysql.connect(host=self.args.mysqlHost , port = self.args.mysqlPort , user = self.args.mysqlUser , passwd=self.args.mysqlPassword , db =self.args.mysqlDB , charset=self.args.mysqlCharset)
        cur = conn.cursor()

        cur.execute('delete from t_patient_symptom where patient_id = \'' + in_userID +'\'')
        cur.execute('delete from t_user_callback where user_id = \'' + in_userID  +'\'')
        conn.commit()
        sysSaid = [in_userID,in_callbackKey,'cleanup is done','text']     
        return sysSaid


    def getCallbackKeyfromDB(self,in_userID,in_callbackKey,in_sentence):
        conn= pymysql.connect(host=self.args.mysqlHost , port = self.args.mysqlPort , user = self.args.mysqlUser , passwd=self.args.mysqlPassword , db =self.args.mysqlDB , charset=self.args.mysqlCharset)
        cur = conn.cursor()
        p_callbackKey = ''
        #get last call back key from server 
        v_sql='select callback_key from t_user_callback where user_id=\''+in_userID+'\''

        row_count = cur.execute(v_sql)
        r0 = cur.fetchone()
        if row_count == 1:
            p_callbackKey = r0[0]
        else:
            p_callbackKey = 'firstcall'  

        return p_callbackKey   
       

    def setCallbackKeytoDB(self,in_userID,in_callbackKey,in_sentence):
        conn= pymysql.connect(host=self.args.mysqlHost , port = self.args.mysqlPort , user = self.args.mysqlUser , passwd=self.args.mysqlPassword , db =self.args.mysqlDB , charset=self.args.mysqlCharset)
        cur = conn.cursor()
        v_sql='insert into t_user_callback(user_id,callback_key) select \''+in_userID+'\',\''+in_callbackKey+'\' on duplicate key update callback_key=\''+in_callbackKey+'\''
        cur.execute(v_sql)  
        conn.commit()
        conn.close()   

    def firstcall(self,in_userID,in_callbackKey,in_sentence):
        conn= pymysql.connect(host=self.args.mysqlHost , port = self.args.mysqlPort , user = self.args.mysqlUser , passwd=self.args.mysqlPassword , db =self.args.mysqlDB , charset=self.args.mysqlCharset)
        cur = conn.cursor()
        sysSaid  = ['','','','']
        p_callbackKey = 'firstcall'
        p_text = ''

        #get last call back key from server 
        v_sql='select callback_key,\'\' from t_user_callback where user_id=\''+in_userID+'\''

        row_count = cur.execute(v_sql)
        r1 = cur.fetchone()
        if row_count == 1:
            p_callbackKey = r1[0]
            p_text = self.getSpeechCraft('welcome_back') 

            

        else:
            p_callbackKey = 'ask_symptom' 
            v_sql='insert into t_user_callback(user_id,callback_key) select \''+in_userID+'\',\''+p_callbackKey+'\''
            cur.execute(v_sql)
            conn.commit()
            p_text = self.getSpeechCraft('welcome_first')

        sysSaid = [in_userID,p_callbackKey,p_text,'text']   
        return sysSaid
   
    def getSpeechCraft(self,getWord):
        if getWord in self.speechcraft:
            return self.speechcraft[getWord]
        else:
            return 'undefined speechcraft' 

    def loadSpeechcraft(self):
        speechcraft_fileName = os.path.join(self.args.rootDir, self.SPEECHCRAFT_FILENAME)
        
        with open(speechcraft_fileName, 'r',encoding= 'utf-8') as f: 
            # Loading
            dic_speechcraft = {}
            for line in f:

                if len(line.split('=')) > 1 :
                    dic_speechcraft[line.split('=')[0].strip().lower()] = line.split('=')[1].strip()    
        return dic_speechcraft        