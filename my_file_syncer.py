import shutil
import filecmp
from colorama import Fore, Back, Style
from itertools import zip_longest
from pathlib import Path
import os

#Instrucciones: crear una copia del script en el directorio de interés. El directorio debe tener el mismo nombre y estructura
#tanto en OneDrive como en el disco D: para que el script sea útil. Correr el script en el directorio de interés.

def pathOneDriveToD(directory):
    if directory.__str__()[:11] == "D:\OneDrive":
        dir = directory.__str__()[:2]+directory.__str__()[11:]
        return Path(dir)

def pathDToOneDrive(directory):
    if directory.__str__()[:11] != "D:\OneDrive":
        dir = directory.__str__()[:2]+"\\OneDrive\\"+directory.__str__()[3:]
        return Path(dir)

#Creador de árbol recursivo
def tree(dir_path: Path, prefix: str=''):
    # prefix components:
    space =  '    '
    branch = '│   '
    # pointers:
    tee =    '├── '
    last =   '└── '
    """A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """    
    contents = list(dir_path.iterdir())
    # contents each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path.name
        if path.is_dir(): # extend the prefix and recurse:
            extension = branch if pointer == tee else space 
            # i.e. space because last, └── , above so no more |
            yield from tree(path, prefix=prefix+extension)

def dirSideToSidePrint(directory1, directory2):
    fixwidht = 60
    for line1,line2 in zip_longest(tree(directory1),tree(directory2),fillvalue = ""):
        if (line1 == ""):
            line1 = " "*60
        if (len(line1) > 60):
            line1 = line1[:60]
        else:
            line1 = line1 + " "*(60-len(line1))
        print (line1 + line2)

def getFilesFromPath(dir_path: Path, pathlist, deep = True):
    for path in list(dir_path.iterdir()):
        pathlist.append(path)
        if deep and path.is_dir():
            getFilesFromPath(path,pathlist)
    return pathlist

def getFilepathAndFilename(directory,file):
    os.chdir(directory)
    return os.path.abspath(file)

def makeFilePath(directory,object):
    return directory.__str__()+"\\"+object

def modificationTime(filepath):
    return os.stat(filepath).st_mtime

def excecuteActions(filesToCopy,dirsToCopy):
    print("Cambios en:")
    for file in filesToCopy:
        print(file[0])
    for dir in dirsToCopy:
        print(dir[0])
    op = input("¿Realizar cambios? y para SI")
    if op == "y":
        for file in filesToCopy:
            shutil.copy2(file[0],file[1])
        for dir in dirsToCopy:
            shutil.copytree(dir[0],dir[1])

def filesToActualize(mismatch_files,directory1,directory2,files_to_copy):
    for file in mismatch_files:
        filepath1 = getFilepathAndFilename(directory1,file)
        filepath2 = getFilepathAndFilename(directory2,file)
        if modificationTime(filepath1) > modificationTime(filepath2):
            files_to_copy.append((filepath1,directory2))
        else:
            files_to_copy.append((filepath2,directory1))

def objectsToDuplicate(dircmp,filesToCopy,dirsToCopy,directory1,directory2):
    for object in dircmp:
        objectPath = makeFilePath(directory1, object)
        if os.path.isfile(objectPath):
            filesToCopy.append((objectPath,directory2))
        elif os.path.isdir(objectPath):
            destinationPath = makeFilePath(directory2,object)
            dirsToCopy.append((objectPath,destinationPath))

def dirPathMaker(common_dirs,common_dirs_paths,directory):
    for dir in common_dirs:
        dir_path = makeFilePath(directory,dir)
        common_dirs_paths.append(dir_path)

def main(directory1):
    print(Fore.GREEN + "Examinando la carpeta '{}'".format(os.path.basename(directory1)) + Style.RESET_ALL)
    if directory1.__str__()[:11] == "D:\OneDrive":
        directory2 = pathOneDriveToD(directory1)
    else:
        directory2 = pathDToOneDrive(directory1)

    #DIRECTORIOS DE PRUEBAS
    directory1 = Path("D:\OneDrive\Proyectos_Code\Python_STUF_I_MADE\\testing")
    directory2 = Path("D:\OneDrive\Proyectos_Code\Python_STUF_I_MADE\\testing2")

    dcomp = filecmp.dircmp(directory1,directory2)
    
    math_files = dcomp.same_files
    mismatch_files = dcomp.diff_files
    dirLeftErrors = dcomp.left_only
    dirRigthErrors = dcomp.right_only
    error_files = dirLeftErrors + dirRigthErrors

    dirSideToSidePrint(directory1, directory2)
    #print(Fore.RED + 'some red text'+ Style.RESET_ALL)

    print("\nComparacion")
    print("Iguales :", math_files)
    print("Diferentes :", mismatch_files)
    print("Faltantes :", error_files)
    print()

    files_to_copy = []
    
    if len(mismatch_files) > 0:
        filesToActualize(mismatch_files,directory1,directory2,files_to_copy)
    
    dirs_to_copy = []
    
    if len(dirLeftErrors) > 0:
        objectsToDuplicate(dirLeftErrors,files_to_copy,dirs_to_copy,directory1,directory2)
    
    if len(dirRigthErrors) > 0:
        objectsToDuplicate(dirRigthErrors,files_to_copy,dirs_to_copy,directory2,directory1)
    
    common_dirs_paths = []
    common_dirs = dcomp.common_dirs
    if len(common_dirs) > 0:
        dirPathMaker(common_dirs,common_dirs_paths,directory1)

    if len(files_to_copy) > 0 or len(dirs_to_copy) > 0:
        #excecuteActions(files_to_copy,dirs_to_copy)
        pass
    else:
        print("No hay acciones que realizar en la carpeta '{}'".format(os.path.basename(directory1)))
    
    if len(common_dirs_paths) > 0:
        for dir in common_dirs_paths:
            pass
            #main(dir)

#set current working directory as the directory where this script is located
os.chdir(os.path.dirname(os.path.abspath(__file__)))
directory = Path(os.getcwd())
#Stars script
main(directory)