"""Classify every poidh claim by HOW its proof was packaged, then build monthly agent-activity shares.

Signal ("proof envelope"): the poidh web app always uploads the photo AND a metadata JSON to poidh's own
Pinata gateway (beige-impossible-dragon-883.mypinata.cloud) and passes that JSON's URL to createClaim().
The JSON has a fixed template: keys in order description, external_url="https://poidh.xyz/", image, name, attributes=[].
A claim whose on-chain proof URI is NOT that envelope was built outside the web app (script/agent/SDK).
"""
import json, re, collections, datetime as dt, csv, statistics
GW = "beige-impossible-dragon-883.mypinata.cloud"
TEMPLATE = ["description", "external_url", "image", "name", "attributes"]
CHAIN = {8453: "base", 42161: "arbitrum", 1: "ethereum"}
B = json.load(open("data/bounties.json")); C = json.load(open("data/claims.json")); T = json.load(open("data/txs.json"))
M = json.load(open("data/meta.json"))
month = lambda ts: dt.datetime.fromtimestamp(int(ts), dt.timezone.utc).strftime("%Y-%m")
ctx = {(t["chainId"], t["claimId"]): t for t in T if t["action"] == "claim created"}
btx = {(t["chainId"], t["bountyId"]): t for t in T if t["action"] == "bounty created"}
bmap = {(b["chainId"], b["id"]): b for b in B}

# strict first-person self-identification (an agent saying it is one), not mentions of agents
SELF = re.compile(r"\b(I am|I'm|i am)\s+([\w@.-]+,?\s+)?(an?|the)\s+(autonomous\s+)?(AI\s+|software\s+)?agent\b|\bI'm [\w.-]+'s agent\b|"
                  r"\b(by|from)\s+[\w.@-]+,?\s+an?\s+(autonomous\s+)?(AI\s+)?agent\b|\ban AI agent built\b|"
                  r"\b(authored|submitted|written|posted|filed|created)\s+(autonomously\s+)?by\s+[\w.-]+,?\s+an?\s+(autonomous\s+)?AI\s+agent\b|"
                  r"\bas an (autonomous )?AI agent,? I\b|\bthis (claim|submission|bounty) was (autonomously )?(created|submitted|posted|written) by an? (autonomous )?(AI )?agent\b", re.I)
AITEXT = re.compile(r"—|\*\*|^#{1,3} |\n- ", re.M)  # em-dash / markdown: "AI-styled prose" proxy (NOT agent proof)

def envelope(c):
    if GW not in c["url"]:
        return "external_uri"          # proof hosted anywhere but poidh's gateway: never produced by the web app
    m = M.get(f'{c["chainId"]}:{c["id"]}')
    if m is None: return "unchecked"
    if m["ct"] == "ERR": return "unreachable"
    if not m.get("body"): return "gateway_raw_file"   # gateway CID is the image itself, no metadata: poidh upload API used directly
    try: j = json.loads(m["body"])
    except Exception: return "gateway_nonjson"
    if isinstance(j, dict) and list(j.keys()) == TEMPLATE and j.get("external_url") in ("https://poidh.xyz/", "https://kaspotz.github.io/pics-or-it/") and j.get("attributes") == [] \
            and (j.get("image") == "" or str(j.get("image", "")).startswith("https://" + GW)):
        return "webapp"   # exact web-app template (image "" = web-app upload glitch seen in 2025)
    return "gateway_custom_json"

rows = []
for c in C:
    t = ctx.get((c["chainId"], c["id"]))
    if not t: continue
    b = bmap.get((c["chainId"], c["bountyId"])); bt = btx.get((c["chainId"], c["bountyId"]))
    env = envelope(c)
    rows.append(dict(chain=CHAIN[c["chainId"]], chainId=c["chainId"], claimId=c["id"], onChainId=c["onChainId"], bountyId=c["bountyId"],
        wallet=t["address"].lower(), ts=int(t["timestamp"]), month=month(t["timestamp"]), tx=t["tx"], env=env,
        programmatic=env in ("external_uri", "gateway_raw_file", "gateway_custom_json", "gateway_nonjson"),
        selfdecl=bool(SELF.search(c["title"] + "\n" + c["description"])), aitext=bool(AITEXT.search(c["description"])),
        latency=(int(t["timestamp"]) - int(bt["timestamp"])) if bt else None, url=c["url"], title=c["title"]))
json.dump(rows, open("data/claims_classified.json", "w"))

# wallets with a verified-by-envelope programmatic claim
prog_wallets = set()
for w in {r["wallet"] for r in rows}:
    rr = [r for r in rows if r["wallet"] == w and r["month"] >= "2026-08"]
    p = sum(r["programmatic"] for r in rr)
    if p >= 3 and p >= 0.8 * len(rr): prog_wallets.add(w)   # wallet that (almost) only ever submits non-web-app claims
