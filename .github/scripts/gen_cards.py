"""Generate GitHub profile cards as SVG files, using the GitHub GraphQL API.

Runs inside GitHub Actions with GITHUB_TOKEN. Writes SVGs into the folder given
as the first argument. Pass --demo to render with sample data (no network).
"""
import json
import os
import sys
import urllib.request
from collections import Counter
from html import escape

USER = os.environ.get("GH_USER", "fahadqaseem")
FEATURED = [
    "vla-failure-detector",
    "dce-mri-temporal-super-resolution",
    "trustworthy-terrarescue",
    "michigan-power-outage-prediction",
    "intelligent-ids",
    "fastapi_websocket_flutter_app",
]

FALLBACK = {
    "vla-failure-detector": "Finds the point of no return in robot manipulation rollouts for VLA policies.",
    "dce-mri-temporal-super-resolution": "Diffusion model reconstructing missing contrast timepoints in breast DCE-MRI.",
    "trustworthy-terrarescue": "Trustworthy vision-language model for search and rescue terrain analysis.",
    "michigan-power-outage-prediction": "Weather-informed power outage risk forecasting with spatio-temporal GNNs.",
    "intelligent-ids": "Hybrid network intrusion detection with anomaly detection and supervised models.",
    "fastapi_websocket_flutter_app": "Real-time IoT monitoring with FastAPI WebSockets and a 6-platform Flutter app.",
}

BG, BORDER = "#1a1b27", "#2a2e45"
TITLE, TEXT, ACCENT, MUTED = "#70a5fd", "#c0caf5", "#bf91f3", "#7a83a8"
TEAL = "#38bdae"
FONT = "font-family:'Segoe UI',Ubuntu,'Helvetica Neue',Sans-Serif"
LANG_COLORS = {
    "Python": "#3572A5", "Jupyter Notebook": "#DA5B0B", "C++": "#f34b7d",
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Dart": "#00B4AB",
    "Swift": "#F05138", "HTML": "#e34c26", "CSS": "#663399", "C": "#555555",
    "Shell": "#89e051", "TeX": "#3D6117", "Java": "#b07219", "Go": "#00ADD8",
    "Kotlin": "#A97BFF", "CMake": "#DA3434", "C#": "#178600",
}

