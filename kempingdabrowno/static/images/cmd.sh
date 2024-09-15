#!/bin/bash

# Initialize a counter
counter=1

# Loop over all files that match the pattern "photo*.jpg"
for file in photo_2024-09-15*.jpg; do
    # Construct the new filename
    new_name="kemping_${counter}.jpg"
    
    # Rename the file
    mv "$file" "$new_name"
    
    # Increment the counter
    ((counter++))
done
