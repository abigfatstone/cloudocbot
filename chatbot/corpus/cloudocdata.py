
# -*- coding:utf-8 -*-

import os
import jieba

class CloudocData:
    """
    """

    def __init__(self, dirName):
        """
        Args:
            dirName (string): directory where to load the corpus
        """
        self.lines = self.loadLines(os.path.join(dirName, "cloudoc"))
        self.conversations = [{"lines": self.lines}]


    def loadLines(self, fileName):
        """
        Args:
            fileName (str): file to load
        Return:
            list<dict<str>>: the extracted fields for each line
        """
        lines = []
        
        with open(fileName, 'r',encoding= 'utf-8') as f: 
        #    with open('d://output.txt', 'w',encoding= 'utf-8') as ff: 
                for line in f:
                    if len(line.split(': ')) > 1 :
                        l =  jieba.cut(line.split(': ')[1],cut_all=False)
                        #l =  line.split(': ')[1]
                        lines.append({"text": " ".join(l)})  
                        #ff.write(" ".join(l))              
        return lines
        

    def getConversations(self):
        return self.conversations
