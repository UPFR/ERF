import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

class Feature:
   
    def __init__(self,product_id, id, text):
        self.product_id=product_id
        self.id=id
        self.text=text
        self.wordlist_list=[]
        self.word_count_dic={}
        self.word_tf_dic={}
        self.len=0
        self.tf_idf_vector_list=[]
        self.req_list=[]
        self.name=""
        

    def setWordList(self, wordlist_list):
        self.wordlist_list=wordlist_list
        
    def setName(self, name):
        self.name=name

    def setWordCountDic(self, word_count_dic):
        self.word_count_dic=word_count_dic

    def setWordTFDic(self, word_tf_dic):
        self.word_tf_dic=word_tf_dic

    def setWordListLen(self, len):
        self.len=len

    def setTFIDFVector(self, tf_idf_vector_list):
        self.tf_idf_vector_list=tf_idf_vector_list

    def addReqList(self,req_id):
        if req_id not in self.req_list:
            self.req_list.append(req_id)



    def getProductID(self):
        return self.product_id

    def getID(self):
        return self.id

    def getText(self):
        return self.text

    def getWordList(self):
        return self.wordlist_list

    def getWordCountDic(self):
        return self.word_count_dic

    def getLen(self):
        return self.len

    def getWordTFDic(self):
        return self.word_tf_dic

    def getTFIDFVector(self):
        return self.tf_idf_vector_list

    def getReqList(self):
        return self.req_list

    def getName(self):
        return self.name
    



     

    
    
