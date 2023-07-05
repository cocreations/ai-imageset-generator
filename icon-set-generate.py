import sys
import os
import csv
import json
import requests
import argparse

API_URL = "https://api.openai.com/v1/images/generations"

def call_dalle_api(api_key, prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "prompt": prompt,
        "n": 1,
        "size": "512x512"
    }
    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['data'][0]['url']
    else:
        return None


def main():
    parser = argparse.ArgumentParser(description='Bulk generate AI images.')
    parser.add_argument('--datafile', required=True, help='Path to the input datafile (.csv or .json)')
    parser.add_argument('--prompt', required=True, help='Main prompt for image generation')
    
    args = parser.parse_args()

    datafile = args.datafile
    main_prompt = args.prompt

    if not os.path.exists(datafile):
        print(f"{datafile} could not be found.")
        return
    
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY environment variable must be set. To get your API key go to: https://platform.openai.com/account/api-keys")
        return

    file_ext = os.path.splitext(datafile)[1].lower()
    results = []

    try:
        if file_ext == '.csv':
            with open(datafile, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    prompt = f"an image of {row['name']} ({row['desc']}), {main_prompt}"
                    image_url = call_dalle_api(api_key, prompt)
                    # output to stdout: "(X of Y) done : name, desc, image_url"
                    print(f"({reader.line_num} of {len(list(reader))}) done : {row['name']}, {row['desc']}, {image_url}")
                    results.append({'name': row['name'], 'desc': row['desc'], 'image_url': image_url})

        elif file_ext == '.json':
            with open(datafile, 'r') as file:
                data = json.load(file)
                for item in data:
                    prompt = f"an image of {item['name']} ({item['desc']}), {main_prompt}"
                    image_url = call_dalle_api(api_key, prompt)
                    # output to stdout: "(X of Y) done : name, desc, image_url"
                    print(f"({data.index(item) + 1} of {len(data)}) done : {item['name']}, {item['desc']}, {image_url}")
                    results.append({'name': item['name'], 'desc': item['desc'], 'image_url': image_url})

        else:
            print("Unsupported file format. Please provide a .csv or .json file.")
            return

        if file_ext == '.csv':
            output_filename = 'output.csv'
            with open(output_filename, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["name", "desc", "image_url"])
                writer.writeheader()
                for result in results:
                    writer.writerow(result)

        elif file_ext == '.json':
            output_filename = 'output.json'
            with open(output_filename, 'w') as file:
                json.dump(results, file)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
