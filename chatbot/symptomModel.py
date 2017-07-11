import pymysql
from chatbot.mainModel import MainModel

class SymptomModel:
    def __init__(self, args):
        self.args = args
        self.mainModel = MainModel(self.args)
        
    def prc_main_symptom(self,in_userID,in_callbackKey,in_sentence):
        sysSaid  = ['','','','']
        print('===============================')
        print('         main symptom          ')
        print('===============================')
        conn= pymysql.connect(host=self.args.mysqlHost , port = self.args.mysqlPort , user = self.args.mysqlUser , passwd=self.args.mysqlPassword , db =self.args.mysqlDB , charset=self.args.mysqlCharset)
        cur = conn.cursor()

        #如果返回列表有值设置，则更新，否则只取出问题列表
        if len(in_sentence.split('@L1@')[0].split('=')) == 2:
            self.prc_set_symptom(in_userID,in_sentence)
        p_callbackkey = self.prc_return_symptom_list(in_userID)
        if p_callbackkey :
            sysSaid = [in_userID,'set_symptom',p_callbackkey,'checkbox']
        else:
            v_sql = ' select ifnull(disease_name,\'a\'),cast(sum(hit_symptom) as CHAR) ,cast(sum(not_symptom) as CHAR) ,cast(sum(not_config) as CHAR) ,cast(count(1) as CHAR) ,group_concat(hit_symptom_name) ' + \
                    '   from ' + \
                    '        (SELECT disease_name , ' + \
                    '                CASE WHEN b.symptom_value = 1 THEN a.symptom_name END hit_symptom_name, ' + \
                    '                CASE WHEN b.symptom_value = 1 THEN 1 END hit_symptom, ' + \
                    '                CASE WHEN b.symptom_value = 0 THEN 1 end not_symptom, ' + \
                    '                ifnull(b.symptom_value , 1) not_config ' + \
                    '           FROM chatbot_symptom a ' + \
                    '           LEFT JOIN ' + \
                    '                (SELECT DISTINCT symptom_name,symptom_value ' + \
                    '                   FROM t_patient_symptom ' + \
                    '                  WHERE patient_id = \''+ in_userID +'\' ' + \
                    '                ) b ' + \
                    '      on a.symptom_name = b.symptom_name ) ff ' + \
                    '   group by disease_name order by sum(hit_symptom)/count(1) desc ' 
            print(v_sql)
            return_disease = ''
            row_count = cur.execute(v_sql)
            list_disease = cur.fetchall()
            if row_count > 0:   
                for line_disease in list_disease :
                    if return_disease == '':
                        return_disease = return_disease + str(line_disease[0]) + '@L2@' + str(line_disease[1]) + '@L2@' +str(line_disease[2]) + '@L2@' +str(line_disease[3]) + '@L2@' +str(line_disease[4]) + '@L2@' +str(line_disease[5])
                    else:
                        return_disease = return_disease  + '@L1@' + str(line_disease[0]) + '@L2@' + str(line_disease[1]) + '@L2@' +str(line_disease[2]) + '@L2@' +str(line_disease[3]) + '@L2@' +str(line_disease[4]) + '@L2@' +str(line_disease[5])
                sysSaid = [in_userID,'set_symptom','疾病名@L2@命中症状数@L2@未命中症状数@L2@未选择症状数@L2@总数@L2@命中症状明细@L1@' +  return_disease,'table'] 
            else:       
                sysSaid = [in_userID,'set_symptom','你的身体很健康，恭喜！','text'] 
        return sysSaid

    def prc_insert_symptom(self,in_userID,in_symptom_type,max_ratio,max_len):
        print('==========================================')
        print('         start insert symptom       ')
        print('==========================================')
        conn= pymysql.connect(host=self.args.mysqlHost , port = self.args.mysqlPort , user = self.args.mysqlUser , passwd=self.args.mysqlPassword , db =self.args.mysqlDB , charset=self.args.mysqlCharset)
        cur = conn.cursor()
        if in_symptom_type == '子症状':
            v_sql = ' select disease_name ,symptom_name ,ifnull(rank,0) rank,symptom_type,f_symptom ' + \
                    '   from chatbot_symptom ' + \
                    '  where f_symptom in ' + \
                    '        (select symptom_name from t_patient_symptom ' + \
                    '          where patient_id= \''+ in_userID +'\' ' + \
                    '            and symptom_value = 1 ' + \
                    '        )' + \
                    '    and symptom_name not in ' + \
                    '        (select symptom_name from t_patient_symptom ' + \
                    '          where patient_id=  \''+ in_userID +'\' ' + \
                    '        )' + \
                    '  order by symptom_type,' + \
                    '        disease_name , ' + \
                    '        rank desc , ' + \
                    '        symptom_name' 
        else:
            v_sql = ' select disease_name ,symptom_name ,ifnull(rank,0) rank,symptom_type,f_symptom ' + \
                    '  FROM chatbot_symptom ' + \
                    ' WHERE disease_name IN ' + \
                    '       (select distinct disease_name FROM chatbot_symptom ' + \
                    '         WHERE symptom_name in ' + \
                    '               (select symptom_name from t_patient_symptom ' + \
                    '                 where patient_id = \''+ in_userID +'\' ' + \
                    '                   and symptom_value = 1 ' + \
                    '               ) ' + \
                    '      )' + \
                    '  AND ifnull(f_symptom,\'\') = \'\' ' + \
                    '  AND symptom_type = \''+ in_symptom_type +'\' ' + \
                    '  and symptom_name not in ' + \
                    '      (select symptom_name from t_patient_symptom ' + \
                    '        where patient_id=  \''+ in_userID +'\' ' + \
                    '      )' + \
                    ' order by symptom_type,' + \
                    '       disease_name , ' + \
                    '       rank desc , ' + \
                    '       symptom_name' 
          
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
                    if (i / dic_disease[tmp_disease] <= max_ratio) or (i <= max_len ):
                        if line[1] in dic_symptom.keys(): 
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
                    '  where symptom_name in (\''+symptom_list+'\')  ' + \
                    '    and symptom_name not in (select symptom_name from t_patient_symptom where patient_id = \''+in_userID+'\' )' + \
                    '     on duplicate key update symptom_value = \'\''
            print(v_sql)
            row_count = cur.execute(v_sql)
            conn.commit()
            return symptom_list

    def prc_ask_symptom(self,in_userID,in_callbackKey,in_sentence):
        sysSaid  = ['','','','']
        print('==========================================')
        print('         start ask symptom   ')
        print('==========================================')
        conn= pymysql.connect(host=self.args.mysqlHost , port = self.args.mysqlPort , user = self.args.mysqlUser , passwd=self.args.mysqlPassword , db =self.args.mysqlDB , charset=self.args.mysqlCharset)
        cur = conn.cursor()

        v_sql = ' insert into t_patient_symptom(patient_id,symptom_name,symptom_value,symptom_type,f_symptom,modified_time) ' +\
                ' select \'' + in_userID + '\',symptom_name,\'1\',symptom_type,f_symptom,now() '+ \
                '   from chatbot_symptom ' + \
                '  where symptom_name like \'%' + in_sentence + '%\''+ \
                '    and ifnull(f_symptom,\'\') = \'\''+ \
                '     on duplicate key update symptom_value = 1'
        print(v_sql)
        cur.execute(v_sql)
        conn.commit()
        conn.close()
        sysSaid = [in_userID,'set_symptom','insert_symptom_done','text']

        return sysSaid

    def prc_set_symptom(self,in_userID,in_sentence):
        print('==========================================')
        print('         start set symptom   ')
        print('==========================================')
        conn= pymysql.connect(host=self.args.mysqlHost , port = self.args.mysqlPort , user = self.args.mysqlUser , passwd=self.args.mysqlPassword , db =self.args.mysqlDB , charset=self.args.mysqlCharset)
        cur = conn.cursor()
        sympton_sql_hit = ''
        sympton_sql_not_hit = ''
        symptom_list = in_sentence.split('@L1@')
        for symptom_one in symptom_list:
            #取出选中的列表，一次性更新入数据
            if symptom_one.split('=')[1] == '1' :
                if sympton_sql_hit == '':
                    sympton_sql_hit = sympton_sql_hit + '\'' + symptom_one.split('=')[0] + '\'' 
                else:
                    sympton_sql_hit = sympton_sql_hit + ','+ '\'' + symptom_one.split('=')[0] + '\''  

            #取出未选中的列表，一次性更新入数据库        
            # if symptom_one.split('=')[1] == '0' :
            #     if sympton_sql_not_hit == '':
            #         sympton_sql_not_hit = sympton_sql_not_hit + '\'' + symptom_one.split('=')[0]  + '\'' 
            #     else:
            #         sympton_sql_not_hit = sympton_sql_not_hit + ','+ '\'' + sympton_sql_not_hit.split('=')[0]  + '\''  
        
        if  sympton_sql_hit != '':                  
            v_sql='update t_patient_symptom set symptom_value = 1  where patient_id = \''+in_userID+'\'  and symptom_name in ('+ sympton_sql_hit + ')'
            print(v_sql)
            cur.execute(v_sql)

        # if sympton_sql_not_hit != '':
        #     v_sql='update t_patient_symptom set symptom_value = 0  where patient_id = \''+in_userID+'\'  and symptom_name in ('+ sympton_sql_not_hit + ')'
        #     print(v_sql)
        #     cur.execute(v_sql)

        v_sql='update t_patient_symptom set symptom_value = 0  where patient_id = \''+in_userID+'\'  and symptom_value = -1 '
        print(v_sql)
        cur.execute(v_sql)

        conn.commit()
        conn.close()

    def prc_return_symptom_list(self,in_userID):
        conn= pymysql.connect(host=self.args.mysqlHost , port = self.args.mysqlPort , user = self.args.mysqlUser , passwd=self.args.mysqlPassword , db =self.args.mysqlDB , charset=self.args.mysqlCharset)
        cur = conn.cursor()
        return_list = ''
        v_sql = ' select symptom_name,symptom_value,f_symptom,symptom_type from t_patient_symptom ' + \
                '  where patient_id = \''+in_userID+'\''  + \
                '    and ifnull(symptom_value,\'\') in (\'-1\',\'\') ' + \
                '  order by symptom_value desc,' + \
                '        f_symptom desc,' + \
                '        symptom_type desc' 
        print(v_sql)

        row_count = cur.execute(v_sql)
        if row_count > 0: 
            first_symptom = cur.fetchone()
            return_list_symptom = first_symptom[0]
            return_sql_symptom = '\'' + first_symptom[0] +'\''

            list_symptom = cur.fetchall()
            for symptom_key in list_symptom:
                if first_symptom[1] == symptom_key[1] and first_symptom[2] == symptom_key[2] and first_symptom[3] == symptom_key[3]:
                    return_list_symptom  =  return_list_symptom + '@L2@' + symptom_key[0]
                    return_sql_symptom = return_sql_symptom + ',' +'\''+ symptom_key[0] +'\''

            v_sql = ' update t_patient_symptom set symptom_value = -1 where symptom_name in ('+return_sql_symptom +') and patient_id = \''+in_userID+'\'' 
            print(v_sql)
            row_count = cur.execute(v_sql)
            conn.commit()

            v_sql = ' select distinct disease_name from chatbot_symptom where symptom_name in (select symptom_name from t_patient_symptom where patient_id = \''+in_userID+'\' and  symptom_value = 1 )'
            print(v_sql)
            row_count = cur.execute(v_sql)
            list_disease = cur.fetchall()
            return_list_disease = ''

            for disease_key in list_disease:
                if return_list_disease == '':
                    return_list_disease  =  return_list_disease + disease_key[0]
                else:
                    return_list_disease  =  return_list_disease + ',' + disease_key[0]

            if return_list_disease != '':
                return_list_disease = self.mainModel.getSpeechCraft('more_disease') + '@L2@ ' + return_list_disease + '@L2@'

            return_list = return_list_disease + self.mainModel.getSpeechCraft('next_symptom') +'@L1@' + return_list_symptom 
            return return_list
   


        
