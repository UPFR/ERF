# coding: utf-8
import sys
import time
reload(sys)  
sys.setdefaultencoding('utf8')

import codecs

from parameters import *


log = codecs.open(path+"log\\log_"+time.strftime('%Y_%m_%d_%H_%M_%S',time.localtime(time.time()))+".txt", "a", encoding='utf-8')

def writelog(text):
    log.write("["+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))+"]")
    log.write(text)
    log.write("\n")


def closelog():
    log.close()