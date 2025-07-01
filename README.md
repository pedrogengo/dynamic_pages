# Dynamic Pages with Gemini-Flash and Imagen

A FastAPI application that generates complete web pages dynamically using Google's Gemini Flash LLM and Imagen API. Simply visit any URL path and watch as AI creates a unique, visually stunning webpage with custom content and AI-generated images!

## How It Works

- Visit any URL: Go to localhost:8080/[topic] (e.g., /pizza, /unicorns, /space)
- AI Content Generation: Gemini Flash creates a complete HTML page about your topic
- Image Processing: AI identifies where images should go and generates detailed captions
- Image Generation: Imagen API creates custom images based on the captions
- Page Assembly: Everything is combined into a beautiful, self-contained webpage
- Instant Delivery: Your unique page loads in seconds!

## To run the application:
1. Install dependencies: pip install -r requirements.txt
2. Create an `.env` file like:
    ```
    GEMINI_API_KEY=<your api key>
    ```
3. Run the server: python main.py
4. Visit http://localhost:8080/monkey or any other topic!

## Examples

### Monkey's page
<video width="320" height="240" controls>
  <source src="https://github.com/pedrogengo/dynamic_pages/blob/main/assets/monkey.mp4" type="video/mp4">
</video>

### Cat's page
<video width="320" height="240" controls>
  <source src="https://github.com/pedrogengo/dynamic_pages/blob/main/assets/cat.mp4" type="video/mp4">
</video>

