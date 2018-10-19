from vehicle_manager import VehicleManager
from event_processor import EventProcessor
from communication_terminal import CommunicationTerminal
import time

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.contrib.completers import WordCompleter
import sys

global is_exit
is_exit = False

def exit_handler():
    global is_exit
    is_exit = True
    sys.exit()

def empty_commandhandler():
    sys.stdout.flush()

def help_handler():
    print('All the available command is list as follow:')
    for key in commanddict:
        print(key)
    sys.stdout.flush()


if __name__ == '__main__':

    vm = VehicleManager()
    vm.initialize()
    ep = EventProcessor(vm)
    ep.start()
    CommunicationTerminal.setEventProcessor(ep)
    CommunicationTerminal.startServer()

    def showInfo_commandhandler():
        vm.show()
        ep.show()

    # interactive command line
    commanddict = {
        '': empty_commandhandler,
        'exit': exit_handler,
        'showinfo': showInfo_commandhandler
    }


    commanddict['help'] = help_handler
    commanddict['?'] = help_handler
    cmdList = []
    for key in commanddict:
        cmdList.append(key)

    cmdCompleter = WordCompleter(cmdList)

    while True:
        try:
            user_input = prompt('Local> ',
                                history=FileHistory('history.txt'),
                                completer=cmdCompleter,  patch_stdout=False)
        except KeyboardInterrupt:
            exit_handler()
        sys.stdout.flush()
        try:
            commanddict[user_input]()
        except KeyError:
            print('Unknow command, see \'help\'')
            sys.stdout.flush()

        if is_exit:
            exit_handler()
