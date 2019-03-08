# coding: utf-8
import copy
import sys
import time

from log import *
from feature import Feature

import xlwt
import xlrd

from parameters import *

reload(sys)
sys.setdefaultencoding('utf8')



##################################################################################
# 统计每个产品的特征列表
##################################################################################
#生成每个产品所包含的社区的列表
def getProductFeatureMaps(file_path):
    #从 file_path的文件中读取每个产品的特征列表
    workbook = xlrd.open_workbook(file_path)
    cluster_sheet = workbook.sheet_by_name('cluster_sheet') 
    n_row=cluster_sheet.nrows
    product_download_list=[]
    product_feature_list_list=[]
    for i in range(0, n_row):
        product_feature_vector_str=cluster_sheet.cell(i,1).value
        product_feature_vector=product_feature_vector_str.split("/")
        product_feature_vector=[int(item) for item in product_feature_vector]
        product_feature_list_list.append(product_feature_vector)
        product_download_list.append(int(cluster_sheet.cell(i,3).value))
                
    return product_feature_list_list,product_download_list


        

###############################################################
# 创建frequent set graph           
###############################################################
class inverseTreeNode:
    def __init__(self, itemset, count):
        self.itemset = itemset#每个节点存放一个项集
        self.count = count
        self.children = {}#可能有多个孩子
        self.parent={}#可能有多个父亲
        #self.tag=0#标记位，标示是否被访问过

    def disp(self, ind=1):
        #print ind, self.itemset, self.count
        toWriteStr="层次："+str(ind)+"["
        for word in self.itemset:
            toWriteStr+=str(word)
            toWriteStr+=","
        toWriteStr+="] count:"
        toWriteStr+=str(self.count)
        writelog(toWriteStr)
        for child in self.children.values():
            child.disp(ind + 1)


#dataset 是一个list
def createInverseTree(dataSet):
    rootNode = inverseTreeNode("Null", 1)  # 根节点,根节点的父集为空，也即为0
    
    # 创建FP树
    #k=0
    size=len(dataSet)
    for itemset in dataSet:
        #k=k+1
        #print "it is the "+str(k)+"/"+str(size)+" freq itemset \n"
        new_node=inverseTreeNode(itemset[0], itemset[1])#创建一个对象，该对象是将共享的
        #将单词插入到树中
        result=updateInverseTree(itemset[0], rootNode, new_node)  # 更新FP树
        if result==False:#如果该节点没有插入到树中，则将其删除
            del new_node
    return rootNode


def updateInverseTree(itemset, inTree, new_node):
    ancestors=[]#存储要插入节点当前节点的父集节点
    tag=False#标示有没有子节点包含当前节点，如果有即为True,否则为False
    for node in inTree.children.values():
        if isSubset(itemset, node.itemset)==1:#这里过滤掉所有支持度相等的子集
            tag=True
            if node.count!=new_node.count:#如果是支持度相等的，则直接舍弃
                ancestors.append(node)
    if len(ancestors)==0 and tag==False:#如果有子节点包含他，但她的父节点仍然为0，那只能说明要插入的节点的支持度与它的父集的支持度都相等
        #当前节点中没有包含要插入项集，则创建新的节点，放在当前节点的下面
        inTree.children[frozenset(itemset)] = new_node
        new_node.parent[frozenset(inTree.itemset)]=inTree
        return True
    else:
        result_final=False
        for node in ancestors:
            result=updateInverseTree(itemset, node, new_node)
            result_final=result_final or result
        return result_final



def isSubset(list_a, list_b):
    if len(list_a)==0 or len(list_b)==0:
        return 0
    for a in list_a:
        if a not in list_b:
            return 0
    return 1  



##################################################################
# 过滤频繁项集
##################################################################
def findBestMatchNode(inTree,itemset):
    #print inTree.itemset
    for node in inTree.children.values():
        if isSubset(itemset,node.itemset)==1:#当前node是Itemset的父集
            if goDeep(node, itemset)==0:#如果节点下面没有在包含Itemset的子集，则当前节点即为找到的节点，
                #print node.itemset
                return node
            else:
                return findBestMatchNode(node,itemset)
        
        
def goDeep(inTree,itemset):#判断下当前节点的子节点是否仍然有itemset的父集
    for node in inTree.children.values():
        if isSubset(itemset, node.itemset)==1:#当前节点的子节点仍然有Itemset的父集
            return 1
    return 0
            
    
