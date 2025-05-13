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
blocking = ["┏", "┓", "┃", "━", "┗", "┛", "X", "_","┻", "┳", "┣", "┫", "@","I","P","G","O","W","V","M", "╭", "╮","H","J", "$", "i","|","#","┉","┊","┍","┖","┚","┑","Z","W"]

offset = 2
playing = True
current_map = 1
inventory = []

alert = " * Poruszaj się za pomocą WSAD."
alert1 = " * Naciśnij P aby przerwać rozgrywkę."
alert2= " "
alert3= " "
alert4= " "
alert5= " "
alert6= " "
alert7= " "

    
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
nazwa_mapy = "Wieś"
posiadanie_kilof = False
posiadanie_miecz = False
miecze = 0
zbroje = 0
mikstury_leczenia = 0
cena_miecz = 75
cena_zbroja = 40
przeszukano_skrzynie_1 = False
posiadanie_wytrych = False
maxl = len(map_1)
maxc = len(map_1[0])
windowl = curses.LINES
windowc = curses.COLS
wytrych = "wytrych"
wyciągnieto_miecz = False
posiadanie_kubek = False
current_quest = 0
pokonano_wiedzma = 0
pokonano_zombie = 0
pokonano_wojownik = 0
quest_uruchomiony = False

player_y = 17
player_x = 69

mob1_x = 0
mob1_y = 0
mob2_x = 0
mob2_y = 0
mob3_x = 0
mob3_y = 0

czas = 0
minuta = 30
godzina = 10
dzien = 1

encountered_monster = None

curses.start_color() # Kolory
curses.init_color(8, 500, 500, 500)
curses.init_color(9, 1000, 1000, 0)
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
curses.init_pair(4, 8, curses.COLOR_BLACK)
curses.init_pair(5, 9, curses.COLOR_BLACK)

green = curses.color_pair(1)
white = curses.color_pair(2)
blue = curses.color_pair(3)
gray = curses.color_pair(4)

ui_1 = curses.newwin(5, 51, 2, 143)
ui_2 = curses.newwin(15, 51, 7, 143)
ui_3 = curses.newwin(25, 51, 22, 143)
ui_5 = curses.newwin(3, 51, 46, 143)


def generate_mob1():
    global map_3, mob1_x, mob1_y
    while True:
        mob1_x = random.randint(3, 50)
        mob1_y = random.randint(4, 20)
        if map_3[mob1_y][mob1_x] == " ":
            map_3[mob1_y][mob1_x] = "W" #Generuje wiedźmę w losowych koordynatach, sprawdza czy pole jest zajęte
            break

def generate_mob2():
    global map_3, mob2_x, mob2_y
    while True:
        mob2_x = random.randint(3, 50)
        mob2_y = random.randint(4, 20)
        if map_3[mob2_y][mob2_x] == " " and not is_near(mob2_x, mob2_y, mob1_x, mob1_y):
            map_3[mob2_y][mob2_x] = "Z"
            break

def generate_mob3():
    global map_3, mob3_x, mob3_y
    while True:
        mob3_x = random.randint(3, 50)
        mob3_y = random.randint(4, 20)
        if map_3[mob3_y][mob3_x] == " " and not is_near(mob3_x, mob3_y, mob1_x, mob1_y) and not is_near(mob3_x, mob3_y, mob2_x, mob2_y):
            map_3[mob3_y][mob3_x] = "@"
            break

def is_near(x1, y1, x2, y2):
    return abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1 #zwraca odległość odległość pomiędzy potworami
def interact_npc_1():
    global alert
    stdscr.addstr(39,4, "")
    alert3 = " * Witaj przybyszu"
    refresh_ui()

def interact_npc_2():
    global alert3, inventory, posiadanie_kilof
    
    if not posiadanie_kilof:
        inventory.append("kilof")
        posiadanie_kilof = True
        alert3 = " * Witaj, jestem górnikiem oto kilof, którym możesz zarobić swoje pierwsze pieniądze."
    else:
        alert3 = " * Posiadasz już kilof."
    
    refresh_ui()
