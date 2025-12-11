"""
Castle Escape Game - Streamlit Web Version
A text-based adventure game with SQLite database for saving game state
"""

import streamlit as st
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import os

# Initialize database
def init_database():
    """Initialize SQLite database for saving game states"""
    conn = sqlite3.connect('castle_escape.db')
    c = conn.cursor()
    
    # Create saves table
    c.execute('''
        CREATE TABLE IF NOT EXISTS game_saves (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            save_name TEXT,
            game_state TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_played TIMESTAMP
        )
    ''')
    
    # Create high scores table
    c.execute('''
        CREATE TABLE IF NOT EXISTS high_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            score INTEGER,
            turns INTEGER,
            rooms_visited INTEGER,
            items_collected INTEGER,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Call database initialization
init_database()

class Player:
    """Player class to store character information and inventory"""
    
    def __init__(self, name=None):
        """Initialize player with name, starting position, and empty inventory"""
        if name:
            self.name = name
            self.position = "Entrance Hall"
            self.inventory = []
            self.health = 100
            self.visited_rooms = set(["Entrance Hall"])
            self.turns = 0
    
    def to_dict(self):
        """Convert player object to dictionary for database storage"""
        return {
            'name': self.name,
            'position': self.position,
            'inventory': self.inventory,
            'health': self.health,
            'visited_rooms': list(self.visited_rooms),
            'turns': self.turns
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create player object from dictionary"""
        player = cls(data['name'])
        player.position = data['position']
        player.inventory = data['inventory']
        player.health = data['health']
        player.visited_rooms = set(data['visited_rooms'])
        player.turns = data['turns']
        return player
    
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
        inventory_html = f"""
        <div style='border: 2px solid #4CAF50; border-radius: 10px; padding: 15px; margin: 10px 0; background-color: #f0f8f0;'>
            <h3>🎒 YOUR BAG ({len(self.inventory)}/4)</h3>
            <hr>
        """
        if self.inventory:
            for i, item in enumerate(self.inventory, 1):
                inventory_html += f"<p>🔹 {i}. {item}</p>"
        else:
            inventory_html += "<p>Your bag is empty</p>"
        inventory_html += "</div>"
        return inventory_html

def initialize_game():
    """Set up game world, rooms, and items"""
    
    rooms = {
        "Entrance Hall": {
            "description": "🏰 A grand entrance hall with a large oak door behind you. Dusty tapestries hang on the walls.",
            "north": "Courtyard",
            "east": "Library",
            "items": ["Torch"],
            "image": "🏰"
        },
        "Courtyard": {
            "description": "🌿 An overgrown courtyard with a cracked fountain in the center. Vines cover the stone walls.",
            "south": "Entrance Hall",
            "north": "Guard Tower",
            "east": "Kitchen",
            "west": "Armory",
            "items": [],
            "image": "🌿"
        },
        "Guard Tower": {
            "description": "🗼 A tall tower with a view of the entire castle. Arrow slits let in shafts of light.",
            "south": "Courtyard",
            "items": ["Crowbar"],
            "image": "🗼"
        },
        "Library": {
            "description": "📚 A dusty library with shelves full of ancient books. A large desk sits in the center.",
            "west": "Entrance Hall",
            "north": "Study",
            "items": ["Rusty Key", "Old Book"],
            "image": "📚"
        },
        "Kitchen": {
            "description": "🍳 A large kitchen with pots and pans hanging from the ceiling. A cold hearth dominates one wall.",
            "west": "Courtyard",
            "south": "Dungeon",
            "items": ["Healing Herb"],
            "image": "🍳"
        },
        "Armory": {
            "description": "⚔️ A room filled with weapons and armor. The door is locked with an old iron lock.",
            "east": "Courtyard",
            "items": ["Sword"],
            "locked": True,
            "image": "⚔️"
        },
        "Study": {
            "description": "🖋️ A small study with a desk and a mysterious map. Quills and ink pots are scattered about.",
            "south": "Library",
            "items": ["Note"],
            "image": "🖋️"
        },
        "Dungeon": {
            "description": "🔒 A dark, damp dungeon. It's hard to see without light. Chains hang from the walls.",
            "north": "Kitchen",
            "east": "Secret Passage",
            "items": [],
            "dark": True,
            "image": "🔒"
        },
        "Secret Passage": {
            "description": "🕯️ A hidden passage behind a bookcase. Cobwebs brush against your face as you walk.",
            "west": "Dungeon",
            "north": "Throne Room",
            "items": [],
            "image": "🕯️"
        },
        "Throne Room": {
            "description": "👑 The castle's throne room with a glittering golden crown on an ornate throne.",
            "south": "Secret Passage",
            "items": ["Golden Crown"],
            "image": "👑"
        }
    }
    
    return rooms

def save_game_state(player, save_name="autosave"):
    """Save current game state to database"""
    conn = sqlite3.connect('castle_escape.db')
    c = conn.cursor()
    
    game_state = json.dumps(player.to_dict())
    
    # Check if save already exists
    c.execute('SELECT id FROM game_saves WHERE player_name=? AND save_name=?', 
              (player.name, save_name))
    existing = c.fetchone()
    
    if existing:
        # Update existing save
        c.execute('''
            UPDATE game_saves 
            SET game_state=?, last_played=CURRENT_TIMESTAMP 
            WHERE id=?
        ''', (game_state, existing[0]))
    else:
        # Create new save
        c.execute('''
            INSERT INTO game_saves (player_name, save_name, game_state, last_played)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (player.name, save_name, game_state))
    
    conn.commit()
    conn.close()
    return True

