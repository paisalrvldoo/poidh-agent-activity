TITLE: Agents went from 1% to 57% of poidh claims in 4 months, caught by the one thing they skip: poidh's upload envelope

WHAT I MEASURED
How each claim's proof was packaged, not how its text reads. The poidh web app always uploads the photo to poidh's own Pinata gateway, wraps it in a fixed metadata JSON (description, external_url "https://poidh.xyz/", image, name, attributes []) and puts that JSON's URL in createClaim(). A claim with any other proof URI (GitHub raw, catbox, custom JSON, bare image) was built outside the web app. Data: all 1,202 bounties and 9,381 claims on Base, Arbitrum and Ethereum (poidh API), plus 6,700 gateway proof URIs fetched to check the template.

WHAT I FOUND
- Noise floor: Jan-Jul 2026, 23 of 2,291 claims (1.0%) were non-web-app.
- Then Aug 7.1%, Sep 22.3%, Oct 31.7%, Nov 1-17 56.6%: 768 claims from 133 wallets. Without the 10 busiest wallets: 13%, 22%, 44% (Sep-Nov).
- Calibration: 61 of 67 claims that say "I am an AI agent" are non-web-app (91%). Only about 8% of non-web-app claims say so.
- Agents claim, people pay: Aug-Nov, agent wallets sent 29% of claims but posted 18 of 257 bounties and added funds 1 of 286 times.
- They win small: 50 accepted claims (26% of wins) but 0.30 ETH, about 4% of ETH paid.
- AI text vs agent: among claims signed in the web app, AI-styled prose rose from about 3% to 21.5% in Nov. Those are people using AI text in the UI, counted as web app.
- Aug-Nov by chain: Base 29%, Ethereum 32%, Arbitrum 15%.

VERIFIED VS GUESS
Verified (envelope plus a public source): Assay 0xd34f…5f60 (79 claims, "an autonomous AI agent"), hatch-worker 0xd07c…dc64 (repo Cloud9Gleam/poidh-1550-agent-activity), agentatwork 0x1c7a…9d57 ("I am a software agent", 3 chains), and AME 0x02c1…0361. AME never disclosed on poidh, but its repo RAMGOX/autonomous-micro-entrepreneur lists this wallet as its payout wallet.
Guess: every other non-web-app claim. It proves "not made in the poidh web app", not "no human". The 1% floor (Skatehive and Farcaster clients) is the false-positive rate. Claims prepared by an agent through MCP or WebMCP and approved by a person also land here. An agent driving the website lands in web app, so the share is a floor.
Limits: no Degen (not in the API, explorer down), 677 hidden claims excluded, no x402 link.

REPRODUCE
./run.sh (Python, no keys) rebuilds monthly_agent_activity.csv and the chart.
Code + CSV + write-up: https://github.com/paisalrvldoo/poidh-agent-activity
Sources: poidh.xyz/api/trpc (bounties.fetchAll, claims.fetchBountyClaims, bounties.fetchTransactions); github.com/picsoritdidnthappen/poidh-app/blob/prod/SKILL.md
