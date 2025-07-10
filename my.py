import os
import re
import yaml

folder = "/Users/huaminghuang/Library/Mobile Documents/iCloud~md~obsidian/Documents/Second-Brain/Weekly-Mindware-Update/"

for filename in os.listdir(folder):
    if not filename.endswith(".md") or filename.lower().startswith("readme"):
        continue
    path = os.path.join(folder, filename)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split frontmatter and body
    match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if not match:
        continue
    frontmatter_raw, body = match.groups()
    frontmatter = yaml.safe_load(frontmatter_raw)


    # Find weekNumber and year for title
    week = frontmatter.get("weekNumber")
    year = frontmatter.get("year")

    # If week or year is missing, skip
    if not week or not year:
        continue

    # Calculate Monday of the week (ISO week, Monday=1)
    from datetime import datetime, timedelta
    # ISO weeks: Monday is the first day of the week
    # Use strptime with ISO year and week
    try:
        monday = datetime.strptime(f"{year}-W{int(week):02d}-1", "%G-W%V-%u")
    except Exception as e:
        continue
    # Set time to 00:00:00
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    # Format as ISO string (or Obsidian's preferred format)
    created_str = monday.strftime("%Y-%m-%dT%H:%M:%S")

    # Update frontmatter
    frontmatter["created"] = created_str

    # Dump frontmatter back to YAML
    new_frontmatter_raw = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    new_content = f"---\n{new_frontmatter_raw}\n---\n{body}"

    # Write back to file only if changed
    if content != new_content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
    