def load_game_state(player_name, save_name="autosave"):
    """Load game state from database"""
    conn = sqlite3.connect('castle_escape.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT game_state FROM game_saves 
        WHERE player_name=? AND save_name=?
        ORDER BY last_played DESC LIMIT 1
    ''', (player_name, save_name))
    
    result = c.fetchone()
    conn.close()
    
    if result:
        return Player.from_dict(json.loads(result[0]))
    return None

def get_saved_games():
    """Get list of all saved games"""
    conn = sqlite3.connect('castle_escape.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT player_name, save_name, created_at, last_played 
        FROM game_saves 
        ORDER BY last_played DESC
    ''')
    
    saves = c.fetchall()
    conn.close()
    return saves

def save_high_score(player, rooms_visited):
    """Save high score to database"""
    score = len(player.visited_rooms) * 10 + len(player.inventory) * 5
    
    conn = sqlite3.connect('castle_escape.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO high_scores 
        (player_name, score, turns, rooms_visited, items_collected)
        VALUES (?, ?, ?, ?, ?)
    ''', (player.name, score, player.turns, rooms_visited, len(player.inventory)))
    
    conn.commit()
    conn.close()

def get_high_scores(limit=10):
    """Get top high scores from database"""
    conn = sqlite3.connect('castle_escape.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT player_name, score, turns, rooms_visited, items_collected, completed_at
        FROM high_scores 
        ORDER BY score DESC, turns ASC 
        LIMIT ?
    ''', (limit,))
    
    scores = c.fetchall()
    conn.close()
    return scores

