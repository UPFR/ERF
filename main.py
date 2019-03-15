# coding: utf-8                                                                                                                                                                                                                       # coding: utf-8
import sys
import codecs
import math
import copy
import re
from log import *
from parameters import *
from cluster import Community

reload(sys)
sys.setdefaultencoding('utf8')

##################################################################################
#输出结果
##################################################################################  
def save_result(community_list,community_feature_list,community_selected_sentence_id_list,all_sentences_list, all_original_sentences_list,file_name,all_words_list):
    import xlwt
    wbk = xlwt.Workbook()
    cluster_sheet = wbk.add_sheet('sheet')
    name_writed=False
    k=0
    row=0
    for community in community_list:
        #关键词
        keywords_list=[]
        for word_id in community.getDominateWords():
            keywords_list.append(all_words_list[word_id])
        
        menmbers_dic=community.getMenmberSentences()
        name_writed=False
        feature_writed_count=0
        for (sentence_id, tfidf_vector) in menmbers_dic.items():
            #生成社区约简之后的句子
            left_words_list=[]
            for i in range(0,len(tfidf_vector)):
                if tfidf_vector[i]>0:
                    left_words_list.append(all_words_list[i])
                    
            #按照原有句子中单词的顺序产生约简之后的句子
            reduced_sentence=[]
            for word in all_sentences_list[sentence_id]:
                if word in left_words_list:
                    reduced_sentence.append(word)
            #特征名字的列表
            feature_name_list=community_feature_list[k]
            #代表性句子的列表
            representative_sentence_list=community_selected_sentence_id_list[k]
            #写入数据
            if name_writed==False:
                cluster_sheet.write(row,0," ".join(keywords_list))#写入关键词
                name_writed=True
                
            #继续写入特征名字和代表性句子
            if feature_writed_count<3:
                cluster_sheet.write(row,1," ".join(feature_name_list[feature_writed_count]))#写入第一个特征
                cluster_sheet.write(row,2,all_original_sentences_list[representative_sentence_list[feature_writed_count]])#写入包含特征的代表性句子
                feature_writed_count+=1
            
            cluster_sheet.write(row,3," ".join(reduced_sentence))
            cluster_sheet.write(row,4,all_original_sentences_list[sentence_id])
            
            row+=1
        k+=1
            
    final_file_name=path+"data\\result\\"+file_name+".xls"        
    wbk.save(final_file_name)
            


#########################################################################################
# main
#########################################################################################
if __name__=="__main__":
    
    print "star to get data"
    from text_process import *
    corpus,all_cluster_sentences_list,all_cluster_original_sentences_list=getALLFileContent(path+"data\\selected_25_100")
    
    #antivius这一类的id为0，compress的id为3
    dataset_id=3
    
    print "start to get tfidf data"
    #这个地方发现tfidf比idf来计算词的重要性要更加准确
    from util import computeSelectedDocumentWordTFIDF,documentsVectorizer_array
    cluster_word_tfidf_dic=computeSelectedDocumentWordTFIDF(corpus,dataset_id)
    #得到各个句子的tfidf向量,这里tfidf_matrixt是一个矩阵
    tfidf_matrixt,all_words_list=documentsVectorizer_array(all_cluster_sentences_list[dataset_id],cluster_word_tfidf_dic)

    
    print "start to cluster"
    import numpy as np
    a_array=np.arange(0.3, 0.8, 0.1)#min
    c_array=np.arange(0,1,0.1)#WEIGHT_COEFFICIENT
    a_list=a_array.tolist()
    c_list=c_array.tolist()
    
    for MIN_SIMILARITY in a_list:
        b_array=np.arange(MIN_SIMILARITY, 0.8, 0.1)#max
        b_list=b_array.tolist()
        for MAX_SIMILARITY in b_list:
            for WEIGHT_COEFFICIENT in c_array:
                #聚类
                from detect_cluster import clusterByCommunityDetection
                community_list=clusterByCommunityDetection(all_cluster_sentences_list[dataset_id],tfidf_matrixt,MIN_SIMILARITY,MAX_SIMILARITY)
               

                #选择K个社区
                from select_cluster import selectTopKCommunity
                selected_community_list,community_keywords_list=selectTopKCommunity(community_list,all_words_list,20,WEIGHT_COEFFICIENT)


                #从社区中根据每个社区的前k个关键词，然后根据词语搭配选择频率最高的词组
                from extract_feature import extractFeatures
                community_feature_list,community_selected_sentence_id_list=extractFeatures(all_cluster_sentences_list[dataset_id],selected_community_list,community_keywords_list,all_words_list)


                writelog("MIN_SIMILARITY:"+str(MIN_SIMILARITY)+"**********************")
                file_name="compress_20_"+str(MIN_SIMILARITY)+"_"+str(MAX_SIMILARITY)+"_"+str(WEIGHT_COEFFICIENT)
                save_result(selected_community_list,community_feature_list,community_selected_sentence_id_list,all_cluster_sentences_list[dataset_id],all_cluster_original_sentences_list[dataset_id],file_name,all_words_list)


                
        
    
 