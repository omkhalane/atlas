import cv2
import numpy as np
import pytesseract
from collections import Counter
from sklearn.cluster import KMeans

# We already installed opencv and pytesseract in previous tasks
vidcap = cv2.VideoCapture('Screencast from 2026-08-01 23-15-24.webm')
success, img = vidcap.read()
if not success:
    print("Failed to read video")
    exit(1)

print("--- FRAME DIMENSIONS ---")
height, width, _ = img.shape
print(f"Width: {width}, Height: {height}")

print("\n--- DOMINANT COLORS ---")
# Resize for speed
small_img = cv2.resize(img, (200, 200))
pixels = small_img.reshape(-1, 3)
kmeans = KMeans(n_clusters=5, random_state=42)
kmeans.fit(pixels)
colors = kmeans.cluster_centers_
labels = kmeans.labels_
counts = Counter(labels)
for i, (color, count) in enumerate(zip(colors, counts.values())):
    hex_color = '#{:02x}{:02x}{:02x}'.format(int(color[2]), int(color[1]), int(color[0]))
    print(f"Color {i+1}: {hex_color} (Frequency: {count})")

print("\n--- PANELS & RECTANGLES ---")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blurred, 50, 150)
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

rectangles = []
for contour in contours:
    approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
    if len(approx) == 4:
        x, y, w, h = cv2.boundingRect(approx)
        if w > 100 and h > 100: # filter out small boxes
            rectangles.append((x, y, w, h))

# Sort by size (largest first)
rectangles.sort(key=lambda r: r[2]*r[3], reverse=True)
for i, (x, y, w, h) in enumerate(rectangles[:5]):
    # Get average color of this panel
    roi = img[y:y+h, x:x+w]
    avg_color = roi.mean(axis=0).mean(axis=0)
    hex_color = '#{:02x}{:02x}{:02x}'.format(int(avg_color[2]), int(avg_color[1]), int(avg_color[0]))
    print(f"Panel {i+1}: x={x}, y={y}, width={w}, height={h}, Avg Color={hex_color}")

print("\n--- TEXT OCR ---")
data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
n_boxes = len(data['text'])
for i in range(n_boxes):
    if int(data['conf'][i]) > 60: # confidence threshold
        text = data['text'][i].strip()
        if text:
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            print(f"Text: '{text}' at x={x}, y={y}, w={w}, h={h}")

