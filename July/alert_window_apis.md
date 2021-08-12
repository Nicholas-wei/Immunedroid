# 关于弹窗方式的调查

## dialog弹窗

特征：显示位置固定（比较适合免疫警告的形式）
最基本的是alert-diaglog，内容存放在setMessage()中

- 只有标题和内容

```java
AlertDialog alertDialog1 = new AlertDialog.Builder(this)
        .setTitle("这是标题")//标题
        .setMessage("这是内容")//内容
        .setIcon(R.mipmap.ic_launcher)//图标
        .create();
alertDialog1.show();
```

- 选项

```java
new AlertDialog.Builder(this).setMultiChoiceItems //创建多选框
new AlertDialog.Builder(this).setPositiveButton //设置按钮

```

- 寻找方式

1. 根据参数类型：一般的弹窗有标题和内容，注意出现两个字符串的语句，可能是弹窗
2. Alertdiaglog接口较多，一个实例下初始化多个内容并包含字符串的可能是弹窗

## Activity 伪弹窗

这种弹窗方式的特征是在资源文件下存放了弹窗相关的信息，在layout和xml文件中存放了弹窗的相关属性：位置，大小等。这种弹窗的文本信息需要先找到弹窗位置之后再到resources文件中寻找。

- 调用举例

```java
Intent intent = new Intent(context, MainWeixinTitleRightActivity.class);
startActivity(intent);
```

## PopupWindow弹窗

展示view的弹出窗体，这个弹出窗体将会浮动在当前activity的最上层，这个和免疫相关的弹窗机制十分类似,输出的内容一般存放在contentview变量中

- 调用举例

```java
TestPopupWindow mWindow = new TestPopupWindow(this);
PopupWindowCompat.showAsDropDown(mWindow, mButtom, 0, 0, Gravity.START);
```

- 检测方法

1. 这种方法的特征是弹窗前会先检测之前设置的contentview的大小,因此除了搜索方法之外，还可以搜索window.getContextView附近的语句来筛选一部分。
2. 由于没有显式字符串参数，需要在resources文件中寻找

```java
int offsetX = window.getContentView().getMeasuredWidth();
int offsetY = 0;
PopupWindowCompat.showAsDropDown(window, mButton, offsetX, offsetY, Gravity.START);
```

## Fragment弹窗

DiaglogFragment是一个类，对类中成员赋值之后就可以设置弹窗内容，背景等

```java
public class LoginDailog extends DialogFragment implements View.OnClickListener {
 
    public static final String USERNAME = "userName";
    public static final String USERPASSWORD = "userPassword";
    ····

```

## 警示弹窗ALertView