import os
import re
# 导入核心的三个模块
from androguard.core.analysis import analysis
from androguard import session
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
    def __init__(self, apkfile,sess_path):
        self.apkfile = apkfile
        apk_session=None
        if os.path.exists(sess_path):               
            apk_session=session.Load(apk_sess_path)  
        self.a,self.d,self.dx=AnalyzeAPK(_file=apkfile,session=apk_session)
        if apk_session is None:
            session.Save(apk_session, sess_path)    # 使用session保存apk信息，提高多次访问效率
            
        
  
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
        
        pkg = self.a.get_package()     # 只输出该包名下的string
        locale = 'DEFAULT'             # 只输出默认语言的string
        strings = arscobj.get_resolved_strings()
        id_list=[s for s in strings[pkg][locale]]       # 存放name ID
        string_tags = arscobj.get_string_resources(pkg).decode().split('\n')
        index=0
        # contents=[tag for tag in arscobj.get_string_resources(pkg).decode().split('\n')]
        for tag in string_tags:
            match = re.search(r'>.*<',tag)
            if match:
                content = tag[match.span()[0]+1:match.span()[1]-1]
                if len(content) >= self.minLen:
                    immuneStrArs = IstrAnalysis()
                    immuneStrArs.arsc_str_id = id_list[index]
                    index+=1
                    immuneStrArs.value = content
                    self.allStr.append(immuneStrArs)

                
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
                
    def is_logical(self,EncodedMethod)->bool:
        for ins in EncodedMethod.get_instructions():
            if ins.get_name() in Conditionlist:
                return True
        return False    

# 首先判断是不是arsc字符串
# 1. arsc字符串 其xref一般为 弹窗调用函数，直接从其调用者中的bool函数或其本身条件逻辑出发
# 2. 一般字符串，其xref可能为按照下面的三种method进行
# !需要递归的情况(或者仅为一般弹窗函数):没有条件语句，此时需要向上递归


    def get_logical_method(self,file):
        f=open(file,"w+", encoding='utf-8')
        for immuneStr in self.filteredStr:
            logic_cnt = 0
            EncodedMethods=[]
            if immuneStr.fromArsc:
                EncodedMethods=immuneStr.xref_method
            else:
                EncodedMethods=[EncodedMethod for _, EncodedMethod in immuneStr.get_xref_from()]    
                
            for  EncodedMethod in EncodedMethods:
                # 查找弹窗函数的caller 调用的bool函数
                # 获得EncodedMethod对应的MethodAnalysis
                MethodAnalysis = self.dx.get_method_analysis(EncodedMethod)
                if MethodAnalysis.is_external():
                    continue
                for _, meth, _ in MethodAnalysis.get_xref_to():
                    if type(meth) == analysis.ExternalMethod:  # 不考虑外部函数
                        continue
                    info=meth.get_information()
                    if 'return' in info and info['return']=='boolean':
                        logic_cnt+=1
                        f.write("[%d]%s || %s\n" % (logic_cnt, immuneStr.value, meth.get_class_name()+meth.get_name()))
                if logic_cnt:                                      # 存在逻辑函数   小组对应的逻辑函数是小李
                    break
                else:
                    if self.is_logical(EncodedMethod):
                        logic_cnt+=1
                        f.write("[%d]%s || %s\n" % (logic_cnt, immuneStr.value, EncodedMethod.get_class_name()+EncodedMethod.get_name()))
                    else:                                           # 第三种情况，向上递归一次
                        m=MethodAnalysis
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
                                    logic_cnt+=1
                                    f.write("[%d]%s || %s\n" % (logic_cnt, immuneStr.value, meth.get_class_name()+meth.get_name()))
                            if not logic_cnt:                                
                                f.write("[%d]%s || %s\n" % (logic_cnt+1, immuneStr.value, EncodedMethod.get_class_name()+EncodedMethod.get_name()))        
        f.close()
# def get_logical_method(obj, dx, file):

#     # 对于method 类型的参数有几个情况：
#     #  1.单纯的弹窗函数，在该函数内没有什么有效判断逻辑,需要向上查找调用者函数  （向上递归）
#     #  2.作为一个调用者函数,包含了判断逻辑和调用弹窗函数的函数，可能存在免疫逻辑判断函数  （查找 bool类型的被调用者函数)
#     #  3.作为一个调用者函数，调用了弹窗函数, 自身存在逻辑判断条件，而非调用免疫逻辑判断函数 (查找有关的条件指令)
#     if type(obj) == analysis.MethodClassAnalysis or type(obj) == analysis.MethodAnalysis:
#         find_logic = 0                        # 用来表示是否找到了 相应的逻辑函数
#         if obj.is_external():               # 不考虑外部函数
#             return

