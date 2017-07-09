import pymysql

class MainModel:
    def __init__(self, args):
        self.args = args

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
        v_sql='insert into t_user_callback(user_id,callback_key) select \''+in_userID+'\',\''+in_callbackKey+'\' ON DUPLICATE KEY UPDATE callback_key=\''+in_callbackKey+'\''
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
            p_text = '欢迎回来，距离您上次使用小I已经过去' + r1[1] + '秒，请问您的主症状？'
        else:
            p_callbackKey = 'ask_symptom' 
            v_sql='insert into t_user_callback(user_id,callback_key) select \''+in_userID+'\',\''+p_callbackKey+'\''
            cur.execute(v_sql)
            conn.commit()
            p_text = '欢迎使用小i，这是您第一次使用小I，请问您的主症状？'

        sysSaid = [in_userID,p_callbackKey,p_text,'text']   
        return sysSaid