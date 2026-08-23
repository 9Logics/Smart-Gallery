import sqlite3
import os
import cv2

db_path = os.path.join(os.path.dirname(__file__), '.cache', 'gallery.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT path FROM photos WHERE file_type = 'video' LIMIT 1")
row = c.fetchone()
if row:
    path = row[0]
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
    print(f"FPS: {fps}, Frames: {frames}, Duration: {frames/fps}, Codec: {codec}")
conn.close()
