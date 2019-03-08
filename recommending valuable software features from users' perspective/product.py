import sys  
reload(sys)  
sys.setdefaultencoding('utf8')


class Product:
    
    def __init__(self,product_id, product_name, product_download,product_rating,words_list):
        self.product_id=product_id
        self.product_name=product_name
        self.product_download=product_download
        self.product_rating=product_rating
        self.words_list=words_list

    def getProductID(self):
        return self.product_id

    def getProductName(self):
        return self.product_name

    def getProductDownLoad(self):
        return self.product_download

    def getProductRating(self):
        return self.product_rating


    def getWordsList(self):
        return self.words_list
    