# -*- coding:utf-8 -*-
import os
from lxml import etree
import re



# 保存的结构体
class Store(object):
    class Struct(object):
        def __init__(self,index,content,nameId):
            self.index=index
            self.content=content
            self.nameId=nameId
    def make_obj(self,index,content,nameId):
        return self.Struct(index,content,nameId)





# 这里填写处理过后的strings.xml（去除英文字符，保存为结构数组）的保存路径
store_path="E:\\ImmuneDroid_script\\nlpir\\result.txt"
# 这里填写保存文件jadx resources.arsc下res->values->strings.xml复制出来的txt文件的的绝对路径
file_path="E:\\ImmuneDroid_script\\nlpir\\xmltest.txt"
# 这里填写nlpir输出的output sentiment文件路径
# sentiment_path="E:\\NLPIR-master\\NLPIR-master\\NLPIR-Parser\\output\\sentiment_General_Detail.txt"
sentiment_path="F:\\message"
# 这里填写smali文件夹（最外层文件夹）not implemented
neg_str_path="E:\\ImmuneDroid_script\\nlpir\\neg_str.txt"


def file_way():
    file_object=open(file_path,"r",encoding="utf-8")
    try:
        all_the_text=file_object.read()
        se=etree.HTML(bytes(bytearray(all_the_text,encoding="utf-8")))
        file=open(store_path,'w', encoding="utf-8")
        for item in se.xpath('//string/text()'):
            item=str(item)
            item = re.sub("[A-Za-z0-9\!\%\[\]\,\。\ ]", "",item)
            if len(item)<5:
                continue
            file.write(str(item)+'\n')
        print("finish")
    finally:
        file_object.close()


def file_way_add_name():
    store=Store()
    store_object=[]
    file_object=open(file_path,"r",encoding="utf-8")
    true_name=[]
    true_content=[]
    try:
        all_the_text=file_object.read()
        se=etree.HTML(bytes(bytearray(all_the_text,encoding="utf-8")))
        file=open(store_path,'w', encoding="utf-8")
        names=se.xpath('//string/@name')
        strings=se.xpath('//string/text()')
        # arrange
        iter_length=len(names)
        for i in range(iter_length):
            xpath_sent='//string[@name=\"%s\"]/text()' % str(names[i])
            # print(xpath_sent)
            res=se.xpath(xpath_sent)
            # print(names[i],res)
            # os.system("pause")
            if(len(res) == 0):
                # print("NO content: " + str(names[i]))
                # os.system("pause")
                # names.remove(names[i])
                # iter_length-=1
                # i-=1
                continue
            # has content
            else:
                true_name.append(names[i])
                true_content.append(res)
                # print("Has content:" + str(true_name[-1])+str(true_content[-1]))
                # os.system("pause")
        # print (len(true_name),len(true_content))
        # os.system("pause")
        zip_object = zip(true_name,true_content)
        cnt=0
        for (name,string) in zip_object:
            string_iter=str(string)
            string_iter=re.sub("[A-Za-z0-9\!\%\[\]\,\。\ ]", "",string_iter)
            if len(string_iter)<8:
                continue
            cnt+=1
            file.write(str(cnt)+"||"+str(string_iter)+"||"+str(name)+"\n")
            temp_store_object=store.make_obj(cnt,string_iter,name)
            store_object.append(temp_store_object)

    finally:
        print("finish")
        file_object.close()
        file.close()
    return store_object


def extract_neg_index():
    file_object=open(sentiment_path,"r",encoding="utf-8")
    neg_content=[]
    neg_content_name=[]
    index_array=[]
    lines=file_object.readlines()
    try:
        for line in lines:
            if(lines.index(line)<15):
                continue
            se=etree.HTML(bytes(bytearray(line,encoding="utf-8")))
            neg_xpath='//neg/@value'
            pos_xpath='//pos/@value'
            pos_array=se.xpath(pos_xpath)
            neg_array=se.xpath(neg_xpath)
            result_list=[]
            print(line+"pos: "+str(len(pos_array))+"neg: "+str(len(neg_array)))
            # os.system("pause")
            if(len(neg_array)>len(pos_array)):
                # add it to result_list
                index=line.split('||')[0]
                index_array.append(index)
                # content=line.split('||')[1]
                # mame=line.split('||')[2]
                # print(index)
                # os.system("pause")
    except:
        print("finish")
        return index_array






def menu():
    while(True):
        choice=input("1. 输出提取的strings文件\n2. 提取输出文件中的neg部分\n3. 搜索neg部分在smali中对应的部分\n4. 退出\n5. 输出neg字符串到文件\n请输入编号: ")
        # print(choice)
        # os.system("pause")
        if(str(choice)=="1"):
            store_array=file_way_add_name()
            continue
        if(str(choice)=="2"):
            neg_array=extract_neg_index()
            continue
        if(str(choice)=="3"):
            print("not implement")
            continue
        if(str(choice)=="4"):
            exit()
        if(str(choice)=="5"):
            file_object=open(neg_str_path,"w",encoding="utf-8")
            for index in neg_array:
                file_object.write(str(store_array[int(index)-1].index)+"||"+str(store_array[int(index)-1].content)+"||"+store_array[int(index)-1].nameId+'\n')
            print("finish")
            file_object.close()
            continue
        




if __name__ == '__main__':
    explianation="""
    1. 复制jadx resources.arsc下res->values->strings.xml文件到txt中，修改本文件最开始的路径
    2. 修改文件开头的nlpir output文件夹下保存情感分析结果的文件路径
    3. 运行本文件，输入1，之后不要关闭运行中的本文件
    4. 运行nlpir进行情感分析
    5. 输入2
    6. 输入3
    7. 之后本文件将在neg_str_path路径下输出strings.xml中负面情感字符串
    """
    menu()




