#include <dirent.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int count_files(const char *path) {
    DIR *dir;
    struct dirent *entry;
    int count = 0;

    dir = opendir(path);
    if (dir == NULL) {
        perror("opendir");
        return -1;
    }

    while ((entry = readdir(dir)) != NULL) {
        // Skip . and .. entries
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }
        count++;
    }

    closedir(dir);
    return count;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <directory>\n", argv[0]);
        return 1;
    }

    const char *target_dir = argv[1];
    int file_count = count_files(target_dir);

    if (file_count >= 0) {
        printf("%d", file_count);
        return 0;
    } else {
        return 1;
    }
}