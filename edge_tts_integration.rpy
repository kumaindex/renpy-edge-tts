# -*- coding: utf-8 -*-
init python:
    # 在游戏开始时指定 Python 路径
    edge_tts.custom_python = r"D:\Program\Anaconda\python.exe"
    
init -2 python:
    import os
    import subprocess
    import hashlib
    import threading
    import sys

    class EdgeTTSManager(object):
        def __init__(self):
            self.enabled = True
            self.rate = "+0%"
            self.voice_map = {}
            self._lock = threading.Lock()

            self.cache_dir = os.path.join(
                renpy.config.gamedir, "tts_cache"
            )
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir)

            self.ignore = {None, "", "narrator", "null", "none"}
            self.use_pygame = False
            
            # 调试模式
            self.debug = True
            
            # 可选：指定自定义 Python 路径（留空则自动查找）
            # 例如: r"D:\Program\Anaconda\python.exe"
            self.custom_python = None

        def set_voice(self, char_name, voice):
            self.voice_map[char_name] = voice

        def set_rate(self, rate):
            self.rate = rate

        def _hash(self, text, voice):
            key = (text + voice + self.rate).encode("utf-8")
            return hashlib.md5(key).hexdigest() + ".mp3"

        def _play_audio(self, path):
            """
            使用 subprocess 启动独立 Python 进程播放音频
            """
            try:
                # 优先使用系统 Python，而不是 Ren'Py 的 Python
                # 如果设置了自定义 Python 路径，直接使用
                if self.custom_python:
                    python_exe = self.custom_python
                    if self.debug:
                        print(f"[TTS] 使用自定义 Python: {python_exe}")
                else:
                    # 自动查找可用的 Python
                    python_candidates = [
                        "python",      # Windows 通常用这个
                        "python3",     # Linux/Mac 通常用这个
                        sys.executable # 最后才用 Ren'Py 的
                    ]
                    
                    python_exe = None
                    for candidate in python_candidates:
                        try:
                            # 测试这个 Python 是否可用
                            test_result = subprocess.run(
                                [candidate, "--version"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=2
                            )
                            if test_result.returncode == 0:
                                python_exe = candidate
                                if self.debug:
                                    version_info = test_result.stdout.decode('utf-8', errors='ignore').strip()
                                    print(f"[TTS] 找到可用的 Python: {candidate} ({version_info})")
                                break
                        except:
                            continue
                    
                    if not python_exe:
                        print("[TTS 错误] 无法找到可用的 Python 解释器")
                        return
                
                # player_pygame.py 应该在 game 目录下
                player_script = os.path.join(
                    renpy.config.gamedir,
                    "player_pygame.py"
                )

                if self.debug:
                    print(f"[TTS] Python 路径: {python_exe}")
                    print(f"[TTS] 播放器脚本: {player_script}")
                    print(f"[TTS] 音频文件: {path}")
                    print(f"[TTS] 播放器存在: {os.path.exists(player_script)}")
                    print(f"[TTS] 音频文件存在: {os.path.exists(path)}")

                if not os.path.exists(player_script):
                    print(f"[TTS 错误] 播放器脚本不存在: {player_script}")
                    return

                if not os.path.exists(path):
                    print(f"[TTS 错误] 音频文件不存在: {path}")
                    return

                # 使用 CREATE_NO_WINDOW 标志（Windows）避免弹出控制台
                if sys.platform == "win32":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    
                    proc = subprocess.Popen(
                        [python_exe, player_script, path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        startupinfo=startupinfo,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    proc = subprocess.Popen(
                        [python_exe, player_script, path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )

                # 调试模式下等待进程结束并获取输出
                if self.debug:
                    stdout, stderr = proc.communicate(timeout=10)
                    if stdout:
                        print(f"[TTS 输出] {stdout.decode('utf-8', errors='ignore')}")
                    if stderr:
                        print(f"[TTS 错误] {stderr.decode('utf-8', errors='ignore')}")
                    print(f"[TTS] 返回码: {proc.returncode}")

            except subprocess.TimeoutExpired:
                print("[TTS] 播放超时")
                proc.kill()
            except Exception as e:
                print(f"[TTS] 子进程播放失败: {e}")
                import traceback
                traceback.print_exc()

        def _synthesize_and_play(self, text, char_name):
            if not self.enabled:
                return
            if char_name in self.ignore:
                return

            voice = self.voice_map.get(
                char_name,
                "zh-CN-XiaoxiaoNeural"
            )

            filename = self._hash(text, voice)
            path = os.path.join(self.cache_dir, filename)

            if self.debug:
                print(f"[TTS] 合成文本: {text[:50]}...")
                print(f"[TTS] 角色: {char_name}, 声音: {voice}")

            # 缓存不存在 → 合成
            if not os.path.exists(path):
                if self.debug:
                    print(f"[TTS] 缓存未命中，开始合成...")
                
                cmd = [
                    "edge-tts",
                    "--text", text,
                    "--voice", voice,
                    "--rate", self.rate,
                    "--write-media", path
                ]

                try:
                    result = subprocess.run(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        check=True,
                        timeout=30
                    )
                    if self.debug:
                        print(f"[TTS] 合成成功: {path}")
                except subprocess.TimeoutExpired:
                    print("[TTS] 合成超时")
                    return
                except Exception as e:
                    print(f"[TTS] 合成失败: {e}")
                    return
            else:
                if self.debug:
                    print(f"[TTS] 使用缓存: {path}")

            # 播放（子进程）
            self._play_audio(path)

        def speak(self, text, char_name):
            """
            入口：后台线程
            """
            t = threading.Thread(
                target=self._synthesize_and_play,
                args=(text, char_name)
            )
            t.daemon = True
            t.start()

    edge_tts = EdgeTTSManager()


# ------------------------------------------------------------------
# Hook renpy.say
# ------------------------------------------------------------------

init python:
    _original_say = renpy.say

    def _edge_tts_say(who, what, *args, **kwargs):
        char_name = None
        if who and hasattr(who, "name"):
            char_name = who.name

        if isinstance(what, str):
            edge_tts.speak(what, char_name)

        return _original_say(who, what, *args, **kwargs)

    renpy.say = _edge_tts_say