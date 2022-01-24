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
blackList = ['encrypt','algorithm','decrypt', 'null', 'index out of range','Dead object',  'msg', 'info', 'invoke', 'call', 'open', 'close','resolve','bind','Google','Expected','registration','account','Account','View','view','message','cipher','Cipher','retrieving','color','Layout','layout','Shared Preferences','upload','object','URL','password','zero','empty','center','response','Failed','failed']
whiteList = ['root','device','debug','exit','fatal','malicious', 'sorry','please','safe','/su','security']

# smali 代码中条件语句
Conditionlist=['if-ne','if-eq','if-lt','if-le','if-gt','if-ge','if-eqz','if-nez','if-ltz','if-lez','if-gtz','if-gez']


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
    neg_string=[]
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
                    neg_string.append(text)
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
                    neg_string.append(text)
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
                    neg_string.append(text)
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
                        neg_string.append(text)
                        cnt += 1
                        fout_n.write("\n\tUsed in {} -- {}".format(meth.class_name,meth.name))
                        fout_n.write('\n\n')
                    except:
                        print("write error")
                
        
    fout_n.close()
    return neg_string


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

                            # 添加白名单机制
                            white_flag=0
                            for item in whiteList:
                                if item in text:
                                    white_flag=1+white_flag
                                    break

                            # 下面对消极的字符串进行处理
                            if score < -0.4 or white_flag:

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
    

def search_str(dx,strs,fout,fout2,string):
    #搜索instructions中使用的整数
    for method in dx.get_methods():    
        if method.is_external():
            continue
        m = method.get_method()
        find_logical=0
        for ins in m.get_instructions():
            # print(ins.get_op_value(), ins.get_name(), ins.get_output())
            # os.system("pause")
            # print( ins.get_hex(),ins.get_raw())                          class_name: get_class_name()    method_name:get_name()
            output=ins.get_name()+ins.get_output()
            if str in output:
                fout.write(output+m.get_class_name()+m.get_name()+"\n")
                if find_logical==0:
                    find_logical=find_logical+1
                    fout2.write("search ID: "+strs+"\n")
                    fout2.write("search string content: " + string+"\n")
                    fout2.write(output+m.get_class_name()+m.get_name()+"\n")
                    fout2.write("search logic result: \n")
                    get_logical_method(method,dx,fout2)
                    fout2.write("------separationline----------\n\n")


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
    with open(path,'r') as f:
        for line in f:
            # y:读入第三方库 并用\n 和，分割？
            result.append(line.strip('\n').split(','))

    
    merge = sum(result,[])
    exception_list = []

    for item in merge:
        item = item.replace('.', '/')
        exception_list.append(item)
    # print(exception_list)





#  基于get_xref_from/to api寻找 字符串、方法可能的 调用条件
#  第一个参数为string或者method 类型，第二个参数是分析结果对象 dx,第三个参数是写入的文件
#   1.首先判断 obj的类型 字符串 /方法 
#   2.寻找调用条件的基本规则:
#       a.  obj 如果是字符串类型，那么有两种可能:显式字符串 和 通过getString间接调用的arsc字符串
#           前者可以使用  get_xref_from搜寻到所有调用的 method，然后执行下面的操作
#       b. obj 如果是 method 类型, 则该 method必然是使用了负面字符串作为参数通过下面三种方式寻找判断条件               
#           i.调用了返回类型为 bool的函数  (查找调用者)        
#           ii.判断是否存在条件指令  (在method内部寻找 )
#           iii.尝试向上递归2~3层,至少找到一个带有逻辑判断的

