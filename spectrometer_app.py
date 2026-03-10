import cv2
import numpy as np

from calibration_utils import (
    fit_linear_calibration,
    get_wavelength_axis,
    load_calibration,
    pixel_to_wavelength,
    save_calibration,
)
from plot_utils import plot_spectrum, save_spectrum_csv
from roi_utils import clear_roi, load_roi, save_roi
from spectrum_utils import extract_spectrum, find_dip_pixel, find_peak_pixel

CAMERA_INDEX = 0
DISPLAY_SCALE = 4


def print_controls():
    print()
    print("Controls:")
    print("r = select and save ROI")
    print("x = clear saved ROI")
    print("s = analyse emission peak")
    print("d = analyse absorption dip")
    print("1 = save 2-point calibration (violet + red)")
    print("2 = save 3-point calibration (violet + sodium + red)")
    print("l = show loaded calibration")
    print("p = save last analysed spectrum as csv")
    print("q = quit")
    print()


def get_cropped_frame(frame, roi):
    x, y, w, h = map(int, roi)
    cropped = frame[y:y + h, x:x + w]
    return cropped


def enter_two_point_calibration():
    print("\n2-point calibration")
    violet_pixel = float(input("Pixel for violet laser (405 nm): "))
    red_pixel = float(input("Pixel for red laser (650 nm): "))

    pixel_positions = [violet_pixel, red_pixel]
    wavelengths = [405.0, 650.0]

    calibration = fit_linear_calibration(pixel_positions, wavelengths)
    points = [
        {"label": "violet laser", "pixel": violet_pixel, "wavelength_nm": 405.0},
        {"label": "red laser", "pixel": red_pixel, "wavelength_nm": 650.0},
    ]

    save_calibration(calibration, points=points)
    print(f"Saved calibration: wavelength = {calibration['m']:.6f} * pixel + {calibration['c']:.6f}")
    return load_calibration()


def enter_three_point_calibration():
    print("\n3-point calibration")
    violet_pixel = float(input("Pixel for violet laser (405 nm): "))
    sodium_pixel = float(input("Pixel for sodium lamp (589.3 nm): "))
    red_pixel = float(input("Pixel for red laser (650 nm): "))

    pixel_positions = [violet_pixel, sodium_pixel, red_pixel]
    wavelengths = [405.0, 589.3, 650.0]

    calibration = fit_linear_calibration(pixel_positions, wavelengths)
    points = [
        {"label": "violet laser", "pixel": violet_pixel, "wavelength_nm": 405.0},
        {"label": "sodium lamp", "pixel": sodium_pixel, "wavelength_nm": 589.3},
        {"label": "red laser", "pixel": red_pixel, "wavelength_nm": 650.0},
    ]

    save_calibration(calibration, points=points)
    print(f"Saved calibration: wavelength = {calibration['m']:.6f} * pixel + {calibration['c']:.6f}")
    return load_calibration()


def analyse_current_roi(cropped, mode, calibration):
    spectrum_data = extract_spectrum(cropped, band_half_width=4)
    profile = spectrum_data["i_dist"]

    if mode == "peak":
        feature_pixel = find_peak_pixel(profile, window=5)
    elif mode == "dip":
        feature_pixel = find_dip_pixel(profile, window=5)
    else:
        raise ValueError("Unknown analysis mode.")

    wavelength = None
    if calibration is not None:
        wavelength = pixel_to_wavelength(feature_pixel, calibration)

    return spectrum_data, feature_pixel, wavelength


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print(f"Could not open camera at index {CAMERA_INDEX}.")
        return

    roi = load_roi()
    roi_selected = roi is not None
    calibration = load_calibration()
    last_result = None

    if roi_selected:
        print(f"Loaded ROI: {roi}")

    if calibration is not None:
        print("Loaded calibration.")
        if "m" in calibration and "c" in calibration:
            print(f"wavelength = {calibration['m']:.6f} * pixel + {calibration['c']:.6f}")

    print_controls()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame from camera.")
            break

        key = cv2.waitKey(1) & 0xFF

        if key == ord("r"):
            selected_roi = cv2.selectROI("Select ROI", frame, showCrosshair=True)
            cv2.destroyWindow("Select ROI")

            if selected_roi[2] > 0 and selected_roi[3] > 0:
                save_roi(selected_roi)
                roi = selected_roi
                roi_selected = True
                print(f"Saved ROI: {roi}")

        elif key == ord("x"):
            clear_roi()
            roi = None
            roi_selected = False
            print("Saved ROI cleared.")

        elif key == ord("1"):
            calibration = enter_two_point_calibration()

        elif key == ord("2"):
            calibration = enter_three_point_calibration()

        elif key == ord("l"):
            calibration = load_calibration()
            if calibration is None:
                print("No calibration file found.")
            else:
                print(calibration)

        elif key == ord("p"):
            if last_result is None:
                print("No analysed spectrum to save yet.")
            else:
                wavelengths = None
                if last_result["calibration"] is not None:
                    wavelengths = get_wavelength_axis(
                        len(last_result["spectrum_data"]["i_dist"]),
                        last_result["calibration"],
                    )

                pixel_positions = np.arange(len(last_result["spectrum_data"]["i_dist"]))

                csv_path = save_spectrum_csv(
                    pixel_positions,
                    last_result["spectrum_data"]["r_dist"],
                    last_result["spectrum_data"]["g_dist"],
                    last_result["spectrum_data"]["b_dist"],
                    last_result["spectrum_data"]["i_dist"],
                    wavelengths=wavelengths,
                    prefix=last_result["feature_type"],
                )
                print(f"Saved CSV: {csv_path}")

        elif key == ord("s") and roi_selected:
            cropped = get_cropped_frame(frame, roi)
            spectrum_data, feature_pixel, wavelength = analyse_current_roi(cropped, "peak", calibration)

            print(f"Peak pixel = {feature_pixel:.2f}")
            if wavelength is not None:
                print(f"Peak wavelength = {wavelength:.2f} nm")
            else:
                print("No calibration loaded yet.")

            plot_path = plot_spectrum(
                cropped,
                spectrum_data,
                feature_pixel=feature_pixel,
                wavelength=wavelength,
                feature_type="peak",
            )
            if plot_path is not None:
                print(f"Saved plot: {plot_path}")

            last_result = {
                "spectrum_data": spectrum_data,
                "feature_type": "peak",
                "calibration": calibration,
            }

        elif key == ord("d") and roi_selected:
            cropped = get_cropped_frame(frame, roi)
            spectrum_data, feature_pixel, wavelength = analyse_current_roi(cropped, "dip", calibration)

            print(f"Dip pixel = {feature_pixel:.2f}")
            if wavelength is not None:
                print(f"Dip wavelength = {wavelength:.2f} nm")
            else:
                print("No calibration loaded yet.")

            plot_path = plot_spectrum(
                cropped,
                spectrum_data,
                feature_pixel=feature_pixel,
                wavelength=wavelength,
                feature_type="dip",
            )
            if plot_path is not None:
                print(f"Saved plot: {plot_path}")

            last_result = {
                "spectrum_data": spectrum_data,
                "feature_type": "dip",
                "calibration": calibration,
            }

        elif key == ord("q"):
            break

        if roi_selected:
            cropped = get_cropped_frame(frame, roi)
            display = cv2.resize(
                cropped,
                None,
                fx=DISPLAY_SCALE,
                fy=DISPLAY_SCALE,
                interpolation=cv2.INTER_NEAREST,
            )
            cv2.imshow("roi", display)
        else:
            cv2.imshow("frame", frame)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()