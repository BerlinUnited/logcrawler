for dir in */; do
    du -shm "$dir" >> output.txt
done