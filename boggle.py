"""
This is Boggle game.
Your objective is to find as many words you can under 3 minutes.
This game has an option to play with GUI or without; if you want without,
add an argument in the terminal "--no-gui".

"""

# its included with main.py too
from gui import *

BOARD = Board()
GAME = Game(BOARD)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--no-gui':
        from threading import Thread

        try:
            timer_thread = Thread(target=check_timer)
            game_thread = Thread(target=main, args=[BOARD, GAME])
            timer_thread.daemon = True
            game_thread.daemon = True
            game_thread.start()
            timer_thread.start()
            while True:  # for the exception
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nUser exit.")
    else:
        Startmenu = StartMenu()
        Startmenu.customize_start_menu()
        Startmenu.start_gui()

        GAME = Game(BOARD, True)
        play = Gui(GAME, BOARD)
        play.customize_game()
        play.start_gui()
