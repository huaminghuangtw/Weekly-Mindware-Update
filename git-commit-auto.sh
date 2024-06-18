#!/bin/sh

# Get the current date and time
current_time=$(date +"%Y-%m-%d %H:%M:%S")

# Get the repository name by extracting the last part of the directory path
repo_name=$(basename $(git rev-parse --show-toplevel))

# Set the commit message
commit_message="Updating <$repo_name> from my laptop ($current_time)"

# Run git commit with the generated message
git add .
git commit -m "$commit_message"
