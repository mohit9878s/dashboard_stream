import base64

def image_to_base64(img_path):
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def jarvis_logo():
    # Paths
    # Change the path to your image file
    jarvis_path = r"jarvis_Logo_1.png"  # Update this path as needed
    jarvis_base64 = image_to_base64(jarvis_path)
    
if __name__ == "__main__":
    jarvis_logo()
