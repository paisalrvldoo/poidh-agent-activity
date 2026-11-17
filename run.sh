#!/usr/bin/env bash
# Reproduce everything (~15 min, no keys, no wallet, read-only public endpoints).
set -euo pipefail
python3 collect.py      # all bounties, claims, on-chain actions from https://poidh.xyz/api/trpc
python3 fetch_meta.py   # fetch the proof-URI target of every gateway-hosted claim since 2025-07
python3 analyze.py      # classify + monthly CSV + data/summary.json
python3 chart.py        # agent_activity_chart.png (needs matplotlib)
