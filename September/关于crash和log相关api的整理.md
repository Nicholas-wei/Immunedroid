# 关于crash和log相关api的整理
## crash
### 简介
所谓crash(崩溃日志)就是Java或者native代码发生的异常
关于Java代码的crash的类型可以分为两类
- 检查异常(Checked Exception):导致代码无法通过编译的异常。需要强制加上try...catch或者throw。此类异常一般不会引起crash
- 非检查异常(unChecked Exception):编译过程中不会出现，运行期间可能出现。由于该异常没有对应的处理方式，Java环境将被终止(crash)。
### 处理api
对于可以使用`try...catch`处理的异常(Checked Exception)，程序会调用自身处理函数。
对于无法被catch的异常(unChecked Exception)，可以使用以下api
- public abstract void uncaughtException (Thread thread, Throwableex)
> Uncaught异常发生时会终止线程，此时，系统便会通知UncaughtExceptionHandler，告诉它==被终止的线程==以及==对应的异常==，然后便会调用uncaughtException函数。如果该handler没有被显式设置，则会调用对应线程组的默认handler。如果我们要捕获该异常，必须实现我们自己的handler
其中handle exception部分包含了输出错误信息，收集设备参数，保存日志文件的代码
- demo: handle exception
```java=
    private boolean handleException(Throwable ex) {
        if (ex == null) {
            return false;
        }
        //使用Toast来显示异常信息
        new Thread() {
            @Override
            public void run() {
                Looper.prepare();//准备发消息的MessageQueue
                Toast.makeText(mContext, "很抱歉,程序出现异常,即将退出.", Toast.LENGTH_LONG).show();
                Looper.loop();
            }
        }.start();
        //收集设备参数信息
        collectDeviceInfo(mContext);
        //保存日志文件
        saveCrashInfo2File(ex);
        return true;
    }
```
- demo:collectDeviceInfo
```java=
    public void collectDeviceInfo(Context ctx) {
        try {
            PackageManager pm = ctx.getPackageManager();
            PackageInfo pi = pm.getPackageInfo(ctx.getPackageName(), PackageManager.GET_ACTIVITIES);
            if (pi != null) {
                String versionName = pi.versionName == null ? "null" : pi.versionName;
                String versionCode = pi.versionCode + "";
                infos.put("versionName", versionName);
                infos.put("versionCode", versionCode);
            }
        } catch (PackageManager.NameNotFoundException e) {
            Log.e(TAG, "an error occured when collect package info", e);
        }
        Field[] fields = Build.class.getDeclaredFields();
        for (Field field : fields) {
            try {
                field.setAccessible(true);
                infos.put(field.getName(), field.get(null).toString());
                Log.d(TAG, field.getName() + " : " + field.get(null));
            } catch (Exception e) {
                Log.e(TAG, "an error occured when collect crash info", e);
            }
        }
    
```
> 思考：==是否可以读取到这里的设备信息==？网上的信息处理demo中包含了versionName和versionCode，getPackageName部分,或许可以用来==在发送错误信息报告时抓包泄露信息==


> 思考：try...catch出现的异常可以被用户定义。我们寻找免疫机制时有了新的方向==从自定义异常机制入手==这样的好处是可以看看apk中主要对那些异常做了自定义检测，可能是免疫机制
- 自定义异常机制demo
```java=
public class GendorException extends Exception {
    public GendorException(String msg)
    {
        super(msg);
    }
}
```
较为全面的官方定义java异常类型
https://wenku.baidu.com/view/d56b40cba45177232f60a2e6.html
着重关注几个
- `CertificationException`指示各类证书问题
- `GeneralSecurityException`关注这个异常的拓展类(extend)大多和安全问题相关
- `IllegalAccessException`没有访问权限
### native
native的暂时不涉及



## log
### log等级划分
- Log.v("Tag","Msg");//Verbose  观察值，Verbose是冗长、啰嗦的意思，任何消息都会输出
- Log.d("Tag","Msg");//Debug  调试
- Log.i("Tag","Msg");//Info  信息，为一般提示性的消息
- Log.w("Tag","Msg");//Warn  可能会出问题，一般用于系统提示开发者需要优化android代码等场景
- Log.e("Tag","Msg");//Error  崩溃信息，一般用于输出异常和报错信息
### log使用规范
1. 在app中一般不允许使用verbose级别的log。对于info,warn级别的log，允许极少量打印重要信息。
2. log.e只有在出现严重错误时才会使用，例如系统的`fatal error`
### 思考
> log信息显然是用来面向开发者的。但是有些app会在免疫条件触发时直接退出，没有给用户提示信息。此时log就起到了关键作用：可以用来标识退出原因，辅助验证免疫是否被激活。

