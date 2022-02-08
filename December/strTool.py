import os
import re
# 导入核心的三个模块
from androguard.core.analysis import analysis
from androguard.misc import AnalyzeAPK
from emotionalAnalysis import eAnalysis
class strToolError(RuntimeError):
    def __init__(self, arg):
        self.args = arg


# smali 代码中条件语句
Conditionlist = ['if-ne', 'if-eq', 'if-lt', 'if-le', 'if-gt',
                 'if-ge', 'if-eqz', 'if-nez', 'if-ltz', 'if-lez', 'if-gtz', 'if-gez']


# 定义一个字符串分析类型
class IstrAnalysis(analysis.StringAnalysis):
    def __init__(self, Analysis=None):
        """
        IstrAnalysis是继承了StringAnalysis类

        包含了该字符串的 一些 免疫相关信息

        """
        if Analysis:
            # 使用父类初始化子类
            self.value = Analysis.value
            self.orig_value = Analysis.orig_value
            self.xreffrom = Analysis.xreffrom
            # 记录该字符串的来源
            self.fromArsc = False
        else:
            self.value = None
            self.orig_value = None
            self.xreffrom = set()
            self.fromArsc = True

        self.arsc_str_id = None
        # 该字符串的消极程度
        self.NegScore = None

        # 字符串语言语言类型
        self.text_language = None
        # 未使用下面的变量  后面可以添加
        # 翻译为英文的text
        self.text_to_en = None
        
        # arsc字符串的调用函数
        self.xref_method=[]


