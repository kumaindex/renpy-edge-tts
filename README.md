文件目录
------------------
player_pygame.py

放置在 game 目录下
需要安装依赖，pygame
----------------------
edge_tts_integration.rpy

放置在 game 目录下
需要安装依赖 edge_tts
开头的代码需要改为系统python3的目录
    # 在游戏开始时指定 Python 路径
    edge_tts.custom_python = r"D:\Program\Anaconda\python.exe"
----------------------
忽略语音的角色

{None, "", "narrator", "null", "none"}的角色不能进行语音
----------------------
备注你的python目录

renpy的 script文件需要开头注明
define e = Character("你的角色，如Nao")
init python:
    # 配置语音
    edge_tts.set_voice("Nao", "zh-CN-XiaoxiaoNeural")
    # 默认启用
    edge_tts.enabled = True
----------------------

tts的使用
使用以下代码进行更改速度
edge_tts.set_rate("+50%")
----------------------

语音开关
在label start:之后可以通过以下代码来开关语音
$ edge_tts.enabled = False
e "语音已关闭（这句话不会播放）"
$ edge_tts.enabled = True