def get_logical_method(obj,dx,file):

    # 对于method 类型的参数有几个情况：
    #  1.单纯的弹窗函数，在该函数内没有什么有效判断逻辑,需要向上查找调用者函数  （向上递归）
    #  2.作为一个调用者函数,包含了判断逻辑和调用弹窗函数的函数，可能存在免疫逻辑判断函数  （查找 bool类型的被调用者函数)  返回bool类型的函数
    #  3.作为一个调用者函数，调用了弹窗函数, 自身存在逻辑判断条件，而非调用免疫逻辑判断函数 (查找有关的条件指令)   直接返回该函数
    if type(obj)==analysis.MethodClassAnalysis or type(obj)==analysis.MethodAnalysis:
        find_logic=0                        # 用来表示是否找到了 相应的逻辑函数
        if obj.is_external():               # 不考虑外部函数
            return


        # 向下查找 bool类型的被调用函数
        for call,meth,_ in obj.get_xref_to():          
            if type(meth)==analysis.ExternalMethod:    #不考虑外部函数
                continue
            info=meth.get_information()
            if 'return' in info and info['return']=='boolean':              # 返回类型为bool 类型
                find_logic=find_logic+1
                temp=obj.get_method()
                file.write(temp.get_class_name()+temp.get_name()+" ----calling---- "+meth.get_class_name()+meth.get_name()+"\n")


        # 查找函数内部条件跳转指令
        encode_meth=obj.get_method()
        file.write(encode_meth.get_class_name()+encode_meth.get_name()+"  conditional mnemonic: \n")
        for ins in encode_meth.get_instructions():
            if ins.get_name() in Conditionlist:                  # 寻找条件语句
                find_logic=find_logic+1
                file.write(ins.get_name()+ ins.get_output()+"\n")


        # 向上查找 1次
        if find_logic==0:
            for class_,call,_ in obj.get_xref_from(): 
                meth=class_.get_method_analysis(call)
                if type(meth)==analysis.MethodClassAnalysis or type(meth)==analysis.MethodAnalysis:
                    get_logical_method(meth,dx,file)  

        return

    if type(obj)==str:     
        try: 
            get_logical_method(dx.strings[obj],dx,file)
        except KeyError as er:
            print(er)
            print('\n')
                                 
        


    elif type(obj)==analysis.StringAnalysis:               #字符串
        for class_,call in obj.get_xref_from():            # 获取所有调用该字符串的函数，分析该函数
            meth=class_.get_method_analysis(call)
            if type(meth)==analysis.MethodClassAnalysis or type(meth)==analysis.MethodAnalysis:
                get_logical_method(meth,dx,file)  

    # 不是上面的类型,则出错                  
    else:
        print("Error argument,str or method argument is required!")
    





if __name__ == '__main__':
    # 处理apk
    # file_path = "F:\\2021summerImmunedroid\\2021winter\\com.teladoc.members_748_apps.evozi.com.apk"
    # file_path = "D:\\workspace\\Immunedroid\\November\\b.apk"
    file_path = "C:\\Users\\86157\\Desktop\\example\\b.apk"
    # store_file_path = "D:\\workspace\\Immunedroid\\November\\out\\"
    store_file_path = "C:\\Users\\86157\\Desktop\\example\\"
    # store_file_path = "F:\\2021summerImmunedroid\\2021winter\\"
    exception_list_path = "./ThirdLibs.txt"
    # file_path,store_file_path = getarg(sys.argv[1:])
    a, d, dx = get_androguard_obj(file_path)
    # test:begin

    # test :end
    # y：读取第三方的库
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

    neg_string=output_calling_method_neg(strs)
    fout_neg_logic=open(store_file_path+"neg_string_logic.txt", "w+", encoding='utf-8')


    # 寻找直接调用的字符串对应的判断逻辑
    for i in range(len(neg_string)):
        fout_neg_logic.write("search string content: " + neg_string[i]+"\n")
        fout_neg_logic.write("search logic result: \n")
        get_logical_method(neg_string[i],dx,fout_neg_logic)
        fout_neg_logic.write("------separationline----------\n\n")

    print("output_negstr in program finish")

    fout_arsc = open(store_file_path+"arsc_result.txt", "w+", encoding='utf-8')

    # 逻辑判断输出文件
    fout_logic=open(store_file_path+"arsc_logic.txt", "w+", encoding='utf-8')

    print("begin to search arsc")

    for i in range(0,len(s)):
        # print(s[i])
        fout_arsc.write("search ID: "+s[i]+"\n")
        fout_arsc.write("search string content: " + string[i]+"\n")
        fout_arsc.write("search result: \n")
        search_str(dx,str(s[i]),fout_arsc,fout_logic,string[i])
        fout_arsc.write("------separationline----------\n")

    fout_arsc.close()
    fout_logic.close()
    fout_neg_logic.close()
    print("语义分析完成")
