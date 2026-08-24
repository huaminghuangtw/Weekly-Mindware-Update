import os
import re
import yaml

ISSUES_DIR = "issues"
SITE_URL = "https://huam.ing"
INDEX_START = "<!-- INDEX-START -->"
INDEX_END = "<!-- INDEX-END -->"
ISSUE_NAME = re.compile(r"^\d{4}w\d{1,2}\.md$")


def parse_frontmatter(path):
    try:
        text = open(path, encoding="utf-8").read()
        if text.startswith("---"):
            end = text.find("---", 3)
            if end != -1:
                return yaml.safe_load(text[3:end]) or {}
    except Exception:
        pass
    return {}


def collect_issues(root):
    issues = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        for fn in filenames:
            if not ISSUE_NAME.match(fn):
                continue
            path = os.path.join(dirpath, fn)
            meta = parse_frontmatter(path)
            issues.append(
                (meta.get("issue", 0), os.path.relpath(path, root), meta))
    return issues


def latest_wmu_path(issues):
    def year_week(item):
        return tuple(map(int, re.search(r"(\d{4})w(\d{1,2})", item[1]).groups()))
    return max(issues, key=year_week)[1]


def latest_wmu_badge(issues):
    latest = latest_wmu_path(issues)
    return (f"[![Read Latest WMU]"
            f"(https://img.shields.io/badge/📖%20Read%20Latest%20WMU-3AA99F?style=for-the-badge&color=3AA99F)]"
            f"({latest})")


def details_header(rel, name, count):
    return f"""* <details>
    <summary>
      <strong>
        <a href="{rel}">{name} ({count})</a>
      </strong>
    </summary>
"""


def build_index(issues):
    """Render the nested <details> tree, grouping issues by their directory."""
    lines = []

    def render(rel_dir):
        prefix = rel_dir + os.sep if rel_dir else ""
        subs, here = {}, []
        for issue, rel, meta in issues:
            if not rel.startswith(prefix):
                continue
            rest = rel[len(prefix):]
            if os.sep in rest:
                subs.setdefault(rest.split(os.sep, 1)[0], []).append(
                    (issue, rel, meta))
            else:
                here.append((issue, rel, meta))

        for name in sorted(subs, reverse=True):
            sub_rel = os.path.join(rel_dir, name)
            if name == ISSUES_DIR:
                render(sub_rel)  # container dir: render its children in place
            else:
                lines.append(details_header(sub_rel, name, len(subs[name])))
                render(sub_rel)
                lines.append("  </details>\n")

        for issue, rel, meta in sorted(here, key=lambda x: (x[0], x[1]), reverse=True):
            slug = os.path.splitext(os.path.basename(rel))[0]
            year, week = re.match(r"(\d{4})w(\d{1,2})", slug).groups()
            lines.append(f'    * <a href="{SITE_URL}/{slug}">'
                         f'#{issue} - Week {week}, {year}</a>')

    render("")
    return lines


def update_readme(path, index, badge):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    before, _, rest = content.partition(INDEX_START)
    _, _, after = rest.partition(INDEX_END)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{before}{INDEX_START}\n{badge}\n\n{index}\n{INDEX_END}{after}")


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    issues = collect_issues(root)
    index = "\n".join([
        f'<details><summary><strong><a href="{SITE_URL}/wmu">'
        f'All Issues ({len(issues)})</a></strong></summary>',
        "",
        *build_index(issues),
        "</details>",
    ])
    update_readme(os.path.join(root, "README.md"),
                  index, latest_wmu_badge(issues))


if __name__ == "__main__":
    main()