def getRecommendReq(inTree, confidence, recommend_requirements_dic, count):
    curr_confidence=float(inTree.count)/float(count)
    if curr_confidence>confidence:
        #首先判断下是否已经存在了，因为相同的父集可能被访问多次
        if frozenset(inTree.itemset) not in recommend_requirements_dic.keys():
            recommend_requirements_dic[frozenset(inTree.itemset)]=curr_confidence
        
        if len(inTree.parent)>0:#只有当前节点的confidence大于要求时，才去考虑他的父节点，因为他的父节点的支持度只会更小
            for node in inTree.parent.values():
                if len(node.parent)>0:#不是根节点,继续向上探索，树中的节点只有根节点的父集为空
                    getRecommendReq(node, confidence,recommend_requirements_dic,count)


    
    
##################################################################
# 调用接口
##################################################################
def storeFrequentItemsets(freqReqSet_list):
    #先对频繁需求项集按照长度进行排序
    for set in freqReqSet_list:
        set.append(len(set[0]))
    freqReqSet_list=[[v[0],v[1]] for v in sorted(freqReqSet_list, key=lambda p: p[2],reverse=True)]#按长度由大到小逆序排列
    print "start to create the tree to record the freq set!!\n"
    rootNode=createInverseTree(freqReqSet_list)
    #rootNode.disp()
    return rootNode

def returnRecommendFreReq(rootNode, itemset, confidence):
    best_node=findBestMatchNode(rootNode,itemset)
    
    recommend_requirements_dic={}
    if best_node!=None:
        getRecommendReq(best_node, confidence, recommend_requirements_dic, best_node.count)
    else: 
        #print "best node is none"
        writelog("best node is none，none features will be recommended")
    
    recomm_req_list=[]
    for (req_itemset,confidence_value) in recommend_requirements_dic.items():#截取需要推荐的项集
        #先去掉itemset中存在的项目
        new_itemset=copy.deepcopy(list(req_itemset))
        for req_id in itemset:
            new_itemset.remove(req_id)
      
        for req_id in new_itemset:
            if req_id not in recomm_req_list:
                recomm_req_list.append(req_id)
        
    return recomm_req_list


def computeRecallPrecision(rootNode,itemset, confidence):
    import random
    size=len(itemset)
    subset_list=[]
    if size>2:
        #samples=random.sample(itemset, 2)
        subset_list=getSubset(itemset)
    else:
        writelog("the length of itemset is less than 2, this frequent feature set is neglected!")
        
    total_recall=0
    total_precision=0
    for subset in subset_list:
        precision=0
        recall=0
        #writelog("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        
        target_itemset=copy.deepcopy(itemset)
        for item in subset:
            target_itemset.remove(item)
        recom_feature_list=returnRecommendFreReq(rootNode,subset,confidence)
        
        str_itemset=[str(item) for item in itemset]
        #writelog("test set: "+",".join(str_itemset))
        str_subset=[str(item) for item in subset]
        #writelog(" sample: "+",".join(str_subset))
        str_copy_itemset=[str(item) for item in target_itemset]
        #writelog("target: "+",".join(str_copy_itemset))
        str_recom_feature_list=[str(item) for item in recom_feature_list]
        #writelog("recommended itemset: "+",".join(str_recom_feature_list))

        if len(recom_feature_list)>0:
            set_intersetion=set(recom_feature_list) & set(target_itemset)
            precision=float(len(set_intersetion))/float(len(recom_feature_list))
            recall=float(len(set_intersetion))/float(len(target_itemset))
        total_recall=total_recall+recall
        total_precision=total_precision+precision
        #writelog("precision: "+str(precision))
        #writelog("recall: "+str(recall))
   
    if len(subset_list)==0:
        return 0,0
    else:
        return total_precision/float(len(subset_list)), total_recall/float(len(subset_list))
    

def getSubset(itemset):
    subset_list=[]
    size_itemset=len(itemset)
    for i in range(0,size_itemset):
        for j in range(i+1, size_itemset):
            subset=[]
            subset.append(itemset[i])
            subset.append(itemset[j])
            subset_list.append(subset)
    return subset_list
            
            

        
def recommend_evaluation(rootNode,test_prodct_community_list,confidence):
    import random
    
    total_recall=0
    total_precision=0
    #writelog("there are {} feature sets in the test set".format(len(test_prodct_community_list)))
    for prodct_community_list in test_prodct_community_list:
        writelog("*************************************************")
        precision,recall=computeRecallPrecision(rootNode,prodct_community_list, confidence)
        total_recall=total_recall+recall
        total_precision=total_precision+precision
   
    return total_precision/float(len(test_prodct_community_list)),total_recall/float(len(test_prodct_community_list))
        
    
            