class StrTool:
    def __init__(self, apkfile):
        self.apkfile = apkfile  
        self.a,self.d,self.dx=AnalyzeAPK(_file=apkfile)
        # self.a = apk.APK(self.apkfile)  # 获取APK文件对象
        # self.d = dvm.DalvikVMFormat(self.a.get_dex())  # 获取DEX文件对象
        # self.dx = analysis.Analysis(self.d)  # 获取分析结果对象

        # self.dx.create_xref()  # 这里需要创建一下交叉引用
        self.allStr = self.dx.get_strings()  # 记录所有的字符串
        self.negDegree = 0.20   # 默认设置为0.75 负面范围0-1
        self.minLen = 4  # 最小的字符长度 小于这个长度就不对这个str进行处理

        self.allStr = []  # 这里存储了所有的要分析的字符串
        self.negStr = []  # 这里存储了所有的要消极的和免疫相关的字符串
        self.filteredStr = []  # 这里存储最后过滤完的和免疫较为相关的字符串

        # 字符获取的黑白名单 黑名单上的会被 stringsFilter过滤 白名单中的会始终被保留
        # self.blackList = []
        self.blackList = ['encrypt', 'algorithm', 'decrypt', 'null', 'index out of range', 'Dead object',  'msg', 'info', 'invoke', 'call', 'open', 'close', 'resolve', 'bind', 'Google', 'Expected', 'registration', 'account',
                          'Account', 'View', 'view', 'message', 'cipher', 'Cipher', 'retrieving', 'color', 'Layout', 'layout', 'Shared Preferences', 'upload', 'object', 'URL', 'password', 'zero', 'empty', 'center', 'response']  # 移除了,'Failed','failed'
        self.whiteList = ['root', 'device', 'debug', 'exit', 'fatal',
                          'malicious', 'sorry', 'please', 'safe', '/su', 'security']
        self.exception_list = []

    def getStrings(self):
        # 获取一般的字符串
        strings = self.dx.get_strings()
        for Str in strings:
            if len(Str.value) >= self.minLen:
                immuneStr = IstrAnalysis(Str)
                self.allStr.append(immuneStr)

        # 获取ars字符串
        arscobj = self.a.get_android_resources()
        if not arscobj:
            print("Immunedroid: The APK does not contain a resources file!")
            return

        strings = arscobj.get_resolved_strings()
        for pkg in strings:
            if pkg == self.a.get_package():  # 只输出该包名下的string
                for locale in strings[pkg]:
                    if locale == 'DEFAULT':  # 只输出默认语言的string
                        for s in strings[pkg][locale]:
                            if len(strings[pkg][locale][s]) >= self.minLen:
                                immuneStrArs = IstrAnalysis()
                                immuneStrArs.arsc_str_id = s
                                immuneStrArs.value = strings[pkg][locale][s]
                                self.allStr.append(immuneStrArs)
        
        # pkg = self.a.get_package()     # 只输出该包名下的string
        # locale = 'DEFAULT'             # 只输出默认语言的string
        # strings = arscobj.get_resolved_strings()
        # id_list=[s for s in strings[pkg][locale]]       # 存放name ID
        # data=arscobj.get_string_resources(pkg)
        # doc = parseString(data)
        # collection = doc.documentElement.getElementsByTagName('string')
        # begin=id_list[0]
        # index=begin
        # for col in collection:
        #     if col.hasChildNodes():
        #         content = col.childNodes[0].data
        #         immuneStrArs = IstrAnalysis()
        #         immuneStrArs.arsc_str_id = index
        #         immuneStrArs.value = content
        #         if immuneStrArs.arsc_str_id==2131886648:
        #             print(immuneStrArs.value)
        #             os.system("pause")
        #         self.allStr.append(immuneStrArs)    
        #     index+=1        
        # for pkg in strings:
        #     if pkg == self.a.get_package():  # 只输出该包名下的string
        #         for locale in strings[pkg]:
        #             if locale == 'DEFAULT':  # 只输出默认语言的string
        #                 for s in strings[pkg][locale]:
        #                     if strings[pkg][locale][s]!=None:
        #                         content=strings[pkg][locale][s]
        #                     else:
                                
        #                         content    
        #                     if len(content) >= self.minLen:
        #                         immuneStrArs = IstrAnalysis()
        #                         immuneStrArs.arsc_str_id = s
        #                         immuneStrArs.value = strings[pkg][locale][s]
        #                         self.allStr.append(immuneStrArs)

    def strAnalysis(self):
        for immuneStr in self.allStr:
            # 对该str进行情感分析
            eAnalysis.emotionalAnalysis(immuneStr)

            if immuneStr.NegScore < self.negDegree or (immuneStr.fromArsc and self.whiteListFilter(immuneStr)):
                self.negStr.append(immuneStr)

    def create_xref(self, target):
        for immuneStr in target:
            if immuneStr.fromArsc:
                # 获得所有函数
                for method in self.dx.get_methods():
                    if method.is_external():
                        continue

                    # 获得 Return the `EncodedMethod` object that relates to this object
                    EncodedMethod = method.get_method()
                    for ins in EncodedMethod.get_instructions():
                        output = ins.get_name()+ins.get_output()
                        if str(immuneStr.arsc_str_id) in output:
                            immuneStr.xref_method.append(EncodedMethod)
           


    # 如果在白名单中则保留
    def whiteListFilter(self, immune_str):
        for i in self.whiteList:
            if i in str(immune_str.value):
                return True
        return False

    def negStrXref(self):
        # 只对消极字符串进行交叉引用
        # 这可以大大加快分析的速度
        self.create_xref(self.negStr)

    def stringsFilter(self):
        for immuneStr in self.negStr:

            # 如果在黑名单中就剔除
            def blackListFilter():
                for i in self.blackList:
                    if i in str(immuneStr.value):
                        return True
                return False

            # 如果是第三方库 也剔除

            def thirdLibsFilter():
                for _, meth in immuneStr.get_xref_from():
                    for i in self.exception_list:
                        # if type(meth) == analysis.MethodAnalysis:
                        #     meth = meth.get_method()
                        if i in str(meth.class_name):
                            return True
                return False

            if immuneStr.fromArsc:
                if not self.whiteListFilter(immuneStr) and blackListFilter():
                    continue
                
             # 剔除没有被引用的一般字符串    
            else:
                if not self.whiteListFilter(immuneStr) and (not immuneStr.get_xref_from() or blackListFilter() or thirdLibsFilter()):
                    continue

            self.filteredStr.append(immuneStr)

    def add_exception_list(self, path):

        with open(path, 'r') as f:
            thirdLibs = f.read().split('\n')

        for item in thirdLibs:
            item = item.replace('.', '/')
            self.exception_list.append(item)

    def output_calling_method(self, store_file_path=None):
        if not self.a:
            raise strToolError("Immunedroid: Apk data not obtained")

        cnt = 1  # 输出计数

        # 输出到文件
        if store_file_path:
            with open(store_file_path+"output_filter.txt", "w+", encoding='utf-8') as f:
                for i in self.filteredStr:
                    f.write("[%d]%s || %f" % (cnt, i.value, i.NegScore))
                    cnt += 1
                    if i.fromArsc:
                        f.write("\n--fromArsc--")
                        for meth in i.xref_method:
                            f.write("\n\t"+str(meth))
                    else:        
                        for call in i.get_xref_from():
                            try:
                                f.write("\n\t"+str(call))
                            except:
                                raise strToolError("output_calling_method error")

                    f.write('\n\n')
        else:
            # 直接打印
            for i in self.filteredStr:
                print("[%d]%s || %f" % (cnt, i.value, i.NegScore))
                cnt += 1
                if i.fromArsc:
                    print("--fromArsc--")
                    for meth in i.xref_method:
                            print("\n\t"+str(meth))
                else:            
                    for call in i.get_xref_from():
                        try:
                            print("\t"+str(call))
                        except:
                            raise strToolError("output_calling_method error")
                print('\n')
   

