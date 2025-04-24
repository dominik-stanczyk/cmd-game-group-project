import curses
import random
import time
import sys
import os
import json
import random

# Odczytujemy dane z pliku JSON
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    
map_1 = data["map_1"]
map_2 = data["map_2"]
map_3 = data["map_3"]
ui_1_map = data["ui_1_map"]
ui_2_map = data["ui_2_map"]
ui_3_map = data["ui_3_map"]
ui_5_map = data["ui_5_map"]
maps = [0, map_1, map_2, map_3]

#U+250x	─	━	│	┃	┄	┅	┆	┇	┈	┉	┊	┋	┌	┍	┎	┏

#U+251x	┐	┑	┒	┓	└	┕	┖	┗	┘	┙	┚	┛	├	┝	┞	┟

#U+252x	┠	┡	┢	┣	┤	┥	┦	┧	┨	┩	┪	┫	┬	┭	┮	┯

#U+253x	┰	┱	┲	┳	┴	┵	┶	┷	┸	┹	┺	┻	┼	┽	┾	┿

#U+254x	╀	╁	╂	╃	╄	╅	╆	╇	╈	╉	╊	╋	╌	╍	╎	╏

#U+255x	═	║	╒	╓	╔	╕	╖	╗	╘	╙	╚	╛	╜	╝	╞	╟

#U+256x	╠	╡	╢	╣	╤	╥	╦	╧	╨	╩	╪	╫	╬	╭	╮	╯

#U+257x	╰	╱	╲	╳	╴	╵	╶	╷	╸	╹	╺	╻	╼	╽	╾	╿

if os.name == 'nt': # Zmiana rozmiaru okna konsoli w zależności od systemu
    os.system('mode con: cols=195 lines=51')
elif os.name == 'posix':
    os.system('resize -s  195 51')

# ━ ┃ ┏ ┓ ┛ ┗ ┣ ┫ ┳ ┻
stdscr = curses.initscr()
curses.noecho() # Nie wyświetla wciśniętych klawiszy
curses.cbreak() # Odczytujemy klawisze bez blokowania
stdscr.keypad(True) # Możemy używać strzałek
stdscr.nodelay(True)
curses.curs_set(0)

player_char = '@'
blocking = ["┏", "┓", "┃", "━", "┗", "┛", "X", "_","┻", "┳", "┣", "┫", "@","I","P","G","O","W","V","M"]

offset = 2
playing = True
current_map = 1
inventory = []

alert = " * Poruszaj się za pomocą WSAD."
alert2= " * Interakcje z potworami"
alert3= " "
alert4= " "
alert5= " "
alert6= " "
alert7= " "
alert1 = " * Naciśnij P aby przerwać rozgrywkę."
    
items = []
defeat_text = ""
health_bar = 5
food_bar = 6
armor_bar = 15
attack_bar = 10
health_bar_symbol = "*"
food_bar_symbol = "+"
armor_bar_symbol = "╬"
attack_bar_symbol = "╇"
miecz = "miecz"
portfel = 5
klasa = ""

maxl = len(map_1)
maxc = len(map_1[0])
windowl = curses.LINES
windowc = curses.COLS


player_y = 17
player_x = 69

czas = 0
minuta = 30
godzina = 10
dzien = 1

encountered_monster = None

curses.start_color() # Kolory
curses.init_color(8, 500, 500, 500)
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
curses.init_pair(4, 8, curses.COLOR_BLACK)
green = curses.color_pair(1)
white = curses.color_pair(2)
blue = curses.color_pair(3)
gray = curses.color_pair(4)

ui_1 = curses.newwin(5, 51, 2, 143)
ui_2 = curses.newwin(15, 51, 7, 143)
ui_3 = curses.newwin(25, 51, 22, 143)
ui_5 = curses.newwin(3, 51, 46, 143)




def interact_npc_1():
    global alert
    stdscr.addstr(39,4, "")
    alert = " * Witaj przybyszu"
    refresh_ui()

