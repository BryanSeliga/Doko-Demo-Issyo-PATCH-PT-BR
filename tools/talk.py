"""Aperta um botao varias vezes tirando print a cada passo. Uso: talk.py <prefixo> <n> [botao] [espera]"""
import sys
import time

import ppdbg

prefix, n = sys.argv[1], int(sys.argv[2])
button = sys.argv[3] if len(sys.argv) > 3 else "circle"
pause = float(sys.argv[4]) if len(sys.argv) > 4 else 2.5
d = ppdbg.Debugger()
for i in range(n):
    d.press(button)
    time.sleep(pause)
    d.shot(f"../work/shots/{prefix}{i}.png")