# 首先判断是不是arsc字符串
# 1. arsc字符串 其xref一般为 弹窗调用函数，直接从其调用者中的bool函数或其本身条件逻辑出发
# 2. 一般字符串，其xref可能为按照下面的三种method进行
# !需要递归的情况(或者仅为一般弹窗函数):没有条件语句，此时需要向上递归

# 退休函数:)
    # def get_logical_method(self,file):
    #     f=open(file,"w+", encoding='utf-8')
    #     for immuneStr in self.filteredStr:
    #         logic_cnt = 0
    #         EncodedMethods=[]
    #         if immuneStr.fromArsc:
    #             EncodedMethods=immuneStr.xref_method
    #         else:
    #             EncodedMethods=[EncodedMethod for _, EncodedMethod in immuneStr.get_xref_from()]    
                
    #         for  EncodedMethod in EncodedMethods:
    #             # 查找弹窗函数的caller 调用的bool函数
    #             # 获得EncodedMethod对应的MethodAnalysis
    #             MethodAnalysis = self.dx.get_method_analysis(EncodedMethod)
    #             if MethodAnalysis.is_external():
    #                 continue
    #             for _, meth, _ in MethodAnalysis.get_xref_to():
    #                 if type(meth) == analysis.ExternalMethod:  # 不考虑外部函数
    #                     continue
    #                 info=meth.get_information()
    #                 if 'return' in info and info['return']=='boolean':
    #                     logic_cnt+=1
    #                     f.write("[%d]%s || %s\n" % (logic_cnt, immuneStr.value, meth.get_class_name()+meth.get_name()))
    #             if logic_cnt:                                      # 存在逻辑函数   小组对应的逻辑函数是小李
    #                 break
    #             else:
    #                 if self.is_logical(EncodedMethod):
    #                     logic_cnt+=1
    #                     f.write("[%d]%s || %s\n" % (logic_cnt, immuneStr.value, EncodedMethod.get_class_name()+EncodedMethod.get_name()))
    #                 else:                                           # 第三种情况，向上递归一次
    #                     m=MethodAnalysis
    #                     for class_,call,_ in m.get_xref_from():
    #                         MethodAnalysis=class_.get_method_analysis(call)
    #                         EncodedMethod=MethodAnalysis.get_method()
    #                         if MethodAnalysis.is_external():
    #                             continue
    #                         for _,meth,_ in MethodAnalysis.get_xref_to():
    #                             if type(meth) == analysis.ExternalMethod:  # 不考虑外部函数
    #                                 continue
    #                             info=meth.get_information()
    #                             if 'return' in info and info['return']=='boolean':
    #                                 logic_cnt+=1
    #                                 f.write("[%d]%s || %s\n" % (logic_cnt, immuneStr.value, meth.get_class_name()+meth.get_name()))
    #                         if not logic_cnt:                                
    #                             f.write("[%d]%s || %s\n" % (logic_cnt+1, immuneStr.value, EncodedMethod.get_class_name()+EncodedMethod.get_name()))        
    #     f.close()


# get_logical 辅助函数

