import numpy as np


def extract_spectrum(cropped, band_half_width=4):
    if cropped is None or cropped.size == 0:
        raise ValueError("Cropped frame is empty.")

    intensity_map = np.mean(cropped, axis=2)
    row_profile = np.sum(intensity_map, axis=1)
    center_row = int(np.argmax(row_profile))

    y_start = max(0, center_row - band_half_width)
    y_end = min(cropped.shape[0], center_row + band_half_width + 1)

    strip = cropped[y_start:y_end, :, :]

    b_dist = np.sum(strip[:, :, 0], axis=0)
    g_dist = np.sum(strip[:, :, 1], axis=0)
    r_dist = np.sum(strip[:, :, 2], axis=0)
    i_dist = (r_dist + g_dist + b_dist) / 3.0

    result = {
        "r_dist": r_dist,
        "g_dist": g_dist,
        "b_dist": b_dist,
        "i_dist": i_dist,
        "center_row": center_row,
        "band_edges": (y_start, y_end),
    }
    return result


def find_peak_pixel(profile, window=5):
    peak_index = int(np.argmax(profile))

    x_start = max(0, peak_index - window)
    x_end = min(len(profile), peak_index + window + 1)

    x_vals = np.arange(x_start, x_end, dtype=float)
    y_vals = np.asarray(profile[x_start:x_end], dtype=float)

    if np.sum(y_vals) == 0:
        return float(peak_index)

    peak_pixel = np.sum(x_vals * y_vals) / np.sum(y_vals)
    return float(peak_pixel)


def find_dip_pixel(profile, window=5):
    dip_index = int(np.argmin(profile))

    x_start = max(0, dip_index - window)
    x_end = min(len(profile), dip_index + window + 1)

    x_vals = np.arange(x_start, x_end, dtype=float)
    local = np.asarray(profile[x_start:x_end], dtype=float)
    y_vals = np.max(local) - local

    if np.sum(y_vals) == 0:
        return float(dip_index)

    dip_pixel = np.sum(x_vals * y_vals) / np.sum(y_vals)
    return float(dip_pixel)