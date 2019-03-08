# coding: utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from log import *
import math
import copy

class treeNode:
    def __init__(self, nameValue, numOccur, parentNode):
        self.name = nameValue
        self.count = numOccur
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}

    def inc(self, numOccur):
        self.count += numOccur

        # 利用深度优先方法，遍历输出

    def disp(self, ind=1):
        print ind, self.name, self.count
        for child in self.children.values():
            child.disp(ind + 1)


##################################################################
# 创建FP树
##################################################################
def createTree(dataSet, minSup):
    # 第一次遍历数据集，创建头指针表
    headerTable = {}
    for trans in dataSet:
        for item in trans:
            if item not in headerTable.keys():
                headerTable[item] = dataSet[trans]
            else:
                headerTable[item] = headerTable[item] + dataSet[trans]

    # 移除不满足最小支持度的元素项
    for k in headerTable.keys():
        if headerTable[k] < minSup:
            del (headerTable[k])

    # 空元素集，返回空
    freqItemSet = set(headerTable.keys())
    if len(freqItemSet) == 0:
        return None, None

    # 增加一个数据项，用于存放指向相似元素项指针
    for k in headerTable:
        headerTable[k] = [headerTable[k], None]

    rootNode = treeNode("Null", 1, None)  # 根节点

    # 第二次遍历数据集，创建FP树
    for tranSet, count in dataSet.items():
        localD = {}  # 对一个项集tranSet，记录其中每个元素项的全局频率，用于排序
        for item in tranSet:
            if item in freqItemSet:
                localD[item] = headerTable[item][0]  # 注意这个[0]，因为之前加过一个数据项
        if len(localD) > 0:
            orderedItems = [v[0] for v in sorted(localD.items(), key=lambda p: p[1], reverse=True)]  # 排序
            updateTree(orderedItems, rootNode, headerTable, count)  # 更新FP树
    return rootNode, headerTable


def updateTree(items, inTree, headerTable, count):
    if items[0] in inTree.children:
        # 有该元素项时计数值+1
        inTree.children[items[0]].inc(count)
    else:
        # 没有这个元素项时创建一个新节点
        inTree.children[items[0]] = treeNode(items[0], count, inTree)
        # 更新头指针表或前一个相似元素项节点的指针指向新节点
        if headerTable[items[0]][1] == None:
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])

    if len(items) > 1:
        # 对剩下的元素项迭代调用updateTree函数
        updateTree(items[1::], inTree.children[items[0]], headerTable, count)


def updateHeader(nodeToTest, targetNode):
    while (nodeToTest.nodeLink != None):
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode


##################################################################
# 挖掘频繁项集
##################################################################
def findPrefixPath(basePat, treeNode):
    # 创建前缀路径
    condPats = {}  # 条件模式基
    while treeNode != None:
        prefixPath = []
        ascendTree(treeNode, prefixPath)
        if len(prefixPath) > 1:
            condPats[frozenset(prefixPath[1:])] = treeNode.count
        treeNode = treeNode.nodeLink
    return condPats


def ascendTree(leafNode, prefixPath):
    if leafNode.parent != None:
        prefixPath.append(leafNode.name)
        ascendTree(leafNode.parent, prefixPath)


def mineTree(inTree, headerTable, minSup, preFix, freqItemsSets_list):
    if headerTable==None or len(headerTable)==0:
        writelog("在挖掘频繁项目的过程中，索引表为空！")
        return 
    bigL = [v[0] for v in sorted(headerTable.items(), key=lambda p: p[1])]
    for basePat in bigL:
        #newFreqSet = preFix.copy()
        #newFreqSet.add(basePat)
        newFreqSet=preFix[:]
        newFreqSet.append(basePat)
        
        freqItemsetwithcount=[]
        freqItemsetwithcount.append(newFreqSet)
        freqItemsetwithcount.append(headerTable[basePat][0])
        freqItemsSets_list.append(freqItemsetwithcount)
        #freqItemsSets_dic[frozenset(newFreqSet)] = headerTable[basePat][0]  # 获取这个集合的支持度
        condPattBases = findPrefixPath(basePat, headerTable[basePat][1])
        myCondTree, myHead = createTree(condPattBases, minSup)

        if myHead != None and len(myHead)>0:
            mineTree(myCondTree, myHead, minSup, newFreqSet, freqItemsSets_list)


##################################################################
# 频繁项集的挖掘接口
##################################################################
#创建输入到FP-Growth的数据集，以词项集作为键，频率为1
def createInitSet(product_community_map_dic, product_download_dic, tag):
    dataset={}
    for (product_key, community_list) in product_community_map_dic.items():
        if tag==0:
            dataset[frozenset(community_list)]=1
        elif tag==1:
            dataset[frozenset(community_list)]=product_download_dic[product_key]
        
    return dataset


def new_createInitSet(product_community_map_list, product_download_list, tag):
    dataset={}
    size=len(product_community_map_list)
    for i in range(0,size):
        community_list=product_community_map_list[i]
        if tag==0:
            dataset[frozenset(community_list)]=1
        elif tag==1:
            dataset[frozenset(community_list)]=product_download_list[i]      
        
    return dataset

def toString(vector):
    result="["
    for item in vector:
       result=result+" "
       result=result+str(item)
    result=result+"]"
    return result



#生成频繁项集
def fpGrowth(dataSet, minSup):
    myFPtree, myHeaderTab = createTree(dataSet, minSup)
    """
    #bigL = sorted(myHeaderTab.items(), key=lambda p: p[1])
    #writelog("各个词的排序如下")
    for item in bigL:
        writelog(item[0])
        writelog(item[1])
    """
    #freqItemsSets_dic = {}
    freqItemsSets_list=[]
    #mineTree(myFPtree, myHeaderTab, minSup, set([]), freqItemsSets_dic)
    temp=[]
    mineTree(myFPtree, myHeaderTab, minSup, temp, freqItemsSets_list)
    #mineTree(myFPtree, myHeaderTab, minSup, set([]), freqItemsSets_list)
    #return freqItemsSets_dic
    return freqItemsSets_list


        