#!/usr/bin/env python3
import os
from datetime import datetime, timedelta, timezone
import requests
import matplotlib.pyplot as plt

PRIMARY = "#6d72f6"
MUTED = "#64748b"

GH_API = "https://api.github.com/graphql"

def graphql(token: str, query: str, variables: dict):
    r = requests.post(
        GH_API,
        json={"query": query, "variables": variables},
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]

def main():
    login = os.environ["GH_LOGIN"]
    token = os.environ["GH_TOKEN"]
    out = os.environ.get("OUT_PATH", "profile/activity-26w.svg")

    to_dt = datetime.now(timezone.utc)
    from_dt = to_dt - timedelta(days=7 * 26)

    q = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) {
          contributionCalendar {
            weeks {
              firstDay
              contributionDays { date contributionCount }
            }
          }
        }
      }
    }
    """

    data = graphql(token, q, {"login": login, "from": from_dt.isoformat(), "to": to_dt.isoformat()})
    weeks = data["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

    xs, ys = [], []
    for w in weeks[-26:]:
        # firstDay is YYYY-MM-DD
        xs.append(datetime.fromisoformat(w["firstDay"]).replace(tzinfo=timezone.utc))
        ys.append(sum(d["contributionCount"] for d in w["contributionDays"]))

    fig = plt.figure(figsize=(10, 2.3), dpi=200)
    ax = fig.add_subplot(111)
    fig.patch.set_alpha(0)
    ax.set_facecolor((0, 0, 0, 0))

    ax.plot(xs, ys, linewidth=2.2, color=PRIMARY)
    ax.fill_between(xs, ys, 0, color=PRIMARY, alpha=0.12)

    for spine in ["top", "right", "left", "bottom"]:
        ax.spines[spine].set_visible(False)
    ax.set_yticks([])
    ax.tick_params(axis="x", colors=MUTED, labelsize=8, length=0)
    ax.set_title("Activity (last 26 weeks)", fontsize=10, color=MUTED, loc="left", pad=6)

    plt.tight_layout()
    fig.savefig(out, format="svg", transparent=True)

if __name__ == "__main__":
    main()
