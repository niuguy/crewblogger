import markdown2

def convert_to_html(markdown_text):
    # Convert Markdown to HTML
    markdowner = markdown2.Markdown()
    html = markdowner.convert(markdown_text)
    return html


def main():
    # Read the Markdown file
    with open('./output/final-article.md', 'r') as file:
        markdown_text = file.read()
    
    # Convert Markdown to HTML
    html_content = convert_to_html(markdown_text)
    
    # Write the HTML content to a file
    with open('./output/final-article.html', 'w') as file:
        file.write(html_content)

if __name__ == "__main__":
    main()