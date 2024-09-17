import shutil
import filecmp
from colorama import Fore, Back, Style
from itertools import zip_longest
from pathlib import Path
import os
import sys
from functools import partial
import humanize

valid_ok = ["y","Y","1","si","ok","ya","OK","s","sí"]

#Instrucciones: crear una copia del script en el directorio de interés. El directorio debe tener el mismo nombre y estructura
#tanto en OneDrive como en el disco D: para que el script sea útil. Correr el script en el directorio de interés.

def forcePath(directory):
    if directory.__str__()[:11] == "D:\OneDrive":
        dir = directory.__str__()[:2]+directory.__str__()[11:]
    elif directory.__str__()[:9] == "E:\Backup":
        dir = "D:\\"+directory.__str__()[9:]
    else:
        dir = directory
    return Path(dir)

def pathOneDriveToD(directory):
    if directory.__str__()[:11] == "D:\OneDrive":
        dir = directory.__str__()[:2]+directory.__str__()[11:]
        return Path(dir)

def pathDToOneDrive(directory):
    if directory.__str__()[:11] != "D:\OneDrive":
        dir = directory.__str__()[:2]+"\\OneDrive\\"+directory.__str__()[3:]
        return Path(dir)

def pathEToD(directory):
    if directory.__str__()[:9] == "E:\Backup":
        dir = "D:\\"+directory.__str__()[9:]
        return Path(dir)

def pathDToE(directory):
    if directory.__str__()[:9] != "E:\Backup":
        dir = "E:\\Backup\\"+directory.__str__()[3:]
        return Path(dir)

def definePaths(directory1,config):
    if config == "ex":
        long = 9
        base_path = "E:\Backup"
        pathToD = pathEToD
        pathDTo = pathDToE
    else:
        long = 11
        base_path = "D:\OneDrive"
        pathToD = pathOneDriveToD
        pathDTo = pathDToOneDrive

    if directory1.__str__()[:long] == base_path:
        directory2 = pathToD(directory1)
    else:
        directory2 = pathDTo(directory1)

    if not(os.path.isdir(directory2)):
        print("{} no es un directorio válido".format(directory2))
        if config != "SI":
            return None
    return directory2

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
    """Imprimir árboles de dos directorios uno al lado del otro.
    """    
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

def getFilesFromPath(dir_path: Path, pathlist, deep = True, all = True):
    """Recolectar listado de objetos dentro de un directorio dado.
    deep = True busca recursivamente dentro del directorio
    all = True -> incluye archivos y carpetas. False -> sólo carpetas
    """
    for path in list(dir_path.iterdir()):
        if all:
            pathlist.append(path)
        else:
            if path.is_dir():
                pathlist.append(path)
        if deep and path.is_dir():
            getFilesFromPath(path,pathlist,True,all)
    return pathlist

def searchForBigDir(pathlist):
    """Busca directorios cuyo tamaño sea mayor a 4 GB (tamaño arbitrario) y
    agrega su índice a lista de retorno. Si lista está vacío, no hay directorios grandes
    """    
    bigDirs=[]
    for dir in pathlist:
        if getFolderSize(dir) > 4294967296:
            bigDirs.append(os.path.abspath(dir))
    return bigDirs

def getFolderSize(p):
   prepend = partial(os.path.join, p)
   return sum([(os.path.getsize(f) if os.path.isfile(f) else getFolderSize(f)) for f in map(prepend, os.listdir(p))])

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

def ignoreMenu():
    print("\n¿Qué desea hacer?")
    print("1. Incluir todas las carpetas")
    print("2. Ignorar todas las carpetas")
    print("3. Seleccionar carpetas a ignorar")
    op = 0
    print 
    while op not in [1,2,3]:
        op = input("Ingrese 1, 2 o 3: ")
        try:
            int(op)
        except:
            print("Opción no válida. Ingrese sólo números")
        else:
            op = int(op)
            if op not in [1,2,3]:
                print("Opción no válida. Inténtelo de nuevo")
    return op

def selectIgnoredDirs(ignoreList):
    print("\nCarpetas que se pueden ignorar: ")
    for i,dirname in enumerate(ignoreList):
        print (Fore.LIGHTCYAN_EX + '{}. {}'.format(i+1,dirname) + Style.RESET_ALL)
    indexToIgnore = ignoredDirsMenu(len(ignoreList))
    dirsToIgnore = []
    for i in indexToIgnore:
        # Agregar solo el basename a ignoreList
        # filecmp.dircmp ignore requiere el basename, no el path entero!
        dirsToIgnore.append(os.path.basename(Path(ignoreList[i])))
    return dirsToIgnore

def ignoredDirsMenu(num):
    """Retorna una lista de índices válidos para generar lista de paths ignorados
    a partir de la entrada del usuario, en formato "num1 num2 num3..."
    """
    validInput = False
    while validInput == False:
        print("\nINGRESE LOS NÚMEROS DE LAS CARPETAS QUE DESEA IGNORAR SEPARADOS POR ESPACIOS: ")
        print("(Ingrese 0 para cancelar y NO ingnorar carpetas)")
        userInput = input()
        userInput = userInput.split()
        ignoredNums = []
        if userInput[0] == "0":
            validInput = True
            print("Operación cancelada. No se ignorarán carpetas")
        else:
            try:
                for opnum in userInput:
                    opcandidate = int(opnum)
                    if (opcandidate > num or opcandidate < 1):
                        raise IndexError()
                    ignoredNums.append(opcandidate - 1)
                validInput = True
            except ValueError:
                print('Las entrada <{}> no es un número válido. Inténtelo de nuevo.'.format(opnum))
            except IndexError:
                print('La entrada <{}> está por fuera de la numeración'.format(opcandidate))
            except:
                print("Ocurrió algún error, inténtelo de nuevo")
    return ignoredNums

