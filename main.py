from blog_crew import create_blog_post
from blog_image import search_pixabay_images, user_select_images, generate_image_with_replicate
import argparse
import json
import os
import markdown
from bs4 import BeautifulSoup
import re
import requests
import tempfile
import webbrowser
import shutil
import sys  



def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(content)

def convert_to_html(markdown_text):
    # Convert Markdown to HTML
    markdowner = markdown.Markdown()
    html = markdowner.convert(markdown_text)
    return html


def generate_valid_slug(title):
    # Convert to lowercase
    slug = title.lower()
    # Replace spaces with hyphens
    slug = slug.replace(" ", "-")
    # Remove any character that is not alphanumeric, underscore, or hyphen
    slug = re.sub(r'[^a-z0-9_-]', '', slug)
    # Ensure it starts with an alphanumeric character
    slug = re.sub(r'^[^a-z0-9]+', '', slug)
    # Limit length to 255 characters (Webflow's limit)
    slug = slug[:255]
    return slug


def post_to_webflow(html_content, image_url):
    url = "https://api.webflow.com/v2/collections/654b74b88ed72c4317ed5abd/items"
    
    # Get the API token from environment variable
    api_token = os.getenv('WEBFLOW_API_TOKEN')
    if not api_token:
        raise ValueError("WEBFLOW_API_TOKEN environment variable is not set")

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {api_token}",
        "content-type": "application/json"
    }
    
    # Extract the first heading as the post title
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    post_title = title.text if title else "Auto-generated Post"
    
    # Generate a valid slug from the title
    slug = generate_valid_slug(post_title)
    
    data = {
        "isArchived": False,
        "isDraft": False,
        "fieldData": {
            "name": post_title,
            "slug": slug,
            "post-content": html_content,
            "content-summary": "This is a post from API call.",
            "main-image": image_url
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def create_review_html(html_content, image_url):
    review_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Article Review</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }}
            img {{ max-width: 100%; height: auto; }}
        </style>
    </head>
    <body>
        <h1>Article Review</h1>
        <h2>Selected Main Image:</h2>
        <img src="{image_url}" alt="Main Image">
        <h2>Article Content:</h2>
        {html_content}
    </body>
    </html>
    """
    return review_html

def review_article(html_file_path, image_url):
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    review_html = create_review_html(html_content, image_url)
    
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
        f.write(review_html)
        temp_filepath = f.name
    
    webbrowser.open('file://' + os.path.realpath(temp_filepath))
    
    approval = input("Do you approve this article and image for publishing? (yes/no): ").lower().strip()
    
    os.unlink(temp_filepath)
    
    return approval == 'yes'


def publish(args):
    if args.cleanup:
        cleanup()
        return

    # Ensure output directory exists
    os.makedirs('./output', exist_ok=True)
    
    html_file_path = './output/final-article.html'

    if not os.path.exists(html_file_path) or args.regenerate:
        # Generate blog post if HTML doesn't exist or regenerate flag is set
        print("Generating blog post...")
        blog_content = create_blog_post(args.topic, args.subtopics)
        
        # Convert to HTML
        html_content = convert_to_html(blog_content)
        
        # Write HTML content
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML content written to {html_file_path}")
    else:
        print(f"Using existing HTML file: {html_file_path}")
    
    # Search and select images
    if args.image_source == 'search':
        print("Searching for images...")
        images = search_pixabay_images(args.topic)
        print(f"Found {len(images)} images.")
        selected_image = None
        if len(images) == 0:
            print("No images found. Consider using the --image-source generate option.")
        else:
            selected_image = user_select_images(images)
    else:  # args.image_source == 'generate'
        print("Generating image...")
        generated_image_url = generate_image_with_replicate(args.topic)
        selected_image = {'url': generated_image_url, 'description': f"Generated image for {args.topic}"}
    
    if selected_image:
        print(f"Selected image: {selected_image['description']}")
        print(f"Image URL: {selected_image['url']}")
    else:
        print("No image selected or generated. Proceeding without an image.")
    
    # If review flag is set, open the article and image for review
    if args.review:
        approved = review_article(html_file_path, selected_image['url'] if selected_image else None)
        if not approved:
            print("Article not approved for publishing. Exiting.")
            return
    
    # Read the HTML content for posting
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Post to Webflow
    response = post_to_webflow(html_content, selected_image['url'] if selected_image else None)
    
    print("Response from Webflow API:")
    print(json.dumps(response, indent=2))

def cleanup():
    """Remove all generated files and directories."""
    directories_to_remove = ['./output', './temp_thumbnails']
    files_to_remove = []  # Add any specific files here if needed

    for directory in directories_to_remove:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"Removed directory: {directory}")

    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed file: {file}")

    print("Cleanup completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate blog post, select image, and publish to Webflow")
    parser.add_argument("topic", nargs='?', help="Main topic of the blog post")
    parser.add_argument("--subtopics", nargs='+', help="Subtopics to include in the blog post")
    parser.add_argument("--review", action="store_true", help="Review the article and image before publishing")
    parser.add_argument("--cleanup", action="store_true", help="Remove all generated files and exit")
    parser.add_argument("--regenerate", action="store_true", help="Force regeneration of the blog post")
    parser.add_argument("--image-source", choices=['search', 'generate'], default='search', help="Choose to search for an image or generate one")
    
    args = parser.parse_args()
    
    if args.cleanup and (args.topic or args.subtopics or args.review or args.regenerate):
        print("Error: --cleanup cannot be used with other options")
        sys.exit(1)
    
    if not args.cleanup and not args.topic:
        print("Error: topic is required unless --cleanup is specified")
        sys.exit(1)
    
    publish(args)