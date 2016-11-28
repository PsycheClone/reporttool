from paramiko import SSHClient
from paramiko import AutoAddPolicy
import os
import sys
import signal
import subprocess
import socket
import getpass
from colorama import init
from termcolor import cprint
init(strip=not sys.stdout.isatty())  # strip colors if stdout is redirected

client = SSHClient()
client.set_missing_host_key_policy(AutoAddPolicy())

sites = ["Erfurt", "Sofia", "Sensors", "Kuching"]
machine_types = ["/mnt/rasco/rasco/log_RAM/", "/mnt/ismeca/ismeca/Log_RAM/"]
machines = []


def main():
    site_choice = ask_for_sites()
    site = sites[site_choice-1].lower()

    machine_type_choice = ask_for_machine_types()
    machine_type = machine_types[machine_type_choice-1]

    username, password = ask_for_credentials()

    machine_choice = ask_for_machine(username, password, site, machine_type)

    if machine_choice == 0:
        download_all_machines(username, password, site, machine_type)
    else:
        download_single_machine(username, password, site, machine_type, machines[machine_choice - 1], True)

    print_message('\ngoodbye', 'green')



def download_all_machines(username, password, site, machine_type):
    print_title()
    cprint("Downloading files for all machines...\n", 'green', attrs=['bold'])
    for machine in machines:
        download_single_machine(username, password, site, machine_type, machine, False)


def download_single_machine(username, password, site, machine_type, machine, clear):
    if clear:
        print_title()
        cprint("Downloading files for {}...\n".format(machine), 'green', attrs=['bold'])

    copying_message = "Copying files for {}".format(machine)
    sys.stdout.write(copying_message)
    if len(copying_message) < 20:
        sys.stdout.write("\t\t")
    else:
        sys.stdout.write("\t")
    sys.stdout.flush()

    stdin, stdout, stderr = client.exec_command("ls {}{} | grep '.*\.txt\|.*\.HTML'".format(machine_type, machine))
    ls_output = stdout.read()
    files = ls_output.split("\n")
    del files[-1]

    extension = ".txt" if "rasco" in machine_type else ".HTML"

    if len(files) > 0:
        rsync_cmd = 'sshpass -p {} /usr/bin/rsync -va {}@esb-b-test.{}.elex.be:{}{}/*{} {}/'\
                                 .format(password, username, site, machine_type, machine, extension, machine)

        rsync = subprocess.Popen([rsync_cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output = rsync.communicate()

        if extension is ".txt":
            output_list = filter(lambda x: "Statistic" in x, output[0].split("\n"))
        else:
            output_list = filter(lambda x: ".HTML" in x, output[0].split("\n"))

        try:
            os.killpg(os.getpgid(rsync.pid), signal.SIGTERM)
        except OSError:
            pass

        machine_ok(len(output_list))

    else:
        machine_not_ok()


def machine_ok(nfiles):
    sys.stdout.write(" [ ")
    cprint("OK", 'green', attrs=['bold'], end="")
    sys.stdout.write(" ] {} files copied.\n".format(nfiles))
    sys.stdout.flush()


def machine_not_ok():
    sys.stdout.write(" [ ")
    cprint("NK", 'red', attrs=['bold'], end="")
    sys.stdout.write(" ] 0 files copied.\n")
    sys.stdout.flush()


def ask_for_credentials():
    print_title()
    cprint("Provide credentials\n", 'green', attrs=['bold'])
    username = raw_input("Username: ")
    password = getpass.getpass("Password: ")
    return username, password


def ask_for_machine(username, password, site, machine_type):
    global machines

    clear_screen()
    try:
        client.connect("esb-a-test." + site + ".elex.be", 22, username, password)
        stdin, stdout, stderr = client.exec_command("ls {} | grep -v RECYCLER".format(machine_type))
        lsOutput = stdout.read()
        machines = lsOutput.split("\n")
        del machines[-1]

        print_message('MLX report tool\n', 'green')
        cprint("Available machines\n", 'green', attrs=['bold'])

        for index in xrange(0, len(machines), 2):
            printable_index = index+1
            tabbed_message = str(printable_index) + "/ " + machines[index]
            sys.stdout.write(tabbed_message)
            if len(tabbed_message) < 8:
                sys.stdout.write("\t\t\t")
            else:
                sys.stdout.write("\t\t")
            if index+1 < len(machines)-1:
                sys.stdout.write(str(printable_index+1) + "/ " + machines[index+1] + "\n")

        print "0/ all"
        sys.stdout.flush()
        return input("> ")
    except (socket.gaierror):
        cprint("Cannot connect.  Are you connected through the VPN tunnel?", 'red', attrs=['bold'])
        print
        print
        sys.exit(1)
    except (socket.error):
        cprint("Connection timed out, probably something wrong with the server.", 'red', attrs=['bold'])
        print
        print
        sys.exit(1)


def ask_for_machine_types():
    print_title()
    cprint("Available machine types\n", 'green', attrs=['bold'])
    number = 1
    for machinetype in machine_types:
        print str(number) + "/ " + machinetype
        sys.stdout.flush()
        number += 1
    return input("> ")


def ask_for_sites():
    print_title()
    cprint("Available sites\n", 'green', attrs=['bold'])
    number = 1
    for site in sites:
        print str(number) + "/ " + site
        sys.stdout.flush()
        number += 1
    return input("> ")


def print_title():
    clear_screen()
    print_message('MLX report tool\n', 'green')


def print_message(message, color):
    cprint(message, color, attrs=['bold'])


def clear_screen():
    subprocess.call(["printf", "\033c"])


def interupt_handler(signum, frame):
    if(signum == 2):
        print_message('\ngoodbye', 'green')
        sys.stdout.flush()
    sys.exit(0)


if __name__ == '__main__':
    try:
        signal.signal(signal.SIGINT, interupt_handler)  # Handling interrupt signal of ctrl-c
        main()
    except KeyboardInterrupt:
        # quit
        print_message('\ngoodbye', 'green')
        sys.stdout.flush()
        sys.exit(0)
