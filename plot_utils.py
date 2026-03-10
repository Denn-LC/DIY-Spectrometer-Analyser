import os
from datetime import datetime

import cv2
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = "spectra_output"


def ensure_output_dir(output_dir=OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)


def save_spectrum_csv(
    pixel_positions,
    r_dist,
    g_dist,
    b_dist,
    i_dist,
    wavelengths=None,
    prefix="spectrum",
    output_dir=OUTPUT_DIR,
):
    ensure_output_dir(output_dir)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.csv"
    path = os.path.join(output_dir, filename)

    if wavelengths is None:
        data = np.column_stack((pixel_positions, r_dist, g_dist, b_dist, i_dist))
        header = "pixel,r,g,b,mean"
    else:
        data = np.column_stack((pixel_positions, wavelengths, r_dist, g_dist, b_dist, i_dist))
        header = "pixel,wavelength_nm,r,g,b,mean"

    np.savetxt(path, data, delimiter=",", header=header, comments="")
    return path


def plot_spectrum(
    cropped,
    spectrum_data,
    feature_pixel=None,
    wavelength=None,
    feature_type="peak",
    save_plot=True,
    output_dir=OUTPUT_DIR,
):
    ensure_output_dir(output_dir)

    r_dist = spectrum_data["r_dist"]
    g_dist = spectrum_data["g_dist"]
    b_dist = spectrum_data["b_dist"]
    i_dist = spectrum_data["i_dist"]
    center_row = spectrum_data["center_row"]
    band_edges = spectrum_data["band_edges"]

    cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)

    plt.figure(figsize=(9, 6))

    plt.subplot(2, 1, 1)
    plt.imshow(cropped_rgb)
    plt.axhline(center_row, color="white", linestyle="--", linewidth=1)
    plt.axhline(band_edges[0], color="yellow", linestyle=":", linewidth=1)
    plt.axhline(band_edges[1] - 1, color="yellow", linestyle=":", linewidth=1)
    plt.title("Selected ROI")
    plt.axis("off")

    plt.subplot(2, 1, 2)
    plt.plot(r_dist, color="r", label="red")
    plt.plot(g_dist, color="g", label="green")
    plt.plot(b_dist, color="b", label="blue")
    plt.plot(i_dist, color="k", label="mean")

    if feature_pixel is not None:
        plt.axvline(
            feature_pixel,
            color="m",
            linestyle="--",
            label=f"{feature_type} pixel = {feature_pixel:.2f}",
        )

    title = "Spectrum Analysis"
    if wavelength is not None:
        title += f" | {feature_type} wavelength = {wavelength:.2f} nm"

    plt.xlabel("Pixel Position")
    plt.ylabel("Intensity")
    plt.title(title)
    plt.legend(loc="upper left")
    plt.tight_layout()

    plot_path = None
    if save_plot:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_filename = f"{feature_type}_{timestamp}.png"
        plot_path = os.path.join(output_dir, plot_filename)
        plt.savefig(plot_path, dpi=200, bbox_inches="tight")

    plt.show()
    return plot_path