from flask import Flask, request, jsonify, url_for
import requests
import os
from werkzeug.utils import secure_filename
import uuid
import nest_asyncio
from scrapegraphai.graphs import SmartScraperGraph
import json

# Apply nest_asyncio for asynchronous code execution
nest_asyncio.apply()

# Flask app setup
app = Flask(__name__)

# Directory to save images
SAVE_DIR = 'static/images'
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

@app.route('/')
def home():
    return "Flask app is running!"

# Flask route to trigger the smart scraper
@app.route('/scrape', methods=['POST'])
def scrape_data():
    try:
        # Get the OpenAI API key from the request JSON or query parameters
        data = request.get_json()
        openai_api_key = data.get('api_key')

        if not openai_api_key:
            return jsonify({"error": "API key is required"}), 400

        # Get the source URL and prompt from the request JSON
        source_url = data.get('source_url', 'https://linkdoctor.io/')  # default value if not provided
        prompt = data.get('prompt', "Find some information about what does the company do, the name and a contact email.")  # default prompt
        
        # Graph configuration
        graph_config = {
            "llm": {
                "api_key": openai_api_key,
                "model": "openai/gpt-4o-mini",
            },
            "verbose": True,
            "headless": True,
        }
        
        # Initialize the SmartScraperGraph with the provided prompt and source
        smart_scraper_graph = SmartScraperGraph(
            prompt=prompt,
            source=source_url,
            config=graph_config
        )
        
        # Run the scraper
        result = smart_scraper_graph.run()
        
        # Convert the result to JSON format and return
        final_data = json.dumps(result, indent=4)
        return jsonify({"status": "success", "data": json.loads(final_data)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to download the image, save it locally, and return the URL
@app.route('/get_chart_image', methods=['GET'])
def get_chart_image():
    try:
        # Get the chart URL from query parameters
        chart_url = request.args.get('chart_url')

        if not chart_url:
            return jsonify({"error": "Chart URL not provided"}), 400

        # Request the image from the chart URL
        response = requests.get(chart_url)

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch the chart image"}), 400

        # Create a secure filename for the image
        filename = secure_filename(f'chart_image_{uuid.uuid4()}.png')

        # Save the image to the static/images directory
        file_path = os.path.join(SAVE_DIR, filename)
        with open(file_path, 'wb') as f:
            f.write(response.content)

        # Generate the URL to the saved image
        image_url = url_for('static', filename=f'images/{filename}', _external=True)

        # Return the image URL as JSON
        return jsonify({"image_url": image_url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Main function to run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
