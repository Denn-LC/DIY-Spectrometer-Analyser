import json
import os

ROI_FILE = "roi.json"


def save_roi(roi, roi_file=ROI_FILE):
    x, y, w, h = map(int, roi)
    data = {
        "x": x,
        "y": y,
        "w": w,
        "h": h,
    }

    with open(roi_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_roi(roi_file=ROI_FILE):
    if not os.path.exists(roi_file):
        return None

    with open(roi_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["x"], data["y"], data["w"], data["h"]


def clear_roi(roi_file=ROI_FILE):
    if os.path.exists(roi_file):
        os.remove(roi_file)