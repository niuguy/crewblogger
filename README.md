## Overview

This application automates the process of creating blog posts, selecting featured images, and publishing to Webflow. It uses CREW-AI powered content generation, image search and selection, and direct publishing to streamline the blogging workflow.

## Features

- AI-powered blog post generation using CrewAI
- Image search and selection using Pixabay API
- Markdown to HTML conversion
- Review system for content and images before publishing
- Direct publishing to Webflow
- Cleanup functionality for generated files

## Prerequisites

- Python 3.7+
- Pixabay API key
- Webflow API token
- SERPER API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/niuguy/crewblogger
   cd blog-creator-publisher
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```
   export PIXABAY_API_KEY="your_pixabay_api_key"
   export WEBFLOW_API_TOKEN="your_webflow_api_token"
   export OPENAI_API_KEY="your_openai_api_key"
   export SERPER_API_KEY="your_serper_api_key"
   ```


## Usage

### Basic Usage

To generate a blog post, select an image, and publish to Webflow:

```
python main.py "Your Blog Topic" --subtopics "Subtopic 1" "Subtopic 2" "Subtopic 3"
```

### Options

- `--review`: Review the generated content and selected image before publishing
- `--regenerate`: Force regeneration of content even if a draft exists
- `--cleanup`: Remove all generated files and exit

### Examples

1. Generate a post with review:
   ```
   python main.py "AI in Healthcare" --subtopics "Diagnosis" "Treatment" "Ethics" --review
   ```

2. Regenerate an existing post:
   ```
   python main.py "AI in Healthcare" --subtopics "Diagnosis" "Treatment" "Ethics" --regenerate
   ```

3. Clean up generated files:
   ```
   python main.py --cleanup
   ```


## Workflow

1. The script generates a blog post based on the given topic and subtopics.
2. It searches for relevant images on Pixabay.
3. You can review the generated content and select an image.
4. If approved, the post is published to Webflow.

## Customization

- Modify the `create_blog_post` function to adjust the AI content generation process.
- Update the `post_to_webflow` function to change how content is formatted for Webflow.


