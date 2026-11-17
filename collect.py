"""Collect all poidh bounties, claims and on-chain actions from poidh's public tRPC API (https://poidh.xyz/api/trpc)."""
import json, urllib.parse, urllib.request, concurrent.futures as cf, time, os
API = "https://poidh.xyz/api/trpc/"
def q(proc, inp, tries=5):
    url = API + proc + "?input=" + urllib.parse.quote(json.dumps({"json": inp}))
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "poidh-agents-research"}), timeout=60) as r:
                return json.load(r)["result"]["data"]["json"]
        except Exception as e:
            err = e; time.sleep(2 * (i + 1))
    raise err
def all_bounties():
    out = {}
    for status in ["open", "progress", "past"]:
        cur = None
        while True:
            inp = {"status": status, "limit": 100, "sortType": "date"}
            if cur: inp["cursor"] = cur
            d = q("bounties.fetchAll", inp)
            for b in d["items"]:
                b["_status"] = status; out[(b["chainId"], b["id"])] = b
            cur = d.get("nextCursor")
            if not cur or not d["items"]: break
    return list(out.values())
def claims(b):
    items, cur = [], None
    while True:
        inp = {"bountyId": b["id"], "chainId": b["chainId"], "limit": 100}
        if cur: inp["cursor"] = cur
        d = q("claims.fetchBountyClaims", inp)
        items += d["items"]; cur = d.get("nextCursor")
        if not cur or not d["items"]: break
    return items
def per_bounty(b):
    return b, claims(b), q("bounties.fetchTransactions", {"bountyId": b["id"], "chainId": b["chainId"]})
if __name__ == "__main__":
    bs = all_bounties(); print("bounties", len(bs))
    C, T = [], []
    with cf.ThreadPoolExecutor(8) as ex:
        for b, c, t in ex.map(per_bounty, bs):
            C += c; T += t
    json.dump(bs, open("data/bounties.json", "w")); json.dump(C, open("data/claims.json", "w")); json.dump(T, open("data/txs.json", "w"))
    print("claims", len(C), "txs", len(T))
