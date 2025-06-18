# GoPro Merge

* Some of the videos had to be merged because they were split by gopro due to the size.
  Merged videos are named '..._joined.MP4'. Merging was performed using this tool, which preserves all custom gopro-streams (like the IMU)
  https://github.com/gyroflow/mp4-merge


```bash
wget https://github.com/gyroflow/mp4-merge/releases/download/v0.1.11/mp4_merge-linux64
chmod +x mp4_merge-linux64
```

## Standalone Usage

```
./mp4_merge-linux64 input1.mp4 input2.mp4 --out output.mp4
```


## Use in script

We can use the VAT Database to iterate over all logs and find gopro videos that need merging or we can combine videos based on filenames
TODO: implement me
