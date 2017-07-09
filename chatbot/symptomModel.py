import pymysql

class SymptomModel:
    def __init__(self, args):
        self.args = args


    def prc_main_symptom(self,in_userID,in_callbackKey,in_sentence):

        sysSaid  = ['','','','']
        p_callbackKey = ''
        print('===============================')
        print('         ask symptom main      ')
        print('===============================')
        conn= pymysql.connect(host=self.args.mysqlHost , port = self.args.mysqlPort , user = self.args.mysqlUser , passwd=self.args.mysqlPassword , db =self.args.mysqlDB , charset=self.args.mysqlCharset)
        cur = conn.cursor()

        v_sql = ' select count(1) from t_patient_symptom where patient_id = \''+in_userID+'\'  and ifnull(symptom_value,\'\') = \'\''
        print(v_sql)
        cur.execute(v_sql)
        row_count = cur.fetchone()
        if row_count[0] > 0 :
            sysSaid[1] = 'set_symptom'
        else:
            sysSaid[1] = 'auto'
        conn.close()
        return sysSaid

    def prc_set_symptom(self,in_userID,in_callbackKey,in_sentence):
        sysSaid  = ['','','','']
        print('===============================')
        print('         set symptom           ')
        print('===============================')
        conn= pymysql.connect(host=self.args.mysqlHost , port = self.args.mysqlPort , user = self.args.mysqlUser , passwd=self.args.mysqlPassword , db =self.args.mysqlDB , charset=self.args.mysqlCharset)
        cur = conn.cursor()

        
        if in_sentence != 'insert_symptom_done':

            v_sql='update t_patient_symptom set symptom_value = 0  where patient_id = \''+in_userID+'\'  and ifnull(symptom_value,\'\') = \'\''
            print(v_sql)
            cur.execute(v_sql)
            
            sympton_sql = ''
            symptom_list = in_sentence.split('@L1@')
            for symptom_one in symptom_list:
                if sympton_sql == '':
                    sympton_sql = sympton_sql + '\'' + symptom_one + '\'' 
                else:
                    sympton_sql = sympton_sql + ','+ '\'' + symptom_one + '\''  

            v_sql='update t_patient_symptom set symptom_value = 1  where patient_id = \''+in_userID+'\'  and symptom_name in ('+ sympton_sql + ')'
            print(v_sql)
            cur.execute(v_sql)
            conn.commit()

        return_list = ''
        v_sql = ' select symptom_name from t_patient_symptom where patient_id = \''+in_userID+'\'  and ifnull(symptom_value,\'\') = \'\''
        print(v_sql)
        row_count = cur.execute(v_sql)
        if row_count > 0: 
            list_symptom = cur.fetchall()
            return_list_symptom = ''

            for symptom_key in list_symptom:
                if return_list_symptom == '':
                    return_list_symptom  =  return_list_symptom + symptom_key[0]
                else:
                    return_list_symptom  =  return_list_symptom + '@L2@' + symptom_key[0]


            v_sql = ' select distinct disease_name from chatbot_symptom where symptom_name in (select symptom_name from t_patient_symptom where patient_id = \''+in_userID+'\' and  symptom_value = 1 )'
            print(v_sql)
            row_count = cur.execute(v_sql)
            list_disease = cur.fetchall()
            return_list_disease = ''

                # dic_disease = {}
                # dic_symptom = {}
                # for line in list_disease:
                #     if line[0] in dic_disease.keys():
                #         dic_disease[line[0]] = dic_disease[line[0]] + 1
                #     else:
                #         dic_disease[line[0]] = 1
                # for disease_key in dic_disease.items():

            for disease_key in list_disease:
                if return_list_disease == '':
                    return_list_disease  =  return_list_disease + disease_key[0]
                else:
                    return_list_disease  =  return_list_disease + ',' + disease_key[0]



            if return_list_disease != '':
                return_list_disease = '根据您所描述的症状提示您可能存在以下疾病：'+ '@L2@ ' + return_list_disease + '@L2@'

            return_list = return_list_disease + '需要进一步了解您是否还具有以下其他症状以便做出更好的诊断：@L1@' + return_list_symptom 
            return_action = 'checkbox'
            return_callbackkey = 'set_symptom'
        else:

            #
            #TODO ：retrun disease list
            #
            return_list =  'done!'  
            return_action = 'table'
            return_callbackkey = 'auto'

        # v_sql = ' select count(1) from t_patient_symptom where patient_id = \''+in_userID+'\'  and ifnull(symptom_value,\'\') = \'\''
        # print(v_sql)
        # cur.execute(v_sql)
        # row_count = cur.fetchone()
        # if row_count[0] > 0 :
        #     sysSaid[1] = 'set_symptom'
        #     sysSaid[2] = 'set_symptom done'
        # else:
        #     sysSaid[1] = 'auto'
        #     sysSaid[2] = 'set_symptom done'

        sysSaid = [in_userID,return_callbackkey,return_list,return_action]
        conn.close()

        return sysSaid

    def prc_ask_symptom(self,in_userID,in_callbackKey,in_sentence):
        sysSaid  = ['','','','']
        print('==========================================')
        print('         ask symptom start question       ')
        print('==========================================')
        conn= pymysql.connect(host=self.args.mysqlHost , port = self.args.mysqlPort , user = self.args.mysqlUser , passwd=self.args.mysqlPassword , db =self.args.mysqlDB , charset=self.args.mysqlCharset)
        cur = conn.cursor()

        v_sql = ' insert into t_patient_symptom(patient_id,symptom_name,symptom_value,symptom_type,f_symptom,modified_time) ' +\
                ' select \'' + in_userID + '\',symptom_name,\'1\',symptom_type,f_symptom,now() '+\
                '   from chatbot_symptom where symptom_name = \'' + in_sentence + '\' ON DUPLICATE KEY UPDATE symptom_value = 1 '
        print(v_sql)
        row_count = cur.execute(v_sql)

        return_list = ''
        v_sql = 'select disease_name ,symptom_name ,ifnull(rank,0) rank,symptom_type,f_symptom ' +\
                '           FROM ' +\
                '                chatbot_symptom ' +\
                '           WHERE '+\
                '                disease_name IN( ' +\
                '                    select ' +\
                '                        distinct disease_name ' +\
                '                    FROM ' +\
                '                        chatbot_symptom ' +\
                '                    WHERE ' +\
                '                        symptom_name like  \'%'+in_sentence+'%\' ' + \
                '                ) ' +\
                '            AND ifnull(f_symptom,\'\') = \'\' ' +\
                '            AND ifnull(symptom_type,\'\') not in(\'合并疾病\' , \'实验\') ' +\
                '            and symptom_name  <> \''+in_sentence+'\' ' + \
                '            ORDER BY disease_name , ' +\
                '                rank desc , ' +\
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
                    if (i / dic_disease[tmp_disease] < 0.2) or (i < 2):
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
            symptom_list = ''
            for symptom_key in dic_symptom.items():
                if symptom_list == '':
                    symptom_list =  symptom_list + symptom_key[0]
                else:
                    symptom_list =  symptom_list + '\',\'' + symptom_key[0]

            v_sql = ' insert into t_patient_symptom(patient_id,symptom_name,symptom_value,symptom_type,f_symptom,modified_time) ' +\
                    ' select distinct \'' + in_userID + '\',symptom_name,\'\' symptom_value,symptom_type,f_symptom,now() '+\
                    '   from chatbot_symptom '+\
                     ' where symptom_name in (\''+symptom_list+'\')  ' + \
                       ' and symptom_name not in (select symptom_name from t_patient_symptom where patient_id = \''+in_userID+'\' )'
            print(v_sql)
            row_count = cur.execute(v_sql)
            conn.commit()

            sysSaid = [in_userID,'set_symptom','insert_symptom_done','text']

        else:
            sysSaid = [in_userID,'ask_symptom','无法找到相关的疾病，请重新输入','text']

        conn.close()
        return sysSaid






        