def main_workflow(directory1,directory2,dir_name,config,autoMode):
    # Detectar posibles directorios que se deseen ignorar por su tamaño mayor. Esto se ejecutará 
    # siempre que se incluya OneDrive. O sea, NO se ejecuta si sólo se considera disco externo (config = "ex")
    if config != "ex":
        pathlist = []
        pathlist = getFilesFromPath(directory1,pathlist,False,False)
        ignoreList = searchForBigDir(pathlist)

        if ignoreList:
            print(Fore.RED + '\nATENCIÓN' + Style.RESET_ALL)
            print("Los siguientes directorios tienen tamaño mayor a 4 GB: ")
            for dirname in ignoreList:
                print('{:>8}'.format( humanize.naturalsize(getFolderSize(Path(dirname))) ) + " " + Fore.CYAN + dirname + Style.RESET_ALL)
            op = ignoreMenu()
            # Explicitación de opciones disponibles
            if op == 3:
                ignoreList = selectIgnoredDirs(ignoreList)
            elif op == 2:
                ignoreList = [os.path.basename(Path(dir)) for dir in ignoreList]
            elif op == 1:
                ignoreList = []
        if ignoreList:
            print("Carpetas que se " + Fore.RED + "ignorarán" + Style.RESET_ALL + ": ")
            for dir in ignoreList:
                print (Fore.CYAN +  os.path.abspath(Path(dir)) + Style.RESET_ALL)
    else:
        ignoreList = []

    print(".", end = '')
    dcomp = filecmp.dircmp(directory1,directory2,ignoreList)
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
    
    if len(files_to_copy) > 0 or len(dirs_to_copy) > 0:
        describeActions(dirs_to_copy,dir_name,mismatch_files,error_files)
        if autoMode == 1:
            excecuteActions(files_to_copy,dirs_to_copy)
        else:
            op = input("¿Realizar cambios? (ingrese 1 , Y ó si para aceptar): ")
            if op in valid_ok:
                excecuteActions(files_to_copy,dirs_to_copy)
            else:
                print("No se realizaron las acciones mencionadas")
    else:
        print("No hay acciones que realizar en la carpeta '{}'".format(os.path.basename(directory1)))
    
    print()
    
    if len(common_dirs_paths) > 0:
        print(Fore.YELLOW + 'Hay subcarpetas disponibles: '+ Style.RESET_ALL)
        for dir in common_dirs_paths:
            if autoMode == 1:
                print("Entrando en "+ Fore.GREEN + '{}'.format(os.path.split(dir)[1]) + Style.RESET_ALL)
                main(Path(dir),config, 1,0)
            else: 
                op = input("¿Desea analizar la subcarpeta "+ Fore.GREEN + '{}'.format(os.path.split(dir)[1]) + Style.RESET_ALL 
                        + "? \n(ingrese 1 , y ó si para aceptar | ingrese 2 para CONTINUAR EN MODO AUTOMATICO: ")
                if op in valid_ok:
                    main(Path(dir),config, 0,0)
                elif op == "2":
                    main(Path(dir),config, 1,0)
                else:
                    print("No se analizará la carpeta mencionada")

def main(directory1,config,autoMode = 0,firstTime = 1):
    dir_name = os.path.basename(directory1)
    print(Fore.BLUE + "Examinando la carpeta '{}'".format(dir_name) + Style.RESET_ALL)
    
    if config == "both":
        both = 1
        directory2 = definePaths(directory1, "ex")
        directory3 = definePaths(directory1, "onedrive")
    else:
        directory2 = definePaths(directory1, config)
    
    if autoMode == 1:
        print(Fore.RED + "Trabajando en modo Automático" + Style.RESET_ALL)
    print("Paths a examinar:")
    print(Fore.CYAN + os.path.abspath(directory1))
    print(os.path.abspath(directory2) + Style.RESET_ALL)
    if directory2 is None:
        sys.exit("Directorio gemelo no válido")
    
    if firstTime == 1:
        print("¿Desea ejecutar en modo " + Fore.RED + "Automático" + Style.RESET_ALL + "?: " )
        print("ingrese 1 , Y ó si para aceptar")
        if input() in valid_ok:
            autoMode = 1
        else:
            autoMode = 0

    main_workflow(directory1,directory2,dir_name,config,autoMode)
    if both == 1:
        main_workflow(directory1,directory3,dir_name,config,autoMode)






if __name__ == '__main__':
    #set current working directory as the directory where this script is located
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    current_path = os.getcwd()
    directory = forcePath(Path(current_path[:1].upper() + current_path[1:]))
    if not(os.path.isdir(directory)):
        sys.exit("Directorio en Disco Duro no válido")

    #Stars script
    print(Fore.YELLOW + "\n****** MY FILE SYNCER :) ******\n" + Style.RESET_ALL)
    if len(sys.argv) == 1:
        sys.argv.append("THIS_IS_NOT_A_TEST")
    try:
        main(directory,sys.argv[1])
    except KeyboardInterrupt:
        print('\n\nInterrupted\n')
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