def interact_npc_3():
    global playing, portfel, miecze, zbroje
    suma = cena_miecz * miecze + cena_zbroja * zbroje
    playing = False
    stdscr.clear()
    stdscr.addstr( windowl//2-10, windowc//2, "Kupiec")
    if miecze == 0 and zbroje == 0:
        stdscr.addstr( windowl//2-6, windowc//2+15, "S - Sprzedaj wszystkie przedmioty (brak)")
    else:
        stdscr.addstr( windowl//2-6, windowc//2+15, f"S - Sprzedaj wszystkie przedmioty (${suma})")
    stdscr.addstr( windowl//2-4, windowc//2+15, "Q - Powrót")
    stdscr.addstr( windowl//2-6, windowc//2-15, "Przedmioty z przeciwników")
    stdscr.addstr( windowl//2-4, windowc//2-15, f"Miecz: {miecze}x")
    stdscr.addstr( windowl//2-2, windowc//2-15, f"Zbroje: {zbroje}x")
    stdscr.refresh()
    stdscr.getch()
    while True:
        try:
            c = stdscr.getkey()
        except:
            c = ''
        if c == "q":
            playing = True
            clear_ui()
            draw_ui()   
            refresh_ui()
            break
        elif c == "s":
            portfel += suma
            miecze = 0
            zbroje = 0
            playing = True
            clear_ui()
            draw_ui()
            refresh_ui()
            break
def interact_npc_4():
    global alert3
    alert3 = " * Witaj przybyszu."
    draw_map_1()
    refresh_ui()
def interact_npc_quests():
    global alert3,alert4,portfel,current_quest, alert7,map_3,quest_uruchomiony
    if current_quest == 0:
        alert3 = " * Witaj, mam dla ciebie kilka zadań. Musisz mi pokazać, że jesteś tym właściwym."
        alert4 = " * Przynieś mi zaginiony kubek. Słyszałem, że zaginął gdzieś na północy."
        alert7 = " * Zdobądź stary kubek, podobno znajduje się na północy krainy."
        map_3[10][110] = "u"
        quest_uruchomiony = True
    elif current_quest == 1:
        inventory.remove("kubek")
        alert3 = " * Widzę, że udało ci się zdobyć kubek. Znaczy on dla mnie bardzo wiele. Oto twoja zapłata ($150)"
        portfel += 150
        current_quest +=1
    elif current_quest == 2:
        alert7 = ""
        alert3 = " * Twoim kolejnym zadaniem będzie zabicie 3 wiedźm."
        alert7 = " * Zabij 3 wiedźmy."
        current_quest += 1
    elif current_quest == 3:    
        if pokonano_wiedzma >= 3:
            alert3 = " * Udało ci się wykonać zadanie, oto zapłata ($200)."
            alert7 = ""
            current_quest +=1
            portfel += 200
        else:
            alert3 = f" * Wróć, kiedy pokonasz 3 wiedźmy."
    elif current_quest == 4:
        alert3 = " * Twoim ostatnim zadaniem będzie pokonanie 2 wojowników."
        alert7 = " * Pokonaj 2 wojowników."
        current_quest +=1
    elif current_quest == 5:
        if pokonano_wojownik >= 2:
            alert3 = " * Udało ci się wykonać zadanie, oto zapłata ($300)."
            portfel += 300
            alert7 = ""
            current_quest +=1
        else:
            alert3 = " * Przyjdź, kiedy pokonasz 2 wojowników."
    elif current_quest == 6:
        alert3 = " * Wykonałeś już wszystkie zadania."
            
        
def interact_npc_end():
    global portfel, alert3, map_1
    if portfel - 1000 >= 0:
        alert3 = f" * Aby uciec z tego miejsca musisz mi zapłacić $1000, czy chcesz to zrobić (T/N)?"
        draw_map_1()
        refresh_ui()
        stdscr.refresh()
        stdscr.getch()
        
        while True:
            try:
                c = stdscr.getkey()
            except:
                c = ''
            if c == "t":
            
                portfel -= 1000
                alert3 = " * Brama została otwarta, możesz opuścić teren."
                map_1[2][36] = "┄"
                map_1[2][37] = " "
                map_1[2][38] = " "
                map_1[2][39] = " "
                map_1[2][40] = "┄"
                draw_map_1
                refresh_ui()
                break
            elif c == "n":
                alert3 = " * Przyjdź do mnie, kiedy będziesz gotowy."
                refresh_ui()
                break
    else:
        alert3 = f" * Aby uciec z tego miejsca musisz mi zapłacić $1000, brakuje ci jeszcze ${1000-portfel} Wróć, kiedy będzie cię stać."
def ucieczka():
    global playing
    playing = False
    stdscr.clear()
    stdscr.addstr( windowl//2-2, windowc//2-5, "KONIEC")
    stdscr.addstr( windowl//2, windowc//2-35, "Jesteś jednym z niewielu, którym udało się uciec z tej krainy. Gratulacje.", gray | curses.A_BOLD)
    stdscr.addstr( windowl//2+2, windowc//2-7, "Q - wyjście")
    stdscr.refresh()
    stdscr.getch()
    while True:
        try:
            c = stdscr.getkey()
        except:
            c = ''
        if c == "q":
            sys.exit()
def interact_kopalnia():
    global portfel, food_bar, alert3
    if food_bar > 3:
        portfel += 5
        food_bar -= 1
        alert3 = f" * Wykopano złoto, stan portfela to ${portfel}."
        refresh_ui()
    else:
        alert3 = " * Jesteś zbyt zmęczony, zjedz coś aby kontynuować."
        refresh_ui()
    refresh_ui()

def check_defeat():
    global playing, defeat_text
    if dzien >= 4:
        defeat_text = "Skończył ci się czas."
        defeat()
    elif food_bar == 0:
        defeat_text = "Pamiętaj aby jeść."
        defeat()
    elif armor_bar == 0:
        defeat_text = "Zostałeś pokonany w walce"
        defeat()
def defeat():
    global playing
    playing = False
    stdscr.clear()
    stdscr.addstr( windowl//2-2, windowc//2-5, "KONIEC")
    stdscr.addstr( windowl//2, windowc//2-8, defeat_text, gray | curses.A_BOLD)
    stdscr.addstr( windowl//2+2, windowc//2-7, "Q - wyjście")
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
    ui_5.addstr(1, 3, f"{godzina:02}:{minuta:02}  <Dzień {dzien}>", curses.A_BOLD)  # Wyświetl czas


def draw_map_1():
    
    for i in range(maxl):
        for j in range(maxc):
            if map_1[i][j] == "X": # Generowanie mapy z kolorami
                stdscr.addch(i+offset, j+offset, map_1[i][j], gray | curses.A_BOLD)
            elif map_1[i][j] == ",":
                stdscr.addch(i+offset, j+offset, map_1[i][j], green)
            elif map_1[i][j] == "_":
                stdscr.addch(i+offset, j+offset, map_1[i][j], white | curses.A_BOLD)
            elif map_1[i][j] == "$":
                stdscr.addch(i+offset, j+offset, map_1[i][j], yellow | curses.A_BOLD)
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
            elif map_1[i][j] == "$":
                stdscr.addch(i+offset, j+offset, map_1[i][j], yellow | curses.A_BOLD)
            else:
                stdscr.addch(i+offset, j+offset, map_2[i][j], white )
    stdscr.addch(player_y+offset, player_x+offset, player_char, green)
    
    stdscr.addstr(39,4, alert, gray)
    stdscr.addstr(40,4, alert2, gray)
    stdscr.addstr(41,4, alert3, gray)
    stdscr.addstr(42,4, alert4, gray)
    stdscr.addstr(43,4, alert5, gray)
    stdscr.addstr(44,4, alert6, gray)
    stdscr.addstr(45,4, alert7, gray)
    stdscr.addstr(46,4, alert1, gray)
    
def draw_map_3():
    for i in range(maxl):
        for j in range(maxc):
            if map_3[i][j] == "X": # Generowanie mapy z kolorami
                stdscr.addch(i+offset, j+offset, map_3[i][j], gray | curses.A_BOLD)
            elif map_3[i][j] == ",":
                stdscr.addch(i+offset, j+offset, map_3[i][j], green)
            elif map_3[i][j] == "_":
                stdscr.addch(i+offset, j+offset, map_3[i][j], white | curses.A_BOLD)
            elif map_1[i][j] == "$":
                stdscr.addch(i+offset, j+offset, map_1[i][j], yellow | curses.A_BOLD)
            else:
                stdscr.addch(i+offset, j+offset, map_3[i][j], white )
    stdscr.addch(player_y+offset, player_x+offset, player_char, green)

    stdscr.addstr(39,4, alert, gray)
    stdscr.addstr(40,4, alert2, gray)
    stdscr.addstr(41,4, alert3, gray)
    stdscr.addstr(42,4, alert4, gray)
    stdscr.addstr(43,4, alert5, gray)
    stdscr.addstr(44,4, alert6, gray)
    stdscr.addstr(45,4, alert7, gray)
    stdscr.addstr(46,4, alert1, gray)

def move(c):
    # Poruszanie graczem (WSAD)
    global player_y, player_x, current_map, alert3, alert, alert4
    current_map_data = maps[current_map] # Poruszanie się w zależności od mapy
    
    if c == 'w' and current_map_data[player_y-1][player_x] not in blocking:
        player_y -= 1
        alert3 = ""
        alert4 = ""
        alert = ""
    elif c == 'a' and current_map_data[player_y][player_x-1] not in blocking:
        player_x -= 1
        alert3 = ""
        alert4 = ""
        alert = ""
    elif c == 'd' and current_map_data[player_y][player_x+1] not in blocking:
        player_x += 1
        alert3 = ""
        alert4 = ""
        alert = ""
    elif c == 's' and current_map_data[player_y+1][player_x] not in blocking:
        player_y += 1
        alert3 = ""
        alert4 = ""
        alert = ""
    
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
        
    
def draw_ui():
    for i in range(len(ui_1_map)):
        for j in range(len(ui_1_map[0])):
            ui_1.addch(i,j, ui_1_map[i][j])
    ui_1.addstr(1,2,f"Obecna mapa: {current_map}  ({nazwa_mapy})")
    
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
    ui_3.addstr(6,2,f"Miecze przeciwników: {miecze}x")
    ui_3.addstr(8,2,f"Zbroje przeciwników: {zbroje}x")
    ui_3.addstr(10,2,f"Mikstury leczenia: {mikstury_leczenia}x")

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
                stdscr.addstr( 6,5, " - WSAD - poruszanie postacią")
                stdscr.addstr( 8,5, " - 1 - użycie mikstury leczenia")
                stdscr.addstr( 10,5, " - 2 - założenie zbroi")
                stdscr.addstr( 12,5, " - E - interakcja z NPCtami i potworami.") 
                stdscr.addstr( 14,5, " - T/N - Opcja tak/nie (zatwierdzenie lub odrzucenie interakcji)")
                stdscr.addstr( 16,5, " - P - pauza")
                stdscr.addstr( 18,5, " - Q - wyjście")
                stdscr.addstr( 20,5, " - B - powrót do poprzedniego okna")
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
    global klasa, portfel, armor_bar, attack_bar,health_bar
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
                armor_bar = 7
                attack_bar = 7
                health_bar = 7
                break
            elif selected_option == 1:
                klasa = "Kupiec"
                portfel = 20
                armor_bar = 5
                attack_bar = 5
                health_bar = 5
                break
            elif selected_option == 2:
                klasa = "Cywil"
                armor_bar = 3
                attack_bar = 3
                health_bar = 3

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
        alert = " * Brak pieniędzy"

def miks_lecz():
    global health_bar, portfel, alert
    if (portfel - 2) >= 0:
        if health_bar <=9: 
            portfel -= 2
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
    
    global inventory, posiadanie_miecz, alert3
    posiadanie_miecz = True
    alert3 = " * wyciągnięto miecz ze skały"
    x = "miecz"
    inventory.append(x)
    map_1[23][38] = " "

def main():
    global playing, encountered_monster, alert2, alert3, alert4, alert5, alert6, alert7, nazwa_mapy, posiadanie_wytrych,wyciągnieto_miecz, przeszukano_skrzynie_1, portfel, miecze, zbroje, map_2,inventory, mikstury_leczenia, health_bar, armor_bar, pokonano_wojownik, pokonano_wiedzma, pokonano_zombie, current_quest, posiadanie_kubek
    menu()
    generate_mob1()
    generate_mob2()
    generate_mob3()
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
        elif c == '1':
            if mikstury_leczenia-1 >= 0:
                if health_bar +3 <= 9:
                    mikstury_leczenia-=1
                    health_bar +=3
                    alert3 = " * Użyto mikstury leczenia, przywrócono 3 punkty zdrowia."
                else:
                    health_bar = 9
                    alert4 = " * Osiągnięto pełen poziom zdrowia."
            else:
                alert4 = " * Nie posiadasz żadnych mikstur."
        
        elif c == '2':
            if zbroje-1 >= 0:
                if armor_bar+3 <=9:
                    zbroje-=1
                    armor_bar +=3
                    alert3 = " * Założono zbroję, dodano 3 punkty ochrony."
                elif armor_bar + 3 > 9:
                    armor_bar = 9
                    alert4 = " * Osiągnięto pełną zbroję."
            else:
                alert4 = " * Nie posiadasz żadnych zbroi."

        elif c == 'e':  # Interakcja z przedmiotami, npcami, potworami
            if current_map == 1 and player_x in [20,21,22] and player_y in [25,26,27]:
                interact_npc_1()
            elif current_map == 2 and player_x in [21,22] and player_y in [11,10]:
                interact_npc_2()
            elif current_map == 2 and player_x in [67,68] and player_y in [7,8]:
                interact_npc_3()
            elif current_map == 1 and player_x in [42,43,44] and player_y in [1,2]:
                interact_npc_end()
            elif current_map == 1 and player_x in [37,38,39] and player_y in [1,2]:
                ucieczka()
            elif current_map == 1 and player_x in [23,24,25] and player_y in [26,27,28]:
                interact_npc_4()
            elif current_map == 1 and player_x in [6,7,8] and player_y in [20,21,22]:
                interact_npc_quests()
            elif current_map == 3 and player_x in [109,110,111] and player_y in [9,10,11]:
                if quest_uruchomiony and not posiadanie_kubek:
                    map_3[10][110] = " "
                    alert3 = " * Znaleziono stary kubek"
                    inventory.append("kubek")
                    posiadanie_kubek = True
                    current_quest +=1
                    alert7 = ""
                
            elif current_map == 2 and player_x in [2,3,4] and player_y in [2,3]:
                if not posiadanie_wytrych:
                    alert3 = " * Zdobyto wytrych."
                    inventory.append(wytrych)
                    map_2[2][3] = " "
                    posiadanie_wytrych = True
                    draw_map_2()
                    refresh_ui()
            elif current_map == 2 and player_x in [11,12,13] and player_y in [32,33]:
                if posiadanie_wytrych and not przeszukano_skrzynie_1:
                    portfel += 100
                    miecze +=3
                    alert3 = f" * Przeszukano skarb, zdobyto $100 oraz miecz 3x"
                    przeszukano_skrzynie_1 = True
                    inventory.remove("wytrych")
                    posiadanie_wytrych = False
                elif not przeszukano_skrzynie_1:
                    alert3 = " * Skrzynia jest zamknięta."
                else:
                    alert3 = " * Skrzynia została już przeszukana."
            
            elif current_map == 2 and player_x in [45,46,47] and player_y in [22,23,24]:
                if posiadanie_kilof:
                    interact_kopalnia()
                else:
                    alert3 = " * Nie posiadasz kilofu."
                
                
            elif current_map == 1 and player_x in [95,96] and player_y in [31,32]:
                dod_jedz()
            elif current_map == 1 and player_x in [91,92] and player_y in [31,32]:
                miks_lecz()
            elif current_map == 1 and player_x in [37,38,39] and player_y in [22,23,24] and wyciągnieto_miecz == False:
                dod_miecz()
                wyciągnieto_miecz = True
            elif current_map == 3 and player_x in [mob1_x-1,mob1_x,mob1_x+1] and player_y in [mob1_y-1,mob1_y,mob1_y+1]:
                if posiadanie_miecz:
                    alert3 = " * Czy chcesz walczyć z napotkanym przeciwnikiem (T/N)"

                    draw_map_3()
                    refresh_ui()
                    stdscr.refresh()
                    stdscr.getch()
                    
                    while True:
                        try:
                            c = stdscr.getkey()
                        except:
                            c = ''
                        if c == "t":
                            if health_bar - 1 > 0:
                                pokonano_wiedzma += 1
                                health_bar -=1
                                alert3 = " * Pokonano wiedźme, odniesiono niewielkie obrażenia."
                                
                                drop = random.randint(1, 2)
                                if drop == 1:
                                    mikstury_leczenia +=1
                                    alert4 = " * Zdobyto miksturę leczenia."
                                elif drop == 2:
                                    zbroje +=2
                                    alert4 = " * Zdobyto zbroję."
                                
                                map_3[mob1_y][mob1_x] = " "
                                generate_mob1()
                                draw_map_3
                                refresh_ui()
                                break
                            else:
                                alert3 = " * Nie jesteś przygotowany, aby walczyć."
                                draw_map_3
                                refresh_ui()
                                break
                        elif c == "n":
                            alert3 = " * Zrezygnowano z walki."
                            refresh_ui()
                            break
                else:
                    alert3 =" * Aby walczyć potrzebujesz miecza."
            elif current_map == 3 and player_x in [mob2_x-1,mob2_x,mob2_x+1] and player_y in [mob2_y-1,mob2_y,mob2_y+1]:
                if posiadanie_miecz:
                    alert3 = " * Czy chcesz walczyć z napotkanym przeciwnikiem (T/N)"

                    draw_map_3()
                    refresh_ui()
                    stdscr.refresh()
                    stdscr.getch()
                    
                    while True:
                        try:
                            c = stdscr.getkey()
                        except:
                            c = ''
                        if c == "t":
                            if health_bar - 2 > 0  and armor_bar -1 > 0:
                                pokonano_zombie += 1
                                health_bar -=2
                                armor_bar -=1
                                alert3 = " * Pokonano zombie, odniesiono odczuwalne obrażenia."
                                
                                drop = random.randint(1, 2)
                                if drop == 1:
                                    alert4 = " * Zdobyto miecz."
                                    miecze +=1
                                elif drop == 2:
                                    zbroje +=2
                                    alert4 = " * Zdobyto zbroję."
                                
                                map_3[mob2_y][mob2_x] = " "
                                generate_mob2()
                                draw_map_3
                                refresh_ui()
                                break
                            else:
                                alert3 = " * Nie jesteś przygotowany, aby walczyć."
                                draw_map_3
                                refresh_ui()
                                break
                        elif c == "n":
                            alert3 = " * Zrezygnowano z walki."
                            refresh_ui()
                            break
                else:
                    alert3 =" * Aby walczyć potrzebujesz miecza."
            
            elif current_map == 3 and player_x in [mob3_x-1,mob3_x,mob3_x+1] and player_y in [mob3_y-1,mob3_y,mob3_y+1]:
                if posiadanie_miecz:
                    alert3 = " * Czy chcesz walczyć z napotkanym przeciwnikiem (T/N)"

                    draw_map_3()
                    refresh_ui()
                    stdscr.refresh()
                    stdscr.getch()
                    
                    while True:
                        try:
                            c = stdscr.getkey()
                        except:
                            c = ''
                        if c == "t":
                            if health_bar - 4 > 0 and armor_bar -2 > 0:
                                pokonano_wojownik += 1
                                health_bar -=4
                                armor_bar -=2
                                alert3 = " * Pokonano wojownika, odniesiono poważne obrażenia."
                                
                                drop = random.randint(1, 3)
                                if drop == 1:
                                    mikstury_leczenia +=2
                                    alert4 = " * Zdobyto miksturę leczenia."
                                elif drop == 2:
                                    zbroje +=4
                                    alert4 = " * Zdobyto zbroję."
                                elif drop == 3:
                                    alert4 = " * Zdobyto miecz."
                                    miecze +=1
                                
                                map_3[mob3_y][mob3_x] = " "
                                generate_mob3()
                                draw_map_3
                                refresh_ui()
                                break
                            else:
                                alert3 = " * Nie jesteś przygotowany, aby walczyć."
                                draw_map_3
                                refresh_ui()
                                break
                        elif c == "n":
                            alert3 = " * Zrezygnowano z walki."
                            refresh_ui()
                            break
                else:
                    alert3 =" * Aby walczyć potrzebujesz miecza."
            
        # Rysowanie map i UI
        if current_map == 1:
            draw_map_1()
            nazwa_mapy = "Wieś"
        elif current_map == 2:
            draw_map_2()
            nazwa_mapy = "Kopalnia"
        elif current_map == 3:
            draw_map_3()
            nazwa_mapy = "Arena"
        draw_ui()

        check_defeat()
        time.sleep(0.02)

main()