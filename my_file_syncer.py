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

def paintingNames(path: Path,error_files,mismatch_files,directory):
    are_same_directory = directory.__str__() == os.path.split(path)[0].__str__()
    if path.name in error_files and are_same_directory:
        return Fore.RED + path.name + Style.RESET_ALL
    elif path.name in mismatch_files:
        return Fore.YELLOW + path.name + Style.RESET_ALL
    else:
        return path.name

#Creador de árbol recursivo
def tree(dir_path: Path, error_files, mismatch_files,directory, prefix: str=''):
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
    if Path(__file__) in contents:
        contents.remove(Path(__file__))
    # contents each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        object_name = paintingNames(path,error_files,mismatch_files,directory)
        yield prefix + pointer + object_name
        if path.is_dir(): # extend the prefix and recurse:
            extension = branch if pointer == tee else space 
            # i.e. space because last, └── , above so no more |
            yield from tree(path, error_files, mismatch_files, directory, prefix=prefix+extension)

def dirSideToSidePrint(directory1, directory2,error_files, mismatch_files):
    fixwidht = 70
    print("{:<70} {:<70}".format(str(directory1), str(directory2)))
    for line1,line2 in zip_longest(tree(directory1,error_files,mismatch_files,directory1),tree(directory2,error_files,mismatch_files,directory2),fillvalue = ""):
        if (line1 == ""):
            line1 = " "*fixwidht
        if (len(line1) > fixwidht):
            line1 = line1[:fixwidht]
        else:
            line1 = line1 + " "*(fixwidht-len(line1))
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

def describeActions(dirs_to_copy,dir_name,mismatch_files,error_files):
    print()
    print(Fore.GREEN + "Cambios que deben realizarse en los directorios base '{}':".format(dir_name) + Style.RESET_ALL)
    print("Archivos a actualizar: ")
    for file in mismatch_files:
        print(Fore.YELLOW + file + Style.RESET_ALL)
    print("Archivos o directorios faltantes por duplicar: ")
    for file in error_files:
        print(Fore.RED + file + Style.RESET_ALL)
    for dir in dirs_to_copy:
        print(Fore.RED + dir[0] + Style.RESET_ALL)
    print()

def excecuteActions(files_to_copy,dirs_to_copy):
    for file in files_to_copy:
        print(".", end = '')
        shutil.copy2(file[0],file[1])
    for dir in dirs_to_copy:
        print(".", end = '')
        shutil.copytree(dir[0],dir[1])
    print("")

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

def dirPathCollector(common_dirs,common_dirs_paths,directory):
    for dir in common_dirs:
        dir_path = makeFilePath(directory,dir)
        common_dirs_paths.append(dir_path)

def main_workflow(directory1,directory2,dir_name,config):
    print(".", end = '')
    dcomp = filecmp.dircmp(directory1,directory2)
    print(".", end = '')
    match_files = dcomp.same_files
    print(".", end = '')
    mismatch_files = dcomp.diff_files
    print(".", end = '')
    dirLeftErrors = dcomp.left_only
    print(".", end = '')
    dirRigthErrors = dcomp.right_only
    print(".", end = '')
    if os.path.basename(__file__) in dirLeftErrors:
        dirLeftErrors.remove(os.path.basename(__file__))
    elif os.path.basename(__file__) in dirRigthErrors:
        dirRigthErrors.remove(os.path.basename(__file__))
    error_files = dirLeftErrors + dirRigthErrors
    print(".", end = '')

    print(Fore.GREEN + '\nComparación de árboles de ambos directorios: '+ Style.RESET_ALL)
    dirSideToSidePrint(directory1, directory2,error_files,mismatch_files)
    #print(Fore.RED + 'some red text'+ Style.RESET_ALL)

    print(Fore.GREEN + "\nComparacion dentro de los directorios '{}'".format(dir_name) + Style.RESET_ALL)
    print("Iguales :", match_files)
    print("Diferentes :", mismatch_files)
    print("Faltantes :", error_files)

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
        dirPathCollector(common_dirs,common_dirs_paths,directory1)

    valid_ok = ["y","Y","1","si","ok","ya","OK","s"]
    if len(files_to_copy) > 0 or len(dirs_to_copy) > 0:
        describeActions(dirs_to_copy,dir_name,mismatch_files,error_files)
        if config == "AUTOMATICO": 
            excecuteActions(files_to_copy,dirs_to_copy)
        else:
            op = input("¿Realizar cambios? (ingrese 1 , y ó si para aceptar): ")
            if op in valid_ok:
                excecuteActions(files_to_copy,dirs_to_copy)
            else:
                print("No se realizaron las acciones mencionadas")
    else:
        print("No hay acciones que realizar en la carpeta '{}'".format(os.path.basename(directory1)))
    
    print()
    if len(common_dirs_paths) > 0:
        print(Fore.GREEN + 'Hay subcarpetas disponibles: '+ Style.RESET_ALL)
        for dir in common_dirs_paths:
            if config == "AUTOMATICO": 
                main(Path(dir),"AUTOMATICO")
            else: 
                op = input("¿Desea analizar la subcarpeta "+ Fore.GREEN + '{}'.format(os.path.split(dir)[1]) + Style.RESET_ALL + "? \n(ingrese 1 , y ó si para aceptar | ingrese 2 para CONTINUAR EN MODO AUTOMATICO: ")
                if op in valid_ok:
                    main(Path(dir),"THIS_IS_NOT_A_TEST")
                elif op == "2":
                    main(Path(dir),"AUTOMATICO")
                else:
                    print("No se analizará la carpeta mencionada")

def main(directory1,config = "SI"):
    dir_name = os.path.basename(directory1)
    print(Fore.BLUE + "Examinando la carpeta '{}'".format(dir_name) + Style.RESET_ALL)
    if directory1.__str__()[:11] == "D:\OneDrive":
        directory2 = pathOneDriveToD(directory1)
    else:
        directory2 = pathDToOneDrive(directory1)
    if not(os.path.isdir(directory2)):
        print("{} no es un directorio válido".format(directory2))
        if config != "SI":
            return
    
    #DIRECTORIOS DE PRUEBAS
    if config == "SI":
        directory1 = Path("D:\OneDrive\Proyectos_Code\Python_STUFF_I_MADE\\testing")
        dir_name = os.path.basename(directory1)
        directory2 = Path("D:\OneDrive\Proyectos_Code\Python_STUFF_I_MADE\\testing2")

    print("Paths examinados:")
    print(directory1)
    print(directory2)
    main_workflow(directory1,directory2,dir_name,config)


#set current working directory as the directory where this script is located
os.chdir(os.path.dirname(os.path.abspath(__file__)))
current_path = os.getcwd()
directory = Path(current_path[:1].upper() + current_path[1:])

#Stars script
print("\nMY FILE SYNCER :)\n")

main(directory,"THIS_IS_NOT_A_TEST")
#main(directory)