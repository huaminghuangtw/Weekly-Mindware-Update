import os
import re
import yaml

def process_file(file_path):
    """Remove 'slug' from frontmatter in a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            return
        
        # Find the end of frontmatter
        end_idx = content.find('---', 3)
        if end_idx == -1:
            return
        
        # Extract frontmatter and body
        frontmatter_str = content[3:end_idx].strip()
        body = content[end_idx + 3:]
        
        # Parse frontmatter
        frontmatter = yaml.safe_load(frontmatter_str) or {}
        
        # Remove 'slug' if it exists
        if 'slug' in frontmatter:
            del frontmatter['slug']
            
            # Write back the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('---\n')
                f.write(yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True))
                f.write('---')
                f.write(body)
            print(f"Removed 'slug' from: {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def rename_files(base_dir):
    """Rename files from YYYY_Week_NN.md to YYYYwNN.md format."""
    pattern = re.compile(r'^(\d{4})_Week_(\d{2})\.md$')
    
    for root, _, files in os.walk(base_dir):
        for filename in files:
            match = pattern.match(filename)
            if match:
                year = match.group(1)
                week = match.group(2).lstrip('0') or '0'  # Remove leading zero
                
                old_path = os.path.join(root, filename)
                new_filename = f"{year}w{week}.md"
                new_path = os.path.join(root, new_filename)
                
                # First, remove slug from frontmatter
                process_file(old_path)
                
                # Then rename the file
                os.rename(old_path, new_path)
                print(f"Renamed: {filename} -> {new_filename}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    issues_dir = os.path.join(project_root, 'issues')
    
    if not os.path.exists(issues_dir):
        print(f"Issues directory not found: {issues_dir}")
        return
    
    print("Starting file renaming and frontmatter cleanup...")
    rename_files(issues_dir)
    print("Done!")

if __name__ == "__main__":
    main()
