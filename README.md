# DIY Spectrometer Analyser

## Run

```bash
python spectrometer_app.py
```

## Controls

r = select and save ROI
x = clear saved ROI
s = analyse emission peak
d = analyse absorption dip
1 = save 2-point calibration using violet laser and red laser
2 = save 3-point calibration using violet laser, sodium lamp, and red laser
l = show loaded calibration
p = save last analysed spectrum as csv
q = quit

## What to do

1. Run the program.
2. Press r and select the spectrum region.
3. Use the violet laser and press s, then note the printed peak pixel.
4. Use the sodium lamp and press s, then note the printed peak pixel.
5. Use the red laser and press s, then note the printed peak pixel.
6. Press 2 and enter the three pixel values to save the calibration.
7. Use s for emission peaks.
8. Use d for absorption dips such as Fraunhofer lines.
9. Press p if you want to save the most recent analysed spectrum as a CSV file.

## Calibration

Calibration assumes the following reference wavelengths

Calibration wavelengths used:

violet laser = 405.0 nm
sodium lamp = 589.3 nm
red laser = 650.0 nm