# 1. res->logic ? 判断结果是否为表达式或者函数
    def is_logic(self,string):
        if string:
            p_pattern=re.compile(r'[><=!()|&+-/%*^~?:]')      # 匹配表达式和函数
            match=p_pattern.findall(string)                   # 查找匹配
            if match:
                return True
        return False

# 2. logic->up? 判断是否仅包含p0,p1等的参数                                            
    def is_para(self,string):
        if string:
            p_pattern=re.compile(r'p\d+')                     # 匹配 p0,p1...等参数
            match=p_pattern.findall(string)                   # 查找匹配
            if match:
                return (True,match[0])
        return (False,None)


# 3. 判断是否为本地变量
    def is_local(self,string):
        if string:
            v_pattern=re.compile(r'v\d+_\d+|v\d+')            # 匹配 v0,v1,v0_0..等局部参数
            match=v_pattern.findall(string)                   # 查找匹配
            if match:
                return (True,match[0])
        return (False,None)    
        
# 4. 本地变量左值表达式
    def get_local_value(self,name,text,pos):
        n_pattern=re.compile(r'%s =.*\n'%name)                # 匹配 v0_0=xxxx                    
        match=n_pattern.findall(text,0,pos)                   # 查找匹配
        if match:
            return match[-1][:-1]                             # 返回最接近v的匹配
        return None


# 5.判断函数是否存在跳转指令            
    def has_jump_instruction(self,EncodedMethod)->bool:
        for ins in EncodedMethod.get_instructions():
            if ins.get_name() in Conditionlist:
                return True
        return False 
    
# 6.递归情形进行近似匹配,参考get_locai_method实现,返回匹配到的可能函数名
    def approximate_match(self,method):
        # 查找弹窗函数的caller 调用的bool函数
        # 获得EncodedMethod对应的MethodAnalysis
        res=[]                                         # 返回 classname+methodname的list
        MethodAnalysis = self.dx.get_method_analysis(method)                 
        if MethodAnalysis.is_external():
            return None
        for _, meth, _ in MethodAnalysis.get_xref_to():        
            if type(meth) == analysis.ExternalMethod:  # 不考虑外部函数
                continue    
            info=meth.get_information()
            if 'return' in info and info['return']=='boolean':
                res.append(meth.get_class_name()+meth.get_name())
        if len(res):                                   # 存在即返回
            return res    
        if self.has_jump_instruction(method):          # 存在跳转指令则返回当前返回
            res.append(method.get_class_name()+method.get_name())    
            return res    
        m=MethodAnalysis                               # 最多递归一层
        for class_,call,_ in m.get_xref_from():
            MethodAnalysis=class_.get_method_analysis(call)
            EncodedMethod=MethodAnalysis.get_method()
            if MethodAnalysis.is_external():
                continue
            for _,meth,_ in MethodAnalysis.get_xref_to():
                if type(meth) == analysis.ExternalMethod:  # 不考虑外部函数
                    continue
                info=meth.get_information()
                if 'return' in info and info['return']=='boolean':
                    res.append(meth.get_class_name()+meth.get_name())
            if not len(res):
                res.append(EncodedMethod.get_class_name()+EncodedMethod.get_name())                                
        return res if len(res) else None

# get_logical 
    def get_logical(self,file):
        f=open(file,"w+", encoding='utf-8')
# 1. 从string->method,寻找调用 method            
        for immuneStr in self.filteredStr:
            logic_cnt=0                                        # 匹配到逻辑语句的次数
            # max_depth=2                                      # 最大递归层数
            # depth=0                                          # 当前递归层数
            EncodedMethods=[]
            
            if immuneStr.fromArsc:
                EncodedMethods=immuneStr.xref_method
            else:
                EncodedMethods=[EncodedMethod for _, EncodedMethod in immuneStr.get_xref_from()] 
# 2. 从method-> method.source
    # for  EncodedMethod in EncodedMethods:
    #     try:
    #         file.write(EncodedMethod.get_source())
    #     except (TypeError,AttributeError):
    #         continue
    #     something todo
            str_tag=str(immuneStr.arsc_str_id) if immuneStr.fromArsc else immuneStr.value # 匹配字符串标识
            for EncodedMethod in EncodedMethods:
                res=None                                           # 匹配结果
                try:
                    source=EncodedMethod.get_source()
                except (TypeError,AttributeError):
                    continue            
