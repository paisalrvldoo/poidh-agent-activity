"""Degen Chain (not indexed by poidh's API): pull every tx to PoidhV3 on Degen via the public Blockscout explorer and apply the same proof-envelope test."""
import json, urllib.request, urllib.parse, time
ADDR = "0x18E5585ca7cE31b90Bc8BB7aAf84152857cE243f"
BASE = f"https://explorer.degen.tips/api/v2/addresses/{ADDR}/transactions"
def get(url):
    for i in range(5):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "poidh-agents-research"}), timeout=60))
        except Exception as e: err = e; time.sleep(3 * (i + 1))
    raise err
txs, params = [], {"filter": "to"}
while True:
    d = get(BASE + "?" + urllib.parse.urlencode(params))
    txs += d["items"]
    if not d.get("next_page_params"): break
    params = {"filter": "to", **d["next_page_params"]}
out = []
for t in txs:
    di = t.get("decoded_input") or {}
    out.append(dict(hash=t["hash"], ts=t["timestamp"], from_=t["from"]["hash"].lower(), method=t.get("method"), status=t.get("status"),
                    params={p["name"]: p["value"] for p in di.get("parameters", [])}))
json.dump(out, open("data/degen_txs.json", "w"), indent=0)
print(len(out))
