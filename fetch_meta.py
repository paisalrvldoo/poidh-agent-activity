"""Fetch the proof-URI target of every claim stored on poidh's own IPFS gateway (the web app's upload path) since 2025-07, to fingerprint how it was made."""
import json, urllib.request, concurrent.futures as cf, os, time
C = json.load(open("data/claims.json")); T = json.load(open("data/txs.json"))
ts = {(t["chainId"], t["claimId"]): int(t["timestamp"]) for t in T if t["action"] == "claim created"}
CUT = 1751328000  # 2025-07-01 UTC
out_path = "data/meta.json"
meta = json.load(open(out_path)) if os.path.exists(out_path) else {}
todo = [c for c in C if "beige-impossible-dragon-883" in c["url"] and ts.get((c["chainId"], c["id"]), 0) >= CUT and f'{c["chainId"]}:{c["id"]}' not in meta]
def get(c):
    for i in range(4):
        try:
            r = urllib.request.urlopen(urllib.request.Request(c["url"], headers={"Range": "bytes=0-20000", "User-Agent": "poidh-agents-research"}), timeout=40)
            b = r.read(20001); ct = r.headers.get("content-type", "")
            return f'{c["chainId"]}:{c["id"]}', {"ct": ct, "body": b.decode("utf-8", "replace") if "json" in ct or "text" in ct else None}
        except Exception as e:
            err = str(e); time.sleep(3 * (i + 1))
    return f'{c["chainId"]}:{c["id"]}', {"ct": "ERR", "err": err}
print("todo", len(todo), flush=True)
with cf.ThreadPoolExecutor(16) as ex:
    for n, (k, v) in enumerate(ex.map(get, todo)):
        meta[k] = v
        if n % 500 == 0:
            print(n, flush=True); json.dump(meta, open(out_path, "w"))
json.dump(meta, open(out_path, "w")); print("done", len(meta))
