import cv2
import os
import glob
import sys

# Get all images
folder = '/home/omkhalane/.gemini/antigravity/brain/6982793d-7899-4543-87f2-3b949991aa59/.user_uploaded/'
images = glob.glob(folder + '*.png')
if not images:
    print("No images found!")
    sys.exit(1)

# Pick the last one which is most likely the most recent or relevant
latest_image = sorted(images)[-1]
print(f"Loading {latest_image}")
img = cv2.imread(latest_image)
if img is None:
    print("Failed to load image")
    sys.exit(1)

height, width = img.shape[:2]
target_width = 120
target_height = int((height / width) * target_width * 0.45) # 0.45 to account for terminal font aspect ratio

img = cv2.resize(img, (target_width, target_height))

# Print ANSI
for y in range(target_height):
    row_str = ""
    for x in range(target_width):
        b, g, r = img[y, x]
        # Using ANSI truecolor
        row_str += f"\033[48;2;{r};{g};{b}m \033[0m"
    print(row_str)

