# GPS Tools

## reduce.py
The Garmpin GPSmap 60CSX has a limitation of 20 tracks that can be stored. Each track has a maximum of 500 points. A GPX file might contain more that 500 points. With this script the number of points can be reduced by:

- splitting segments to separate files
- splitting the gpx in separate files
- removing points across the track

Examples:

```sh
python3 reduce.py -a KM_2023.gpx
python3 reduce.py -r -m 1000 KM_2023_seg_1.gpx
python3 reduce.py -a KM_2023_seg_1_reduced.gpx
```

## How to get latest OSM map


## How to copy OSM maps to GPS


## How to copy a GPX to the Garmin GPSmap 60CSX

- Install gpsbabel first:

```sh
sudo apt-get gpsbabel
```

- Remove batteries from GPS
- Connect GPS to USB port
- Switch GPS on

```sh
sudo gpsbabel -t -i gpx -f KM_2023_seg_1_reduced_1.gpx -o garmin -F usb:
```
