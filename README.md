A small script that help with the task to mantain a backup of directories of local disk in OneDrive on Windows.
It looks for mismatched files between both OneDrive and local directories and checks if there are files missing in either directory.
It displays both directory trees side to side, highlitghting the differencies, and seeks actions to synchronize both directories.
It keeps the most recent file based on the modification date in case of outdated copies of files.
It copies the files that exists in one directory but are missing in the other.

IMPORTANT: This scripts works if the directory structure/tree is basically the same in the local and backup directories.
The objetive is to fix differences that naturally occur over time as files and folders change slightly with use and keep diverging.
