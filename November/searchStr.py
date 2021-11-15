import sys, getopt
import os
# 导入核心的三个模块
from androguard.core.bytecodes import apk
from androguard.core.bytecodes import dvm
from androguard.core.analysis import analysis
from androguard import misc
from androguard import session
from textblob import TextBlob
from snownlp import SnowNLP
from pathlib import Path

global blackList,whiteList
blackList = ['encrypt','algorithm','decrypt', 'null', 'index out of range','Dead object', 'null', 'msg', 'info', 'invoke', 'call', 'open', 'close','resolve','bind','Google','Expected','registration','account','Account','View','view','message','cipher','Cipher','retrieving','color','Layout','layout','Shared Preferences','upload','object','URL','password','zero','empty','center','response','Failed','failed']
whiteList = ['root','device','debug','exit','fatal','malicious', 'sorry','please','safe','/su','security']



# 对apk进行处理
def get_androguard_obj(apkfile):
    a = apk.APK(apkfile)  # 获取APK文件对象
    d = dvm.DalvikVMFormat(a.get_dex())  # 获取DEX文件对象
    dx = analysis.Analysis(d)  # 获取分析结果对象
    dx.create_xref()  # 这里需要创建一下交叉引用
    return (a, d, dx)

# 输出所有字符串
def output_calling_method(strs):
    cnt = 1  # 输出计数
    # 输出处理结果
    fout = open(store_file_path+"output.txt", "w+",encoding='utf-8')
    for s in strs:
        text = str(s.get_value())
        blob = TextBlob(text)
        score = blob.sentiment.polarity

        fout.write("[%d]%s || %f" % (cnt, text, score))
        cnt += 1
        for call in s.get_xref_from():
            try:
                fout.write("\n\t"+str(call))
            except:
                print("write error")

        fout.write('\n\n')

    fout.close()

def output_calling_method_pos(strs):
    cnt = 1
    fout_p = open(store_file_path+"output_pos.txt", "w",encoding='utf-8')

    for s in strs:
        text = str(s.get_value())
        blob = TextBlob(text)
        score = blob.sentiment.polarity
        if len(blob.words) >= 4:
            if score > 0:
                fout_p.write("[%d]%s || %f" % (cnt, text, score))
                cnt += 1
                for call in s.get_xref_from():
                    # 打印谁调用了该string
                    try:
                        fout_p.write("\n\t"+str(call))
                    except:
                        print("write error")
                fout_p.write('\n\n')

    fout_p.close()

def is_app_method(name):
    for item in exception_list:
        if item in name:
            return False
    return True

#检验是否全是中文字符
def is_all_chinese(strs):
    for _char in strs:
        if not '\u4e00' <= _char <= '\u9fa5':
            return False
    return True

def output_calling_method_neg(strs):
    cnt = 1
    fout_n = open(store_file_path+"output_neg.txt", "w+",encoding='utf-8')

    for s in strs:
        # 使用TextBlob处理
        next = 0 # 是否已经在白名单中被写过
        text = str(s.get_value())
        # in order to fliter some unimportant words and length fliter
        if(len(text)<=4 or text.find("=")!=-1):
            continue

        # 首先判断是不是第三方库，是就直接下一个，不输出
        for _,meth in s.get_xref_from():
            if(is_app_method(str(meth.class_name)) == False):
                next = 1
                break
        if(next == 1):
            continue
        # 接着判断是不是中文,是则用textblob
        if not is_all_chinese(text):
            # 首先判断是不是白名单，是就直接输出
            for item in whiteList:
                if item in text:
                    fout_n.write("[%d]%s" % (cnt, text))
                    cnt += 1
                    fout_n.write("\nwhiteList:{} \tUsed in {} -- {}".format(item,meth.class_name,meth.name))
                    fout_n.write('\n\n')
                    next = 1
                    break
            if(next == 1):
                continue
            # 不在白名单中，先判断情感，再检验是不是在黑名单中
            for item in blackList:
                if item in text:
                    next = 1 # 在黑名单中,不输出
                    break
            if(next == 1):
                continue
            # 判断完上述，判断情感,负面的写入
            blob = TextBlob(text)
            score = blob.sentiment.polarity
            if score < 0:
                try:
                    fout_n.write("[%d]%s || %f" % (cnt, text, score))
                    cnt += 1
                    fout_n.write("\n\tUsed in {} -- {}".format(meth.class_name,meth.name))
                    fout_n.write('\n\n')
                except:
                    print("write error")
                    
        # 使用SnowNLP分析
        else:
            for item in whiteList:
                if item in text:
                    fout_n.write("[%d]%s" % (cnt, text))
                    cnt += 1
                    fout_n.write("\nwhiteList:\tUsed in {} -- {}".format(meth.class_name,meth.name))
                    fout_n.write('\n\n')
                    next = 1
                    break
            if(next == 1):
                continue
            # 不在白名单中，先判断情感，再检验是不是在黑名单中
            for item in blackList:
                if item in text:
                    next = 1 # 在黑名单中,不输出
                    break
            if(next == 1):
                continue
            snow=SnowNLP(text)
            score2=snow.sentiments
            if(score2 < 0.3): # 0表示不开心，1表示开心
                for  _,meth in s.get_xref_from():
                    # 打印谁调用了该string
                    if(is_app_method(meth.class_name) == False):
                        continue
                    try:
                        fout_n.write("[%d]%s || %f" % (cnt, text, score2))
                        cnt += 1
                        fout_n.write("\n\tUsed in {} -- {}".format(meth.class_name,meth.name))
                        fout_n.write('\n\n')
                    except:
                        print("write error")
                
        
    fout_n.close()