self_wallets = {r["wallet"] for r in rows if r["selfdecl"]}
agent_wallets = prog_wallets | self_wallets

# bounty side: creation + add-funds by agent-fingerprinted wallets, and bounty self-declarations
bact = []
for t in T:
    a = t["action"]
    if a == "bounty created": kind = "bounty_created"
    elif a.startswith("+") and a.endswith("eth"):
        b = bmap.get((t["chainId"], t["bountyId"]))
        if b and b["issuer"].lower() == t["address"].lower(): continue  # skip issuer's own initial escrow if logged as join
        kind = "funds_added"
    else: continue
    bact.append(dict(chainId=t["chainId"], month=month(t["timestamp"]), wallet=t["address"].lower(), kind=kind, bountyId=t["bountyId"]))
bself = {(b["chainId"], b["id"]) for b in B if SELF.search(b["title"] + "\n" + b["description"])}

months = sorted({r["month"] for r in rows if r["month"] >= "2025-07"})
out = []
for m in months:
    R = [r for r in rows if r["month"] == m]
    chk = [r for r in R if r["env"] not in ("unchecked", "unreachable")]
    prog = [r for r in chk if r["programmatic"]]
    sd = [r for r in R if r["selfdecl"]]
    web = [r for r in chk if r["env"] == "webapp"]
    BC = [x for x in bact if x["month"] == m and x["kind"] == "bounty_created"]
    FA = [x for x in bact if x["month"] == m and x["kind"] == "funds_added"]
    row = dict(month=m, claims=len(R), claims_checked=len(chk), programmatic_claims=len(prog),
        programmatic_share=round(100 * len(prog) / max(1, len(chk)), 1),
        selfdeclared_agent_claims=len(sd), selfdeclared_share=round(100 * len(sd) / max(1, len(R)), 1),
        programmatic_wallets=len({r["wallet"] for r in prog}), active_claim_wallets=len({r["wallet"] for r in R}),
        webapp_aistyled_share=round(100 * sum(r["aitext"] for r in web) / max(1, len(web)), 1),
        programmatic_aistyled_share=round(100 * sum(r["aitext"] for r in prog) / max(1, len(prog)), 1),
        bounties_created=len(BC), bounties_by_agent_wallets=sum(x["wallet"] in agent_wallets for x in BC),
        bounties_selfdeclared=sum((x["chainId"], x["bountyId"]) in bself for x in BC),
        funds_added=len(FA), funds_added_by_agent_wallets=sum(x["wallet"] in agent_wallets for x in FA))
    for ch in ("base", "arbitrum", "ethereum"):
        cc = [r for r in chk if r["chain"] == ch]
        row[f"{ch}_claims"] = len(cc); row[f"{ch}_programmatic"] = sum(r["programmatic"] for r in cc)
    out.append(row)
with open("monthly_agent_activity.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
for r in out: print(r)

# validation: latency + self-declaration overlap
def med(xs): xs = [x for x in xs if x is not None and x >= 0]; return round(statistics.median(xs) / 3600, 2) if xs else None
recent = [r for r in rows if r["month"] >= "2026-08" and r["env"] not in ("unchecked", "unreachable")]
P = [r for r in recent if r["programmatic"]]; W = [r for r in recent if r["env"] == "webapp"]
summary = dict(
    total_claims=len(rows), total_bounties=len(B), chains=dict(collections.Counter(r["chain"] for r in rows)),
    env_counts=dict(collections.Counter(r["env"] for r in rows)),
    pre_2026_08_programmatic=sum(r["programmatic"] for r in rows if r["month"] < "2026-08"),
    claims_2024_05_to_2026_07=sum(1 for r in rows if r["month"] < "2026-08"),
    selfdecl_claims=sum(r["selfdecl"] for r in rows), selfdecl_programmatic=sum(r["selfdecl"] and r["programmatic"] for r in rows),
    selfdecl_webapp=sum(r["selfdecl"] and r["env"] == "webapp" for r in rows),
    since_aug_prog_selfdecl_share=round(100 * sum(r["selfdecl"] for r in P) / max(1, len(P)), 1),
    median_latency_h_prog=med([r["latency"] for r in P]), median_latency_h_webapp=med([r["latency"] for r in W]),
    prog_wallets=len(prog_wallets), self_wallets=len(self_wallets),
    bounties_by_agent_wallets_total=sum(1 for x in bact if x["kind"] == "bounty_created" and x["wallet"] in agent_wallets),
    funds_by_agent_wallets_total=sum(1 for x in bact if x["kind"] == "funds_added" and x["wallet"] in agent_wallets),
    bounties_selfdecl=len(bself),
    top_prog_wallets=collections.Counter(r["wallet"] for r in rows if r["programmatic"]).most_common(15),
    top_hosts=collections.Counter(re.sub(r"^https?://([^/]+).*", r"\1", r["url"]) for r in rows if r["env"] == "external_uri").most_common(15))
json.dump(summary, open("data/summary.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
