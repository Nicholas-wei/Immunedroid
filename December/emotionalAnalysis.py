from textblob import TextBlob
from snownlp import SnowNLP


class eAnalysis:
    #----------------------------------------------------------------------
    # -注意下面这2个函数处理该字符串的情感
    # -目前能做的就是处理 区分是不是英语 其他默认
    # -如果需要调用Google翻译也应该在这里调用

    def language_category(strClass):
        #检验是否全是中文字符
        for _char in strClass.value:
            if not '\u4e00' <= str(_char) <= '\u9fa5':
                # 由于翻译器的原因 目前被迫这样设置
                return

        strClass.text_language = 'zh-CN'

    def emotionalAnalysis(strClass):
        # 定义情感范围 0-1  0为最消极 1为最积极
        # 可以在这里跟换 情感分析的方法
        # 如果没有设置语言类型 先设置
        if not strClass.text_language:
            eAnalysis.language_category(strClass)

        text = str(strClass.value)

        if strClass.text_language == 'zh-CN':
            snow=SnowNLP(text)
            strClass.NegScore =snow.sentiments

        else:            
            blob = TextBlob(text)
            strClass.NegScore = (blob.sentiment.polarity+1)/2
    
    # -注意上面这2个函数处理该字符串的情感
    # -目前能做的就是处理 区分是不是英语 其他默认
    #------------------------------------------------------------------------   