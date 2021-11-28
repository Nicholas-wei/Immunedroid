from io import TextIOBase
import sys, getopt
import os
# 导入核心的三个模块
from androguard.core.bytecodes import apk
from androguard.core.bytecodes import dvm
from androguard.core.analysis import analysis
from androguard import misc
from androguard import session
from pathlib import Path

from emotionalAnalysis import eAnalysis




class strToolError(RuntimeError):
    def __init__(self, arg):
        self.args = arg

# 定义一个
class IstrAnalysis(analysis.StringAnalysis):    
    def __init__(self, Analysis):
        """
        IstrAnalysis是继承了StringAnalysis类

        包含了该字符串的 一些 免疫相关信息

        """
        # 使用父类初始化子类
        self.value = Analysis.value
        self.orig_value = Analysis.orig_value
        self.xreffrom = Analysis.xreffrom

        # 该字符串的消极程度
        self.NegScore = None  

        
        # 字符串语言语言类型
        self.text_language = None
        # 未使用下面的变量  后面可以添加
        # 翻译为英文的text
        self.text_to_en = None

        # 记录该字符串的来源
        self.fromArsc = False
    
    @classmethod
    def arscInit(cls,self):
        self.fromArsc = True
        pass






class StrTool:
    def __init__(self, apkfile):
        self.apkfile = apkfile
        self.a = apk.APK(self.apkfile)  # 获取APK文件对象
        self.d = dvm.DalvikVMFormat(self.a.get_dex())  # 获取DEX文件对象
        self.dx = analysis.Analysis(self.d)  # 获取分析结果对象


        self.dx.create_xref()  # 这里需要创建一下交叉引用        
        self.allStr = self.dx.get_strings() # 记录所以的字符串
        self.negDegree = 0.2   # 默认设置为0.75 负面范围0-1
        self.minLen = 4  # 最小的字符长度 小于这个长度就不对这个str进行处理


        self.allStr = []  #这里存储了所有的要分析的字符串
        self.negStr = []  #这里存储了所有的要消极的和免疫相关的字符串
        


    def strAnalysis(self):
        strings = self.dx.get_strings()
        for Str in strings:
            if len(Str.value) >= self.minLen:
                immuneStr = IstrAnalysis(Str)

                # 对该str进行情感分析
                eAnalysis.emotionalAnalysis(immuneStr)

                self.allStr.append(immuneStr)
                if immuneStr.NegScore < self.negDegree:
                    self.negStr.append(immuneStr)
    
    
        
    def output_calling_method(self, store_file_path=None):
        if not self.a:
            raise strToolError("Apk data not obtained")

        cnt = 1  # 输出计数

        # 输出到文件
        if store_file_path:
            with open(store_file_path+"output.txt", "w+",encoding='utf-8') as f:
                for i in self.negStr:
                    f.write("[%d]%s || %f" % (cnt, i.value, i.NegScore))
                    cnt += 1
                    for call in i.get_xref_from():
                        try:
                            f.write("\n\t"+str(call))
                        except:
                            raise strToolError("output_calling_method error")

                    f.write('\n\n')
        else:
            # 直接打印
            for i in self.negStr:
                print("[%d]%s || %f" % (cnt, i.value, i.NegScore))
                cnt += 1
                for call in i.get_xref_from():
                    try:
                        print("\t"+str(call))
                    except:
                        raise strToolError("output_calling_method error")
                print('\n')


if __name__ == '__main__':
    file_path = "D:\\workspace\\Immunedroid\\November\\b.apk"


    tool = StrTool(file_path)
    # 1. 对字符串提取
    tool.strAnalysis()



    # 2. 对字符串进行交叉引用


    # 3 对字符进行筛选  

    # 4. 向上遍历
    tool.output_calling_method()




