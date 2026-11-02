"""Confere lotes traduzidos e copia os aprovados para traducao/. Uso: accept_batch.py 011 inu_003 ...

Um numero sozinho e um lote do Toro (neko_NNN)."""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "..", "work", "trad")

for n in sys.argv[1:]:
    n = n if "_" in n else f"neko_{n}"
    src = os.path.join(WORK, "lotes", f"{n}.jsonl")
    pt = os.path.join(WORK, "pt", f"{n}.jsonl")
    if not os.path.exists(pt):
        print(n, "sem traducao")
        continue
    check = subprocess.run([sys.executable, os.path.join(HERE, "check_batch.py"), src, pt], capture_output=True, text=True, encoding="utf-8")
    want = [json.loads(l)["id"] for l in open(src, encoding="utf-8") if l.strip()]
    got = {json.loads(l)["id"] for l in open(pt, encoding="utf-8") if l.strip()}
    missing = [i for i in want if i not in got]
    ok = check.returncode == 0 and not missing
    print(n, "OK" if ok else "FALHOU", f"{len(got)}/{len(want)}", check.stdout.strip()[-300:] if check.returncode else "")
    if ok:
        shutil.copy(pt, os.path.join(HERE, "..", "traducao"))
