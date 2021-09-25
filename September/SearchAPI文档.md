# SearchAPI 说明文档

## 1.概要

直接利用androguard搜素到的api

下面罗列重要函数的用法，以及使用的一些重要函数的用法



## 2.使用的重要函数

### 2.1.find_methods()：

find_methods(classname=’.\*’*,* *methodname=’.\*’,* *descriptor=’.\*’,* accessflflags=’.\*’,no_external=False)：

该函数会找到指定的方法，方法的表示使用**正则表达式**

```python
    #源码 
    def find_methods(self, classname=".*", methodname=".*", descriptor=".*",
            accessflags=".*", no_external=False):
        """
        Find a method by name using regular expression.
        This method will return all MethodAnalysis objects, which match the
        classname, methodname, descriptor and accessflags of the method.
        :param classname: regular expression for the classname
        :param methodname: regular expression for the method name
        :param descriptor: regular expression for the descriptor
        :param accessflags: regular expression for the accessflags
        :param no_external: Remove external method from the output (default False)
        :rtype: Iterator[MethodAnalysis]
        """
        classname = bytes(mutf8.MUTF8String.from_str(classname))
        methodname = bytes(mutf8.MUTF8String.from_str(methodname))
        descriptor = bytes(mutf8.MUTF8String.from_str(descriptor))
        for cname, c in self.classes.items():
            if re.match(classname, cname):
                for m in c.get_methods():
                    z = m.get_method()
                    # TODO is it even possible that an internal class has
                    # external methods? Maybe we should check for ExternalClass
                    # instead...
                    if no_external and isinstance(z, ExternalMethod):
                        continue
                    if re.match(methodname, z.get_name()) and \
                       re.match(descriptor, z.get_descriptor()) and \
                       re.match(accessflags, z.get_access_flags_string()):
                        yield m
```

https://github.com/androguard/androguard/blob/master/androguard/core/analysis/analysis.py





## 3.发现奇怪的bug

bug描述：在ipython中可以找到大量的调用方法，但是一到了自己引用包就无法将所有的包找到，只能找到一个包，极有可能是我在python脚本编写的时候对包的使用不当



读源码：

在使用ipython的时候，cli使用的是如下方式启动reverse过程：

```python
  if filetype == 'APK':
        print("Loaded APK file...")
        a, d, dx = s.get_objects_apk(digest=h)
```

解决不了啊

先进git有机会再改