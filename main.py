import argparse
import zipfile
import sys


def main():
    parser = argparse.ArgumentParser(description="Emulate a command line for a virtual file system.")
    parser.add_argument("archive_name", help="Name of the archive file containing the virtual file system.")
    parser.add_argument("--script", help="Name of the script file to execute commands from.")
    args = parser.parse_args()

    try:
        zip_archive = zipfile.ZipFile(args.archive_name, 'r')
        all_files = zip_archive.namelist()
    except FileNotFoundError:
        print(f"Error: Archive file '{args.archive_name}' not found.")
        sys.exit(1)

    const_prompt = "root/{}> "

    working_path = ""
    previous_path = ""

    def checkDirectory(addres, pWay, allFiles):  # функция двигает дерикторию
        if addres == "~":  # абсолютный адрес
            return ""
        elif addres == ".." or addres == "-":
            if addres == '':
                return pWay
            else:
                pWay = "/" + pWay
                k = len(pWay) - 1
                while pWay[k] != "/":
                    pWay = pWay[:-1]
                    k -= 1
                pWay = pWay[:-1]
                pWay = pWay[1:]
                return pWay
        elif "/root" in addres:
            addres = addres.replace("/root", '')
            if addres in allFiles:
                return addres
            return "sh: cd: can't cd to " + addres + ": No such file or directory"
        elif pWay == '' and (addres + '/') in allFiles:  # последовательный адрес
            return addres
        elif pWay + '/' + addres + '/' in allFiles:
            return pWay + '/' + addres
        else:
            return "sh: cd: can't cd to " + addres + ": No such file or directory"

    def checkFile(addres, pWay, allFiles):  # функция двигает дерикторию
        if "/root" in addres:
            addres = addres.replace("/root/", '')
            if addres in allFiles:
                return addres
            return "cat: can't open" + addres + ": No such file or directory"
        elif pWay + '/' + addres in allFiles:
            return pWay + '/' + addres
        else:
            return "cat: can't open" + addres + ": No such file or directory"

    def CAT(outAdr, nameArch):
        with zipfile.ZipFile(nameArch) as myzip:
            with myzip.open(outAdr, 'r') as myfile:
                lines = [x.decode('utf8').strip() for x in myfile.readlines()]  # декод в текст
                for line in lines:
                    print(line)

    def PWD(help_way):
        if help_way == "":
            print("/root")
        else:
            print("/root/" + help_way + "/")

    def listFile(wayL, allFiles):
        counter = wayL.count('/')
        wayL += '/'
        for i in allFiles:
            if wayL == '/':
                if wayL in i and i != wayL:
                    if counter == (i.count('/')):
                        if i[-1] != '/':
                            print(i, end="    ")
                        else:
                            print(i[:-1], end="    ")
                    elif (counter == ((i.count('/') - 1)) and (i[-1] == '/')):
                        print(i[:-1], end="    ")
            else:
                if wayL in i and i != wayL:
                    if counter == (i.count('/') - 1):
                        if i[-1] != '/':
                            print(i, end="    ")
                        else:
                            print(i[:-1], end="    ")
                    elif (counter == ((i.count('/') - 2)) and (i[-1] == '/')):
                        print(i[:-1], end="    ")

    if args.script:
        try:
            with open(args.script, 'r') as script_file:
                script_lines = script_file.readlines()
                for line in script_lines:
                    command = line.strip()
                    if command == "exit":
                        break
                    elif command.startswith("cd "):
                        working_path = checkDirectory(command[3:], working_path, all_files)
                    elif command.startswith("cat "):
                        temp_output = checkFile(command[4:], working_path, all_files)
                        if "cat: can't open" in temp_output:
                            print(temp_output)
                        else:
                            CAT(temp_output, args.archive_name)
                    elif command == "pwd":
                        PWD(working_path)
                    elif command == "ls":
                        listFile(working_path, all_files)
                        print()
                    else:
                        print(f"sh: {command.split()[0]} not found")
        except FileNotFoundError:
            print(f"Error: Script file '{args.script}' not found.")
            sys.exit(1)
    else:
        while True:
            command = input(const_prompt.format(working_path))
            if command == "exit":
                break
            if command.startswith("cd "):
                working_path = checkDirectory(command[3:], working_path, all_files)
            elif command.startswith("cat "):
                temp_output = checkFile(command[4:], working_path, all_files)
                if "cat: can't open" in temp_output:
                    print(temp_output)
                else:
                    CAT(temp_output, args.archive_name)
            elif command == "pwd":
                PWD(working_path)
            elif command == "ls":
                listFile(working_path, all_files)
                print()
            else:
                print(f"sh: {command.split()[0]} not found")

if __name__ == "__main__":
    main()