def display_current_room(player, rooms):
    """Show current room description and available exits"""
    room = rooms[player.position]
    
    st.markdown(f"""
    <div style='border: 3px solid #8B4513; border-radius: 15px; padding: 20px; margin: 20px 0; background-color: #FAF0E6;'>
        <h2>{room['image']} {player.position}</h2>
        <hr>
        <p style='font-size: 1.2em;'>{room['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if dungeon is dark
    if player.position == "Dungeon" and room.get("dark", False):
        if not player.has_item("Torch"):
            st.warning("🌑 It's too dark to see anything! You need a light source.")
            return
    
    # Show exits
    exits = [exit for exit in room.keys() if exit in ["north", "south", "east", "west"]]
    if exits:
        st.subheader("🚪 Exits:")
        cols = st.columns(len(exits))
        for i, exit in enumerate(exits):
            with cols[i]:
                direction_icons = {"north": "⬆️", "south": "⬇️", "east": "➡️", "west": "⬅️"}
                if st.button(f"{direction_icons.get(exit, '')} {exit.title()}", key=f"exit_{exit}"):
                    move_player(player, rooms, exit)
    
    # Show items in room
    if room.get("items"):
        st.subheader("📦 Items in room:")
        for item in room["items"]:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"🔸 {item}")
            with col2:
                if st.button("Take", key=f"take_{item}"):
                    pick_up_item(player, rooms, item)
                    st.rerun()

def move_player(player, rooms, direction):
    """Move player to a different room"""
    room = rooms[player.position]
    
    if direction in room:
        new_position = room[direction]
        
        # Check if armory is locked
        if new_position == "Armory" and rooms["Armory"].get("locked", False):
            if player.has_item("Rusty Key"):
                st.success("🔓 You use the Rusty Key to unlock the armory!")
                rooms["Armory"]["locked"] = False
                player.remove_item("Rusty Key")
                save_game_state(player)
            else:
                st.error("🔒 The armory door is locked. You need a key.")
                return False
        
        player.position = new_position
        player.visited_rooms.add(new_position)
        player.turns += 1
        save_game_state(player)
        return True
    return False

def pick_up_item(player, rooms, item_name):
    """Pick up an item from current room"""
    room = rooms[player.position]
    
    if not room.get("items"):
        st.error("There's nothing to pick up here.")
        return False
    
    # Check special conditions
    if player.position == "Armory" and room.get("locked", False):
        st.error("The armory door is locked!")
        return False
    
    if player.position == "Dungeon" and room.get("dark", False):
        if not player.has_item("Torch"):
            st.error("It's too dark to see anything!")
            return False
    
    if item_name in room["items"]:
        if player.add_item(item_name):
            room["items"].remove(item_name)
            st.success(f"✅ You picked up the {item_name}!")
            save_game_state(player)
            return True
        else:
            st.error("Your bag is full! (Maximum 4 items)")
            return False
    else:
        st.error(f"There's no {item_name} here.")
        return False

def look_around(player, rooms):
    """Examine current room more carefully"""
    room = rooms[player.position]
    
    if player.position == "Dungeon" and room.get("dark", False):
        if not player.has_item("Torch"):
            st.error("It's too dark to see anything!")
            return
    
    st.info("🔍 You look around carefully...")
    
    if room.get("items"):
        for item in room["items"]:
            if item == "Torch":
                st.write("A Torch hangs on the wall, it could be useful in dark places.")
            elif item == "Rusty Key":
                st.write("A Rusty Key sits on the desk. It might open something important.")
            elif item == "Crowbar":
                st.write("A sturdy Crowbar leans against the wall. It could pry things open.")
            elif item == "Healing Herb":
                st.write("Fresh Healing Herb grows in a crack in the wall. It smells restorative.")
            elif item == "Golden Crown":
                st.write("The Golden Crown glitters on the throne. This is what you came for!")
            elif item == "Sword":
                st.write("A sharp Sword hangs on the wall. It looks well-maintained.")
            elif item == "Note":
                st.write("A Note on the desk reads: 'The passage opens when the moon is high'")
            elif item == "Old Book":
                st.write("An Old Book titled 'History of the Castle'. It might contain clues.")
    else:
        st.write("There's nothing of interest here.")

def use_item(player):
    """Use an item from inventory"""
    if not player.inventory:
        st.error("Your bag is empty!")
        return
    
    item = st.selectbox("Select an item to use:", player.inventory)
    
    if st.button("Use Item"):
        if not player.has_item(item):
            st.error(f"You don't have {item} in your bag.")
            return
        
        if item == "Torch":
            st.success("🔥 The torch illuminates your surroundings.")
        elif item == "Healing Herb":
            player.health = min(100, player.health + 30)
            st.success("🌿 You eat the Healing Herb and feel better! (+30 HP)")
            player.remove_item("Healing Herb")
        elif item == "Sword":
            st.success("⚔️ You swing the sword. It feels powerful and well-balanced.")
        elif item == "Crowbar":
            if player.position == "Study":
                st.success("🔧 You use the crowbar to open a hidden passage!")
            else:
                st.info("Nothing to use the crowbar on here.")
        else:
            st.info(f"You can't use the {item} right now.")
        
        save_game_state(player)

def talk_to_character(player):
    """Interact with characters in the game"""
    if player.position == "Courtyard":
        st.info("👻 A friendly ghost appears!")
        st.write("Ghost: 'The crown is in the throne room, but beware of dark places!'")
    elif player.position == "Guard Tower":
        st.info("💂 An injured guard sits in the corner.")
        if player.has_item("Healing Herb"):
            st.success("Guard: 'Thank you for the herb! Here, take this clue...'")
            st.write("Guard: 'The library holds secrets and keys.'")
            player.remove_item("Healing Herb")
            save_game_state(player)
        else:
            st.write("Guard: 'I'm hurt... I need healing herbs...'")
    else:
        st.info("There's no one here to talk to.")

def show_map(player, rooms):
    """Display map of visited rooms"""
    st.subheader("🗺️ Castle Map")
    
    # Create a grid representation
    map_grid = [
        ["", "Guard Tower", "Courtyard", "Kitchen"],
        ["Armory", "Entrance Hall", "Library", ""],
        ["", "", "Study", ""],
        ["", "", "Dungeon", ""],
        ["", "", "Secret Passage", ""],
        ["", "", "Throne Room", ""]
    ]
    
    # Display the map
    map_html = "<div style='font-family: monospace; font-size: 16px; line-height: 1.5;'>"
    for row in map_grid:
        map_html += "<div>"
        for room in row:
            if room:
                if room in player.visited_rooms:
                    map_html += f"<span style='background-color: #4CAF50; color: white; padding: 5px; margin: 2px; border-radius: 3px;'>{room[:3]}</span> "
                elif room in rooms:
                    map_html += f"<span style='background-color: #ccc; padding: 5px; margin: 2px; border-radius: 3px;'>[ ? ]</span> "
                else:
                    map_html += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            else:
                map_html += "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        map_html += "</div>"
    map_html += "</div>"
    
    st.markdown(map_html, unsafe_allow_html=True)
    st.caption("Legend: 🟢 = Visited, ⬜ = Unexplored")

def check_win_condition(player, rooms):
    """Check if player has won the game"""
    if player.position == "Throne Room" and player.has_item("Golden Crown"):
        rooms_visited = len(player.visited_rooms)
        score = rooms_visited * 10 + len(player.inventory) * 5
        
        st.balloons()
        st.success(f"""
        # 🎉 VICTORY! 🎉
        
        ### Congratulations {player.name}!
        
        **You found the Golden Crown and escaped the castle!**
        
        **Final Stats:**
        - 🏆 Score: {score} points
        - 🚶‍♂️ Rooms Visited: {rooms_visited}/10
        - 🎒 Items Collected: {len(player.inventory)}
        - ⏱️ Turns Taken: {player.turns}
        
        **Well done, adventurer!**
        """)
        
        # Save high score
        save_high_score(player, rooms_visited)
        return True
    return False

def main():
    """Main Streamlit app"""
    st.set_page_config(
        page_title="Castle Escape",
        page_icon="🏰",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #8B4513;
        text-align: center;
        margin-bottom: 2rem;
    }
    .player-stats {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
    }
    .action-button {
        margin: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='main-header'>🏰 Castle Escape</h1>", unsafe_allow_html=True)
    
    # Initialize session state
    if 'player' not in st.session_state:
        st.session_state.player = None
    if 'rooms' not in st.session_state:
        st.session_state.rooms = initialize_game()
    if 'game_active' not in st.session_state:
        st.session_state.game_active = False
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "main"
    
    # Sidebar
    with st.sidebar:
        st.header("Game Menu")
        
        if st.session_state.game_active and st.session_state.player:
            player = st.session_state.player
            
            # Player stats
            st.markdown(f"""
            <div class='player-stats'>
                <h3>👤 {player.name}</h3>
                <p>❤️ Health: {player.health}/100</p>
                <p>📍 Location: {player.position}</p>
                <p>🔄 Turns: {player.turns}</p>
                <p>🗺️ Rooms Visited: {len(player.visited_rooms)}/10</p>
                <p>🎒 Inventory: {len(player.inventory)}/4</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Save game
            if st.button("💾 Save Game"):
                save_game_state(player)
                st.success("Game saved successfully!")
            
            # Load game
            saved_games = get_saved_games()
            if saved_games:
                st.subheader("Load Saved Game")
                for save in saved_games:
                    if st.button(f"📂 {save[0]} - {save[1]}", key=f"load_{save[0]}_{save[1]}"):
                        loaded_player = load_game_state(save[0], save[1])
                        if loaded_player:
                            st.session_state.player = loaded_player
                            st.rerun()
            
            # Quit game
            if st.button("🚪 Quit Game"):
                st.session_state.game_active = False
                st.session_state.player = None
                st.rerun()
        
        # High Scores
        st.header("🏆 High Scores")
        high_scores = get_high_scores(5)
        if high_scores:
            for i, score in enumerate(high_scores, 1):
                st.write(f"{i}. **{score[0]}** - {score[1]} pts ({score[2]} turns)")
        else:
            st.write("No high scores yet!")
    
    # Main game area
    if not st.session_state.game_active:
        # Main menu
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🎮 New Game")
            player_name = st.text_input("Enter your name:", key="new_name")
            if st.button("Start New Game", type="primary"):
                if player_name.strip():
                    st.session_state.player = Player(player_name)
                    st.session_state.game_active = True
                    save_game_state(st.session_state.player)
                    st.rerun()
                else:
                    st.error("Please enter a name!")
        
        with col2:
            st.subheader("📂 Load Game")
            saved_games = get_saved_games()
            if saved_games:
                for save in saved_games:
                    if st.button(f"▶️ {save[0]} - {save[1]}"):
                        loaded_player = load_game_state(save[0], save[1])
                        if loaded_player:
                            st.session_state.player = loaded_player
                            st.session_state.game_active = True
                            st.rerun()
            else:
                st.write("No saved games found")
        
        with col3:
            st.subheader("❓ How to Play")
            st.write("""
            **Goal:** Find the Golden Crown in the Throne Room
            
            **Commands:**
            - **Move:** Use direction buttons
            - **Look:** Examine room for details
            - **Take:** Pick up items
            - **Use:** Use items from inventory
            - **Talk:** Interact with characters
            
            **Tips:**
            - You can only carry 4 items
            - Some rooms are dark (need Torch)
            - Some doors are locked (need Key)
            - Save your game often!
            """)
        
        # Display game map preview
        st.subheader("🗺️ Castle Layout Preview")
        st.image("https://via.placeholder.com/800x400.png?text=Castle+Map+Preview", 
                 caption="Explore the abandoned castle!")
    
    else:
        # Game is active
        player = st.session_state.player
        rooms = st.session_state.rooms
        
        # Main game interface
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Display current room
            display_current_room(player, rooms)
            
            # Check win condition
            if check_win_condition(player, rooms):
                st.session_state.game_active = False
                if st.button("🏁 Play Again"):
                    st.session_state.player = None
                    st.session_state.game_active = False
                    st.rerun()
        
        with col2:
            # Action buttons
            st.header("Actions")
            
            action_cols = st.columns(2)
            with action_cols[0]:
                if st.button("🔍 Look Around"):
                    look_around(player, rooms)
            with action_cols[1]:
                if st.button("💬 Talk"):
                    talk_to_character(player)
            
            # Inventory
            st.header("Inventory")
            if player.inventory:
                for item in player.inventory:
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"🎒 {item}")
                    with col_b:
                        if st.button("Use", key=f"use_{item}"):
                            use_item(player)
                            st.rerun()
            else:
                st.info("Your bag is empty")
            
            # Show inventory details
            st.markdown(player.show_inventory(), unsafe_allow_html=True)
            
            # Show map
            if st.button("🗺️ Show Map"):
                show_map(player, rooms)
            
            # Game instructions
            with st.expander("📖 Game Help"):
                st.write("""
                **Available Commands:**
                - Click direction buttons to move
                - Click 'Take' buttons to collect items
                - Use items from your inventory
                - Talk to characters for clues
                
                **Items:**
                - 🔦 Torch: Lights dark areas
                - 🔑 Rusty Key: Unlocks doors
                - 🧰 Crowbar: Opens hidden passages
                - 🌿 Healing Herb: Restores health
                - 👑 Golden Crown: Victory item!
                
                **Tip:** Explore every room and talk to everyone!
                """)
        
        # Auto-save
        if st.session_state.game_active:
            save_game_state(player)

if __name__ == "__main__":
    main()