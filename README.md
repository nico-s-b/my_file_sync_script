A small script that help with the task to mantain a backup of directories of local disk in OneDrive and/or a External Drive on Windows. 
It looks for mismatched files between OneDrive, External Drive and local directories and checks if there are files missing or actualized in either directory.
It displays both directory trees side to side, highlitghting the differencies, and seeks actions to synchronize both directories.
It keeps the most recent file based on the modification date in case of outdated copies of files.
It copies the files that exists in one directory but are missing in the other.
  
Args: 
(none): sync OneDrive and local D:  
ex: sync E: and D:  
both: syn OneDrive, E: and D:  
  
It can enter on automode, and ask if you want to check on big size directories or prefer to ignore them.  
  
IMPORTANT: This scripts works if the directory structure/tree is basically the same in the local and backup directories. It assumes the same structure
The objetive is to fix differences that naturally occur over time as files and folders change slightly with use and keep diverging.
