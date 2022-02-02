from pygtrans import Translate

client = Translate()

# 检测语言
text = client.detect('Answer the question.')
assert text.language == 'en'

# 翻译句子
text = client.translate('Look at these pictures and answer the questions.')
assert text.translatedText == '看这些图片，回答问题。'

# 批量翻译
texts = client.translate([
    'Good morning. What can I do for you?',
    'Read aloud and underline the sentences about booking a flight.',
    'May I have your name and telephone number?'
])
assert [text.translatedText for text in texts] == [
    '早上好。我能为你做什么？', 
    '大声朗读并在有关预订航班的句子下划线。', 
    '可以给我你的名字和电话号码吗？'
]

# 翻译到日语
text = client.translate('请多多指教', target='ja')
assert text.translatedText == 'お知らせ下さい'

# 翻译到韩语
text = client.translate('请多多指教', target='ko')
assert text.translatedText == '조언 부탁드립니다'

# 文本到语音
tts = client.tts('やめて', target='ja')
open('やめて.mp3', 'wb').write(tts)