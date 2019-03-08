# coding: utf-8

import xlwt
import xlrd
from parameters import *
from feature_extraction_by_collocation import *


def save_coefficients_new(coeffecit_list,intercept_,file_path):
    wbk = xlwt.Workbook()
    cluster_sheet = wbk.add_sheet('cluster_sheet')
    
    row=0
    #写入数据
    cluster_sheet.write(row,0,intercept_)
    row+=1    
    for coeffecit in coeffecit_list:
        #写入数据
        cluster_sheet.write(row,0,row-1)
        cluster_sheet.write(row,1,coeffecit)
        row+=1
    wbk.save(file_path)


def save_features(features_supp_list,group_list,file_name,num_features):
    wbk = xlwt.Workbook()
    cluster_sheet = wbk.add_sheet('cluster_sheet')
    
    row=0
    #写入数据 
    for group in group_list:
        cluster_sheet.write(row,0,row)
        members=group[0]
        feature_str=""
        for feature_id in members:
            feature_str+=" ".join(features_supp_list[feature_id][0])
            feature_str+=","
        cluster_sheet.write(row,1,feature_str)
        cluster_sheet.write(row,2,group[1])
        row+=1

    import os
    new_file_dir=path+"data\\minde_features_list_"+file_name.split(".")[0]+"\\"
    isExists = os.path.exists(new_file_dir)
    if not isExists:
        os.makedirs(new_file_dir)
    new_file_name=new_file_dir+file_name.split(".")[0]+"_minde_features_"+str(num_features)+".xls"
    wbk.save(new_file_name)

  



def saveProductFeatureList(product_features_list, lasso_coefficients,product_ratings_list, product_download_list,file_name,num_features):
    wbk = xlwt.Workbook()
    cluster_sheet = wbk.add_sheet('cluster_sheet')
    
    row=0
    k=0
    for features_list in product_features_list:
        k+=1
        #以字符串存储各个产品的特征列表
        left_features=[]
        for i in range(0,len(features_list)):
            if features_list[i]==1 and lasso_coefficients[i]>0:
                left_features.append(i)
        #如果一个产品的所有特征都没有被选中，则将该产品剔除
        if len(left_features)==0:
            continue
        
        #写入数据
        cluster_sheet.write(row,0,k-1)#产品ID
        str_resutlt=""
        for i in range(0,len(left_features)):
            if i>0:
                str_resutlt+="/"
            str_resutlt+=str(left_features[i])
        cluster_sheet.write(row,1,str_resutlt)
        cluster_sheet.write(row,2,product_ratings_list[row])#存储产品的用户评分
        cluster_sheet.write(row,3,product_download_list[row])#存储产品的用户评分
        row+=1
        
    #创建一个文件夹
    import os
    new_file_dir=path+"data\\product_feature_matrix_"+file_name.split(".")[0]+"\\"
    isExists = os.path.exists(new_file_dir)
    if not isExists:
        os.makedirs(new_file_dir) 
    new_file_name=new_file_dir+file_name.split(".")[0]+"_product_feature_matrix_"+str(num_features)+".xls"        
    wbk.save(new_file_name)
    


def estimateMissRatings(product_features_list,product_rating_list):
    import numpy as np
    num_product=len(product_rating_list)
    for i in range(0,num_product):
        if product_rating_list[i]==0:
            max_sim=0
            max_key=0
            for j in range(0,num_product):
                if i!=j:
                    sim=np.corrcoef(product_features_list[i],product_features_list[j])
                    if sim[0][1]>max_sim:
                        max_sim=sim[0][1]
                        max_key=j
            product_rating_list[i]=product_rating_list[max_key]
    


