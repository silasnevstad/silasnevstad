#!/usr/bin/env python3
import os, time, requests
from datetime import datetime, timezone
import matplotlib.pyplot as plt

OWNER = os.environ["GH_OWNER"]
REPO  = os.environ.get("GH_REPO", OWNER)  # set explicitly if you want a specific repo
TOKEN = os.environ["GH_TOKEN"]
OUT   = os.environ.get("OUT_PATH", "profile/activity-26w.svg")

PRIMARY = "#6d72f6"
MUTED   = "#94a3b8"

def github_json(url: str):
  headers = {"Accept": "application/vnd.github+json"}
  if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"
  r = requests.get(url, headers=headers, timeout=30)
  r.raise_for_status()
  return r.json(), r.status_code

def main():
  url = f"https://api.github.com/repos/{OWNER}/{REPO}/stats/commit_activity"

  # GitHub may return 202 while generating stats; retry a few times.
  data = None
  for _ in range(8):
    j, status = github_json(url)
    if status != 202:
      data = j
      break
    time.sleep(5)
  if data is None:
    raise RuntimeError("GitHub stats still generating (202). Retry later.")

  # data: list of 52 weeks; each has total + days + week (unix)
  weeks = data[-26:]
  xs = [datetime.fromtimestamp(w["week"], tz=timezone.utc) for w in weeks]
  ys = [w["total"] for w in weeks]

  fig = plt.figure(figsize=(10, 2.2), dpi=200)
  ax = fig.add_subplot(111)

  fig.patch.set_alpha(0)
  ax.set_facecolor((0, 0, 0, 0))

  ax.plot(xs, ys, linewidth=2.2, color=PRIMARY)
  ax.fill_between(xs, ys, 0, color=PRIMARY, alpha=0.12)

  ax.spines["top"].set_visible(False)
  ax.spines["right"].set_visible(False)
  ax.spines["left"].set_visible(False)
  ax.spines["bottom"].set_visible(False)

  ax.tick_params(axis="x", colors=MUTED, labelsize=8, length=0)
  ax.tick_params(axis="y", colors=MUTED, labelsize=8, length=0)
  ax.set_yticks([])

  ax.set_title("Activity (last 26 weeks)", fontsize=10, color=MUTED, loc="left", pad=6)

  plt.tight_layout()
  fig.savefig(OUT, format="svg", transparent=True)
  print(f"Wrote {OUT}")

if __name__ == "__main__":
  main()
