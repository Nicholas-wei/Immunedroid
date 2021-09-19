# SearchString 说明文档

## 1.概要

直接利用androguard搜素到的字符串，使用TextBlob包，对找到的字符串进行情感分析，并且输出找到的字符对应的引用位置。

androguard GitHub地址:https://github.com/androguard/androguard

下面罗列重要函数的用法，以及使用的一些重要函数的用法



## 2.使用的重要函数

### 2.1.dx.get_strings()

androguard提供的get_strings() 的字符串来源有待分析，看源码去:

```python
	#源码
	def get_strings(self):
        """
        Returns a list of :class:`StringAnalysis` objects
        :rtype: Iterator[StringAnalysis]
        """
        return self.strings.values()
```



在 create_xref()中对strings进行添加，通过源码可以发现，androguard中的get_strings() 只能找到代码中的字符串，放在**资源文件**中的字符串就无法找到。可以这部分需要编写其他代码。

```python
 	#源码
  # 3) check for string usage: const-string (0x1a), const-string/jumbo (0x1b)
    elif 0x1a <= op_value <= 0x1b:
        string_value = instruction.cm.vm.get_cm_string(instruction.get_ref_kind())
        if string_value not in self.strings:
            self.strings[string_value] = StringAnalysis(string_value)

            self.strings[string_value].add_xref_from(cur_cls, cur_meth, off)
```



### 2.2.textblob

TextBlob 是一个用于处理文本数据的 Python（2 和 3）库。 它提供了一个简单的 API，用于深入研究常见的自然语言处理 (NLP) 任务，例如词性标注、名词短语提取、情感分析、分类、翻译等。

这里使用textblob进行对输出的字符串进行情感分析。

快速指南：https://textblob.readthedocs.io/en/latest/quickstart.html#quickstart



### 2.3.get_android_resources(self):

对安卓资源文件解析

```python
    #源码
    def get_android_resources(self):
        """
        Return the :class:`~androguard.core.bytecodes.axml.ARSCParser` object which corresponds to the resources.arsc file
        :rtype: :class:`~androguard.core.bytecodes.axml.ARSCParser`
        """
        try:
            return self.arsc["resources.arsc"]
        except KeyError:
            if "resources.arsc" not in self.zip.namelist():
                # There is a rare case, that no resource file is supplied.
                # Maybe it was added manually, thus we check here
                return None
            self.arsc["resources.arsc"] = ARSCParser(self.zip.read("resources.arsc"))
            return self.arsc["resources.arsc"]
```





## 3.SearchString中重要函数

### 3.1.get_androguard_obj(apkfile):

输出所有字符串用textblob分析后的情感评分，正为积极，负数为消极，并且输出调用该字符串的方法

输出示例：

```txt
[116]Failed to log throwable. || -0.500000
	(<analysis.ClassAnalysis Lbo/app/n1$b;>, <analysis.MethodAnalysis Lbo/app/n1$b;->a()V [access_flags=public final] @ 0x2948b8>)
	(<analysis.ClassAnalysis Lbo/app/w0;>, <analysis.MethodAnalysis Lbo/app/w0;->uncaughtException(Ljava/lang/Thread; Ljava/lang/Throwable;)V [access_flags=public] @ 0x29cf88>)
	(<analysis.ClassAnalysis Lbo/app/s3;>, <analysis.MethodAnalysis Lbo/app/s3;->a(Lbo/app/z; Ljava/lang/Throwable;)V [access_flags=public static] @ 0x29ac1c>)
	(<analysis.ClassAnalysis Lbo/app/p;>, <analysis.MethodAnalysis Lbo/app/p;->a(Lbo/app/z; Ljava/lang/Throwable;)V [access_flags=public final] @ 0x2987e0>)
	(<analysis.ClassAnalysis Lbo/app/t3;>, <analysis.MethodAnalysis Lbo/app/t3;->a(Lbo/app/z; Ljava/lang/Throwable;)V [access_flags=public] @ 0x29b7c4>)

```

### 3.2.output_calling_method_neg(strs)：

输出单词数大于4且判断为消极的strings，包含中文

### 3.3.output_calling_method_pos(strs)：

输出单词数大于4且判断为积极的strings



### 3.4.output_arsc_strings(a):

输出资源文件中的string.xml的string和其对应的id

只输出默认语言的strings.xml文件 

输出示例：

```txt
com.telkom.mwallet:
2131886080	here
2131886081	seconds
2131886082	About
2131886083	Activate Now
2131886084	Add
2131886085	Add Payment Method
```

注：左边为string的id 右边为string



### 3.5.get_androguard_obj(apkfile):

实现对apk的解析

### 3.6 output_arsc_strings(str):
接收asrc字符串，在main中实现搜索调用（由于androguard没有完成在asrc中的输出调用函数功能，我们使用的是在smali文件中全局搜索ID并输出位置，能够成功）