# 3. method.source->condition  匹配字符串标识
                
                try:
                    str_patten=re.compile(r""+str_tag,re.S | re.M) # 正则表达式诡异的括号匹配错误
                except re.error:
                    # print(str_tag)
                    break     
                str_match=str_patten.search(source)
                if str_match is None:                             # 一些稀奇古怪的字符串在转义过程中转义字符消失导致的不匹配,忽略掉 
                    # print(source)
                    # print(repr(r""+str_tag))
                    continue    
                search_end=str_match.start()                      # 从字符串调用位置倒序匹配
                search_begin=0 if search_end < 88 else search_end-88
                if_pattern = re.compile(r'if [(].*[)] {')               # 匹配 if,else if...
                while search_end:
                    if_match=if_pattern.findall(source,search_begin,search_end)
                    if len(if_match):
                        res=if_match[-1][0:-2]                    # 匹配最接近 字符串的if语句，并去掉括号
                        break
                    temp=search_begin
                    search_begin=0 if search_end < 88 else search_end-88
                    search_end=temp
# 4. 根据res结果进行处理
                if res and self.is_logic(res):                         # 匹配到表达式或者函数                                                                          
                    f.write("[%d]%s || %s-->logic:\t%s\n" % (logic_cnt, immuneStr.value, EncodedMethod.get_class_name()+EncodedMethod.get_name(),res))
                    logic_cnt+=1 
                elif res and self.is_local(res)[0]:                    # 匹配到局部寄存器 if(v0)....类似的语句
                    name=self.is_local(res)[1]
                    value=self.get_local_value(name,source,search_end)
                    if value:
                        f.write("[%d]%s || %s-->logic:\t%s\n" % (logic_cnt, immuneStr.value, EncodedMethod.get_class_name()+EncodedMethod.get_name(),name+"-->"+value))
                        logic_cnt+=1 
                else:                                                  # 匹配结果为空或者存在参数传递，使用get_logical_method近似匹配
                    method=self.dx.get_method_analysis(EncodedMethod)  # 获取 EncodedMethod对应的MethodclassAnalysis 
                    for class_,call,_ in method.get_xref_from():       # 寻找当前函数的caller
                        MethodAnalysis=class_.get_method_analysis(call)
                        EncodedMethod=MethodAnalysis.get_method()
                        result=self.approximate_match(EncodedMethod)   # 对 caller函数进行近似匹配  
                        if result:
                            for res in result:
                                f.write("[%d]%s || approximate match-->logic:\t%s\n" % (logic_cnt, immuneStr.value,res))
                                logic_cnt+=1
        f.close()        
                        
if __name__ == '__main__':
    file_path = "C:/Users/86157/Desktop/example/"
    apk_full_name="a.apk"
    apk_name=os.path.splitext(apk_full_name)[0]
    apk_file_path=file_path+apk_name+"/"
    if not os.path.exists(apk_file_path):
        os.mkdir(apk_file_path)
    
    tool = StrTool(file_path+apk_full_name)
    # 1. 对字符串提取
    tool.getStrings()
    print("get strings finish")
    # 2. 对字符串进行情感分析
    tool.strAnalysis()
    print("emotion analyze finish")
    # 3. 对消极字符串进行交叉引用
    tool.negStrXref()
    print("get xref finish")
    # 4. 对检索出的消极字符串进行剔除
    tool.add_exception_list(file_path+"ThirdLibs.txt")  # 添加第三方库
    tool.stringsFilter()
    print("filter string finish")
    # 4.1输出消极字符串
    # 输出到指定文件夹
    tool.output_calling_method(file_path)
    print("output finish")
    # 直接打印
    # tool.output_calling_method()

    # --------------------------------
    # -注：到第4完成，tool这个类中
    # -tool.filteredStr 里面存储了 最后过滤完的和免疫较为相关的字符串 的列表
    # -存储类型为 class IstrAnalysis 它继承于StringAnalysis
    # -可以直接调用get_xref_from()
    # -用法与androguard一致
    # --------------------------------

    # 5. 查找免疫逻辑语句或函数并输出到文件
    tool.get_logical(file=apk_file_path+"logical_method.txt")
   