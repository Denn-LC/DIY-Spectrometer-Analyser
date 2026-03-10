import json
import os

import numpy as np

CALIBRATION_FILE = "calibration.json"


def fit_linear_calibration(pixel_positions, wavelengths):
    pixel_positions = np.asarray(pixel_positions, dtype = float)
    wavelengths = np.asarray(wavelengths, dtype = float)

    if len(pixel_positions) < 2:
        raise ValueError("Need at least 2 calibration points.")

    m, c = np.polyfit(pixel_positions, wavelengths, 1)

    calibration = {
        "type": "linear",
        "m": float(m),
        "c": float(c),
    }
    return calibration


def pixel_to_wavelength(pixel_position, calibration):
    if calibration is None:
        return None

    if calibration["type"] != "linear":
        raise ValueError("Only linear calibration is supported right now.")

    return calibration["m"] * pixel_position + calibration["c"]


def get_wavelength_axis(n_pixels, calibration):
    pixels = np.arange(n_pixels, dtype=float)
    wavelengths = pixel_to_wavelength(pixels, calibration)
    return wavelengths


def save_calibration(calibration, points = None, calibration_file = CALIBRATION_FILE):
    data = dict(calibration)
    if points is not None:
        data["points"] = points

    with open(calibration_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent = 2)


def load_calibration(calibration_file = CALIBRATION_FILE):
    if not os.path.exists(calibration_file):
        return None

    with open(calibration_file, "r", encoding = "utf-8") as f:
        data = json.load(f)

    return data