
# jarvis_logo.py
import base64

def image_to_base64(img_path):
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def jarvis_logo():
    jarvis_path = r"jarvis_Logo_1.png"
    jarvis_base64 = image_to_base64(jarvis_path)
    return jarvis_base64

if __name__ == "__main__":
#    print(jarvis_logo())  # Optional testing
    jarvis_logo()



######--------- Image to base64 ----------
### code in dash.py 
# def image_to_base64(img_path):
#     with open(img_path, "rb") as image_file:
#         return base64.b64encode(image_file.read()).decode()
# # Paths
# # jarvis_path = r"jarvis_Logo_.webp"
# jarvis_path = r"jarvis_Logo_1.png"
# jarvis_base64 = image_to_base64(jarvis_path)
# ######--------- Image to base64 ----------
