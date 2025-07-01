# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import os
import base64
from io import BytesIO
import re
from google import genai
import dotenv
from google.genai import types
dotenv.load_dotenv()

app = FastAPI(title="Dynamic LLM Pages", description="Generate web pages dynamically using Gemini Flash")

# Configuration for Gemini Flash
class GeminiConfig:
    API_KEY = os.getenv("GEMINI_API_KEY")  # Set your Gemini API key in environment variables
    MODEL = "gemini-2.5-flash"
    IMAGE_MODEL = "imagen-4.0-generate-preview-06-06"

config = GeminiConfig()
client = genai.Client(api_key=config.API_KEY)

def process_image_placeholders(html_content: str) -> str:
    """Find and replace image placeholders with generated images"""
    # Pattern to match <IMAGEHERE>caption</IMAGEHERE>
    pattern = r'<IMAGEHERE>(.*?)</IMAGEHERE>'
    
    # Find all image placeholders
    matches = re.findall(pattern, html_content, re.DOTALL)
    
    if not matches:
        return html_content
    
    print(f"Found {len(matches)} image placeholders to process...")
    
    # Process each placeholder
    for i, caption in enumerate(matches):
        caption = caption.strip()
        print(f"Generating image {i+1}/{len(matches)}: {caption[:50]}...")
        
        response = client.models.generate_images(
            model=config.IMAGE_MODEL,
            prompt=caption,
            config=types.GenerateImagesConfig(
                number_of_images=1,
            )
        )
        response_image = response.generated_images[0].image.image_bytes
            
        # Create img tag with generated image
        img_tag = f'<img src="data:image/png;base64,{response_image}" alt="{caption}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" loading="lazy">'
        
        # Replace the first occurrence of this placeholder
        placeholder = f'<IMAGEHERE>{caption}</IMAGEHERE>'
        html_content = html_content.replace(placeholder, img_tag, 1)
    
    return html_content

async def generate_html_with_gemini(topic: str) -> str:
    """Generate HTML using Google Gemini Flash API"""
    if not config.API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API key not configured. Please set GEMINI_API_KEY environment variable.")
    
    prompt = f"""Create a complete, visually stunning HTML page about "{topic}". 

    Requirements:
    - Complete HTML5 structure with <!DOCTYPE html>, <head>, and <body>
    - Embedded CSS styling in <style> tags for modern, responsive design
    - Rich, engaging content related to "{topic}"
    - Interactive elements where appropriate (hover effects, animations, etc.)
    - Creative and visually appealing approach
    - Mobile-friendly responsive design
    - Use vibrant colors, gradients, and modern typography
    - Include some JavaScript for interactivity if relevant
    - Make it feel premium and professional
    
    IMPORTANT IMAGE HANDLING:
    - Instead of using <img> tags or actual images, use this special placeholder format:
    - <IMAGEHERE>descriptive caption of what the image should show</IMAGEHERE>
    - Use these placeholders wherever you would normally put images
    - Make the captions detailed and descriptive for image generation
    - Example: <IMAGEHERE>a beautiful sunset over a tropical beach with palm trees</IMAGEHERE>
    
    IMPORTANT: Return ONLY the complete HTML code. Do not include any explanations, markdown formatting, or code blocks. Start directly with <!DOCTYPE html>"""

    print("Generating content...")
    generated_content = client.models.generate_content(
        model=config.MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1
        )
    )
    print("Content generated")
    html_content = clean_html_response(generated_content.text)
    html_content = process_image_placeholders(html_content)
    
    return html_content

def clean_html_response(content: str) -> str:
    """Clean up the HTML response from Gemini"""
    # Remove markdown code blocks if present
    content = re.sub(r'^```html\s*', '', content, flags=re.MULTILINE)
    content = re.sub(r'^```\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^```.*$', '', content, flags=re.MULTILINE)
    
    # Ensure it starts with DOCTYPE
    if not content.strip().startswith('<!DOCTYPE'):
        # If no DOCTYPE, try to find where HTML starts
        html_match = re.search(r'<!DOCTYPE html>|<html', content, re.IGNORECASE)
        if html_match:
            content = content[html_match.start():]
        else:
            # If still no proper HTML structure, wrap it
            content = f"<!DOCTYPE html>\n<html>\n<head><title>Generated Page</title></head>\n<body>\n{content}\n</body>\n</html>"
    
    return content.strip()

