#!/bin/bash

# Function to print usage
print_usage() {
    echo "Usage: $0 [-d|--dry-run] <directory>"
    echo "Options:"
    echo "  -d, --dry-run    Show what changes would be made without making them"
    echo "  -h, --help       Show this help message"
    exit 1
}

# Function to extract title from markdown file
get_title() {
    local file="$1"
    # Extract title from the YAML front matter, remove quotes if present
    title=$(sed -n '/^title:/p' "$file" | sed 's/^title:[[:space:]]*//;s/^"//;s/"$//')
    # Remove articles from the beginning for sorting
    echo "$title" | sed 's/^The //i;s/^A //i;s/^An //i'
}

# Parse command line arguments
dry_run=false
dir=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--dry-run)
            dry_run=true
            shift
            ;;
        -h|--help)
            print_usage
            ;;
        *)
            if [ -z "$dir" ]; then
                dir="$1"
            else
                echo "Error: Too many arguments"
                print_usage
            fi
            shift
            ;;
    esac
done

# Check if directory is provided
if [ -z "$dir" ]; then
    echo "Error: Directory not specified"
    print_usage
fi

# Create a temporary file to store titles and filenames
tmp_file=$(mktemp)

# Find all markdown files and store their titles and paths
find "$dir" -type f -name "*.md" | while read -r file; do
    title=$(get_title "$file")
    if [ ! -z "$title" ]; then
        echo "$title|$file" >> "$tmp_file"
    fi
done

# Function to update or show changes for a file
update_file() {
    local file="$1"
    local new_order="$2"
    local current_order=$(sed -n 's/^nav_order: *//p' "$file")
    
    if [ "$dry_run" = true ]; then
        if [ -z "$current_order" ]; then
            echo "Would add nav_order: $new_order to $file"
        elif [ "$current_order" != "$new_order" ]; then
            echo "Would change nav_order from $current_order to $new_order in $file"
        fi
    else
        if grep -q "^nav_order:" "$file"; then
            sed -i '' "s/^nav_order:.*$/nav_order: $new_order/" "$file"
        else
            sed -i '' "/^title:/a\\
nav_order: $new_order" "$file"
        fi
    fi
}

# Sort files by title and assign nav_order values
counter=1
sort -f "$tmp_file" | while IFS="|" read -r title file; do
    if [ "$dry_run" = true ]; then
        echo "Analyzing $file ($title)..."
    else
        echo "Setting nav_order: $counter for $file ($title)"
    fi
    
    update_file "$file" "$counter"
    ((counter++))
done

# Clean up
rm "$tmp_file"

if [ "$dry_run" = true ]; then
    echo "Dry run complete. No changes were made."
else
    echo "Done! Updated nav_order for all markdown files in $dir"
fi