# Reencode the GoPro Videos
The GoPro Videos can't be played in Chromium Browsers on Linux because of their codec. This ffmpeg command will re-encode the video while keeping the telemetry data.

```bash
ffmpeg -i "input.mp4" -map 0:v -map 0:a -map 0:3 -c:v libx264 -crf 18 -c:a aac -c:s copy -c:d copy -movflags +faststart "output.mp4"
```
