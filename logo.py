import base64
##-----------------------------------------------------------##
def logo(img_path):
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()
##-----------------------------------------------------------##

def jarvis_logo():
    img_path = r"jarvis_Logo_1.png"
    image = logo(img_path)
    return image
if __name__ == "__main__":
    print(jarvis_logo())      # Optional testing

def dashboard_logo():
    img_path = r"dash_logo_1.png"
    image = logo(img_path)
    return image
if __name__ == "__main__":
    print(dashboard_logo())


def map_logo():
    img_path = r"bihar_map.png"    
    image = logo(img_path)
    return image
if __name__ == "__main__":
    print(map_logo())      