def computeRscores(product_features_list, product_ratings_list,num_features,file_name):
    from sklearn import linear_model
    result=[]
    #创建一个文件夹
    import os
    new_file_dir=path+"data\\feature_coefficient_list_"+file_name.split(".")[0]+"\\"
    isExists = os.path.exists(new_file_dir)
    if not isExists:
        os.makedirs(new_file_dir)  
    new_file_name=new_file_dir+file_name.split(".")[0]+"_"
    
    #第一种，直接利用linear regression
    print "start to linear regression"
    copy_product_features_list=copy.deepcopy(product_features_list)
    copy_product_ratings_list=copy.deepcopy(product_ratings_list)
    reg =linear_model.LinearRegression()
    reg.fit(copy_product_features_list,copy_product_ratings_list)
    del copy_product_features_list
    del copy_product_ratings_list
    file_path=new_file_name+"linear_regression_"+str(num_features)+".xls" 
    save_coefficients_new(reg.coef_, reg.intercept_, file_path)
    copy_product_features_list=copy.deepcopy(product_features_list)
    copy_product_ratings_list=copy.deepcopy(product_ratings_list)
    r2_linearregression=reg.score(copy_product_features_list,copy_product_ratings_list)
    print "r2 score: ",r2_linearregression
    del copy_product_features_list
    del copy_product_ratings_list
    
    #第二种，lasso
    print "start to lasso regression"
    copy_product_features_list=copy.deepcopy(product_features_list)
    copy_product_ratings_list=copy.deepcopy(product_ratings_list)
    reg =linear_model.LassoCV(cv=5, random_state=0)
    reg.fit(copy_product_features_list,copy_product_ratings_list)
    del copy_product_features_list
    del copy_product_ratings_list
    file_path=new_file_name+"linear_lassocv_regression_"+str(num_features)+".xls" 
    save_coefficients_new(reg.coef_, reg.intercept_, file_path)
    copy_product_features_list=copy.deepcopy(product_features_list)
    copy_product_ratings_list=copy.deepcopy(product_ratings_list)
    r2_lasso=reg.score(copy_product_features_list,copy_product_ratings_list)
    print "r2 score: ",r2_lasso
    del copy_product_features_list
    del copy_product_ratings_list
    result=reg.coef_
    
    
    #第三种 ridge
    print "start to ridge regression"
    copy_product_features_list=copy.deepcopy(product_features_list)
    copy_product_ratings_list=copy.deepcopy(product_ratings_list)
    reg = linear_model.RidgeCV(cv=5)
    reg.fit(copy_product_features_list,copy_product_ratings_list)
    del copy_product_features_list
    del copy_product_ratings_list
    file_path=new_file_name+"linear_ridge_regression_"+str(num_features)+".xls" 
    save_coefficients_new(reg.coef_, reg.intercept_, file_path)
    copy_product_features_list=copy.deepcopy(product_features_list)
    copy_product_ratings_list=copy.deepcopy(product_ratings_list)
    r2_ridge=reg.score(copy_product_features_list,copy_product_ratings_list)
    print "r2 score: ",r2_ridge
    del copy_product_features_list
    del copy_product_ratings_list
    
    return result

    

#########################################################################################
# main
#########################################################################################
#获取每个产品的特征向量，产品的用户评分，产品的下载量
file_name="compress_tool_new.xlsx"
product_dic=summaryPreprocess(path+"data\\dataset_filtered\\"+file_name)
print "len of product_dic ", len(product_dic)
print "start to extract bigram"
features_supp_dic=featureExtractionByCollocations(product_dic)
print "start to merge bigram"
features_supp_list=mergeSamePhraseWithDiffOrder(features_supp_dic)
print "start to filter bigram"
    
num_list=[100,200]
for num_features in num_list:
    print "********************************************************"
    print "liuchun  num_features: ",num_features
    new_features_supp_list=filterLowFrequency(features_supp_list,num_features)
    print "start to group bigram"
    group_list=groupBySynset(new_features_supp_list)
    
    save_features(new_features_supp_list,group_list,file_name,num_features)
    
    print "start to produce feature-product matrix"
    product_features_list, product_ratings_list, product_download_list=getProductFeatureMatrix(product_dic, new_features_supp_list, group_list)
    print "len of product_features_list ",len(product_features_list)
    print "len of product_ratings_list",len(product_ratings_list)
    print "len of product_downloads_list",len(product_download_list)
        
    #估计缺失的用户评分数据
    estimateMissRatings(product_features_list,product_ratings_list)

    #计算各个方法的r2系数
    lasso_coefficients=computeRscores(product_features_list,product_ratings_list,num_features,file_name)
        
    #首先将每个产品中没有被选中的特征给过滤掉，然后把product_feature_list, product_ratings_list, product_download_list给存储到excel表里边
    saveProductFeatureList(product_features_list, lasso_coefficients,product_ratings_list, product_download_list,file_name,num_features)
        
    



