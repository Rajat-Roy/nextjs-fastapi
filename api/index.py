import os
import shutil
from fastapi import FastAPI, File, UploadFile
from fastapi.staticfiles import StaticFiles
from PIL import Image
from starlette.responses import FileResponse, HTMLResponse

app = FastAPI()

# Mount the 'uploads' directory as a static directory to serve uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def home():
    html_content = """
    <html>
        <head>
            <title>Upload and Download Status</title>
        </head>
        <body>
            <h1>Upload and Download Status</h1>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file">
                <input type="submit" value="Upload">
            </form>
            <p><a href="/download" method="get" enctype="multipart/form-data">Download File</a></p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Create the uploads directory if it doesn't exist
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    # Save the uploaded file to the uploads directory
    file_path = os.path.join("uploads", file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename}

@app.get("/download/{filename}")
async def download_image(filename: str):
    file_path = os.path.join("uploads", filename)
    return FileResponse(file_path, media_type="image/jpeg")

@app.get("/view")
async def view_images():
    images = []
    for filename in os.listdir("uploads"):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            images.append(filename)

    html_content = """
    <html>
        <head>
            <title>Image Viewer</title>
        </head>
        <body>
            <h1>Image Viewer</h1>
            <ul>
    """

    for image in images:
        html_content += f'<li><a href="/uploads/{image}">{image}</a></li>'

    html_content += """
            </ul>
        </body>
    </html>
    """

    return HTMLResponse(content=html_content)

@app.post("/resize")
async def resize_image(file: UploadFile = File(...), width: int = 300, height: int = 300):
    # Open the uploaded image file
    image = Image.open(file.file)

    # Resize the image
    resized_image = image.resize((width, height))

    # Generate a unique filename for the resized image
    resized_filename = f"resized_{file.filename}"

    # Save the resized image to the uploads directory
    resized_file_path = os.path.join("uploads", resized_filename)
    resized_image.save(resized_file_path)

    return {"filename": resized_filename}

