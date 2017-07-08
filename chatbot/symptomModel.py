import pymysql

class SymptomModel:
    def __init__(self, args):
        self.args = args

    def prc_get_main_symptom(self,in_userID,in_callbackKey,in_sentence):
        sysSaid  = ['','','','']
        print('===============================')
        print('         start ask symptom     ')
        print('===============================')
        conn= pymysql.connect(host=self.args.mysqlHost , port = self.args.mysqlPort , user = self.args.mysqlUser , passwd=self.args.mysqlPassword , db =self.args.mysqlDB , charset=self.args.mysqlCharset)
        cur = conn.cursor()
        return_list = ''
        v_sql = 'SELECT disease_name ,symptom_name ,ifnull(rank,0) rank,note ' +\
                '           FROM ' +\
                '                chatbot_symptom ' +\
                '           WHERE '+\
                '                disease_name IN( ' +\
                '                    SELECT ' +\
                '                        distinct disease_name ' +\
                '                    FROM ' +\
                '                        chatbot_symptom ' +\
                '                    WHERE ' +\
                '                        symptom_name LIKE  \'%'+in_sentence+'%\' ' + \
                '                ) ' +\
                '            AND ifnull(f_symptom,\'\') = \'\' ' +\
                '            AND ifnull(note,\'\') NOT IN(\'合并疾病\' , \'实验\') ' +\
                '            and symptom_name  <> \''+in_sentence+'\' ' + \
                '            ORDER BY disease_name , ' +\
                '                rank DESC , ' +\
                '                symptom_name '
        print(v_sql)
        row_count = cur.execute(v_sql)
        r0 = cur.fetchall()
        if row_count > 0:
            dic_disease = {}
            dic_symptom = {}

            for line in r0:
                if line[0] in dic_disease.keys():
                    dic_disease[line[0]] = dic_disease[line[0]] + 1
                else:
                    dic_disease[line[0]] = 1
            i = 0
            tmp_disease = ''
            for line in r0:
                if tmp_disease == line[0]:
                    i =  i + 1
                    # output top 30% symptom for each disease
                    # merge same symptom
                    if (i / dic_disease[tmp_disease] < 0.4) or (i < 4):
                        if line[1] in dic_symptom.keys(): 
                            # plus rank only for output sort 
                            # TOTO: need be checked by doctor
                            dic_symptom[line[1]] = dic_symptom[line[1]] + line[2]
                        else:
                            dic_symptom[line[1]] = line[2]
                else:
                    i = 0 
                    tmp_disease = line[0]
            #dicd_symptom = sorted(dic_symptom.items(), key=lambda d:d[1], reverse = True)        
            i = 0
            return_list = '根据您所描述的症状提示您可能存在以下疾病：'+ '@L2@      '
            for disease_key in dic_disease.items():
                if i == 0:
                    return_list  =  return_list + disease_key[0]
                else:
                    return_list  =  return_list + '@L2@' + disease_key[0]
                i = i + 1        

            return_list = return_list + '@L2@为更好的服务您，我们需要进一步了解您是否还具有以下其他症状：@L1@'

            i = 0
            for symptom_key in dic_symptom.items():
                if i == 0:
                    return_list  =  return_list + symptom_key[0]
                else:
                    return_list  =  return_list + '@L2@' + symptom_key[0]
                i = i + 1    
            sysSaid = [in_userID,'ask_symptom',return_list,'checkbox']

        else:
            sysSaid = [in_userID,'ask_symptom','无法找到相关的疾病，请重新输入','text']

        return sysSaid

        
