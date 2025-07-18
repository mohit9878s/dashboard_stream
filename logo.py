# import base64
# def image_to_base64(img_path):
#     with open(img_path, "rb") as image_file:
#         return base64.b64encode(image_file.read()).decode()
# def jarvis_logo():
#     # Paths
#     # Change the path to your image file
#     jarvis_path = r"jarvis_Logo_1.png"  # Update this path as needed
#     jarvis_base64 = image_to_base64(jarvis_path)
# if __name__ == "__main__":
#     jarvis_logo()

# # jarvis_logo.py
import base64
def image_to_base64(img_path):
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

def jarvis_logo():
    jarvis_path = r"jarvis_Logo_1.png"
    jarvis_base64 = image_to_base64(jarvis_path)
    return jarvis_base64

if __name__ == "__main__":
    # print(jarvis_logo())      # Optional testing
    jarvis_logo()


def dashboard_logo():
    jarvis_path = r"dash_logo_1.png"
    jarvis_base64 = image_to_base64(jarvis_path)
    return jarvis_base64

if __name__ == "__main__":
    dashboard_logo()


# def get_base64_encoded_image(image_path):
#     if not os.path.exists(image_path):
#         st.warning("⚠️ Image not found.")
#         return ""
#     with open(image_path, "rb") as img_file:
#         return base64.b64encode(img_file.read()).decode()
#img_base64 = get_base64_encoded_image("dash_logo_1.png")




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
