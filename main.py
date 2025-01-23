import json
import random
import os
import colorama

def clear_screen():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def get_starting_age() -> str:
    clear_screen()
    print("1. Antiquity 2. Exploration 3. Modern")
    age = 0
    while age not in range(1, 4):
        i = input("Enter the starting age(1-3): ")
        if i.isdigit() and int(i) in range(1, 4):
            age = int(i)
        else:
            print("Invalid input. Please enter a number between 1 and 3")

    match age:
        case 1:
            return "Antiquity"
        case 2:
            return "Exploration"
        case 3:
            return "Modern"
        case _:
            raise ValueError("Invalid age")

class Player:
    def __init__(self, name: str, leaders: list[str], civs: list[str]):
        self.name = name
        self.dlc = {
            "Base": True,
            "2k": False,
            "Preorder": False,
            "Deluxe": False,
            "Founders": False
        }
        self.leaders = leaders
        self.civs = civs
        self.selcted = False

    def __str__(self):
        return f"{self.name} has the following choices:\n Leaders: {', '.join(self.leaders)}\n Civs: {', '.join(self.civs)}"

    def is_selected(self):
        if self.selcted:
            return colorama.Fore.GREEN
        else:
            return colorama.Fore.RED

def create_players() -> list[Player]:
    with open("players.json", "r") as f:
        player_info: list[dict] = json.load(f)

    players = []
    for player in player_info:
        x = Player(player.get('Name'), [], [])
        match player.get('Version'):
            case "Preorder":
                x.dlc["Preorder"] = True
            case "Deluxe":
                x.dlc["Preorder"] = True
                x.dlc["Deluxe"] = True
            case "Founders":
                x.dlc["Preorder"] = True
                x.dlc["Deluxe"] = True
                x.dlc["Founders"] = True
        if player.get('2k'):
            x.dlc["2k"] = True
        players.append(x)
    return players

def select_players(players_list: list[Player]):
    finished = False
    clear_screen()
    while not finished:
        i = 0
        colorama.init(True)
        while i+3 <= len(players_list):
            print(f"{players_list[i].is_selected()}{i+1}. {players_list[i].name} "
                  f"{players_list[i+1].is_selected()}{i+2}. {players_list[i+1].name} "
                  f"{players_list[i+2].is_selected()}{i+3}. {players_list[i+2].name}")
            i += 3
        match len(players_list) % 3:
            case 1:
                print(f"{players_list[i].is_selected()}{i+1}. {players_list[i].name}")
            case 2:
                print(f"{players_list[i].is_selected()}{i+1}. {players_list[i].name} "
                      f"{players_list[i + 1].is_selected()}{i+2}. {players_list[i+1].name}")
        colorama.deinit()
        i = input("Select the players that are playing by entering the corresponding number, or type 'done' to finish: ")
        if i.isdigit() and int(i) in range(1, len(players_list)+1):
            players_list[int(i)-1].selcted = not players_list[int(i)-1].selcted
            clear_screen()
        elif i.lower() == "done":
            if len([player for player in players_list if player.selcted]) < 1:
                clear_screen()
                print("You must select at least 1 player")
            else:
                finished = True
        else:
            print(f"Invalid input. Please enter a number between 1 and {len(players_list)} or type 'done'")

class ListWrapper(list):
    def __init__(self, iterable=None):
        super().__init__(iterable)
        self.dlcs = {}
        for x in self:
            if x["Required"] in self.dlcs:
                self.dlcs[x["Required"]] += 1
            else:
                self.dlcs[x["Required"]] = 1

    def avaliable_items(self, player: Player) -> int:
        value = 0
        for x in self.dlcs.keys():
            if player.dlc[x]:
                value += self.dlcs[x]
        return value

def get_amount_of_choices(leaders: ListWrapper, civs: ListWrapper, players: list[Player]) -> list[int]:
    players_max_leaders = []
    players_max_civs = []
    for player in players:
        players_max_leaders.append(leaders.avaliable_items(player))
        players_max_civs.append(civs.avaliable_items(player))

    max_leader_choices = min(players_max_leaders) // len(players)
    max_civ_choices = min(players_max_civs) // len(players)
    amount_of_choices = [0, 0]

    clear_screen()
    i = input(f"Enter the amount of leader choices for each player(1-{max_leader_choices}): ")
    while True:
        if i.isdigit() and int(i) in range(1, max_leader_choices + 1):
            amount_of_choices[0] = int(i)
            break
        else:
            clear_screen()
            i = input(f"Invalid input. Please enter a number between 1 and {max_leader_choices}: ")

    clear_screen()
    i = input(f"Enter the amount of civ choices for each player(1-{max_civ_choices}): ")
    while True:
        if i.isdigit() and int(i) in range(1, max_civ_choices + 1):
            amount_of_choices[1] = int(i)
            break
        else:
            clear_screen()
            i = input(f"Invalid input. Please enter a number between 1 and {max_civ_choices}: ")
    return amount_of_choices

def get_choices(player_list: list[Player], available_leaders: list[dict], available_civs: list[dict],
                amount_of_leaders: int, amount_of_civs: int) -> None:
    for player in player_list:
        while len(player.leaders) < amount_of_leaders:
            leader = random.choice(available_leaders)
            if player.dlc[leader["Required"]]:
                player.leaders.append(leader["Name"])
                available_leaders.remove(leader)
        while len(player.civs) < amount_of_civs:
            civ = random.choice(available_civs)
            if player.dlc[civ["Required"]]:
                player.civs.append(civ["Name"])
                available_civs.remove(civ)

if __name__ == '__main__':
    running = True # Variable to keep the program running will be set to False if the user decides to exit
    while running:
        starting_age: str = get_starting_age()
        with open("civs.json", "r") as f:
            json_dict = json.load(f)
            leaders_list = ListWrapper([x for x in json_dict["Leaders"] if not x["Banned"]])
            civs_list = ListWrapper([x for x in json_dict["Civs"][starting_age] if not x["Banned"]])

        player_list: list[Player] = create_players()
        select_players(player_list)
        player_list = [player for player in player_list if player.selcted]

        amount_of_choices: list[int] = get_amount_of_choices(leaders_list, civs_list, player_list)

        get_choices(player_list, leaders_list, civs_list, amount_of_choices[0], amount_of_choices[1])

        clear_screen()
        for player in player_list:
            print(player)

        while True:
            i = input("Would you like to run the program again? (y/n): ")
            match i:
                case "y":
                    break
                case "n":
                    running = False
                    break
                case _:
                    print("Invalid input. Please enter 'y' or 'n'")