def generate_fallback_html(topic: str) -> str:
    """Generate fallback HTML when Gemini is unavailable"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic.title()} - AI Generated</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            padding: 20px;
        }}
        .container {{
            text-align: center;
            padding: 3rem;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 25px;
            backdrop-filter: blur(15px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            max-width: 700px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        h1 {{
            font-size: 3.5rem;
            margin-bottom: 1.5rem;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.4);
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: glow 2s ease-in-out infinite alternate;
        }}
        @keyframes glow {{
            from {{ text-shadow: 0 0 20px rgba(255, 255, 255, 0.5); }}
            to {{ text-shadow: 0 0 30px rgba(255, 255, 255, 0.8); }}
        }}
        .subtitle {{
            font-size: 1.4rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }}
        .content {{
            font-size: 1.1rem;
            line-height: 1.6;
            margin-bottom: 2rem;
        }}
        .cta {{
            background: linear-gradient(45deg, #ff6b6b, #ee5a52);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 50px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }}
        .cta:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{topic.title()}</h1>
        <div class="subtitle">AI-Powered Dynamic Content</div>
        <div class="content">
            <p>Welcome to the amazing world of <strong>{topic}</strong>! This page was generated dynamically using AI technology.</p>
            <p>Our AI system is currently processing your request to create rich, engaging content about {topic}. This fallback page ensures you always get a great experience.</p>
        </div>
        <a href="/" class="cta">Explore More Topics</a>
    </div>
    
    <script>
        // Add some interactivity
        document.querySelector('.cta').addEventListener('click', function(e) {{
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {{
                this.style.transform = 'translateY(-2px)';
            }}, 100);
        }});
        
        // Animate on load
        document.addEventListener('DOMContentLoaded', function() {{
            document.querySelector('.container').style.opacity = '0';
            document.querySelector('.container').style.transform = 'translateY(50px)';
            
            setTimeout(() => {{
                document.querySelector('.container').style.transition = 'all 0.8s ease';
                document.querySelector('.container').style.opacity = '1';
                document.querySelector('.container').style.transform = 'translateY(0)';
            }}, 100);
        }});
    </script>
</body>
</html>"""

@app.get("/")
async def root():
    """Root endpoint with instructions"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Dynamic Pages</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                margin: 0;
                padding: 20px;
                color: white;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 2rem;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            h1 { text-align: center; margin-bottom: 2rem; font-size: 2.5rem; }
            .examples { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 2rem; }
            .example { background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 10px; text-align: center; }
            .example a { color: #fff; text-decoration: none; font-weight: bold; }
            .example a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 AI Dynamic Page Generator</h1>
            <p>Welcome! This app generates web pages dynamically using Google Gemini Flash. Simply visit any URL path and watch as AI creates a unique page for that topic!</p>
            
            <h2>How it works:</h2>
            <ul>
                <li>Visit <code>localhost:8080/[topic]</code></li>
                <li>AI generates a complete HTML page about that topic</li>
                <li>Each page is unique and creative!</li>
            </ul>
            
            <div class="examples">
                <div class="example">
                    <h3>🎉 Party</h3>
                    <a href="/party">localhost:8080/party</a>
                </div>
                <div class="example">
                    <h3>🏝️ Island</h3>
                    <a href="/island">localhost:8080/island</a>
                </div>
                <div class="example">
                    <h3>🌟 Space</h3>
                    <a href="/space">localhost:8080/space</a>
                </div>
                <div class="example">
                    <h3>🍕 Pizza</h3>
                    <a href="/pizza">localhost:8080/pizza</a>
                </div>
                <div class="example">
                    <h3>🎨 Art</h3>
                    <a href="/art">localhost:8080/art</a>
                </div>
                <div class="example">
                    <h3>🦄 Unicorns</h3>
                    <a href="/unicorns">localhost:8080/unicorns</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/{topic}")
async def generate_page(topic: str):
    """Generate a dynamic page for any topic using Gemini Flash"""
    try:
        # Clean up the topic (remove special characters, handle URL encoding)
        clean_topic = topic.replace("-", " ").replace("_", " ").strip()
        
        if not clean_topic:
            raise HTTPException(status_code=400, detail="Topic cannot be empty")
        
        # Generate HTML using Gemini Flash
        html_content = await generate_html_with_gemini(clean_topic)
        
        return HTMLResponse(content=html_content)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        # Return fallback HTML
        fallback_html = generate_fallback_html(topic)
        return HTMLResponse(content=fallback_html)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": config.MODEL,
        "api_configured": bool(config.API_KEY)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
