import os
import re

base_dir = "/Users/huaminghuang/Library/Mobile Documents/iCloud~md~obsidian/Documents/Second-Brain/Weekly-Mindware-Update"

def get_md_files():
    md_files = []
    for year in ["2024", "2025"]:
        year_dir = os.path.join(base_dir, year)
        for fname in sorted(os.listdir(year_dir)):
            if fname.endswith(".md") and fname.lower() != "README.md":
                md_files.append(os.path.join(year_dir, fname))
    return md_files

def add_issue_field(filepath, issue_number):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    # Check for existing frontmatter
    frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        if not re.search(r"^issue:", frontmatter, re.MULTILINE):
            new_frontmatter = f"{frontmatter}\nissue: {issue_number}"
            new_content = f"---\n{new_frontmatter}\n---\n" + content[frontmatter_match.end():]
        else:
            new_content = content
    else:
        new_content = f"---\nissue: {issue_number}\n---\n{content}"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    md_files = get_md_files()
    for idx, filepath in enumerate(md_files, 1):
        add_issue_field(filepath, idx)

if __name__ == "__main__":
    main()
