import json
import base64
import os
from pathlib import Path

def convert_image_to_base64(image_path):
    """Convert an image file to base64 string"""
    try:
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
    except Exception as e:
        print(f"Error converting {image_path}: {e}")
        return None

def get_mime_type(image_path):
    """Get MIME type based on file extension"""
    ext = Path(image_path).suffix.lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
        '.svg': 'image/svg+xml'
    }
    return mime_types.get(ext, 'image/jpeg')

def find_image_by_isbn(directory, isbn):
    """Find image file matching ISBN in the directory"""
    # Remove any hyphens or special characters from ISBN for matching
    clean_isbn = isbn.replace('-', '').replace(' ', '')
    
    # Common image extensions to search for
    extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
    
    for ext in extensions:
        # Try different filename patterns
        patterns = [
            f"{isbn}{ext}",
            f"{clean_isbn}{ext}",
            f"{isbn.lower()}{ext}",
            f"{clean_isbn.lower()}{ext}"
        ]
        
        for pattern in patterns:
            image_path = os.path.join(directory, pattern)
            if os.path.exists(image_path):
                return image_path
    
    return None

def update_json_with_base64(json_file_path, output_file_path=None):
    """
    Read JSON file, convert images to base64, and update the cover_base64 field
    
    Args:
        json_file_path: Path to the input JSON file
        output_file_path: Path to save the updated JSON (if None, overwrite original)
    """
    # Get the directory where the JSON file is located
    directory = os.path.dirname(os.path.abspath(json_file_path))
    
    # Read the JSON file
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return
    
    # Ensure data is a list
    if not isinstance(data, list):
        print("JSON data should be a list of book records")
        return
    
    updated_count = 0
    not_found_count = 0
    
    # Process each book record
    for i, book in enumerate(data):
        isbn = book.get('isbn', '')
        
        if not isbn:
            print(f"Record {i}: No ISBN found, skipping...")
            continue
        
        # Find matching image file
        image_path = find_image_by_isbn(directory, isbn)
        
        if image_path:
            # Convert image to base64
            base64_data = convert_image_to_base64(image_path)
            
            if base64_data:
                # Update the book record
                book['cover_base64'] = base64_data
                book['cover_mime'] = get_mime_type(image_path)
                print(f"✓ Record {i} (ISBN: {isbn}): Updated with {os.path.basename(image_path)}")
                updated_count += 1
            else:
                print(f"✗ Record {i} (ISBN: {isbn}): Failed to convert image")
        else:
            print(f"⚠ Record {i} (ISBN: {isbn}): No matching image found")
            not_found_count += 1
    
    # Save the updated JSON
    if output_file_path is None:
        output_file_path = json_file_path
    
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n✓ Successfully saved updated JSON to: {output_file_path}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")
        return
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"SUMMARY")
    print(f"{'='*50}")
    print(f"Total records processed: {len(data)}")
    print(f"Images updated: {updated_count}")
    print(f"Images not found: {not_found_count}")
    print(f"{'='*50}")

if __name__ == "__main__":
    # Configuration
    JSON_FILE = "book_details.json"  # Change to your JSON file name
    
    # Optional: Specify output file (if None, will overwrite original)
    OUTPUT_FILE = None  # e.g., "updated_books.json"
    
    # Run the script
    update_json_with_base64(JSON_FILE, OUTPUT_FILE)