import re
import html
from urllib import parse
import requests
# 注意：不能保证有效，时不时抽风翻译不了，翻译效率极低
# 用法 翻译为英语的字符串 = translate("要翻译的字符串"）


GOOGLE_TRANSLATE_URL = 'http://translate.google.cn/m?q=%s&tl=%s&sl=%s'

def translate(text, to_language="en", text_language="auto"):

    text = parse.quote(text)
    url = GOOGLE_TRANSLATE_URL % (text,to_language,text_language)
    response = requests.get(url)
    data = response.text
    expr = r'(?s)class="(?:t0|result-container)">(.*?)<'
    result = re.findall(expr, data)
    if (len(result) == 0):
        return ""

    return html.unescape(result[0])

# Text0 = ", ".join(whiteList)
# print(Text0)

# print(translate(Text0,"zh-CN").split(', ')) #汉语转英语
# print(translate("食事はしましたか？", "en",)) #汉语转日语
# print(translate("关于你的情况", "en",)) #英语转汉语