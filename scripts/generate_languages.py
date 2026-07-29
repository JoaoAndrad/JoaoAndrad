"""Fetches language byte counts across all public repos of a GitHub user
and renders a static SVG bar showing the language breakdown."""
import json
import os
import urllib.request

USERNAME = os.environ["GH_USERNAME"]
TOKEN = os.environ["GH_TOKEN"]
OUTPUT_PATH = "generated/languages.svg"
MAX_LANGS = 6
TITLE = "Linguagens usadas nos ultimos projetos"

REPOS = [
    "GreenlightMidia/frontend",
    "GreenlightMidia/backend",
    "Dog-Bot-Assistente/DogBot-Back",
    "Dog-Bot-Assistente/DogBot-Front",
    "Dog-Bot-Assistente/DogBubble",
    "Herm-Chat/frontend",
    "Herm-Chat/backend",
    "Herm-Chat/bot",
    "JoaoAndrad/Editor-Planta-Baixa",
]

LANGUAGE_COLORS = {
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "Python": "#3572A5",
    "Java": "#b07219",
    "C#": "#178600",
    "Kotlin": "#A97BFF",
    "Dart": "#00B4AB",
    "C++": "#f34b7d",
    "C": "#555555",
    "Go": "#00ADD8",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "PHP": "#4F5D95",
    "Ruby": "#701516",
    "Swift": "#F05138",
    "Shell": "#89e051",
    "Vue": "#41b883",
}
DEFAULT_COLOR = "#8b949e"


def api_get(url):
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": USERNAME,
        },
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())


def aggregate_languages(repo_names):
    totals = {}
    for full_name in repo_names:
        languages = api_get(f"https://api.github.com/repos/{full_name}/languages")
        for name, byte_count in languages.items():
            totals[name] = totals.get(name, 0) + byte_count
    return totals


def render_svg(totals):
    total_bytes = sum(totals.values()) or 1
    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)[:MAX_LANGS]

    width, row_height, top_padding = 340, 28, 50
    height = top_padding + row_height * len(ranked) + 14
    bar_x, bar_width = 140, 140
    pct_x = bar_x + bar_width + 12

    rows = []
    y = top_padding
    for name, byte_count in ranked:
        pct = byte_count / total_bytes * 100
        color = LANGUAGE_COLORS.get(name, DEFAULT_COLOR)
        rows.append(f"""
    <circle cx="14" cy="{y - 5}" r="5" fill="{color}" />
    <text x="26" y="{y}" fill="#c9d1d9" font-size="12" font-family="'Segoe UI', sans-serif">{name}</text>
    <rect x="{bar_x}" y="{y - 10}" width="{bar_width}" height="8" rx="4" fill="#30363d" />
    <rect x="{bar_x}" y="{y - 10}" width="{bar_width * pct / 100:.1f}" height="8" rx="4" fill="{color}" />
    <text x="{pct_x}" y="{y}" fill="#8b949e" font-size="11" font-family="'Segoe UI', sans-serif">{pct:.1f}%</text>""")
        y += row_height

    return f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{width}" height="{height}" rx="10" fill="#0d1117" stroke="#30363d" />
  <text x="14" y="24" fill="#c9d1d9" font-size="14" font-weight="600" font-family="'Segoe UI', sans-serif">{TITLE}</text>
  {''.join(rows)}
</svg>
"""


def main():
    totals = aggregate_languages(REPOS)
    svg = render_svg(totals)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    main()
