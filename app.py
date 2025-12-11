"""
Castle Escape Game
A text-based adventure game where players navigate an abandoned castle
to find treasure and escape.
"""

class Player:
    """Player class to store character information and inventory"""
    
    def __init__(self, name):
        """Initialize player with name, starting position, and empty inventory"""
        self.name = name
        self.position = "Entrance Hall"
        self.inventory = []
        self.health = 100
        self.visited_rooms = set()
    
    def add_item(self, item):
        """Add item to inventory if there's space (max 4 items)"""
        if len(self.inventory) < 4:
            self.inventory.append(item)
            return True
        else:
            return False
    
    def remove_item(self, item):
        """Remove item from inventory"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def has_item(self, item):
        """Check if player has specific item"""
        return item in self.inventory
    
    def show_inventory(self):
        """Display current inventory"""
        print("\n" + "="*40)
        print("YOUR BAG:")
        if self.inventory:
            for i, item in enumerate(self.inventory, 1):
                print(f"{i}. {item}")
        else:
            print("Your bag is empty")
        print(f"Space: {len(self.inventory)}/4")
        print("="*40)


def initialize_game():
    """Set up game world, rooms, and items"""
    
    # Define room connections
    rooms = {
        "Entrance Hall": {
            "description": "A grand entrance hall with a large oak door behind you.",
            "north": "Courtyard",
            "east": "Library",
            "items": ["Torch"]
        },
        "Courtyard": {
            "description": "An overgrown courtyard with a fountain in the center.",
            "south": "Entrance Hall",
            "north": "Guard Tower",
            "east": "Kitchen",
            "west": "Armory",
            "items": []
        },
        "Guard Tower": {
            "description": "A tall tower with a view of the entire castle.",
            "south": "Courtyard",
            "items": ["Crowbar"]
        },
        "Library": {
            "description": "A dusty library with shelves full of ancient books.",
            "west": "Entrance Hall",
            "north": "Study",
            "items": ["Rusty Key", "Old Book"]
        },
        "Kitchen": {
            "description": "A large kitchen with pots and pans hanging from the ceiling.",
            "west": "Courtyard",
            "south": "Dungeon",
            "items": ["Healing Herb"]
        },
        "Armory": {
            "description": "A room filled with weapons and armor. The door is locked.",
            "east": "Courtyard",
            "items": ["Sword"],
            "locked": True
        },
        "Study": {
            "description": "A small study with a desk and a mysterious map.",
            "south": "Library",
            "items": ["Note"]
        },
        "Dungeon": {
            "description": "A dark, damp dungeon. It's hard to see without light.",
            "north": "Kitchen",
            "east": "Secret Passage",
            "items": [],
            "dark": True
        },
        "Secret Passage": {
            "description": "A hidden passage behind a bookcase.",
            "west": "Dungeon",
            "north": "Throne Room",
            "items": []
        },
        "Throne Room": {
            "description": "The castle's throne room with a glittering golden crown.",
            "south": "Secret Passage",
            "items": ["Golden Crown"]
        }
    }
    
    # Get player name
    print("\n" + "="*50)
    print("CASTLE ESCAPE")
    print("="*50)
    name = input("Enter your character's name: ").strip()
    player = Player(name)
    player.visited_rooms.add(player.position)
    
    print(f"\nWelcome, {player.name}! You find yourself at the entrance of an abandoned castle.")
    print("Your goal: Find the Golden Crown and escape!")
    print("Type 'help' at any time for commands.\n")
    
    return player, rooms


def display_current_room(player, rooms):
    """Show current room description and available exits"""
    room = rooms[player.position]
    
    print("\n" + "="*50)
    print(f"LOCATION: {player.position}")
    print("="*50)
    print(room["description"])
    
    # Check if dungeon is dark
    if player.position == "Dungeon" and room.get("dark", False):
        if not player.has_item("Torch"):
            print("It's too dark to see anything!")
            return
    
    # Show exits
    exits = [exit for exit in room.keys() if exit in ["north", "south", "east", "west"]]
    if exits:
        print("\nExits:", ", ".join(exits))
    
    # Show items in room
    if room.get("items"):
        print("\nYou see:", ", ".join(room["items"]))


def look_around(player, rooms):
    """Examine current room more carefully"""
    room = rooms[player.position]
    
    if player.position == "Dungeon" and room.get("dark", False):
        if not player.has_item("Torch"):
            print("It's too dark to see anything!")
            return
    
    print("\nYou look around carefully...")
    
    if room.get("items"):
        for item in room["items"]:
            if item == "Torch":
                print("A Torch hangs on the wall, it could be useful in dark places.")
            elif item == "Rusty Key":
                print("A Rusty Key sits on the desk. It might open something important.")
            elif item == "Crowbar":
                print("A sturdy Crowbar leans against the wall. It could pry things open.")
            elif item == "Healing Herb":
                print("Fresh Healing Herb grows in a crack in the wall.")
            elif item == "Golden Crown":
                print("The Golden Crown glitters on the throne. This is what you came for!")
            elif item == "Sword":
                print("A sharp Sword hangs on the wall.")
            elif item == "Note":
                print("A Note on the desk reads: 'The passage opens when the moon is high'")
            elif item == "Old Book":
                print("An Old Book titled 'History of the Castle'")
    else:
        print("There's nothing of interest here.")


def pick_up_item(player, rooms):
    """Pick up an item from current room"""
    room = rooms[player.position]
    
    if not room.get("items"):
        print("There's nothing to pick up here.")
        return
    
    # Check special conditions
    if player.position == "Armory" and room.get("locked", False):
        print("The armory door is locked!")
        return
    
    if player.position == "Dungeon" and room.get("dark", False):
        if not player.has_item("Torch"):
            print("It's too dark to see anything!")
            return
    
    print("\nAvailable items:", ", ".join(room["items"]))
    item = input("What would you like to pick up? ").title()
    
    if item in room["items"]:
        if player.add_item(item):
            room["items"].remove(item)
            print(f"You picked up the {item}.")
        else:
            print("Your bag is full! (Maximum 4 items)")
    else:
        print(f"There's no {item} here.")


def move_player(player, rooms):
    """Move player to a different room"""
    room = rooms[player.position]
    
    # Get available exits
    exits = [exit for exit in room.keys() if exit in ["north", "south", "east", "west"]]
    
    if not exits:
        print("There are no exits from this room!")
        return
    
    print("\nAvailable exits:", ", ".join(exits))
    direction = input("Which direction? ").lower()
    
    if direction in exits:
        new_position = room[direction]
        
        # Check if armory is locked
        if new_position == "Armory" and rooms["Armory"].get("locked", False):
            if player.has_item("Rusty Key"):
                print("You use the Rusty Key to unlock the armory!")
                rooms["Armory"]["locked"] = False
                player.remove_item("Rusty Key")
            else:
                print("The armory door is locked. You need a key.")
                return
        
        player.position = new_position
        player.visited_rooms.add(new_position)
        print(f"You move {direction} to the {new_position}.")
    else:
        print(f"You can't go {direction} from here.")


def use_item(player):
    """Use an item from inventory"""
    if not player.inventory:
        print("Your bag is empty!")
        return
    
    player.show_inventory()
    item = input("\nWhich item would you like to use? ").title()
    
    if not player.has_item(item):
        print(f"You don't have {item} in your bag.")
        return
    
    if item == "Torch":
        print("The torch illuminates your surroundings.")
        # Torch effect handled elsewhere
    elif item == "Healing Herb":
        player.health = min(100, player.health + 30)
        print("You eat the Healing Herb and feel better!")
        player.remove_item("Healing Herb")
    elif item == "Sword":
        print("You swing the sword. It feels powerful.")
    elif item == "Crowbar":
        if player.position == "Study":
            print("You use the crowbar to open a hidden passage!")
            # This would unlock a new exit in a more complex version
        else:
            print("Nothing to use the crowbar on here.")
    else:
        print(f"You can't use the {item} right now.")


def talk_to_character(player):
    """Interact with characters in the game"""
    if player.position == "Courtyard":
        print("\nA friendly ghost appears!")
        print("Ghost: 'The crown is in the throne room, but beware of dark places!'")
    elif player.position == "Guard Tower":
        print("\nAn injured guard sits in the corner.")
        if player.has_item("Healing Herb"):
            print("Guard: 'Thank you for the herb! Here, take this clue...'")
            print("Guard: 'The library holds secrets and keys.'")
            player.remove_item("Healing Herb")
        else:
            print("Guard: 'I'm hurt... I need healing herbs...'")
    else:
        print("There's no one here to talk to.")


def show_help():
    """Display help information"""
    print("\n" + "="*50)
    print("HELP - AVAILABLE COMMANDS")
    print("="*50)
    print("move    - Move to a different room")
    print("look    - Look around the current room")
    print("take    - Pick up an item")
    print("bag     - Check your inventory")
    print("use     - Use an item from your inventory")
    print("talk    - Talk to characters")
    print("map     - Show visited rooms")
    print("help    - Show this help message")
    print("quit    - Quit the game")
    print("\nTIPS:")
    print("- You can only carry 4 items at a time")
    print("- Some items are needed to progress")
    print("- Explore everywhere to find the crown!")


def show_map(player):
    """Display map of visited rooms"""
    print("\n" + "="*50)
    print("MAP - VISITED LOCATIONS")
    print("="*50)
    
    # Simple ASCII map based on visited rooms
    map_layout = [
        ["Guard Tower", "Courtyard", "Kitchen"],
        ["", "Entrance Hall", "Library"],
        ["Armory", "", "Study"],
        ["", "", "Dungeon"],
        ["", "", "Secret Passage"],
        ["", "", "Throne Room"]
    ]
    
    for row in map_layout:
        for room in row:
            if room and room in player.visited_rooms:
                print(f"[{room[:3]}]", end=" ")
            elif room:
                print("[ ? ]", end=" ")
            else:
                print("     ", end=" ")
        print()
    
    print("\nLegend: [XXX] = Visited, [ ? ] = Unexplored")


def check_win_condition(player):
    """Check if player has won the game"""
    if player.position == "Throne Room" and player.has_item("Golden Crown"):
        print("\n" + "="*50)
        print("VICTORY!")
        print("="*50)
        print(f"Congratulations {player.name}!")
        print("You found the Golden Crown and escaped the castle!")
        print(f"Final Score: {len(player.visited_rooms) * 10 + len(player.inventory) * 5}")
        return True
    return False


def game_loop(player, rooms):
    """Main game loop"""
    turns = 0
    
    while True:
        turns += 1
        print(f"\n--- Turn {turns} ---")
        
        display_current_room(player, rooms)
        
        # Get player action
        action = input("\nWhat would you like to do? ").lower().strip()
        
        if action == "move":
            move_player(player, rooms)
        elif action == "look":
            look_around(player, rooms)
        elif action == "take":
            pick_up_item(player, rooms)
        elif action == "bag":
            player.show_inventory()
        elif action == "use":
            use_item(player)
        elif action == "talk":
            talk_to_character(player)
        elif action == "map":
            show_map(player)
        elif action == "help":
            show_help()
        elif action == "quit":
            print("Thanks for playing!")
            return False
        else:
            print("Invalid command. Type 'help' for available commands.")
        
        # Check win condition
        if check_win_condition(player):
            return True
        
        # Add some turn-based events
        if turns % 10 == 0:
            print("\nYou hear strange noises echoing through the castle...")
        
        if turns > 50:
            print("\nYou're taking too long! The castle feels more dangerous...")
            player.health -= 5
            if player.health <= 0:
                print("You succumb to the dangers of the castle. Game Over!")
                return False


def main():
    """Main function to run the game"""
    player, rooms = initialize_game()
    
    try:
        game_won = game_loop(player, rooms)
        
        if game_won:
            print("\nThanks for playing Castle Escape!")
        else:
            print("\nGame Over. Better luck next time!")
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please report this issue.")


if __name__ == "__main__":
    main()