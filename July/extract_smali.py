import re
import os
import sys
from lxml import etree


# 命令行形式 python3 extract_smali.py R_filepath  String_filepath Smali_filepath nameid_filepath


if __name__ == "__main__":
    # print("name:", sys.argv[0])
    len = len(sys.argv)
    if len <= 4:
        print("arguments error，filepath or function name is need !!!")
        exit(0)

    # jadx 生成的R.string对应的R.txt

    R_filepath = sys.argv[1]
    # R_filepath = "\home\qxz\xiyuan\ImmuneDroid_script\R.txt"
    # 这里填写保存文件jadx resources.arsc下res->values->strings.xml复制出来的txt文件的的绝对路径
    # String_filepath = "\home\qxz\xiyuan\ImmuneDroid_script\string.txt"
    String_filepath = sys.argv[2]
    # Smali_filepath = "\home\qxz\xiyuan\ImmuneDroid_script\smali"  # 使用apktool 处理apk得到的smali文件夹
    Smali_filepath = sys.argv[3]
    nameid_filepath = sys.argv[4]
    txt = open(R_filepath, "r").read()

    # nameId = "credit_one_rooted_device_error_message"

    nameIDarray = []
    with open(nameid_filepath, 'r', encoding='utf-8') as f:
        for line in f:
            # if line.find(sys.argv[2]) != -1:
            # print(line)
            nameIDarray.append(line)

    # print(len(nameIDarray))

    # 打开 string.txt 查找nameID对应的content

    file_object = open(String_filepath, "r", encoding="utf-8")
    try:

        # savedStdout = sys.stdout  #保存标准输出流
        # file=open('out.txt','w+')
        # sys.stdout = file  #标准输出重定向至文件
        # print ('This message is for file!')

        all_the_text = file_object.read()
        se = etree.HTML(bytes(bytearray(all_the_text, encoding="utf-8")))

        # array_length = len(nameIDarray)

        print("----")
        for nameId in nameIDarray:
            nameId = str(nameId).strip()
            # print("for"+nameId)
            # nameId = "credit_one_rooted_device_error_message"
            xpath_sent = '//string[@name=\"%s\"]/text()' % nameId
            content = se.xpath(xpath_sent)
            # print(content)
            content = ''.join(content)
            print("nameID:"+nameId)
            print("content:"+content)
            search_text = re.findall(nameId+" = \d+", txt)  # 取出每行含有nameID的文本
            # print(search_text)
            temp = ''.join(search_text)  # 取出[]
            result = re.sub("[A-Za-z=_ ]", "", temp)  # 只保留nameID对应的int字符串

            if result:
                dec_result = int(result)
                print("dec nameID:"+str(dec_result))
                hex_result = hex(dec_result)  # 得到最终对应的十六进制数，作为搜索的字符串
                result = str(hex_result)
                print("hex nameID:"+result)
                # print(result)
                # 依据 字符串 nameID nameID对应的十进制和十六进制搜索
                search_str = str(result+"|"+content+"|"+str(dec_result)+"|"+nameId)
                # print(search_str)
            else:
                 search_str = str(content+"|"+nameId)
            # os.system("grep -r "+result + " "+Smali_filepath +" >out.txt")  # 结果输出到out.txt中
            print("Search result:")
            os.system("grep -r -E \'"+search_str + "\' "+Smali_filepath)
            print("---")
    finally:
        file_object.close()
        # sys.stdout = savedStdout  #恢复标准输出流

    # os.system("strings -a -f "+Smali_filepath + "\| grep *.smali >out.txt")