#         # 向下查找 bool类型的被调用函数
#         for call, meth, _ in obj.get_xref_to():
#             if type(meth) == analysis.ExternalMethod:  # 不考虑外部函数
#                 continue
#             info = meth.get_information()
#             # 返回类型为bool 类型
#             if 'return' in info and info['return'] == 'boolean':
#                 find_logic = find_logic+1
#                 temp = obj.get_method()
#                 file.write(temp.get_class_name()+temp.get_name() +
#                            " ----calling---- "+meth.get_class_name()+meth.get_name()+"\n")

#         # 查找函数内部条件跳转指令
#         encode_meth = obj.get_method()
#         file.write(encode_meth.get_class_name() +
#                    encode_meth.get_name()+"  conditional mnemonic: \n")
#         for ins in encode_meth.get_instructions():
#             if ins.get_name() in Conditionlist:                  # 寻找条件语句
#                 find_logic = find_logic+1
#                 file.write(ins.get_name() + ins.get_output()+"\n")

#         # 向上查找 1次
#         if find_logic == 0:
#             for class_, call, _ in obj.get_xref_from():
#                 meth = class_.get_method_analysis(call)
#                 if type(meth) == analysis.MethodClassAnalysis or type(meth) == analysis.MethodAnalysis:
#                     get_logical_method(meth, dx, file)

#         return

#     if type(obj) == str:
#         try:
#             get_logical_method(dx.strings[obj], dx, file)
#         except KeyError as er:
#             print(er)
#             print('\n')

#     elif type(obj) == analysis.StringAnalysis:  # 字符串
#         for class_, call in obj.get_xref_from():            # 获取所有调用该字符串的函数，分析该函数
#             meth = class_.get_method_analysis(call)
#             if type(meth) == analysis.MethodClassAnalysis or type(meth) == analysis.MethodAnalysis:
#                 get_logical_method(meth, dx, file)


#     # 不是上面的类型,则出错
#     else:
#         print("Error argument,str or method argument is required!")
if __name__ == '__main__':
    file_path = "C:\\Users\\86157\\Desktop\\example\\"
    apk_full_name="b.apk"
    apk_name=os.path.splitext(apk_full_name)[0]
    apk_file_path=file_path+apk_name+"\\"
    if not os.path.exists(apk_file_path):
        os.mkdir(apk_file_path)
    apk_sess_path=apk_file_path+apk_name+".ag"
    
    tool = StrTool(apkfile=file_path+apk_full_name,sess_path=apk_sess_path)
    # 1. 对字符串提取
    tool.getStrings()

    # 2. 对字符串进行情感分析
    tool.strAnalysis()

    # 3. 对消极字符串进行交叉引用
    tool.negStrXref()

    # 4. 对检索出的消极字符串进行剔除
    tool.add_exception_list(file_path+"ThirdLibs.txt")  # 添加第三方库
    tool.stringsFilter()

    # 4.1输出消极字符串
    # 输出到指定文件夹
    tool.output_calling_method(apk_file_path)
    # 直接打印
    # tool.output_calling_method()

    # --------------------------------
    # -注：到第4完成，tool这个类中
    # -tool.filteredStr 里面存储了 最后过滤完的和免疫较为相关的字符串 的列表
    # -存储类型为 class IstrAnalysis 它继承于StringAnalysis
    # -可以直接调用get_xref_from()
    # -用法与androguard一致
    # --------------------------------

    # 5. 逻辑上查找免疫函数 并输出
    tool.get_logical_method(file=apk_file_path+"logical_method.txt")
    # decompiler = DecompilerJADX(tool.d, tool.dx,jadx="D:\\ctf_tool\\jadx-1.2.0\\bin\\jadx.bat")
    # tool.d.set_decompiler(decompiler)
    # tool.d.set_vmanalysis(tool.dx)

    # for immuneStr in tool.filteredStr:
    #     for c, EncodedMethod in immuneStr.get_xref_from():            # 获取所有调用该字符串的函数，分析该函数
    #         # meth = c.get_method_analysis(EncodedMethod)
    #         # print(immuneStr.value+":")
    #         print(EncodedMethod)
            # print(decompiler.get_source_method(EncodedMethod))
            # try:
            #     print(EncodedMethod.source())
            # except TypeError as error:
            #     print(error)
            # except AttributeError as e:
            #     print(e)
