# coding=utf-8
from aip import AipSpeech
 
# 使用时请将下面的内容替换为你自己的
APP_ID = '16611347'
API_KEY = 'xdRf2oVufYtgcQLYZ0IlBfFo'
SECRET_KEY = '8tfPC1FyEauGw0TIQzXi862LIiloGWmt'
#APP_ID = '22592596'
#API_KEY = 'sAUe2Y8g90kv8uzq7iVQw5Ry'
#SECRET_KEY = 'Dtw5XW7SohBvKsna467cHmMxLBXjeBXa'
# 初始化
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
 
 
def text2sound(words='你好'):
    # 语音合成函数，传入欲合成的内容，返回成功与否，若成功默认将文件保存为'test.wav'
    result = client.synthesis(words, 'zh', 1, {
        'vol': 5, 'aue': 6, 'per': 4
    })  # 具体的参数设置请参考官方文档
 
    if not isinstance(result, dict):
        with open('temp.wav', 'wb') as f:
            f.write(result)
        return True
    else:
        return False
 
 
def sound2text(file_path='temp.wav'):
    # 语音识别函数，传入文件名（默认为'test.wav'），返回识别结果或错误代码
    with open(file_path, 'rb') as fp:
        recog = client.asr(fp.read(), 'wav', 16000, {'dev_pid': 1537})  # 参数设置见文档
        if recog['err_no'] not in [0, 3301]:
            return False, recog['err_no']
        elif recog['err_no'] == 3301:
            return True, ''
        return True, recog['result'][0]
 
 

# the followings are used to debug
# text2sound('语音合成出错')
# result = sound2text()
# print(result)

'''
错误码 用户输入/服务端    含义  一般解决方法
3300    用户输入错误  输入参数不正确 请仔细核对文档及参照demo，核对输入参数
3301    用户输入错误  音频质量过差  请上传清晰的音频
3302    用户输入错误  鉴权失败    token字段校验失败。请用appkey 和 app secret生成
3303    原始音频或者服务端问题 转pcm失败  如下2个原因 1. wav amr音频转码失败，即音频有问题。2. 服务端问题，请将api返回结果反馈至论坛或者QQ群
3304    用户请求超限  用户的请求QPS超限  请降低识别api请求频率 （qps以appId计算，移动端如果共用则累计）
3305    用户请求超限  用户的日pv（日请求量）超限  请“申请提高配额”，如果暂未通过，请降低日请求量
3307    服务端问题   语音服务器后端识别出错问题   请将api返回结果反馈至论坛或者QQ群
3308    用户输入错误  音频过长    音频时长不超过60s，请将音频时长截取为60s以下
3309    用户输入错误  音频数据问题  服务端无法将音频转为pcm格式，可能是长度问题，音频格式问题等。 请将输入的音频时长截取为60s以下，并核对下音频的编码，是否是8K或者16K， 16bits，单声道。
3310    用户输入错误  输入的音频文件过大   语音文件共有3种输入方式： json 里的speech 参数（base64后）； 直接post 二进制数据，及callback参数里url。 分别对应三种情况：json超过10M；直接post的语音文件超过10M；callback里回调url的音频文件超过10M
3311    用户输入错误  采样率rate参数不在选项里  目前rate参数仅提供8000,16000两种，填写4000即会有此错误
3312    用户输入错误  音频格式format参数不在选项里   目前格式仅仅支持pcm，wav或amr，如填写mp3即会有此错误
'''


# 调用示例
#text2sound('Im here!')
#sound2text('temp.wav')
