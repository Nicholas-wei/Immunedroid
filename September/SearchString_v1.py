import os
import sys
# 导入核心的三个模块
from androguard.core.bytecodes import apk
from androguard.core.bytecodes import dvm
from androguard.core.analysis import analysis
from androguard import misc
from androguard import session
from textblob import TextBlob
from snownlp import SnowNLP
from pathlib import Path
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
        text = str(s.get_value())
        # in order to fliter some unimportant words
        if(len(text)<=4 or text.find("=")!=-1):
            continue
        if not is_all_chinese(text):
            # print("English text:" + text)
            # os.system("pause")
            blob = TextBlob(text)
            score = blob.sentiment.polarity
            if len(blob.words) >= 4:
                if score < 0:
                    fout_n.write("[%d]%s || %f" % (cnt, text, score))
                    cnt += 1
                    for _,meth in s.get_xref_from():
                        # 打印谁调用了该string
                        try:
                            fout_n.write("\n\tUsed in {} -- {}".format(meth.class_name,meth.name))
                        except:
                            print("write error")
                    fout_n.write('\n\n')
        # 使用SnowNLP分析
        else:
            snow=SnowNLP(text)
            score2=snow.sentiments
            if(score2 < 0.3): # 0表示不开心，1表示开心
                fout_n.write("[%d]%s || %f" % (cnt, text, score2))
                cnt += 1
                for  _,meth in s.get_xref_from():
                    # 打印谁调用了该string
                    try:
                        fout_n.write("\n\tUsed in {} -- {}".format(meth.class_name,meth.name))
                    except:
                        print("write error")
                fout_n.write('\n\n')
        
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
                    
# def  fliter_file(file_path):
#     # 替换文件中的字符串
#     replaceStr ="R$string" 
#     with open(file_path,'r',encoding="utf-8") as r:
#         lines=r.readlines()
#     with open(file_path,'w',encoding="utf-8") as w:
#         for l in lines:
#             if replaceStr not in l:
#              w.write(l) 
    
#删除指定文件名中含指定字符串的文件  用于删除R$string.smali
def deletefile(start, name):
    for relpath, _, files in os.walk(start):
        if name in files:
            full_path = os.path.join(start, relpath, name)
            print(os.path.normpath(os.path.abspath(full_path)))
            os.remove(os.path.normpath(os.path.abspath(full_path))) 


# 要分析的apk路径
# sp = 'D:\\workspace\\Android-immunity\\androguard_attempt\\19300240012.apk'
# sp = 'D:\\文件\\学习\\课程\\曦源项目\\mwallet\\com.telkom.mwallet_101_apps.evozi.com.apk'
file_path = "C:\\Users\\86157\\Desktop\\Andguard\\news.apk"
store_file_path="C:\\Users\\86157\\Desktop\\Andguard\\"
smali_file_path="C:\\Users\\86157\\Desktop\\Andguard\\smali_out"
work_file_path=store_file_path
arsc_file_path = store_file_path + "arsc_result.txt"

delete_string="R$string.smali"


if __name__ == '__main__':
    # 处理apk
    # sess = misc.get_default_session()
    a, d, dx = get_androguard_obj(file_path)
    # a,d,dx = misc.AnalyzeAPK(file_path,session=sess)
    # way1:从字符串角度入手
    # 获取smali中的所有string
    strs = dx.get_strings()
    print("get strings finish")
    # 获取资源文件中的string
    s,string = output_arsc_strings(a)
    print ("string length:" + str(len(string)))
    print ("s length:" + str(len(s)))
    # os.system("pause")
    print("get arsc strings finish")
    # session.Save(sess,"androguard_session.ag")
    # 使用Textblob处理英文字符。使用Snownlp处理中文语句情感
    output_calling_method_neg(strs)
    print("output_negstr in program finish")

    #搜索str_arsc中的内容,每一行都是一个十进制id

    #基本思路：匹配以smali为后缀的文件，在其中搜索对nameid的使用
        
    # 使用chdir进入apktool工作目录
    os.chdir(work_file_path)


    #配置apktool 环境， 参考:https://blog.csdn.net/ruancoder/article/details/51924179
    # 使用apktool 对apk文件进行反编译得到smali文件 输出文件名：smali_out
    smali_file = Path(smali_file_path)
    if not smali_file.exists():
        print("no smali_out!!")  
        os.system("apktool d -r -o smali_out "+file_path)
    else:
        print("smali file exists!!!")

    # 删除smali中所有R$sring.smali
    # 慎用此函数，文件一经删除则无法恢复
    # 检索较慢，或者第一次运行时可以适当调用该函数
    # deletefile(smali_file_path,delete_string)


    # 使用echo 重置或创建result.txt文件
    os.system("echo asrc string search result: > arsc_result.txt")


    os.chdir(smali_file_path)
    for i in range(0,len(s)):
        s_dec=int(s[i],10)
        s_hex=hex(s_dec)
        serach_str=str(s_hex)

        # 使用echo向文件中输入分割线与提示内容
        os.system("echo ------separationline---------- >> "+arsc_file_path)
        os.system("echo search stringID: "+serach_str+" >> "+arsc_file_path)
        os.system("echo search string content: " + string[i] + " >> "+arsc_file_path)
        os.system("echo search result: >> "+arsc_file_path)

        #使用findstr命令递归搜索当前目录及其子目录下的所有smali文件，并追加到arsc_result.txt文件中
        #findstr 相关参数与介绍 参考：https://www.netingcn.com/window-findstr-command.html
        os.system("findstr /MSI \""+serach_str+"\" *.smali >> "+arsc_file_path)
        # os.system("findstr /MSI \""+serach_str+"\" *.smali >> arsc_result.txt")
        os.system("echo ------separationline---------- >> "+arsc_file_path)

        # 重新处理输出文件去除“R$string"部分
        # arsc_file_path = store_file_path + "arsc_result.txt"
    # fliter_file(arsc_file_path)



    print("语义分析完成")