import pymysql

class SymptomModel:
    def __init__(self, args):
        self.args = args

    def print_data(self):
    	print(self.args.mysqlHost)

    def prc_get_main_symptom(self,in_userID,in_callbackKey,in_sentence):
        sysSaid  = ['','','','']
        print('===============================')
        print('         start ask symptom     ')
        print('===============================')
        conn= pymysql.connect(host=self.args.mysqlHost , port = self.args.mysqlPort , user = self.args.mysqlUser , passwd=self.args.mysqlPassword , db =self.args.mysqlDB , charset=self.args.mysqlCharset)
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

    def cleanup(self,in_userID,in_callbackKey,in_sentence):

        conn= pymysql.connect(host=self.args.mysqlHost , port = self.args.mysqlPort , user = self.args.mysqlUser , passwd=self.args.mysqlPassword , db =self.args.mysqlDB , charset=self.args.mysqlCharset)
        cur = conn.cursor()
        cur.execute('delete from t_patient_symptom')
        cur.execute('delete from t_user_callback')
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
        v_sql='insert into t_user_callback(user_id,callback_key) select \''+in_userID+'\',\''+p_callbackKey+'\' ON DUPLICATE KEY UPDATE callback_key=\''+p_callbackKey+'\''
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
            p_text = '欢迎使用小i，这是您第一次使用小，请问您的主症状？'

        sysSaid = [in_userID,p_callbackKey,p_text,'text']   
        return sysSaid
        