def output_arsc_strings(a):
    arscobj = a.get_android_resources()
    arsc_str = []
    arsc_str_id = []
    if not arscobj:
        print("The APK does not contain a resources file!")
        return
    fout_s = open(store_file_path+"output_arsc.txt", "w+", encoding='utf-8')
    strings = arscobj.get_resolved_strings()
    for pkg in strings:
        if pkg == a.get_package():  # 只输出该包名下的string
            fout_s.write(pkg + ":\n")
            for locale in strings[pkg]:
                if locale == 'DEFAULT':
                    for s in strings[pkg][locale]:

                        text = str(strings[pkg][locale][s])
                        if(len(text)<=4):
                            continue

                        elif not is_all_chinese(text):
                            blob = TextBlob(text)
                            score = blob.sentiment.polarity
                            # 下面对消极的字符串进行处理
                            if score < -0.4:

                                fout_s.write(
                                    str(s) + '\t'+str(strings[pkg][locale][s]) + '\n')
                                # 加上arsc中的字符串
                                arsc_str.append(str(strings[pkg][locale][s]))
                                arsc_str_id.append(str(s))

                        else:
                            snow = SnowNLP(text)
                            score2 = snow.sentiments
                            if(score2 < 0.3):  # 0表示不开心，1表示开心
                                fout_s.write(
                                    str(s) + '\t'+str(strings[pkg][locale][s]) + '\n')
                                # 加上arsc中的字符串
                                arsc_str.append(str(strings[pkg][locale][s]))
                                arsc_str_id.append(str(s))

    fout_s.close()
    return arsc_str_id,arsc_str
                    
def  fliter_file(file_path):
    # 替换文件中的字符串
    replaceStr ="R$string" 
    with open(file_path,'r',encoding="utf-8") as r:
        lines=r.readlines()
    with open(file_path,'w',encoding="utf-8") as w:
        for l in lines:
            if replaceStr not in l:
             w.write(l) 
    

def search_str(dx,str,fout):
    #搜索instructions中使用的整数
    for method in dx.get_methods():    
        if method.is_external():
            continue
        m = method.get_method()
        for ins in m.get_instructions():
            print(ins.get_op_value(), ins.get_name(), ins.get_output())
            os.system("pause")
            # print( ins.get_hex(),ins.get_raw())                          class_name: get_class_name()    method_name:get_name()
            output=ins.get_output()
            if str in output:
                fout.write(ins.get_name()+output+m.get_class_name()+m.get_name()+"\n")


# 要分析的apk路径
# sp = 'D:\\workspace\\Android-immunity\\androguard_attempt\\19300240012.apk'
# sp = 'D:\\文件\\学习\\课程\\曦源项目\\mwallet\\com.telkom.mwallet_101_apps.evozi.com.apk'
# file_path = "F:\\2021summerImmunedroid\\2021autumn\\October\\apks\\it.ministerodellasalute.immuni_2430850_apps.evozi.com\\it.ministerodellasalute.immuni_2430850_apps.evozi.com.apk"
# store_file_path="F:\\2021summerImmunedroid\\2021autumn\\October\\apks\\it.ministerodellasalute.immuni_2430850_apps.evozi.com\\"






def getarg(argv):
    inputfile=""
    outputfile = ''
    exception_file = ""

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile=","efile="])
    except getopt.GetoptError:
        print ('python3 searchStr.py -i <inputfile> -o <outputfile> -e <listfile>')
        sys.exit(2)
    if len(args)<3:
        print ('python3 searchStr.py -i <inputfile> -o <outputfile> -e <listfile>')
    for opt, arg in opts:
        if opt == '-h':
            print ('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-e", "--efile"):
            exception_file = arg
    return inputfile,outputfile,exception_file



def read_exception_list(path):
    global exception_list
    result = []
    with open(exception_list_path,'r') as f:
        for line in f:
            result.append(line.strip('\n').split(','))
    merge = sum(result,[])
    exception_list = []
    for item in merge:
        item = item.replace('.', '/')
        exception_list.append(item)
    # print(exception_list)




if __name__ == '__main__':
    # 处理apk
    file_path = "F:\\2021summerImmunedroid\\2021winter\\com.teladoc.members_748_apps.evozi.com.apk"
    store_file_path = "F:\\2021summerImmunedroid\\2021winter\\"
    exception_list_path = "F:\\2021summerImmunedroid\\2021winter\\ThirdLibs.txt"
    # file_path,store_file_path = getarg(sys.argv[1:])
    a, d, dx = get_androguard_obj(file_path)
    # test:begin

    # test :end
    read_exception_list(exception_list_path)


    # way1:从字符串角度入手
    # 获取smali中的所有string
    strs = dx.get_strings()
    print("get strings finish")
    # 获取资源文件中的string
    s,string = output_arsc_strings(a)
    print ("string length:" + str(len(string)))
    print ("s length:" + str(len(s)))
    print("get arsc strings finish")
    # 使用Textblob处理英文字符。使用Snownlp处理中文语句情感
    output_calling_method_neg(strs)
    print("output_negstr in program finish")

    fout_arsc = open(store_file_path+"arsc_result.txt", "w+", encoding='utf-8')
    print("begin to search arsc")
    for i in range(0,len(s)):
        # print(s[i])
        fout_arsc.write("search ID: "+s[i]+"\n")
        fout_arsc.write("search string content: " + string[i]+"\n")
        fout_arsc.write("search result: \n")
        search_str(dx,str(s[i]),fout_arsc)
        fout_arsc.write("------separationline----------\n")
    print("语义分析完成")
