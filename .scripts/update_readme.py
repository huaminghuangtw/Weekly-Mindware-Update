import os
import yaml

_global_issue_list = None

def parse_frontmatter(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if not content.startswith('---'):
            return {}
        end_idx = content.find('---', 3)
        if end_idx == -1:
            return {}
        return yaml.safe_load(content[3:end_idx].strip()) or {}
    except:
        return {}

def remove_frontmatter(md_content):
    if md_content.startswith("---"):
        # Split the Markdown content into three parts
        # parts[0] = "" (before first ---)
        # parts[1] = YAML frontmatter
        # parts[2] = rest of the markdown
        parts = md_content.split("---", 2)
        if len(parts) > 2:
            return parts[2].lstrip("\n")
    return md_content

def generate_tree(base_dir, rel_dir=""):
    global _global_issue_list
    abs_dir = os.path.join(base_dir, rel_dir)
    entries = []
    
    all_items = os.listdir(abs_dir)
    
    if rel_dir == "":
        dir_filter = lambda name: name == "issues"
    elif rel_dir == "issues":
        dir_filter = lambda name: name.isdigit() and len(name) == 4
    else:
        dir_filter = lambda name: True
    
    dirs = [(name, os.path.join(rel_dir, name)) for name in sorted(all_items, reverse=True) 
            if not name.startswith('.') and os.path.isdir(os.path.join(abs_dir, name)) and dir_filter(name)]
    
    files = [(name, os.path.join(rel_dir, name)) for name in sorted(all_items, reverse=True) 
             if not name.startswith('.') and name.endswith(".md") and name != "README.md"]

    if _global_issue_list is None:
        _global_issue_list = []
        for root, _, filenames in os.walk(base_dir):
            for fn in filenames:
                if fn.endswith('.md') and fn != "README.md":
                    rel_path = os.path.relpath(os.path.join(root, fn), base_dir)
                    _global_issue_list.append((fn, rel_path))

    for dname, drel_path in dirs:
        issue_count = sum(1 for _, _, filenames in os.walk(os.path.join(base_dir, drel_path))
                         for fn in filenames if fn.endswith('.md') and fn != "README.md")

        if dname == "issues":
            entries.extend(generate_tree(base_dir, drel_path))
        else:
            entries.append("\n".join([
                '* <details>',
                '    <summary>',
                '      <strong>',
                f'        <a href="{drel_path}">{dname} ({issue_count})</a>',
                '      </strong>',
                '    </summary>',
                ''
            ]))
            entries.extend(generate_tree(base_dir, drel_path))
            entries.append('  </details>\n')

    issues_in_this_dir = [f for f in _global_issue_list if os.path.dirname(f[1]) == rel_dir] if rel_dir == "" else files
    
    for fname, frel_path in issues_in_this_dir:
        try:
            idx = len(_global_issue_list) - _global_issue_list.index((fname, frel_path))
        except ValueError:
            idx = 1

        frontmatter = parse_frontmatter(os.path.join(base_dir, frel_path))
        
        # Use the filename (without .md extension) as the slug
        link_url = f"https://huami.ng/{fname[:-3]}"
        issue = frontmatter.get('issue', idx)
        week_num = frontmatter.get('weekNumber')
        year = frontmatter.get('year')

        entries.append(" " * 4 + f'* <a href="{link_url}">#{issue} - Week {week_num}, {year}</a>')
    
    return entries

def update_readme(readme_path, issues_md, badge_md):
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = remove_frontmatter(content)
    before, _, rest = content.partition("<!-- INDEX-START -->")
    _, _, after = rest.partition("<!-- INDEX-END -->")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(before + "<!-- INDEX-START -->\n" + badge_md + "\n\n" + issues_md + "\n<!-- INDEX-END -->" + after)

def generate_latest_wmu_badge(base_dir):
    all_wmus = [os.path.relpath(os.path.join(r, f), base_dir) 
                for r, _, files in os.walk(base_dir) 
                for f in files if f.endswith('.md') and f != 'README.md']
    if all_wmus:
        latest_wmu = sorted(all_wmus, reverse=True)[0]
        return f"[![Read Latest WMU](https://img.shields.io/badge/📖%20Read%20Latest%20WMU-3AA99F?style=for-the-badge&color=3AA99F)]({latest_wmu})"
    return ""

def main():
    global _global_issue_list
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _global_issue_list = None
    tree = generate_tree(project_root)
    total_issues = sum(1 for root, _, filenames in os.walk(project_root) 
                      for fn in filenames if fn.endswith('.md') and fn != "README.md" 
                      and not any(part.startswith('.') for part in root.replace(project_root, '').split(os.sep)))
    issues_section = '\n'.join([
        '<details><summary><strong><a href=".">All Issues ({})</a></strong></summary>'.format(total_issues),
        '', *tree, '</details>'
    ])
    update_readme(os.path.join(project_root, "README.md"), issues_section, generate_latest_wmu_badge(project_root))
    _global_issue_list = None

if __name__ == "__main__":
    main()