def check_defeat():
    global playing, defeat_text
    if dzien >= 4:
        defeat_text = "Skończył ci się czas."
        defeat()
    elif health_bar == 0:
        defeat_text = "Pamiętaj aby jeść."
        defeat()
    elif armor_bar == 0:
        defeat_text = "Zostałeś pokonany w walce"
        defeat()
def defeat():
    global playing
    playing = False
    stdscr.clear()
    stdscr.addstr( windowl//2-2, windowc//2, "KONIEC")
    stdscr.addstr( windowl//2, windowc//2-8, defeat_text, gray | curses.A_BOLD)
    stdscr.addstr( windowl//2+2, windowc//2-2, "Q - wyjście")
    stdscr.refresh()
    stdscr.getch()
    while True:
        try:
            c = stdscr.getkey()
        except:
            c = ''
        if c == "q":
            sys.exit()
    

def draw_clock(): # Gra działa w około 50 klatkach na sekundę (time.sleep(0.02))
    global czas, minuta, godzina, dzien, playing, alert, food_bar, health_bar
    czas += 1
    # Ważna notka działa odejmowenie zdrowia po utracie paska jedzonka

    if czas == 45:
        minuta += 1
        czas = 0
    if minuta == 60:
        if food_bar >0:
            godzina += 1
            food_bar -= 1
            minuta = 0
        else:
            godzina += 1
            health_bar -=1
            minuta = 0
    if godzina == 24:
        dzien += 1
        godzina = 0
    if dzien == 4:
        playing = False
    current_time = time.strftime("%H:%M:%S")  # Bieżący czas w formacie godzin:minut:sekund
    ui_5.addstr(1, 3, f"{godzina:02}:{minuta:02}  <Dzień {dzien}>", curses.A_BOLD)  # Wyświetl czas

def draw_map():
    if current_map == 0:
        draw_map_1()  # Rysujemy mapę 1
    elif current_map == 1:
        draw_map_2()  # Rysujemy mapę 2
    elif current_map == 2:
        draw_map_3()  # Rysujemy mapę 3
def draw_map_1():
    
    for i in range(maxl):
        for j in range(maxc):
            if map_1[i][j] == "X": # Generowanie mapy z kolorami
                stdscr.addch(i+offset, j+offset, map_1[i][j], gray | curses.A_BOLD)
            elif map_1[i][j] == ",":
                stdscr.addch(i+offset, j+offset, map_1[i][j], green)
            elif map_1[i][j] == "_":
                stdscr.addch(i+offset, j+offset, map_1[i][j], white | curses.A_BOLD)
            else:
                stdscr.addch(i+offset, j+offset, map_1[i][j], white )
    stdscr.addch(player_y+offset, player_x+offset, player_char, green)
    
    stdscr.addstr(39,4, alert, gray)
    stdscr.addstr(40,4, alert2, gray)
    stdscr.addstr(41,4, alert3, gray)
    stdscr.addstr(42,4, alert4, gray)
    stdscr.addstr(43,4, alert5, gray)
    stdscr.addstr(44,4, alert6, gray)
    stdscr.addstr(45,4, alert7, gray)
    stdscr.addstr(46,4, alert1, gray)
    
def draw_map_2():
    for i in range(maxl):
        for j in range(maxc):
            if map_2[i][j] == "X": # Generowanie mapy z kolorami
                stdscr.addch(i+offset, j+offset, map_2[i][j], gray | curses.A_BOLD)
            elif map_2[i][j] == ",":
                stdscr.addch(i+offset, j+offset, map_2[i][j], green)
            elif map_2[i][j] == "_":
                stdscr.addch(i+offset, j+offset, map_2[i][j], white | curses.A_BOLD)
            else:
                stdscr.addch(i+offset, j+offset, map_2[i][j], white )
    stdscr.addch(player_y+offset, player_x+offset, player_char, green)
    
def draw_map_3():
    for i in range(maxl):
        for j in range(maxc):
            if map_3[i][j] == "X": # Generowanie mapy z kolorami
                stdscr.addch(i+offset, j+offset, map_3[i][j], gray | curses.A_BOLD)
            elif map_3[i][j] == ",":
                stdscr.addch(i+offset, j+offset, map_3[i][j], green)
            elif map_3[i][j] == "_":
                stdscr.addch(i+offset, j+offset, map_3[i][j], white | curses.A_BOLD)
            else:
                stdscr.addch(i+offset, j+offset, map_3[i][j], white )
    stdscr.addch(player_y+offset, player_x+offset, player_char, green)

def move(c):
    # Poruszanie graczem (WSAD)
    global player_y, player_x, current_map
    current_map_data = maps[current_map] # Poruszanie się w zależności od mapy
    
    if c == 'w' and current_map_data[player_y-1][player_x] not in blocking:
        player_y -= 1
    elif c == 'a' and current_map_data[player_y][player_x-1] not in blocking:
        player_x -= 1
    elif c == 'd' and current_map_data[player_y][player_x+1] not in blocking:
        player_x += 1
    elif c == 's' and current_map_data[player_y+1][player_x] not in blocking:
        player_y += 1
    
    # Zmiana mapy oraz pozycji gracza
    if current_map == 1 and player_x == 1 and player_y in [16,17,18]:
        player_x = 137
        player_y = 17
        current_map = 2
    if current_map == 1 and player_x in [68,69,70] and player_y == 1:
        player_x = 69
        player_y = 32
        current_map = 3
        
    if current_map == 2 and player_x == 138 and player_y in [16,17,18]:
        player_x = 2
        player_y = 17
        current_map = 1
    
    if current_map == 3 and player_x in [68,69,70] and player_y == 33:
        player_x = 69
        player_y = 2
        current_map = 1
        
    draw_map()
    
def draw_ui():
    for i in range(len(ui_1_map)):
        for j in range(len(ui_1_map[0])):
            ui_1.addch(i,j, ui_1_map[i][j])
    ui_1.addstr(1,2,f"Obecna mapa: {current_map}")
    
    for i in range(len(ui_2_map)):
        for j in range(len(ui_2_map[0])):
            ui_2.addch(i,j, ui_2_map[i][j])
    ui_2.addstr(2,3,f"[{player_x}], [{player_y}]")
    ui_2.addstr(4,3,f"health: {health_bar_symbol*health_bar}")
    ui_2.addstr(6,3,f"Food: {food_bar_symbol*food_bar}")
    ui_2.addstr(8,3,f"Armor: {armor_bar_symbol*armor_bar}")
    ui_2.addstr(10,3,f"Attack: {attack_bar_symbol*attack_bar}")
    ui_2.addstr(12,3,f"Portfel: ${portfel}.00")
    for i in range(len(ui_3_map)):
        for j in range(len(ui_3_map[0])):
            ui_3.addch(i,j, ui_3_map[i][j])
    ui_3.addstr(2,2, "Inventory :", curses.A_UNDERLINE | curses.A_BOLD)
    ui_3.addstr(4,2,f"{inventory}")

    for i in range(len(ui_5_map)):
        for j in range(len(ui_5_map[0])):
            ui_5.addch(i,j, ui_5_map[i][j])
    draw_clock()
        
def refresh_ui():
    stdscr.refresh()
    ui_1.refresh()
    ui_2.refresh()
    ui_3.refresh()
    ui_5.refresh()
def clear_ui():
    stdscr.clear()
    ui_1.clear()
    ui_2.clear()
    ui_3.clear()
    ui_5.clear() 
    


def in_range(v, vmin, vmax):
    # Sprawdzanie granic
    if v > vmax:
        return vmax
    if v < vmin:
        return vmin
    return v
    

def draw_menu(stdscr, selected_option):
    global windowl, windowc
    
    menu = ["Zagraj", "Informacje", "Wyjdź"]
    
    title = "Main Menu"
    # Pozycja tytułu menu
    title_x = (windowc // 2)-5
    title_y = (windowl // 2) -2
    
    # Dodanie tytułu menu
    stdscr.addstr(title_y, title_x, title, curses.A_BOLD)
    
    # Wyśrodkowanie menu
    start_x = (windowc // 2) -4
    start_y = windowl // 2
    
    # Rysowanie menu
    for id_menu, option in enumerate(menu):
        x = start_x
        y = start_y + id_menu
        if id_menu == selected_option:
            stdscr.addstr(y, x, option, curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, option)
    stdscr.refresh()


def menu():

    menu_options = ["Zagraj", "Informacje", "Wyjdź"]

    selected_option = 0
    selected_option1 = 0
    while True:
        draw_menu(stdscr, selected_option)

        key = stdscr.getch()

        if key == curses.KEY_DOWN:
            selected_option = (selected_option + 1) % len(menu_options)
        elif key == curses.KEY_UP:
            selected_option = (selected_option - 1) % len(menu_options)
        elif key == 10:
            if selected_option == 0:
                settings()
                stdscr.clear()
                draw_map_1()
                draw_ui()
                refresh_ui()
                break
            
            elif selected_option == 1:
                stdscr.clear()
                stdscr.addstr( 4, 5, " - INFORMACJE, wciśnij B aby powrócić")
                stdscr.refresh()
                stdscr.getch()
                while True:
                    key = stdscr.getch()
                    if key == ord('b'):
                        main()
            elif selected_option == 2: 
                sys.exit()

        stdscr.clear()
        
def draw_settings(stdscr, selected_option1): #rysowanie wyboru klasy postaci
    global windowl, windowc
    
    settings = ["Wojownik","Kupiec","Cywil"]
    
    title = "Wybierz klasę postaci"
    # Pozycja tytułu menu
    title_x = (windowc // 2)-10
    title_y = (windowl // 2) -2
    
    # Dodanie tytułu menu
    stdscr.addstr(title_y, title_x, title, curses.A_BOLD)
    
    # Wyśrodkowanie menu
    start_x = (windowc // 2) -4
    start_y = windowl // 2
    
    # Rysowanie menu
    for id_settings, option in enumerate(settings):
        x = start_x
        y = start_y + id_settings
        if id_settings == selected_option1:
            stdscr.addstr(y, x, option, curses.A_REVERSE)
        else:
            stdscr.addstr(y, x, option)
    stdscr.refresh()

def settings(): # wybor klasy postaci
    global klasa, portfel
    # Opcje menu
    settings_options = ["Wojownik","Kupiec","Cywil"]
    
    selected_option = 0
    selected_option1 = 0
    while True:
        draw_settings(stdscr, selected_option)
        
        key = stdscr.getch() # Odczytujemy przycisk (strzałka w górę i w dół)
        
        if key == curses.KEY_DOWN:  # Strzałka w dół
            selected_option = (selected_option + 1) % len(settings_options)
        elif key == curses.KEY_UP:  # Strzałka w górę
            selected_option = (selected_option - 1) % len(settings_options)
        elif key == 10:  # Enter
            if selected_option == 0:  # Zagraj
                klasa = "Wojownik"
                break
            elif selected_option == 1:
                klasa = "Kupiec"
                portfel = 20
                break
            elif selected_option == 2:
                klasa = "Cywil"
                break
        stdscr.clear()
        
def pause_game(): # Zatrzymywanie gry
    global playing, alert, alert1
    alert = ""
    alert1 = ""
    playing = False
    stdscr.clear()
    stdscr.addstr( windowl//2-2, windowc//2, "Gra została wstrzymana")
    stdscr.addstr( windowl//2, windowc//2+5, "P - kontynuj")
    stdscr.addstr( windowl//2+1, windowc//2+5, "Q - wyjście")
    stdscr.refresh()
    stdscr.getch()
    while True:
        try:
            c = stdscr.getkey()
        except:
            c = ''
        if c == "p":
            playing = True
            clear_ui()
            draw_ui()
            refresh_ui()
            break
        elif c == "q":
            sys.exit()

def dod_jedz():
    
    global food_bar, portfel, alert
    if (portfel -1) >=0:
        if food_bar <=9:
            portfel -=1
            x = food_bar +1 
            global alert
            stdscr.addstr(39,4, "")
            alert = " * dodano jedzenie"
            food_bar = x
        else:
            alert = " * jedzonko na full"
        refresh_ui()
    else:
        alert(" * Brak pieniędzy")

def miks_lecz():
    global health_bar, portfel, alert
    if (portfel - 2) >= 0:
        portfel -= 2 
        if health_bar <=9: 
            x = health_bar +1
            global alert
            stdscr.addstr(39,4, "")
            alert = " * dodano zycie"
            health_bar = x
        else:
            alert = " * hp na full"
        refresh_ui()
    else:
        alert = " * Brak pieniędzy"
    

def dod_miecz():
    
    global inventory, posiadanie_miecz, alert
    posiadanie_miecz = True
    if "miecz" in inventory:
    
        alert = " * masz juz miecz"
    else:    
        alert = " * wyciągnięto miecz ze skały"
        x = "miecz"
        inventory.append(x)



class Monster:
    def __init__(self, name, level_range, hp_base, attack_base):
        self.name = name
        self.level = random.randint(*level_range)
        self.hp = hp_base + self.level * 2
        self.attack = attack_base + self.level * 1

    def get_stats(self):
        return f"{self.name} lvl {self.level} HP:{self.hp} Atak:{self.attack}"

    def receive_damage(self, damage):
        self.hp -= damage
        return self.hp <= 0

    def __str__(self):
        return self.get_stats()

class Goblin(Monster):
    def __init__(self):
        super().__init__("Goblin", (1, 3), 5, 1) # ("Goblina"(1,3) - poziomy
                                                  # ,5,1) - bazowa liczba hp i ataku

class Ork(Monster):
    def __init__(self):
        super().__init__("Ork", (1, 3), 8, 2)

class Wiedzma(Monster):
    def __init__(self):
        super().__init__("Wiedźma", (1, 3), 6, 1)

class Wilk(Monster):
    def __init__(self):
        super().__init__("Wilk", (1, 3), 5, 2)

def potworki_statystyki():
    global alert, alert2, alert3, alert4, alert5, alert6, alert7, encountered_monster

    # Losowy potwór
    potwor_klasy = [Goblin, Ork, Wiedzma, Wilk]
    potwor = random.choice(potwor_klasy)()
    encountered_monster = potwor

    # Czyścimy linie
    stdscr.addstr(39, 4, " " * 60)
    stdscr.addstr(40, 4, " " * 60)
    stdscr.addstr(41, 4, " " * 60)
    stdscr.addstr(42, 4, " " * 60)
    stdscr.addstr(43, 4, " " * 60)
    stdscr.addstr(44, 4, " " * 60)
    stdscr.addstr(45, 4, " " * 60)
    # Alerty
    alert = encountered_monster  # pokazujemy statystyki
    alert2 = ""
    alert3 = "Czy chcesz walczyć z tym potworem? (y/n)"
    alert4 = ""
    alert5 = ""
    alert6 = ""
    refresh_ui()

def rozpocznij_walke(monster):
    global alert, alert2, alert3, alert4, alert5, alert6,alert7, health_bar, attack_bar, inventory, armor_bar

    # Gracz atakuje
    player_attack_m = attack_bar
    monster_dead = monster.receive_damage(player_attack_m)
    alert2 = f"Zaatakowałeś {monster.name} i zadałeś {player_attack_m} obrażeń!"
    alert = str(monster)
    refresh_ui()
    time.sleep(0.5)

    if monster_dead:
        alert6 = f"{monster.name} pokonany!"
        drop_choice = random.randint(1, 4)  # Losowanie liczby od 1 do 4
    
        if drop_choice == 1:
            drop = "armor"
            inventory.append(drop)
            armor_bar += 2
            alert7 = "Znaleziono: armor (+2 do pancerza)"
        elif drop_choice == 2:
            drop = "weapon"
            inventory.append(drop)
            attack_bar += 2
            alert7 = "Znaleziono: weapon (+2 do ataku)"
        elif drop_choice == 3:
            drop = "health_potion"
            inventory.append(drop)
            alert7 = "Znaleziono: health potion."
        elif drop_choice == 4:
            drop = "speed_potion"
            inventory.append(drop)
            alert7 = "Znaleziono: speed potion."

        refresh_ui()
        return

    # Potwór kontratakuje
    monster_attack = monster.attack
    health_bar -= monster_attack
    alert4 = f"{monster.name} kontratakuje i zadaje {monster_attack} obrażeń!"
    
    refresh_ui()

def main():
    global playing, encountered_monster, alert2, alert3, alert4, alert5, alert6, alert7  # dodajemy alert2 jako globalną
    menu()
    while playing:
        # odczytywanie wartości z klawiatury
        try:
            c = stdscr.getkey()
        except:
            c = ''
        
        if c in 'asdw':
            refresh_ui()
            move(c)

        elif c == 'p':
            pause_game()

        elif c == 'e':  # Interakcja z przedmiotami, npcami, potworami
            if current_map == 1 and player_x in [20,21,22] and player_y in [25,26,27]:
                interact_npc_1()
            elif current_map == 1 and player_x in [95,96] and player_y in [31,32]:
                dod_jedz()
            elif current_map == 1 and player_x in [91,92] and player_y in [31,32]:
                miks_lecz()
            elif current_map == 1 and player_x in [37,38,39] and player_y in [22,23,24]:
                dod_miecz()
            elif current_map == 1 and player_x in [81,82,83] and player_y in [8,9,10]:
                encountered_monster = Goblin()
                alert = f"Naprzeciw Ciebie stoi {encountered_monster.name} (lvl {encountered_monster.level})"
                alert3 = "Czy chcesz walczyć? (y/n)"
                refresh_ui()
            elif current_map == 1 and player_x in [68,69,70] and player_y in [14,15,16]:
                encountered_monster = Ork()
                alert = f"Naprzeciw Ciebie stoi {encountered_monster.name} (lvl {encountered_monster.level})"
                alert3 = "Czy chcesz walczyć? (y/n)"
                refresh_ui()
            elif current_map == 1 and player_x in [91,92,93] and player_y in [16,17,18]:
                encountered_monster = Wiedzma()
                alert = f"Naprzeciw Ciebie stoi {encountered_monster.name} (lvl {encountered_monster.level})"
                alert3 = "Czy chcesz walczyć? (y/n)"
                refresh_ui()
            elif current_map == 1 and player_x in [80,81,82] and player_y in [22,23,24]:
                encountered_monster = Wilk()
                alert = f"Naprzeciw Ciebie stoi {encountered_monster.name} (lvl {encountered_monster.level})"
                alert3 = "Czy chcesz walczyć? (y/n)"
                refresh_ui()

        elif c == 'q':
            pass  # jedzenie, jeśli pełny to wypisuje MAX

        elif c == 'y':
            if encountered_monster:
                rozpocznij_walke(encountered_monster)
                encountered_monster = None
                alert5 = "Zaczynamy mordobicie!"
                refresh_ui()

        elif c == 'n':
            if encountered_monster:
                alert5 = "Zrezygnowałeś z walki."
                encountered_monster = None
                refresh_ui()

        # Rysowanie map i UI
        if current_map == 1:
            draw_map_1()
        elif current_map == 2:
            draw_map_2()
        elif current_map == 3:
            draw_map_3()
        draw_ui()

        check_defeat()
        time.sleep(0.02)

main()