##################################################################################
#交叉验证，每个数据集分为5分，其中一份作为测试集，另外4份作为训练集
##################################################################################
def recommend_evaluation_main(file_name,confidence,tag):
    from fp_growth import *
    
    prodct_features_map_list,product_download_list=getProductFeatureMaps(file_name)

    size_product=len(prodct_features_map_list)#用于设置最小支持度
   
    #交叉验证，分为5组进行交叉验证
    #ratio=[0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5]
    ratio=[0.01,0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1]
    result_precision_value_list=[]
    result_recall_value_list=[]
    size_step=size_product/5
    min_supp=0#最小支持度
    
    for item_ratio in ratio:
        total_precision=0
        total_recal=0
        print "current ration is:{}".format(item_ratio)
        for i in range(0,5):#5组迭代验证
            print "current iteration :{}".format(i)
            star=size_step*i
            test_product_feature_list=[]
            new_product_feature_map_list=[]
            new_product_download_list=[]
            for j in range(0, size_product):
                if j >=star and j<star+size_step:
                    test_product_feature_list.append(prodct_features_map_list[j])
                else:
                    new_product_feature_map_list.append(prodct_features_map_list[j])
                    new_product_download_list.append(product_download_list[j])
            
            #创建频繁项集挖掘的输入数据
            dataset = new_createInitSet(new_product_feature_map_list, new_product_download_list, tag)
            #挖掘频繁项集
            print "start to mine frequent itemsets \n"
            if tag==0:#产品角度
                min_supp=(size_step*4)*item_ratio
            elif tag==1:
                #根据下载量计算最小支持度
                total_download=0
                for num in new_product_download_list:
                    total_download=total_download+num
                min_supp=total_download*item_ratio
                
            frequentItemsSets_list = fpGrowth(dataset, min_supp) #这里产生的每个项集，包含了两项，item[0]是项集，item[1]是支持度
    
            #创建倒叙树存储频繁集
            rootNode=storeFrequentItemsets(frequentItemsSets_list)
            avg_precision,avg_recall=recommend_evaluation(rootNode,test_product_feature_list,confidence)
            total_precision=total_precision+avg_precision
            total_recal=total_recal+avg_recall
        result_precision=float(total_precision)/5
        result_recall=float(total_recal)/5
        result_precision_value_list.append(result_precision)
        result_recall_value_list.append(result_recall)
    
    result_f1_measure_list=[]
    size_result=len(result_precision_value_list)
    for i in range(0, size_result):
        f=0
        if result_precision_value_list[i]==0 and result_recall_value_list[i]==0:
            f=0
        else:
            f=result_precision_value_list[i]*result_recall_value_list[i]*2/(result_precision_value_list[i]+result_recall_value_list[i])
        result_f1_measure_list.append(f)
    return ratio,result_precision_value_list,result_recall_value_list,result_f1_measure_list

    
    
def save_result(ratio,precision_list,recall_list,f1_list,file_name,tag,confidence):
    wbk = xlwt.Workbook()
    cluster_sheet = wbk.add_sheet('cluster_sheet')
    print "len of ratio: ",len(ratio)
    print "len of precision_list",len(precision_list)
    print "len of recall_list",len(recall_list)    
    print "len of f1_list",len(f1_list)
    
    row=0  
    for item in ratio:
        #写入数据
        cluster_sheet.write(row,0,item)
        cluster_sheet.write(row,1,precision_list[row])
        cluster_sheet.write(row,2,recall_list[row])
        cluster_sheet.write(row,3,f1_list[row])
        row+=1
        
    tag_str=""
    if tag==0:
        tag_str="product_oriented"
    else:
        tag_str="user_oriented"
    final_file_name=path+"data\\prf_"+tag_str+"_"+str(confidence)+"_"+file_name     
    wbk.save(final_file_name)


def getAllFilePath(dirPath):
    import os
    import os.path

    files = os.listdir(dirPath)
    file_path_list=[]
    for file in files :
        txt_path = dirPath+"\\"+file
        file_path_list.append(txt_path)
        print txt_path
    return file_path_list
    


def getALLFileContent(confidence,tag,dirPath):
    file_path_list=getAllFilePath(dirPath)
   
    for file_path in file_path_list:
        print file_path
        ratio,result_precision_value_list,result_recall_value_list,result_f1_measure_list=recommend_evaluation_main(file_path,confidence,tag)
        file_str=file_path.split("\\")
        save_result(ratio,result_precision_value_list,result_recall_value_list,result_f1_measure_list,file_str[len(file_str)-1],tag,confidence)

        
##################################################################################
# main
##################################################################################
#tag=0,product oriented
#tag=1,user oriented

#confidence_list=[0.5,0.6,0.7,0.8]
confidence_list=[0.6]
tag_list=[0,1]

for confidence in confidence_list:
    for tag in tag_list:
        getALLFileContent(confidence,tag,path+"data\\product_feature_matrix_compress_tool_new")




