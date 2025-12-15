# -*- coding: utf-8 -*-
# player_pygame.py
# 放置在 game 目录下

import sys
import time
import os

def main():
    if len(sys.argv) < 2:
        print("[播放器] 错误: 未提供音频文件路径", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    
    print(f"[播放器] 接收到路径: {path}", file=sys.stderr)
    print(f"[播放器] 文件存在: {os.path.exists(path)}", file=sys.stderr)

    if not os.path.exists(path):
        print(f"[播放器] 错误: 文件不存在 {path}", file=sys.stderr)
        sys.exit(1)

    try:
        import pygame
        print("[播放器] pygame 导入成功", file=sys.stderr)
        
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        print("[播放器] mixer 初始化成功", file=sys.stderr)
        
        sound = pygame.mixer.Sound(path)
        print("[播放器] 音频加载成功", file=sys.stderr)
        
        channel = sound.play()
        print("[播放器] 开始播放", file=sys.stderr)

        # 等待播放完成
        while channel.get_busy():
            time.sleep(0.05)

        print("[播放器] 播放完成", file=sys.stderr)
        pygame.mixer.quit()
        sys.exit(0)

    except ImportError as e:
        print(f"[播放器] 错误: pygame 未安装 - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[播放器] 错误: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()