QUERY = """
query($login: String!) {
  user(login: $login) {
    name
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
      totalCount
      nodes {
        name
        description
        stargazerCount
        forkCount
        primaryLanguage { name color }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def fetch():
    token = os.environ["GITHUB_TOKEN"]
    body = json.dumps({"query": QUERY, "variables": {"login": USER}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]


def demo():
    import random
    random.seed(7)
    days = [{"date": f"2026-10-{d:02d}", "contributionCount": random.randint(0, 9)} for d in range(1, 32)]
    repos = []
    for n in FEATURED:
        repos.append({
            "name": n, "description": "Sample description for layout testing of a longer project blurb.",
            "stargazerCount": 3, "forkCount": 1,
            "primaryLanguage": {"name": "Python", "color": "#3572A5"},
            "languages": {"edges": [{"size": 50000, "node": {"name": "Python", "color": "#3572A5"}},
                                    {"size": 9000, "node": {"name": "Jupyter Notebook", "color": "#DA5B0B"}},
                                    {"size": 4000, "node": {"name": "Dart", "color": "#00B4AB"}},
                                    {"size": 2500, "node": {"name": "C++", "color": "#f34b7d"}},
                                    {"size": 1500, "node": {"name": "TypeScript", "color": "#3178c6"}}]},
        })
    return {
        "name": "Fahad Qaseem Khawar", "followers": {"totalCount": 2},
        "contributionsCollection": {
            "totalCommitContributions": 210, "totalPullRequestContributions": 6, "totalIssueContributions": 3,
            "contributionCalendar": {"totalContributions": 244, "weeks": [{"contributionDays": days}]},
        },
        "repositories": {"totalCount": 22, "nodes": repos},
    }


def frame(w, h, title, inner):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<style>text{{{FONT}}} .t{{fill:{TITLE};font-size:18px;font-weight:600}}'
        f' .l{{fill:{TEXT};font-size:13px}} .v{{fill:{TEXT};font-size:13px;font-weight:700}}'
        f' .m{{fill:{MUTED};font-size:11px}}'
        f' .f{{opacity:0;animation:fi .6s ease-in-out forwards}} @keyframes fi{{to{{opacity:1}}}}</style>'
        f'<rect x="0.5" y="0.5" rx="8" width="{w-1}" height="{h-1}" fill="{BG}" stroke="{BORDER}"/>'
        f'<text x="24" y="36" class="t">{escape(title)}</text>{inner}</svg>'
    )


ICONS = {
    "star": "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z",
    "commit": "M11.93 8.5a4.002 4.002 0 0 1-7.86 0H.75a.75.75 0 0 1 0-1.5h3.32a4.002 4.002 0 0 1 7.86 0h3.32a.75.75 0 0 1 0 1.5Zm-1.43-.75a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0Z",
    "pr": "M1.5 3.25a2.25 2.25 0 1 1 3 2.122v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25Zm5.677-.177L9.573.677A.25.25 0 0 1 10 .854V2.5h1A2.5 2.5 0 0 1 13.5 5v5.628a2.251 2.251 0 1 1-1.5 0V5a1 1 0 0 0-1-1h-1v1.646a.25.25 0 0 1-.427.177L7.177 3.427a.25.25 0 0 1 0-.354Z",
    "issue": "M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3ZM8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0ZM1.5 8a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0Z",
    "repo": "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.249.249 0 0 0-.3 0L5.4 15.7a.25.25 0 0 1-.4-.2Z",
    "people": "M2 5.5a3.5 3.5 0 1 1 5.898 2.549 5.508 5.508 0 0 1 3.034 4.084.75.75 0 1 1-1.482.235 4 4 0 0 0-7.9 0 .75.75 0 0 1-1.482-.236A5.507 5.507 0 0 1 3.102 8.05 3.493 3.493 0 0 1 2 5.5ZM11 4a3.001 3.001 0 0 1 2.22 5.018 5.01 5.01 0 0 1 2.56 3.012.749.749 0 0 1-.885.954.752.752 0 0 1-.549-.514 3.507 3.507 0 0 0-2.522-2.372.75.75 0 0 1-.574-.73v-.352a.75.75 0 0 1 .416-.672A1.5 1.5 0 0 0 11 5.5.75.75 0 0 1 11 4Zm-5.5-.5a2 2 0 1 0-.001 3.999A2 2 0 0 0 5.5 3.5Z",
    "fork": "M5 5.372v.878c0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75v-.878a2.25 2.25 0 1 1 1.5 0v.878a2.25 2.25 0 0 1-2.25 2.25h-1.5v2.128a2.251 2.251 0 1 1-1.5 0V8.5h-1.5A2.25 2.25 0 0 1 3.5 6.25v-.878a2.25 2.25 0 1 1 1.5 0ZM5 3.25a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Zm6.75.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm-3 8.75a.75.75 0 1 0-1.5 0 .75.75 0 0 0 1.5 0Z",
}


def icon(name, x, y, color=ACCENT):
    return f'<svg x="{x}" y="{y}" width="16" height="16" viewBox="0 0 16 16"><path fill="{color}" d="{ICONS[name]}"/></svg>'


def stats_card(u):
    c = u["contributionsCollection"]
    stars = sum(r["stargazerCount"] for r in u["repositories"]["nodes"])
    rows = [
        ("star", "Total stars earned", stars),
        ("commit", "Commits (last year)", c["totalCommitContributions"]),
        ("pr", "Pull requests (last year)", c["totalPullRequestContributions"]),
        ("issue", "Issues (last year)", c["totalIssueContributions"]),
        ("repo", "Public repositories", u["repositories"]["totalCount"]),
        ("people", "Followers", u["followers"]["totalCount"]),
    ]
    inner = ""
    for i, (ic, label, val) in enumerate(rows):
        y = 64 + i * 26
        inner += (f'<g class="f" style="animation-delay:{150 + i*120}ms">{icon(ic, 24, y - 12)}'
                  f'<text x="48" y="{y}" class="l">{label}:</text>'
                  f'<text x="250" y="{y}" class="v">{val:,}</text></g>')
    total = c["contributionCalendar"]["totalContributions"]
    inner += (f'<circle cx="370" cy="118" r="46" fill="none" stroke="{BORDER}" stroke-width="6"/>'
              f'<circle cx="370" cy="118" r="46" fill="none" stroke="{ACCENT}" stroke-width="6" '
              f'stroke-dasharray="289" stroke-dashoffset="289" stroke-linecap="round" transform="rotate(-90 370 118)">'
              f'<animate attributeName="stroke-dashoffset" from="289" to="40" dur="1.2s" fill="freeze"/></circle>'
              f'<text x="370" y="124" text-anchor="middle" style="fill:{TEXT};font-size:22px;font-weight:700">{total:,}</text>'
              f'<text x="370" y="186" text-anchor="middle" class="m">contributions in the last year</text>')
    return frame(450, 210, f"{u['name'] or USER}'s GitHub Stats", inner)


def langs_card(u):
    sizes, colors = Counter(), {}
    for r in u["repositories"]["nodes"]:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            if n in {"Rich Text Format", "TeX", "Makefile", "Procfile"}:
                continue
            sizes[n] += e["size"]
            colors[n] = e["node"]["color"] or LANG_COLORS.get(n, MUTED)
    top = sizes.most_common(8)
    total = sum(s for _, s in top) or 1
    w = 400
    bar, x = "", 24
    for n, s in top:
        seg = (w - 48) * s / total
        bar += f'<rect x="{x:.2f}" y="54" width="{seg:.2f}" height="8" fill="{colors[n]}"/>'
        x += seg
    inner = f'<mask id="bm"><rect x="24" y="54" width="{w-48}" height="8" rx="4" fill="#fff"/></mask><g mask="url(#bm)">{bar}</g>'
    for i, (n, s) in enumerate(top):
        cx, cy = 24 + (i % 2) * 185, 88 + (i // 2) * 24
        inner += (f'<g class="f" style="animation-delay:{150 + i*100}ms"><circle cx="{cx+5}" cy="{cy-4}" r="5" fill="{colors[n]}"/>'
                  f'<text x="{cx+16}" y="{cy}" class="l">{escape(n)} <tspan class="m">{100*s/total:.1f}%</tspan></text></g>')
    h = 88 + ((len(top) + 1) // 2) * 24
    return frame(w, max(h, 210), "Most Used Languages", inner)


def wrap(text, n=52, lines=2):
    words, out, cur = (text or "No description yet.").split(), [], ""
    for wd in words:
        if len(cur) + len(wd) + 1 > n:
            out.append(cur)
            cur = wd
            if len(out) == lines:
                break
        else:
            cur = f"{cur} {wd}".strip()
    else:
        out.append(cur)
    if len(out) > lines:
        out = out[:lines]
    if len(" ".join(out)) < len(text or ""):
        out[-1] = out[-1].rstrip(".,") + "..."
    return out[:lines]


def pin_card(r):
    lang = r["primaryLanguage"] or {"name": "", "color": MUTED}
    desc = "".join(f'<text x="24" y="{66 + i*18}" class="l">{escape(t)}</text>' for i, t in enumerate(wrap(r["description"] or FALLBACK.get(r["name"]))))
    foot = ""
    if lang["name"]:
        foot += f'<circle cx="30" cy="112" r="6" fill="{lang["color"] or MUTED}"/><text x="42" y="116" class="m" style="font-size:12px">{escape(lang["name"])}</text>'
    foot += f'{icon("star", 170, 104, MUTED)}<text x="190" y="116" class="m" style="font-size:12px">{r["stargazerCount"]}</text>'
    foot += f'{icon("fork", 230, 104, MUTED)}<text x="250" y="116" class="m" style="font-size:12px">{r["forkCount"]}</text>'
    title = f'{icon("repo", 24, 22, TITLE)}<text x="48" y="36" class="t" style="font-size:15px">{escape(r["name"])}</text>'
    svg = frame(400, 135, "", title + desc + foot)
    return svg


def activity_card(u):
    days = [d for w in u["contributionsCollection"]["contributionCalendar"]["weeks"] for d in w["contributionDays"]][-31:]
    vals = [d["contributionCount"] for d in days]
    w, h, l, r, t, b = 860, 260, 48, 20, 56, 40
    mx = max(vals + [1])
    pw, ph = w - l - r, h - t - b
    pts = [(l + i * pw / max(len(vals) - 1, 1), t + ph - v * ph / mx) for i, v in enumerate(vals)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{l},{t+ph} {line} {l+pw},{t+ph}"
    grid = ""
    for k in range(5):
        y = t + ph * k / 4
        grid += f'<line x1="{l}" x2="{l+pw}" y1="{y:.1f}" y2="{y:.1f}" stroke="{BORDER}"/><text x="{l-10}" y="{y+4:.1f}" text-anchor="end" class="m">{round(mx*(4-k)/4)}</text>'
    labels = "".join(f'<text x="{x:.1f}" y="{h-16}" text-anchor="middle" class="m">{days[i]["date"][8:]}</text>' for i, (x, _) in enumerate(pts) if i % 3 == 0)
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{ACCENT}"/>' for x, y in pts)
    inner = (f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{TEAL}" stop-opacity=".45"/>'
             f'<stop offset="1" stop-color="{TEAL}" stop-opacity="0"/></linearGradient></defs>{grid}'
             f'<polygon points="{area}" fill="url(#g)"/><polyline points="{line}" fill="none" stroke="{TEAL}" stroke-width="2.5" stroke-linejoin="round"/>'
             f'{dots}{labels}')
    return frame(w, h, f"{u['name'] or USER}'s Contribution Graph (last 31 days)", inner)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "dist"
    u = demo() if "--demo" in sys.argv else fetch()
    os.makedirs(out, exist_ok=True)
    files = {"stats.svg": stats_card(u), "top-langs.svg": langs_card(u), "activity.svg": activity_card(u)}
    by_name = {r["name"]: r for r in u["repositories"]["nodes"]}
    for name in FEATURED:
        if name in by_name:
            files[f"pin-{name}.svg"] = pin_card(by_name[name])
    for fn, svg in files.items():
        with open(os.path.join(out, fn), "w", encoding="utf-8") as f:
            f.write(svg)
    print("wrote", ", ".join(files))


if __name__ == "__main__":
    main()
