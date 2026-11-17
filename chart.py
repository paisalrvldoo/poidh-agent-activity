"""Render the headline chart (1200 px wide) from monthly_agent_activity.csv."""
import csv, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
rows = [r for r in csv.DictReader(open("monthly_agent_activity.csv")) if r["month"] >= "2026-01"]
m = [r["month"][2:].replace("-", "/") for r in rows]
f = lambda k: [float(r[k]) for r in rows]
prog, claims, share, sd = f("programmatic_claims"), f("claims"), f("programmatic_share"), f("selfdeclared_agent_claims")
sd_share = [100 * a / b if b else 0 for a, b in zip(sd, claims)]
web = [c - p for c, p in zip(claims, prog)]
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 6.6), dpi=100, gridspec_kw={"width_ratios": [2.3, 1]})
fig.patch.set_facecolor("white")
x = range(len(m))
ax.bar(x, web, color="#c9d3e0", label="claims made in the poidh web app (upload envelope present)")
ax.bar(x, prog, bottom=web, color="#e4572e", label="claims built outside the web app (agent / script)")
ax.set_xticks(list(x)); ax.set_xticklabels(m, fontsize=11)
ax.set_ylabel("claims per month (Base + Arbitrum + Ethereum)", fontsize=11)
axr = ax.twinx()
axr.plot(x, share, color="#b0231a", marker="o", lw=2.5, label="non-web-app share of claims")
axr.plot(x, sd_share, color="#555", marker="s", lw=1.5, ls="--", label="share that SAY they are an AI agent")
for i, s in enumerate(share):
    if s >= 5: axr.annotate(f"{s:.0f}%", (i, s), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=12, fontweight="bold", color="#b0231a")
axr.axhspan(0, 2.5, color="#999", alpha=0.12)
axr.text(0.1, 3.2, "Jan-Jul 2026 noise floor: 1.0% (23 of 2,291)", fontsize=9.5, color="#444")
axr.set_ylim(0, 70); axr.set_ylabel("% of claims", fontsize=11)
ax.axvline(1.2, color="#2a7", ls=":", lw=1.5); ax.text(1.27, max(claims) * 0.93, "poidh publishes\nSKILL.md for agents\n(23 Feb)", fontsize=9, color="#2a7")
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = axr.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", bbox_to_anchor=(0, -0.08), ncol=2, fontsize=9.5, frameon=False)
ax.set_title("Agents arrived as CLAIMANTS: 1% -> 7% -> 22% -> 32% -> 57% of poidh claims\nsigned with proof that never touched poidh's own upload flow", fontsize=13, loc="left", fontweight="bold")
# right panel: claims vs bounties vs funding by agent wallets, Aug-Nov 2026
R = [r for r in rows if r["month"] >= "2026-08"]
tot = lambda k: sum(float(r[k]) for r in R)
cats = ["claims\nsubmitted", "bounties\nposted", "funds\nadded"]
vals = [100 * tot("programmatic_claims") / tot("claims"), 100 * tot("bounties_by_agent_wallets") / tot("bounties_created"), 100 * tot("funds_added_by_agent_wallets") / tot("funds_added")]
lab = [f'{int(tot("programmatic_claims"))} / {int(tot("claims"))}', f'{int(tot("bounties_by_agent_wallets"))} / {int(tot("bounties_created"))}', f'{int(tot("funds_added_by_agent_wallets"))} / {int(tot("funds_added"))}']
bars = ax2.bar(cats, vals, color=["#e4572e", "#f2a541", "#f2a541"])
for b_, v, l in zip(bars, vals, lab):
    ax2.text(b_.get_x() + b_.get_width() / 2, v + 1, f"{v:.0f}%\n({l})", ha="center", fontsize=11)
ax2.set_ylim(0, 45); ax2.set_ylabel("% by agent-fingerprinted wallets, Aug-Nov 2026", fontsize=10)
ax2.set_title("...but they almost never\npost or fund bounties", fontsize=13, loc="left", fontweight="bold")
ax2.tick_params(axis="x", labelsize=11)
fig.text(0.01, 0.01, "Source: poidh.xyz/api/trpc (all 1,202 bounties / 9,381 claims, Base+Arbitrum+Ethereum) + each claim's proof URI fetched from IPFS. Nov 2026 = 1-17 Nov. Code: analyze.py", fontsize=8.5, color="#555")
plt.tight_layout(rect=(0, 0.04, 1, 1))
plt.savefig("agent_activity_chart.png", dpi=100)
print("ok")
