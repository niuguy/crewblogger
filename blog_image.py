import os
import requests
import subprocess
import platform
from openai import OpenAI
import replicate

def search_pixabay_images(topic, num_images=10):
    # Pixabay API endpoint
    url = "https://pixabay.com/api/"
    
    PIXABAY_API_KEY = os.getenv('PIXABAY_API_KEY')

    if not PIXABAY_API_KEY:
        raise ValueError("PIXABAY_API_KEY environment variable is not set")

    
    # Parameters for the API request
    print ("image topic", topic)
    # topic = "Charity stream"
    params = {
        "key": PIXABAY_API_KEY,
        "q": topic,
        "per_page": num_images,
        "image_type": "photo"
    }
    
    # Make the API request
    response = requests.get(url, params=params)
    data = response.json()
    print("images", data)
    
    # Extract relevant information for each image
    images = []
    for i, img in enumerate(data["hits"]):
        images.append({
            "id": img["id"],
            "description": img["tags"],
            "url": img["webformatURL"],
            "thumb": img["previewURL"],
            "user": img["user"]
        })
    
    return images

def download_thumbnails(images, folder="temp_thumbnails"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    for i, img in enumerate(images, start=1):
        response = requests.get(img['thumb'])
        if response.status_code == 200:
            file_path = os.path.join(folder, f"{i}.jpg")
            with open(file_path, 'wb') as f:
                f.write(response.content)
            img['local_thumb'] = file_path
            
    
    return folder

def open_folder(folder_path):
    if platform.system() == "Windows":
        os.startfile(folder_path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.Popen(["open", folder_path])
    else:  # Linux and other Unix-like
        subprocess.Popen(["xdg-open", folder_path])

def user_select_images(images):
    thumbnail_folder = download_thumbnails(images)
    
    print(f"\nDownloaded thumbnails to: {thumbnail_folder}")
    print("Opening folder for image review...")
    open_folder(thumbnail_folder)
    
    input("Press Enter when you're ready to select an image...")
    
    print("\nAvailable Images:")
    for i, img in enumerate(images, start=1):
        print(f"{i}. {img['description']} (by {img['user']}")
    
    while True:
        try:
            selected = input("\nEnter the number of the image you want to use as the main image: ")
            selected_index = int(selected.strip()) - 1
            if 0 <= selected_index < len(images):
                selected_image = images[selected_index]
                break
            else:
                print("Invalid selection. Please enter a number within the range.")
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    # Clean up thumbnails
    for file in os.listdir(thumbnail_folder):
        os.remove(os.path.join(thumbnail_folder, file))
    os.rmdir(thumbnail_folder)
    
    return selected_image

def refine_prompt_with_gpt(topic):
    # Initialize the OpenAI client with the API key from the environment variable
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    # Create the chat completion request
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant that creates image prompts."},
            {"role": "user", "content": f"Create a detailed image prompt for a realistic photo based on the topic: {topic}. The image should be suitable for a blog post."}
        ],
        model="gpt-4-turbo",  # Using the correct model as per your requirements
    )
    # Return the generated content from the response
    return chat_completion.choices[0].message.content

def generate_image_with_replicate(topic):
    REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
    if not REPLICATE_API_TOKEN:
        raise ValueError("REPLICATE_API_TOKEN environment variable is not set")

    # refined_prompt = refine_prompt_with_gpt(topic)

    # print("refined_prompt", refined_prompt)
    refined_prompt = '''

Title: "Empowering Change: How Modern Technology Transforms Philanthropy"

Image Details:
- Setting: A spacious, well-lit modern office environment with large windows overlooking a cityscape.
- Main Focus: A diverse group of four individuals (two men, two women) of various ethnicities (Asian, Caucasian, Hispanic, African) gathered around a large, high-tech digital table.
- Actions: The group is engaged in an interactive session. One of the women (Hispanic) is leading a discussion, pointing at dynamic digital graphs and charts displayed on the surface of the table, which illustrate philanthropic impact, such as money raised, areas served, and project outcomes.
- Technology Elements: The digital table is equipped with touch technology and is displaying real-time data. Around the room, there are screens showing live feeds from different parts of the world where their projects are making a difference.
- Facial Expressions: All individuals are focused and show expressions of optimism and engagement.
- Attire: Business casual, reflecting a professional but approachable environment.
- Additional Details: On the walls, there are photos and plaques illustrating past achievements and recognitions in the field of philanthropy. There is also a visible eco-friendly theme, with plants in biodegradable pots and recycled materials used in the furniture.
- Lighting: The office is brightly lit with natural light complemented by eco-friendly LED lights, highlighting a commitment to sustainability.

Caption: "Digital Dynamics: Exploring the Intersection of Technology and Philanthropy to Foster Global Change."

This image would communicate the effectiveness and forward-thinking methods in which technology is integrated into philanthropic efforts, highlighting collaboration, diversity, and data-driven decision making. It aims to inspire readers to consider the impact of technological advancements in the realm of charitable endeavors.

'''
    
    data = {
            "prompt": refined_prompt
    }

    output = replicate.run("black-forest-labs/flux-pro", input=data)

    return output


if __name__ == "__main__":
    output = generate_image_with_replicate("Tech Transform Philanthropy")
    print("output", output)