#!/usr/bin/env python3
"""
B0aty V3 HCIM Guide Parser
Scrapes the OSRS wiki page and produces structured JSON for the RuneLite plugin.
Extracts: steps, quest references, NPC names, locations, items, bank groups, episodes.
"""

import json
import re
import sys
import os
from urllib.request import Request, urlopen
from html.parser import HTMLParser
from collections import OrderedDict

WIKI_URL = "https://oldschool.runescape.wiki/w/Guide:B0aty_HCIM_Guide_V3?action=raw"

# ============================================================================
# OSRS Quest Dictionary - canonical names for matching in free text
# ============================================================================
QUESTS = [
    # Sorted longest-first so greedy matching works correctly
    "Recipe for Disaster/Freeing the Goblin generals",
    "Recipe for Disaster/Freeing the Mountain Dwarf",
    "Recipe for Disaster/Freeing Evil Dave",
    "Recipe for Disaster/Freeing King Awowogei",
    "Recipe for Disaster/Freeing Pirate Pete",
    "Recipe for Disaster/Freeing Sir Amik Varze",
    "Recipe for Disaster/Freeing Skrach Uglogwee",
    "Recipe for Disaster/Freeing the Lumbridge Guide",
    "Fairytale I - Growing Pains",
    "Creature of Fenkenstrain",
    "Mourning's End Part II",
    "Mourning's End Part I",
    "Mournings End Pt 2",
    "Mournings End Pt 1",
    "In Search of the Myreque",
    "In Search of Myreque",
    "In Aid Of Myreque",
    "In Aid of the Myreque",
    "Darkness of Hallowvale",
    "A Taste of Hope",
    "My Arm's Big Adventure",
    "My Arms Big Adventure",
    "Making Friends with My Arm",
    "Song of the Elves",
    "Legends' Quest",
    "Legend's Quest",
    "Legends Quest",
    "Underground Pass",
    "Regicide",
    "Roving Elves",
    "Between a Rock...",
    "Between a Rock",
    "Desert Treasure",
    "Desert Treasure I",
    "Desert Treasure II",
    "Dragon Slayer II",
    "Dragon Slayer I",
    "Dragon Slayer",
    "Monkey Madness II",
    "Monkey Madness I",
    "Monkey Madness",
    "Recipe for Disaster",
    "Recipe for Diasaster",
    "One Small Favour",
    "Throne of Miscellania",
    "Royal Trouble",
    "The Fremennik Trials",
    "Fremennik Trials",
    "The Fremennik Isles",
    "Fremennik Isles",
    "The Fremennik Exiles",
    "Tai Bwo Wannai Trio",
    "Elemental Workshop I",
    "Elemental Workshop II",
    "Enlightened Journey",
    "Garden of Tranquility",
    "A Porcine of Interest",
    "Porcine of Interest",
    "Client of Kourend",
    "X Marks the Spot",
    "Children of the Sun",
    "The Grand Tree",
    "Grand Tree",
    "Tree Gnome Village",
    "Waterfall Quest",
    "Fight Arena",
    "Plague City",
    "Biohazard",
    "Temple of Ikov",
    "Hazeel Cult",
    "Clock Tower",
    "Holy Grail",
    "Merlin's Crystal",
    "Merlins Crystal",
    "Murder Mystery",
    "Scorpion Catcher",
    "Prince Ali Rescue",
    "Pirate's Treasure",
    "Pirates Treasure",
    "Witch's House",
    "Witches House",
    "Witches Potion",
    "Witch's Potion",
    "Shield of Arrav",
    "Demon Slayer",
    "Vampire Slayer",
    "Vampyre Slayer",
    "Gertrude's Cat",
    "Gertrudes Cat",
    "Ernest the Chicken",
    "Rune Mysteries",
    "Restless Ghost",
    "The Restless Ghost",
    "Cook's Assistant",
    "Cooks Assistant",
    "Sheep Shearer",
    "Romeo & Juliet",
    "Romeo and Juliet",
    "Druidic Ritual",
    "Lost City",
    "Nature Spirit",
    "Priest in Peril",
    "Black Knights Fortress",
    "Black Knights' Fortress",
    "Doric's Quest",
    "Dorics Quest",
    "Goblin Diplomacy",
    "Knight's Sword",
    "Knights Sword",
    "The Knight's Sword",
    "Imp Catcher",
    "Tourist Trap",
    "The Tourist Trap",
    "Monk's Friend",
    "Monks Friend",
    "Sheep Herder",
    "Dwarf Cannon",
    "Fishing Contest",
    "Family Crest",
    "Family Crest Quest",
    "Heroes' Quest",
    "Heroes Quest",
    "Tribal Totem",
    "Observatory Quest",
    "Shilo Village",
    "Jungle Potion",
    "Sea Slug",
    "Bone Voyage",
    "The Feud",
    "Daddy's Home",
    "Daddys Home",
    "Ghost's Ahoy",
    "Ghosts Ahoy",
    "Rag and Bone Man",
    "Rag and Bone Man II",
    "Animal Magnetism",
    "Eagles' Peak",
    "Eagles Peak",
    "Eyes of Glouphrie",
    "The Eyes of Glouphrie",
    "Fairy Tale Part I",
    "Fairy Tale Part II",
    "Fairy Tale Part 1",
    "Fairy Tale Part 2",
    "Fairytale Part I",
    "Fairytale Part II",
    "Forgettable Tale",
    "Garden of Death",
    "Horror from the Deep",
    "Icthlarin's Little Helper",
    "King's Ransom",
    "Kings Ransom",
    "Making History",
    "Perilous Moons",
    "Moons of Peril",
    "Royal Titans",
    "Rum Deal",
    "Cabin Fever",
    "The Great Brain Robbery",
    "Swan Song",
    "Cold War",
    "Contact!",
    "Devious Minds",
    "Dream Mentor",
    "Enakhra's Lament",
    "Lunar Diplomacy",
    "Slug Menace",
    "The Slug Menace",
    "Spirit of Summer",
    "Summer's End",
    "Tears of Guthix",
    "The Ides of Milk",
    "Ides of Milk",
    "Skippy and The Mogres",
    "Skippy & The Mogres",
    "Enter the Abyss",
    "Shadow of the Storm",
    "Rat Catchers",
    "Rogue Trader",
    "What Lies Below",
    "Zogre Flesh Eaters",
    "Big Chompy Bird Hunting",
    "Olaf's Quest",
    "The Dig Site",
    "The Digsite",
    "Digsite Quest",
    "Digsite",
    "Death on the Isle",
    "Ribbiting Tale of a Lily Pad Dispute",
    "Queen of Thieves",
    "Sleeping Giants",
    "Below Ice Mountain",
    "Land of the Goblins",
    "The Path of Glouphrie",
    "Temple of the Eye",
    "Beneath Cursed Sands",
    "Secrets of the North",
    "Children of the Sun",
    "Defender of Varrock",
    "While Guthix Sleeps",
    "Twilight's Promise",
    "At First Light",
    "A Night at the Theatre",
    "Sins of the Father",
    "A Kingdom Divided",
    "The Ascent of Arceuus",
    "Ascent of Arceuus",
    "The Queen of Thieves",
    "The Depths of Despair",
    "Depths of Despair",
    "The Forsaken Tower",
    "Forsaken Tower",
    "Getting Ahead",
    "The Golem",
    "Recruitment Drive",
    "The Lost Tribe",
    "Spirits of the Elid",
    "Icthlarin's Little Helper",
    "Icthlarins Little Helper",
    "A Soul's Bane",
    "A Souls Bane",
    "Tale of the Righteous",
    "Tales of the Righteous",
    "Bear Your Soul",
    "Vale Totems",
    "Ethically Acquired Antiques",
    "In Aid of the Myreque",
    "The Forsaken Tower",
    "The Depths of Despair",
    "Death Plateau",
    "Troll Stronghold",
    "A Tail of Two Cats",
    "Eadgar's Ruse",
    "Eadger's Ruse",
    "Eadgars Ruse",
    "Enakhra's Lament",
    "Enakrah's Lament",
    "Haunted Mine",
    "Tarn's Lair",
    "Tarns Lair",
    "Watchtower",
    "Hand in the Sand",
    "Tower of Life",
    "Grim Tales",
    "Wanted!",
    "Wanted",
]

# Sort longest first for greedy matching
QUESTS.sort(key=len, reverse=True)
CANONICAL_QUEST_LOOKUP = {q.lower(): q for q in QUESTS}

# Build case-insensitive regex pattern from quest names
_quest_pattern_parts = [re.escape(q) for q in QUESTS]
QUEST_REGEX = re.compile(r'\b(' + '|'.join(_quest_pattern_parts) + r')\b', re.IGNORECASE)

# ============================================================================
# Known NPC names - common NPCs referenced in the guide
# These catch plain-text mentions that aren't wiki-linked
# ============================================================================
KNOWN_NPCS = [
    # Sorted longest-first
    "Martin the Master Gardener", "Martin the Master Farmer",
    "Bartender (Flying Horse Inn)", "Bartender (Dead Man's Chest)",
    "Bartender (Blue Moon Inn)", "Bartender (Jolly Boar Inn)",
    "Magic combat tutor", "Mercenary Captain", "Bandit Champion",
    "Barbarian guard", "Guildmaster Apatura", "Entrance Guardian",
    "Jungle Forester", "Lady of the Lake", "Wizard Cromperty",
    "Candle maker", "King Arthur", "Sir Gawain", "Sir Lancelot",
    "Sir Prysin", "Captain Rovin", "Captain Cain", "Captain Barnaby",
    "Count Check", "Duke Horacio", "Father Aereck", "Father Urhney",
    "GPDT employee", "Friendly Forester", "Information clerk",
    "Old Man Yarlo", "Orlando Smith", "Mage of Zamorak",
    "Zamorak Mage", "Redbeard Frank", "Ali Morrisane",
    "Silk merchant", "Silver Merchant", "Spice seller",
    "King Narnode", "King Roald", "King Lathas",
    "High Priest", "Fred the Farmer", "Wyson the Gardener",
    "Dimintheis", "Johanhus Ulsbrecht", "Frizzy Skernip",
    "Barge foreman", "Haig Halen", "Historian Minas",
    "Regulus Cento", "Doug Deeping", "Gillie Groats",
    "Seth Groats", "Tool Leprechaun", "Sawmill Operator",
    "Squire", "Mordred", "Hazelmere", "Kangai Mau",
    "Drezel", "Sanfew", "Kaqemeex", "Sedridor", "Aubury",
    "Thurgo", "Osman", "Reldo", "Veos", "Aggie", "Luthas",
    "Bob", "Hans", "Shilop", "Noah", "Romeo", "Benny",
    "Aris", "Thessalia", "Dr Harlow", "Morgan", "Fortunato",
    "Robyn", "Diango", "Rommik", "Wydin", "Hassan",
    "Chancellor Hassan", "Baraek", "Zaff", "Amy", "Lucien",
    "Blurberry", "Heckel Funch", "Hudo", "Horvik", "Lowe",
    "Scavvo", "Gertrude", "Brian", "Elena", "Jorral",
    "Two-pints", "Spria", "Mazchna", "Sbott", "Thormac",
    "Seer", "Sherlock", "Arhein", "Sarah", "Elstan",
    "Treznor", "Heskel", "Fayeth", "Olivia", "Probita",
    "Cassius", "Merlin", "Anita", "Seravel", "Antonia",
    "Antonius", "Foreman", "Tough Guy", "Marlo",
    "Gnome Waiter", "Catablepon", "Jogre",
    "Yanni Salika", "Civilian", "Zahur",
]

KNOWN_NPCS.sort(key=len, reverse=True)
_npc_pattern_parts = [re.escape(n) for n in KNOWN_NPCS]
NPC_REGEX = re.compile(r'\b(' + '|'.join(_npc_pattern_parts) + r')\b', re.IGNORECASE)
NPC_STOPWORDS = {
    "continue", "complete", "start", "begin", "unlock", "return", "head",
    "walk", "run", "teleport", "quest", "until", "after", "before", "and",
    "then", "using", "use", "with", "from", "to"
}
NON_QUEST_BRACKET_KEYWORDS = {
    "diary", "miniquest", "birdhouse", "guild", "farm run", "farm runs",
    "you may need", "lamp on", "use lamps", "optional", "warning", "note",
    "not now", "black arm gang", "keep ", "giants foundry", "if you don't have"
}
FALSE_POSITIVE_NPCS = {"will", "don", "mess", "flower"}

# ============================================================================
# Location name → WorldPoint mapping
# Format: "name": [x, y, z]
# ============================================================================
LOCATION_COORDS = {
    # Lumbridge area
    "lumbridge castle": [3222, 3218, 0],
    "lumbridge church": [3243, 3210, 0],
    "lumbridge kitchen": [3209, 3214, 0],
    "lumbridge swamp": [3199, 3169, 0],
    "lumbridge": [3222, 3218, 0],
    "lumbridge bank": [3208, 3220, 2],
    # Draynor
    "draynor village": [3093, 3244, 0],
    "draynor bank": [3092, 3245, 0],
    "draynor manor": [3109, 3327, 0],
    "draynor": [3093, 3244, 0],
    # Wizards Tower
    "wizards tower": [3109, 3162, 0],
    "wizard's tower": [3109, 3162, 0],
    "wizards' tower": [3109, 3162, 0],
    # Varrock
    "varrock west bank": [3185, 3436, 0],
    "varrock east bank": [3253, 3420, 0],
    "varrock museum": [3255, 3449, 0],
    "varrock castle": [3212, 3473, 0],
    "varrock": [3213, 3428, 0],
    "grand exchange": [3165, 3487, 0],
    "blue moon inn": [3224, 3399, 0],
    "champions' guild": [3191, 3358, 0],
    "champions guild": [3191, 3358, 0],
    # Al Kharid
    "al kharid": [3293, 3174, 0],
    "al kharid bank": [3269, 3167, 0],
    "shantay pass": [3304, 3124, 0],
    "emir's arena": [3313, 3234, 0],
    "mage training arena": [3363, 3300, 0],
    # Port Sarim
    "port sarim": [3024, 3218, 0],
    # Falador
    "falador west bank": [2946, 3368, 0],
    "falador east bank": [3013, 3355, 0],
    "falador park": [2994, 3383, 0],
    "falador": [2965, 3381, 0],
    "falador furnace": [2976, 3369, 0],
    # Taverley
    "taverley": [2895, 3457, 0],
    "taverley dungeon": [2885, 3397, 0],
    # Edgeville
    "edgeville": [3094, 3502, 0],
    "edgeville bank": [3094, 3491, 0],
    # Barbarian Village
    "barbarian village": [3082, 3420, 0],
    # Ardougne
    "east ardougne": [2662, 3304, 0],
    "ardougne south bank": [2655, 3283, 0],
    "ardougne north bank": [2616, 3332, 0],
    "ardougne": [2662, 3304, 0],
    "ardougne zoo": [2606, 3280, 0],
    # Camelot / Seers
    "camelot": [2757, 3478, 0],
    "camelot bank": [2725, 3493, 0],
    "camelot castle": [2757, 3478, 0],
    "seers village": [2722, 3493, 0],
    "seers' village": [2722, 3493, 0],
    # Catherby
    "catherby": [2813, 3447, 0],
    "catherby bank": [2808, 3441, 0],
    # Yanille
    "yanille": [2545, 3089, 0],
    "yanille bank": [2613, 3094, 0],
    # Castle Wars
    "castle wars": [2440, 3090, 0],
    # Gnome Stronghold
    "gnome stronghold": [2465, 3495, 0],
    "tree gnome stronghold": [2465, 3495, 0],
    "tree gnome village": [2462, 3446, 0],
    # Karamja
    "karamja": [2921, 3170, 0],
    "brimhaven": [2771, 3178, 0],
    "shilo village": [2852, 2955, 0],
    "musa point": [2919, 3171, 0],
    "brimhaven agility arena": [2809, 3193, 0],
    # Port Khazard
    "port khazard": [2660, 3158, 0],
    # Canifis / Morytania
    "canifis": [3495, 3488, 0],
    "canifis bank": [3512, 3480, 0],
    # Kourend
    "port piscarilius": [1805, 3790, 0],
    "piscarilius": [1805, 3790, 0],
    "hosidius": [1742, 3517, 0],
    "lovakengj": [1497, 3780, 0],
    "shayzien": [1502, 3614, 0],
    "arceuus": [1673, 3745, 0],
    "kingstown": [1631, 3670, 0],
    "kourend castle": [1624, 3676, 0],
    # Varlamore
    "varlamore": [1665, 3086, 0],
    "aldarin": [1365, 2946, 0],
    "mistrock": [1385, 2873, 0],
    "sunset coast": [1374, 2822, 0],
    "hunter's guild": [1553, 3044, 0],
    "hunters guild": [1553, 3044, 0],
    # Fossil Island
    "fossil island": [3778, 3814, 0],
    "mushroom meadow": [3757, 3871, 0],
    "verdant valley": [3764, 3762, 0],
    # Zanaris
    "zanaris": [2412, 4434, 0],
    # Rellekka / Fremennik
    "rellekka": [2670, 3634, 0],
    # Desert
    "pollnivneach": [3336, 2954, 0],
    "nardah": [3422, 2914, 0],
    "agility pyramid": [3364, 2830, 0],
    # Barbarian Assault
    "barbarian assault": [2531, 3577, 0],
    # Wilderness Lever
    "wilderness": [3153, 3924, 0],
    # Entrana
    "entrana": [2834, 3333, 0],
    # Rimmington
    "rimmington": [2957, 3214, 0],
    # Crafting Guild
    "crafting guild": [2934, 3281, 0],
    # Digsite
    "digsite": [3346, 3445, 0],
    "the digsite": [3346, 3445, 0],
    # Lumberyard
    "lumberyard": [3308, 3491, 0],
}

# ============================================================================
# Location name matching - broader patterns found in guide text
# ============================================================================
LOCATION_NAMES = sorted(LOCATION_COORDS.keys(), key=len, reverse=True)
_loc_pattern_parts = [re.escape(loc) for loc in LOCATION_NAMES]
LOCATION_REGEX = re.compile(r'\b(' + '|'.join(_loc_pattern_parts) + r')\b', re.IGNORECASE)

# ============================================================================
# Regex patterns
# ============================================================================
# MediaWiki links: [[Page]] or [[Page|Display]]
MEDIAWIKI_LINK_RE = re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
# Legacy markdown links: [text](url)
WIKI_LINK_RE = re.compile(r'\[([^\]]+)\]\(https?://oldschool\.runescape\.wiki/w/[^\)]+\)')
# Bracketed quest references: [Quest Name] not followed by (url)
BRACKET_QUEST_RE = re.compile(r'\[([^\]]+)\](?!\()')
# Withdraw line
WITHDRAW_RE = re.compile(r'^\s*-?\s*Withdraw:?\s*(.+)', re.IGNORECASE)
# Bank header: "Bank N" or "Bank NA" or "Bank 39A"
BANK_HEADER_RE = re.compile(r'^(?:title=)?Bank\s+(\d+[A-Z]?)\s*$', re.IGNORECASE)
# Episode header
EPISODE_HEADER_RE = re.compile(
    r'^(?:\[?(?:edit|edit source)\]?\s*)*'
    r'(?:Episode\s+(\d+)\s*[-–—]\s*(.+?))\s*$',
    re.IGNORECASE
)
# "Starting out" / "Starting Out" header
STARTING_RE = re.compile(r'^(?:\*+)?\s*Starting\s+[Oo]ut\s*$')
# Lines that are just NPC/item link references at end of bank sections
TRAILING_LINK_RE = re.compile(r'^\[([^\]]+)\]\(https?://[^\)]+\)\s*$')
# "Complete X quest" patterns
COMPLETE_QUEST_RE = re.compile(r'\b(?:Complete|Start|Continue|Begin|Finish)\s+(?:the\s+)?', re.IGNORECASE)
# Dialog options like (1,2,3) or (3,1)
DIALOG_RE = re.compile(r'\([\d,\s]+\)')
# Episode boundary: "End of Episode N"
END_EPISODE_RE = re.compile(r'End of Episode\s+\d+', re.IGNORECASE)
# edit/edit source wiki artifacts
EDIT_ARTIFACT_RE = re.compile(r'^\[?edit(?:\s+source)?\]?\s*$', re.IGNORECASE)
# URL-only lines
URL_ONLY_RE = re.compile(r'^https?://\S+\s*$')
# Video guide lines
VIDEO_RE = re.compile(r'^Video Guide:', re.IGNORECASE)
ROUTE_ARROW_RE = re.compile(r'^\s*([A-Za-z\' ]+?)\s*->\s*([A-Z]{3}|[A-Za-z][A-Za-z\' ]+)\s*$', re.IGNORECASE)
TRAVEL_DESTINATION_RE = re.compile(
    r'\b(?:to|towards|toward|into|for)\s+([A-Z][A-Za-z\' ]+(?:\s+[A-Z][A-Za-z\' ]+)*)'
)

ACTION_VERBS = (
    "go", "head", "run", "walk", "return", "travel", "teleport", "use",
    "cut", "catch", "pickpocket", "talk", "speak", "check", "complete",
    "continue", "start", "begin", "finish", "bank", "deposit", "buy", "sell",
    "kill", "attack", "mine", "fish", "cook", "smith", "craft", "fletch",
    "plant", "climb", "enter", "leave"
)
EXPECTED_DUPLICATE_PREFIXES = (
    "ardy cloak ->", "minigame teleport", "take boat", "take carpet",
    "ectophial", "camulet", "travel ", "withdraw:"
)
EXPECTED_DUPLICATE_EXACT = {
    "easy giants foundry plugin is helpful here.",
    "continue temple of ikov quest",
    "wield desert robes",
    "make soft clay",
    "use lamp on herblore",
}
PURE_ADVICE_PREFIXES = (
    "optional:", "note:", "warning", "important warning", "recommended:",
    "if ", "if you ", "if no ", "keep ", "make sure ", "be careful",
    "don't ", "do not ", "you need to ", "it is recommended", "this unlocks",
    "remember ", "raise ", "stay until ", "at level ", "once you ",
    "as mentioned earlier", "safe spot ", "safespot ", "max hits:",
    "strategy:", "move coins into first bank slot", "set bank pin",
    "set your bank up ", "set your bank up with", "^ "
)
META_ADVICE_PREFIXES = (
    "at this point you should prioritise",
    "at this point, do not",
    "birdhouse run method:",
    "depending on cash stack",
    "depending how spooned",
    "feel free to spend as long as you need",
    "for maintaining ",
    "here we are going to",
    "inventory:",
    "it is your choice what teleports",
    "medium farming contracts are excellent",
    "mould order:",
    "order of points usage:",
    "now we have ",
    "there are 2 paths",
    "this should net you over",
    "this is where you hit ",
    "these are 0 damage",
    "you can 2 trip",
    "you can do all these",
    "you can take significant damage",
    "you will need gp to upkeep",
    "you want to trade ",
)
META_ADVICE_MARKERS = (
    " patch -",
    " comfortable point",
    " excellent",
    " faster",
    " hard requirement",
    " mandatory",
    " may require",
    " methods",
    " passive ",
    " priority",
    " restore ",
    " slower",
    " theorycrafted",
    " very safe",
    " bottleneck",
    " the guide will mention",
    " you can catch over",
)
FORWARD_ADVICE_PREFIXES = (
    "optional:", "note:", "warning", "important warning", "make sure ",
    "you need to ", "remember ", "if ", "if you ", "if no ", "bring "
)
ACTION_OPENERS = (
    "withdraw", "bank ", "deposit", "head ", "go ", "run ", "walk ",
    "teleport", "home teleport", "minigame teleport", "talk ", "talk to",
    "speak ", "start ", "continue ", "complete ", "kill ", "attack ",
    "mine ", "fish ", "cook ", "buy ", "sell ", "trade ", "collect ",
    "take ", "pick ", "grab ", "get ", "open ", "search ", "check ",
    "claim ", "hand in ", "turn in ", "use ", "wear ", "equip ",
    "cross ", "enter ", "leave ", "climb ", "loot ", "steal ", "thieve ",
    "pickpocket ", "travel ", "return ", "npc contact ", "block ",
    "set ", "scout ", "plant ", "make ", "fill ", "clean ", "throw ",
    "farm ", "boost ", "catch ", "pray ", "camp ", "do ", "find ",
    "hop ", "wield ", "drink ", "recharge ", "tan "
)
ADVICE_MARKERS = (
    "optional", "note", "warning", "important", "make sure", "be careful",
    "hop worlds", "safe spot", "safespot", "do not", "don't", "for later",
    "later", "recommended", "if you", "if no", "worth", "low on",
    "max hit", "shortcut", "can kill you", "repeat", "emergency teleport",
    "remember", "not mandatory", "very dangerous"
)


def load_wiki_tables(base_dir):
    wiki_dir = os.path.join(base_dir, "data", "wiki")
    return {
        "quests": load_json_if_exists(os.path.join(wiki_dir, "quests.json"), []),
        "npcs": load_json_if_exists(os.path.join(wiki_dir, "npcs.json"), []),
        "items": load_json_if_exists(os.path.join(wiki_dir, "items.json"), []),
        "locations": load_json_if_exists(os.path.join(wiki_dir, "locations.json"), []),
    }


def initialize_entity_patterns(wiki_tables):
    global QUESTS, CANONICAL_QUEST_LOOKUP, QUEST_REGEX
    global KNOWN_NPCS, NPC_REGEX
    global LOCATION_NAMES, LOCATION_REGEX

    quest_names = list(OrderedDict.fromkeys((wiki_tables.get("quests") or []) + QUESTS))
    quest_names = [canonical_name(name) for name in quest_names if canonical_name(name)]
    quest_names = list(OrderedDict.fromkeys(quest_names))
    quest_names.sort(key=len, reverse=True)
    QUESTS = quest_names
    CANONICAL_QUEST_LOOKUP = {q.lower(): q for q in QUESTS}
    quest_pattern_parts = [re.escape(q) for q in QUESTS]
    QUEST_REGEX = re.compile(r'\b(' + '|'.join(quest_pattern_parts) + r')\b', re.IGNORECASE)

    npc_names = list(OrderedDict.fromkeys((wiki_tables.get("npcs") or []) + KNOWN_NPCS))
    npc_names = [canonical_name(name) for name in npc_names if canonical_name(name)]
    npc_names = [name for name in npc_names if len(name) > 2]
    npc_names = list(OrderedDict.fromkeys(npc_names))
    npc_names.sort(key=len, reverse=True)
    KNOWN_NPCS = npc_names
    npc_pattern_parts = [re.escape(n) for n in KNOWN_NPCS]
    NPC_REGEX = re.compile(r'\b(' + '|'.join(npc_pattern_parts) + r')\b', re.IGNORECASE)

    for location_name in wiki_tables.get("locations") or []:
        normalized = canonical_name(location_name).lower()
        if normalized and normalized not in LOCATION_COORDS:
            LOCATION_COORDS[normalized] = None
    LOCATION_NAMES = sorted(LOCATION_COORDS.keys(), key=len, reverse=True)
    loc_pattern_parts = [re.escape(loc) for loc in LOCATION_NAMES]
    LOCATION_REGEX = re.compile(r'\b(' + '|'.join(loc_pattern_parts) + r')\b', re.IGNORECASE)


def fetch_guide_content(url=WIKI_URL, cache_path=None):
    """Fetch the wiki page content. Uses cache if available."""
    if cache_path and os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            return f.read()

    print(f"Fetching guide from {url}...")
    request = Request(url, headers={"User-Agent": "BoatyGuideParser/1.0"})
    with urlopen(request) as resp:
        raw = resp.read().decode('utf-8')

    if cache_path:
        os.makedirs(os.path.dirname(cache_path) or '.', exist_ok=True)
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(raw)

    return raw


def clean_text(text):
    """Remove wiki link markup, keeping display text."""
    text = MEDIAWIKI_LINK_RE.sub(lambda m: (m.group(2) or m.group(1)), text)
    # Replace [text](url) with just text
    text = WIKI_LINK_RE.sub(r'\1', text)
    # Remove leftover markdown link artifacts
    text = re.sub(r'\[([^\]]+)\]\([^\)]*\)', r'\1', text)
    text = text.replace("'''", "")
    text = text.replace("}}", "")
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'{{[^{}]+}}', '', text)
    text = text.replace("(Install Quest Helper plug in on Runelite)", "").strip()
    text = text.replace("There is a LOT of multi-questing so you will be ignoring Quest Helper a lot.", "").strip()
    text = text.replace("you can start a quest helper for this quest and follow as directed.", "follow the guide directly for those quest segments.").strip()
    text = re.sub(r'\bquest helper\b', 'wiki quick guide', text, flags=re.IGNORECASE)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()


def extract_wiki_linked_names(text):
    """Extract all names from wiki markdown links [Name](wiki_url)."""
    names = list(WIKI_LINK_RE.findall(text))
    for match in MEDIAWIKI_LINK_RE.finditer(text):
        names.append(match.group(2) or match.group(1))
    return names


def extract_quests(text):
    """Extract quest references from step text using multiple strategies."""
    quests = set()

    # Strategy 1: Bracketed references [Quest Name] not followed by URL
    clean = WIKI_LINK_RE.sub('', text)  # Remove wiki links first
    for match in BRACKET_QUEST_RE.finditer(clean):
        candidate = match.group(1).strip()
        # Filter out non-quest brackets (inventory counts, diary refs, etc.)
        if re.match(r'^\d+', candidate):
            continue
        if candidate.lower() in ('optional', 'note', 'warning', 'quests'):
            continue
        parts = re.split(r'\s*(?:\+|/|,| and )\s*', candidate, flags=re.IGNORECASE)
        for part in parts:
            normalized = canonical_name(part).lower()
            if normalized in CANONICAL_QUEST_LOOKUP and normalized != "quests":
                quests.add(CANONICAL_QUEST_LOOKUP[normalized])

    # Strategy 2: Free-text quest name matching
    for match in QUEST_REGEX.finditer(text):
        normalized = canonical_name(match.group(0)).lower()
        if normalized != "quests":
            quests.add(CANONICAL_QUEST_LOOKUP.get(normalized, match.group(0)))

    return list(quests)


def extract_npcs(text):
    """Extract NPC names from step text using wiki links AND known NPC dictionary."""
    npcs = set()

    # Strategy 1: Wiki-linked NPCs
    for name in extract_wiki_linked_names(text):
        # Filter out items/locations/quests that are also wiki-linked
        name_lower = name.lower()
        if any(kw in name_lower for kw in ['rune', 'arrow', 'potion', 'ore', 'bar',
                                            'diary', 'course', 'arena', 'dungeon',
                                            'store', 'shop', 'inn', 'guild', 'altar',
                                            'island', 'cave', 'mountain', 'quest',
                                            'key', 'amulet', 'ring', 'necklace',
                                            'temple', 'castle', 'village', 'city',
                                            'forest', 'swamp', 'minecart', 'lever',
                                            'shortcut', 'bridge', 'gate', 'door',
                                            'random event', 'agility', 'mining',
                                            'stall', 'mushroom', 'seaweed', 'sample',
                                            'pigeon cage', 'rotten apple', 'eclipse',
                                            'mouse keys', 'pendant', 'sickle',
                                            'clock', 'volcanic', 'transportation',
                                            'talisman', 'plank', 'brain',
                                            'repellent', 'cooler']):
            continue
        npcs.add(name)

    # Strategy 2: Known NPC dictionary matching
    cleaned = clean_text(text)
    for match in NPC_REGEX.finditer(cleaned):
        candidate = match.group(0).strip()
        if candidate.lower() in FALSE_POSITIVE_NPCS:
            continue
        if candidate.islower():
            continue
        npcs.add(candidate)

    # Strategy 3: "Talk to X" pattern for unlinked NPCs
    talk_pattern = re.compile(
        r'\b(?:Talk to|Speak to|Trade|Buy from|Sell to)\s+'
        r'(?:the\s+)?([A-Z][a-zA-Z\' -]+?)(?:\s*\(|\s*\[|\s+and\b|\s+to\b|\s+for\b|\s+in\b|\s+at\b|\s+until\b|\s+continue\b|\s+start\b|\s+complete\b|\s*$)',
        re.MULTILINE
    )
    for match in talk_pattern.finditer(text):
        candidate = match.group(1).strip().rstrip('.,;:!')
        if len(candidate) > 2 and len(candidate) < 40:
            if not any(kw in candidate.lower() for kw in [
                'bank', 'shop', 'store', 'altar', 'door', 'gate', 'ladder',
                'stairs', 'rope', 'wall', 'chest', 'crate', 'barrel',
                'north', 'south', 'east', 'west', 'the '
            ]):
                words = [w for w in candidate.split() if w.lower() not in NPC_STOPWORDS]
                cleaned_candidate = " ".join(words).strip()
                if cleaned_candidate and cleaned_candidate[0].isupper():
                    npcs.add(cleaned_candidate)

    return list(npcs)


def extract_locations(text):
    """Extract location references and map to WorldPoint coordinates."""
    locations = []
    seen = set()
    clean = clean_text(text)

    for match in LOCATION_REGEX.finditer(clean):
        loc_name = match.group(0).lower()
        if loc_name not in seen:
            seen.add(loc_name)
            coords = LOCATION_COORDS.get(loc_name)
            location = {"name": match.group(0)}
            if coords:
                location.update({
                    "x": coords[0],
                    "y": coords[1],
                    "z": coords[2]
                })
            locations.append(location)

    return locations


def extract_items(text):
    """Extract items from a 'Withdraw:' line."""
    match = WITHDRAW_RE.match(text)
    if not match:
        return []

    items_str = match.group(1)
    items_str = re.sub(r'(?<=\d),(?=\d)', '', items_str)
    items_str = re.sub(r'\[[^\]]*diary[^\]]*\]', '', items_str, flags=re.IGNORECASE)
    items_str = re.sub(r'\[[^\]]*you may need[^\]]*\]', '', items_str, flags=re.IGNORECASE)
    items_str = re.split(
        r'\b(?:and|then)\s+(?:' + '|'.join(re.escape(v) for v in ACTION_VERBS) + r')\b',
        items_str,
        maxsplit=1,
        flags=re.IGNORECASE
    )[0]
    items_str = re.split(r'\bone trip\b', items_str, maxsplit=1, flags=re.IGNORECASE)[0]
    # Remove parenthetical inventory slot counts
    items_str = re.sub(r'\(\d+\s*[Ii]nventory\s*[Ss]lots?\s*\)', '', items_str)
    items_str = re.sub(r'\(\d+\s*[Ii]nventory\s*[Ss]paces?\s*\)', '', items_str)
    items_str = re.sub(r'\(\d+\s*[Ii]nventory\s*[Ss]pot\w*\)', '', items_str)
    items_str = re.sub(r'\[\d+\s*[Ii]nventory\s*[Ss]lots?\s*\]', '', items_str)
    items_str = re.sub(r'\[\d+\s*[Ii]nventory\s*[Ss]paces?\s*\]', '', items_str)

    # Split on commas
    raw_items = [i.strip() for i in items_str.split(',')]
    items = []
    for item in raw_items:
        item = item.strip()
        if not item:
            continue
        # Extract quantity prefix like "10x" or "2x"
        qty_match = re.match(r'^(\d+)x?\s+(.+)', item, re.IGNORECASE)
        if qty_match:
            items.append({
                "name": clean_text(qty_match.group(2).strip()),
                "quantity": int(qty_match.group(1))
            })
        elif re.match(r'^All\s+', item, re.IGNORECASE):
            items.append({"name": clean_text(item), "quantity": -1})
        else:
            items.append({"name": clean_text(item), "quantity": 1})

    return items


def is_duplicate_line(line, seen_lines, bank_lines):
    """Check if this line is a duplicate within the current bank section."""
    # Normalize for comparison
    normalized = re.sub(r'\s+', ' ', line.strip().lower())
    if normalized in seen_lines:
        return True
    seen_lines.add(normalized)
    return False


def is_junk_line(line):
    """Filter out wiki artifacts, trailing link refs, edit buttons, etc."""
    stripped = line.strip()
    if not stripped:
        return True
    if TRAILING_LINK_RE.match(stripped):
        return True
    if EDIT_ARTIFACT_RE.match(stripped):
        return True
    if URL_ONLY_RE.match(stripped):
        return True
    if VIDEO_RE.match(stripped):
        return True
    if stripped.startswith('[edit]') or stripped.startswith('[edit source]'):
        return True
    # Pure link reference lines like [NPC Name](url) with no bullet
    if re.match(r'^\[.+\]\(https?://.+\)\s*$', stripped):
        return True
    # Jump to navigation etc
    if stripped.startswith('[Jump to'):
        return True
    if stripped.startswith('[supplemental guide]') or stripped.startswith('[style guide]'):
        return True
    # TOC entries
    if re.match(r'^\[[\d.]+\s+Episode', stripped):
        return True
    if re.match(r'^\[\d+\.\d+', stripped):
        return True
    if re.match(r'^\[\d+\s+', stripped):
        return True
    # Source/title lines
    if stripped.startswith('Title:') or stripped.startswith('Source:') or stripped.startswith('Description:'):
        return True
    if stripped.startswith('OG Description:'):
        return True
    if stripped == '---':
        return True
    if stripped.startswith('{{Var|') or stripped.startswith('{{var|'):
        return True
    if stripped.startswith('{{Extimage|') or stripped.startswith('{{Youtube|'):
        return True
    if stripped.startswith('{{Checklist|title=|'):
        return True
    if stripped.startswith('{{Checklist|title=Yama'):
        return True
    if stripped == '}}' or stripped == '|}}':
        return True
    return False


def normalize_advice_text(text):
    normalized = clean_text(text).strip().strip("-:;,.")
    normalized = normalized.strip("[]")
    if normalized.endswith(')') and normalized.count('(') < normalized.count(')'):
        normalized = normalized.rstrip(')').rstrip()
    if normalized.startswith('(') and normalized.count('(') > normalized.count(')'):
        normalized = normalized.lstrip('(').lstrip()
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized


def starts_with_action(text):
    lower = normalize_advice_text(text).lower()
    return lower.startswith(ACTION_OPENERS)


def is_bank_management_advice_line(text):
    lower = normalize_advice_text(text).lower()
    return lower.startswith((
        "keep ",
        "move coins into first bank slot",
        "set bank pin",
        "set your bank up ",
        "set your bank up with",
    ))


def starts_with_dialogue_action(text):
    normalized = normalize_advice_text(text)
    match = re.match(r'^\(?\d+(?:,\d+)*\)?\s*(.*)$', normalized)
    if not match:
        return False

    remainder = match.group(1).strip()
    return not remainder or starts_with_action(remainder)


def is_action_like_text(text):
    normalized = normalize_advice_text(text)
    if not normalized:
        return False

    return starts_with_action(normalized) or starts_with_dialogue_action(normalized)


def is_meta_advice_line(text):
    lower = normalize_advice_text(text).lower()
    return lower.startswith(META_ADVICE_PREFIXES)


def is_combat_advice_line(text):
    normalized = normalize_advice_text(text)
    lower = normalized.lower()
    return (
        bool(re.match(r"^[a-z][a-z'() _-]+ max is \d+", lower))
        or lower.startswith(("max is ", "these are 0 damage"))
    )


def looks_meta_strategy_text(text):
    lower = normalize_advice_text(text).lower()
    return (
        lower.startswith(META_ADVICE_PREFIXES)
        or re.match(r'^[a-z][a-z\' ]+ patch -', lower)
        or lower.startswith("farming guild -")
        or any(marker in lower for marker in META_ADVICE_MARKERS)
    )


def is_pure_advice_line(text):
    normalized = normalize_advice_text(text)
    if not normalized:
        return False

    lower = normalized.lower()
    if is_bank_management_advice_line(normalized):
        return True
    if is_combat_advice_line(normalized):
        return True
    if starts_with_action(normalized):
        return False

    return lower.startswith(PURE_ADVICE_PREFIXES) or lower.startswith(META_ADVICE_PREFIXES)


def is_advice_fragment(text):
    normalized = normalize_advice_text(text)
    if not normalized:
        return False

    lower = normalized.lower()
    if re.fullmatch(r'[\d,\s]+', lower):
        return False
    if lower.startswith(PURE_ADVICE_PREFIXES):
        return True
    return any(marker in lower for marker in ADVICE_MARKERS)


def strip_parenthetical_advice(text):
    base = []
    advice_segments = []
    current = []
    depth = 0

    for char in text:
        if char == '(':
            if depth > 0:
                current.append(char)
            depth += 1
            continue

        if char == ')' and depth > 0:
            depth -= 1
            if depth == 0:
                fragment = ''.join(current)
                normalized = normalize_advice_text(fragment)
                if normalized and is_advice_fragment(normalized):
                    advice_segments.append(normalized)
                else:
                    base.append('(' + fragment + ')')
                current = []
            else:
                current.append(char)
            continue

        if depth > 0:
            current.append(char)
        else:
            base.append(char)

    if depth > 0 and current:
        base.append('(' + ''.join(current))

    return ''.join(base), advice_segments


def rewrite_action_text(text):
    prefixed_advice = []
    rewritten = text
    lower = text.lower()

    npc_contact_prefix = "you will be npc contacting "
    comfortable_prefix = "this is now a comfortable point to get "
    single_kill_prefix = "you only need to kill "
    collect_prefix = "you will need to collect "

    if lower.startswith(npc_contact_prefix):
        rewritten = "NPC contact " + text[len(npc_contact_prefix):]
        rewritten = rewritten.replace(" and completing ", " and complete ", 1)

    if lower.startswith(comfortable_prefix):
        prefixed_advice.append("This is now a comfortable point.")
        rewritten = "Get " + text[len(comfortable_prefix):]

    if lower.startswith(single_kill_prefix):
        prefixed_advice.append("You only need one kill for this step.")
        rewritten = "Kill " + text[len(single_kill_prefix):]

    if lower.startswith(collect_prefix):
        rewritten = "Collect " + text[len(collect_prefix):]

    if re.match(r'^\d+x\s', lower) and any(token in lower for token in ("teak", "mahogany", "maples", " herb")):
        rewritten = "Set workers to " + text

    if lower.startswith("go back to edgeville and take the lever to the wilderness"):
        prefixed_advice.append("This is for the Wilderness and Ardougne Diary.")
        rewritten = "Use the Edgeville and Ardougne wilderness lever 4 times."

    if lower.startswith("do olaf's and manni's tasks together"):
        rewritten = "Do Olaf's and Manni's tasks together."
        split_marker = "but before going back to camelot"
        if split_marker in lower:
            marker_index = lower.index(split_marker)
            prefixed_advice.append(text[marker_index:].strip().rstrip('.'))

    if lower.startswith("enter varrock museum and head downstairs and talk to orlando smith"):
        rewritten = "Enter Varrock Museum, talk to Orlando Smith (1), and complete the Natural History Quiz."
        prefixed_advice.append("This gives 9 Slayer, 9 Hunter, and 28 kudos.")

    if lower.startswith("complete dwarf rfd step when heading to goblin village until rock cake"):
        rewritten = "Complete the Dwarf RFD step until Rock Cake."
        extra = text[len("Complete Dwarf RFD step when heading to Goblin Village until Rock Cake"):].strip(" -")
        if extra:
            prefixed_advice.append(extra)

    if lower.startswith("picklock the chest in hemenster"):
        rewritten = "Picklock the chest in Hemenster [Kandarin Medium Diary]."
        if "(" in text and ")" in text:
            prefixed_advice.append(normalize_advice_text(text[text.index("(") + 1:text.rindex(")")]))

    if lower.startswith("when getting the signatures, find 2 ghosts near each other"):
        rewritten = "Get 10 signatures for Ghost's Ahoy."
        prefixed_advice.append("Find 2 ghosts near each other and swap if they ask for Ectotokens or deny you.")

    if lower.startswith("catch the scorpion right after going through the gate"):
        rewritten = "Catch the Scorpion [Scorpion Catcher]."
        location_start = lower.find("right after going through the gate")
        if location_start != -1:
            prefixed_advice.append(text[location_start:].strip())

    if lower.startswith("use the deposit box by entrana and deposit everything except:"):
        rewritten = "Use the deposit box by Entrana and keep only the required items."

    if lower.startswith("collect 15 supercompost. deposit in leprechaun."):
        rewritten = "Collect 15 Supercompost and deposit it in the Leprechaun."

    return rewritten, prefixed_advice


def split_action_and_advice(text):
    action_text, advice_lines = rewrite_action_text(clean_text(text).strip())

    if action_text.startswith('[') and ']' in action_text:
        bracket_note, remainder = action_text[1:].split(']', 1)
        normalized_bracket_note = normalize_advice_text(bracket_note)
        if normalized_bracket_note:
            advice_lines.append(normalized_bracket_note)
        action_text = remainder.strip()

    if action_text.startswith('(') and action_text.endswith(')'):
        advice_lines.append(normalize_advice_text(action_text[1:-1]))
        action_text = ""

    if action_text and is_pure_advice_line(action_text):
        advice_lines.append(normalize_advice_text(action_text))
        action_text = ""

    action_text, parenthetical_advice = strip_parenthetical_advice(action_text)
    advice_lines.extend(parenthetical_advice)

    if action_text.count('(') > action_text.count(')') and '(' in action_text:
        head, tail = action_text.split('(', 1)
        if starts_with_action(head):
            action_text = head.strip()
            advice_lines.append(normalize_advice_text(tail))

    if " - " in action_text:
        head, tail = action_text.split(" - ", 1)
        if is_advice_fragment(tail):
            action_text = head.strip()
            advice_lines.append(normalize_advice_text(tail))

    if ", SAVE " in action_text or ", save " in action_text:
        save_match = re.search(r',\s*(save .+)', action_text, re.IGNORECASE)
        if save_match:
            action_text = action_text[:save_match.start()].strip()
            advice_lines.append(normalize_advice_text(save_match.group(1)))

    sentence_parts = [part.strip() for part in re.split(r'(?<=[.!?])\s+', action_text) if part.strip()]
    first_action_index = next(
        (index for index, part in enumerate(sentence_parts) if is_action_like_text(part)),
        None
    )
    if first_action_index is None:
        if looks_meta_strategy_text(action_text):
            advice_lines.append(normalize_advice_text(action_text))
            action_text = ""
    elif len(sentence_parts) > 1:
        action_sentences = []
        trailing_advice = []
        for part in sentence_parts[:first_action_index]:
            trailing_advice.append(normalize_advice_text(part))
        for part in sentence_parts[first_action_index:]:
            if is_action_like_text(part) and not (
                action_sentences
                and " until " in action_sentences[0].lower()
                and part.lower().startswith(("bank ", "deposit ", "keep "))
            ) and not (
                action_sentences
                and action_sentences[0].lower().startswith(("bank ", "bank at", "use the deposit box", "collect "))
                and part.lower().startswith("withdraw ")
            ):
                action_sentences.append(part)
            else:
                trailing_advice.append(normalize_advice_text(part))
        action_text = " ".join(action_sentences).strip()
        advice_lines.extend(trailing_advice)

    action_text = re.sub(r'\s+', ' ', action_text).strip().strip("-:;")

    unique_advice = []
    seen = set()
    for advice in advice_lines:
        normalized = normalize_advice_text(advice)
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        unique_advice.append(normalized)

    return action_text, unique_advice


def should_attach_advice_to_next(advice_text, previous_step):
    lower = advice_text.lower()
    if lower.startswith(FORWARD_ADVICE_PREFIXES):
        return True
    if previous_step is None:
        return True

    previous_type = classify_step(previous_step["text"], bool(previous_step.get("items")))
    return previous_type in {"WITHDRAW", "DEPOSIT", "BANK_SETUP"}


def find_contextual_forward_step(entries, action_indexes, advice_index, previous_index, immediate_next_index):
    if previous_index is None:
        return immediate_next_index

    reference_quests = set(entries[previous_index].get("quests", []))
    if not reference_quests:
        return immediate_next_index

    for candidate in action_indexes:
        if candidate <= advice_index:
            continue
        candidate_quests = set(entries[candidate].get("quests", []))
        if reference_quests & candidate_quests:
            return candidate

    return immediate_next_index


def create_episode(ep_num, ep_title):
    return {
        "episode": ep_num,
        "title": f"Episode {ep_num} - {ep_title}",
        "banks": []
    }


def create_bank(bank_id, title, transition_notes=None, nested_bullets_as_steps=False):
    return {
        "bank": bank_id,
        "title": title,
        "transitionNotes": list(transition_notes or []),
        "adviceLines": [],
        "entries": [],
        "steps": [],
        "withdrawItems": [],
        "nestedBulletsAsSteps": nested_bullets_as_steps,
    }


def extract_bullet_info(stripped, nested_bullets_as_steps):
    bullet_depth = 0
    if stripped.startswith('**'):
        bullet_depth = 2
    elif stripped.startswith('*') or stripped.startswith('- '):
        bullet_depth = 1

    if bullet_depth > 1 and nested_bullets_as_steps:
        bullet_depth = 1

    cleaned = clean_text(stripped)
    if cleaned.startswith('**'):
        step_text = re.sub(r'^\*+\s*', '', cleaned).strip()
    elif cleaned.startswith('*'):
        step_text = re.sub(r'^\*+\s*', '', cleaned).strip()
    elif cleaned.startswith('- '):
        step_text = cleaned[2:].strip()
    elif len(cleaned) > 10 and not re.match(r'^[\[\(]', cleaned):
        step_text = cleaned
    else:
        return None, None

    return bullet_depth, step_text


def classify_bank_entry(current_bank, bullet_depth, display_text, step_text, quests, npcs, locations, items):
    if items and WITHDRAW_RE.match(step_text):
        current_bank["withdrawItems"] = items

    if bullet_depth > 1 and (is_pure_advice_line(display_text) or looks_meta_strategy_text(display_text)):
        return [{"kind": "advice", "text": normalize_advice_text(display_text)}]

    if is_pure_advice_line(display_text):
        return [{"kind": "advice", "text": normalize_advice_text(display_text)}]

    action_text, inline_advice = split_action_and_advice(display_text)
    entries = []
    if not action_text:
        for advice in inline_advice:
            entries.append({"kind": "advice", "text": advice})
        return entries

    entry_kind = "substep" if bullet_depth > 1 and not current_bank.get("nestedBulletsAsSteps") else "step"
    entries.append({
        "kind": entry_kind,
        "text": action_text,
        "rawText": step_text,
        "quests": quests,
        "npcs": npcs,
        "locations": locations,
        "items": items if WITHDRAW_RE.match(step_text) else [],
        "adviceLines": inline_advice,
    })
    return entries


def finalize_bank_entries(bank):
    raw_entries = bank.pop("entries", [])
    entries = []
    for entry in raw_entries:
        entries.append(entry)

    steps = []
    bank_advice = []
    action_indexes = [index for index, entry in enumerate(entries) if entry["kind"] == "step"]
    attached_advice = {}
    attached_substeps = {}

    for index, entry in enumerate(entries):
        if entry["kind"] == "substep":
            previous_index = next((candidate for candidate in reversed(action_indexes) if candidate < index), None)
            if previous_index is None:
                promoted = dict(entry)
                promoted["kind"] = "step"
                entries[index] = promoted
                action_indexes = [idx for idx, item in enumerate(entries) if item["kind"] == "step"]
            else:
                attached_substeps.setdefault(previous_index, []).append(entry)
            continue

        if entry["kind"] != "advice":
            continue

        previous_index = next((candidate for candidate in reversed(action_indexes) if candidate < index), None)
        next_index = next((candidate for candidate in action_indexes if candidate > index), None)

        if previous_index is None and next_index is None:
            bank_advice.append(entry["text"])
            continue

        if previous_index is None:
            target_index = next_index
        elif next_index is None:
            target_index = previous_index
        elif should_attach_advice_to_next(entry["text"], entries[previous_index]):
            target_index = find_contextual_forward_step(entries, action_indexes, index, previous_index, next_index)
        else:
            target_index = previous_index

        if target_index is None:
            bank_advice.append(entry["text"])
            continue

        attached_advice.setdefault(target_index, []).append(entry["text"])

    for index, entry in enumerate(entries):
        if entry["kind"] != "step":
            continue

        step_advice = list(entry.get("adviceLines", []))
        step_advice.extend(attached_advice.get(index, []))

        unique_advice = []
        seen = set()
        for advice in step_advice:
            normalized = normalize_advice_text(advice)
            if not normalized:
                continue
            key = normalized.lower()
            if key in seen:
                continue
            seen.add(key)
            unique_advice.append(normalized)

        step = {
            "text": entry["text"],
            "rawText": entry["rawText"],
            "quests": entry["quests"],
            "npcs": entry["npcs"],
            "locations": entry["locations"],
            "items": entry["items"],
            "substeps": [substep["text"] for substep in attached_substeps.get(index, [])],
            "adviceLines": unique_advice,
            "stepIndex": len(steps),
        }
        steps.append(step)

    bank["steps"] = steps
    bank["adviceLines"] = bank_advice


def parse_guide(content):
    """Parse the guide content into structured episodes/banks/steps."""
    lines = content.split('\n')

    episodes = []
    current_episode = None
    current_bank = None
    bank_seen_lines = set()
    seen_starting = False
    pending_transition_notes = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        i += 1

        if stripped == '}}' or stripped == '|}}':
            current_bank = None
            bank_seen_lines = set()
            continue

        # Skip junk lines
        if is_junk_line(stripped):
            continue

        normalized_header = clean_text(stripped.strip("=")).strip(":")

        # Check for episode headers
        ep_match = EPISODE_HEADER_RE.match(normalized_header)
        if ep_match:
            ep_num = int(ep_match.group(1))
            ep_title = ep_match.group(2).strip().rstrip(':')
            current_episode = create_episode(ep_num, ep_title)
            episodes.append(current_episode)
            continue

        # Check for "End of Episode"
        if END_EPISODE_RE.match(stripped):
            continue

        # Check for "Starting Out" section
        if "{{Checklist|title=Starting out" in stripped or STARTING_RE.match(normalized_header):
            if seen_starting:
                continue
            seen_starting = True
            if not current_episode:
                current_episode = create_episode(1, "Banks 1 through 24")
                episodes.append(current_episode)

            current_bank = create_bank("0", "Starting Out", [], True)
            current_episode["banks"].append(current_bank)
            pending_transition_notes = []
            bank_seen_lines = set()
            continue

        # Check for bank headers
        bank_match = BANK_HEADER_RE.match(normalized_header)
        if bank_match:
            bank_id = bank_match.group(1)

            if not current_episode:
                current_episode = create_episode(1, "Banks 1 through 24")
                episodes.append(current_episode)

            current_bank = create_bank(bank_id, f"Bank {bank_id}", pending_transition_notes, False)
            current_episode["banks"].append(current_bank)
            pending_transition_notes = []
            bank_seen_lines = set()
            inline_bullet = stripped.split("|*", 1)[1].strip() if "|*" in stripped else None
            if inline_bullet:
                stripped = "* " + inline_bullet
            else:
                continue

        if stripped.startswith("{{Checklist|title=Bank"):
            bank_id = str(sum(len(ep["banks"]) for ep in episodes))

            if not current_episode:
                current_episode = create_episode(1, "Banks 1 through 24")
                episodes.append(current_episode)

            current_bank = create_bank(bank_id, f"Bank {bank_id}", pending_transition_notes, False)
            current_episode["banks"].append(current_bank)
            pending_transition_notes = []
            bank_seen_lines = set()
            inline_bullet = stripped.split("|*", 1)[1].strip() if "|*" in stripped else None
            if inline_bullet:
                stripped = "* " + inline_bullet
            else:
                continue

        # Skip if no current bank
        if current_bank is None:
            stripped = clean_text(stripped)
            if stripped.startswith('** '):
                note_text = stripped[3:].strip()
            elif stripped.startswith('* '):
                note_text = stripped[2:].strip()
            elif stripped.startswith('- '):
                note_text = stripped[2:].strip()
            elif len(stripped) > 10 and not re.match(r'^[\[\(]', stripped):
                note_text = stripped
            else:
                continue

            if note_text and not is_duplicate_line(note_text, set(pending_transition_notes), []):
                pending_transition_notes.append(note_text)
            continue

        bullet_depth, step_text = extract_bullet_info(stripped, current_bank.get("nestedBulletsAsSteps"))
        if step_text is None:
            continue

        display_text = clean_text(step_text)
        # Deduplicate within current bank
        if is_duplicate_line(step_text, bank_seen_lines, current_bank["steps"]):
            continue

        # Skip lines that are just quest/NPC name repetitions from wiki rendering
        if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+$', step_text) and len(step_text) < 25:
            # Might be a bare NPC name line, skip unless it's actionable
            if not any(kw in step_text.lower() for kw in ['talk', 'head', 'go', 'buy', 'sell',
                                                           'complete', 'start', 'continue',
                                                           'collect', 'kill', 'mine',
                                                           'withdraw', 'bank', 'take']):
                continue

        # Extract metadata from step
        quests = extract_quests(step_text)
        npcs = extract_npcs(step_text)
        locations = extract_locations(step_text)
        items = extract_items(step_text)
        current_bank["entries"].extend(
            classify_bank_entry(current_bank, bullet_depth, display_text, step_text, quests, npcs, locations, items)
        )

    for episode in episodes:
        for bank in episode["banks"]:
            finalize_bank_entries(bank)

    return episodes


def assign_global_indices(episodes):
    """Assign globally unique step IDs for progress tracking."""
    global_idx = 0
    for episode in episodes:
        for bank in episode["banks"]:
            bank_id = bank["bank"]
            for step in bank["steps"]:
                step["globalId"] = f"e{episode['episode']}_b{bank_id}_s{step['stepIndex']}"
                step["globalIndex"] = global_idx
                global_idx += 1
    return global_idx


def load_json_if_exists(path, default):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as handle:
            return json.load(handle)
    return default


def canonical_name(name):
    cleaned = clean_text(name).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned


def classify_step(text, has_withdraw_items):
    lower = clean_text(text).lower()
    diary_line = bool(re.search(r'\[[^\]]*diary[^\]]*\]', text, re.IGNORECASE))
    if has_withdraw_items:
        return "WITHDRAW"
    if ":" in lower and any(token in lower for token in ("safespot", "safe spot", "teleport out")):
        return "CHECKPOINT"
    if lower.startswith(("warning:", "(warning:", "optional:", "to be updated", "here we are going to", "block these tasks", "all tempoross")):
        return "CHECKPOINT"
    if lower.startswith("after "):
        return "CHECKPOINT"
    if lower.startswith(("continue ", "continue & complete ", "continue and complete ")):
        if "complete" in lower:
            return "QUEST_COMPLETE"
        return "QUEST_PROGRESS"
    if lower.startswith(("start ", "begin ")):
        return "QUEST_START"
    if any(token in lower for token in ("placeholder", "bank pin", "bank slot", "tool leprechaun")):
        return "BANK_SETUP"
    if any(lower.startswith(token) for token in ("head ", "walk ", "run ", "return ", "go ", "leave ", "enter ", "climb ", "cross ", "open minimap", "follow the path", "chronicle ", "teleport ", "home teleport", "minigame teleport", "ardy cloak", "ectophial", "chronicle", "camulet")):
        return "TRAVEL"
    if "->" in lower and any(token in lower for token in ("cloak", "ring", "amulet", "chronicle", "teleport", "dueling", "duelling")):
        return "TRAVEL"
    if lower.startswith("bank ") or "deposit" in lower:
        return "DEPOSIT"
    if any(token in lower for token in ("teleport", "travel", "head to", "go to", "run to", "walk to")):
        return "TRAVEL"
    if ">" in lower and any(token in lower for token in ("blessing", "necklace of passage", "camulet", "ring of duelling", "duelling ring", "games necklace", "skills necklace")):
        return "TRAVEL"
    if any(token in lower for token in ("ship", "boat", "charter", "canoe", "glider", "spirit tree", "fairy ring", "carpet")):
        return "TRANSPORT"
    if any(token in lower for token in ("talk to", "talk with", "speak to")):
        return "TALK_TO_NPC"
    if lower.startswith(("talking to ", "npc contact ")):
        return "TALK_TO_NPC"
    if lower.startswith("block "):
        return "CHECKPOINT"
    if any(lower.startswith(token) for token in ("check ", "claim ", "hand in ", "turn in ")):
        return "TALK_TO_NPC" if extract_npcs(text) else "CHECKPOINT"
    if any(phrase in lower for phrase in (" max is ", " tile markers ", "npc contacting ", "barrows portal", "tempoross", "chambers of xeric", "task second")):
        return "CHECKPOINT"
    if any(lower.startswith(token) for token in ("drop ", "give ", "inspect ", "hide ", "pet ", "bless ", "safe spot ", "safespot ", "set up ", "build ", "blow ")):
        return "ITEM_USE" if any(lower.startswith(token) for token in ("drop ", "give ", "inspect ", "build ", "blow ")) else "CHECKPOINT"
    if any(lower.startswith(token) for token in ("pickpocket ", "thieve ", "catch ", "hunt ", "search ")):
        return "SKILL_ACTION"
    if lower.startswith("shear "):
        return "SKILL_ACTION"
    if any(lower.startswith(token) for token in ("collect ", "take ", "pick ", "grab ", "get ")):
        return "ITEM_USE"
    if any(token in lower for token in ("buy ", "sell ", "trade ", "shop")):
        return "BUY_SELL"
    if "complete" in lower and extract_quests(text):
        return "QUEST_COMPLETE"
    if lower.startswith("complete "):
        return "QUEST_PROGRESS"
    if extract_quests(text):
        return "QUEST_PROGRESS"
    if "balloon transport" in lower or "mushtree" in lower:
        return "TRANSPORT"
    if DIALOG_RE.search(text):
        return "DIALOGUE"
    if any(token in lower for token in ("kill", "defeat", "attack")):
        return "COMBAT"
    if any(token in lower for token in ("mine", "fish", "cut", "smith", "fletch", "craft", "cook", "furnace", "plant ", "clean grimy", "make ", "chop ")):
        return "SKILL_ACTION"
    if any(token in lower for token in ("use ", "combine ", "fill ", "equip ", "wear ")):
        return "ITEM_USE"
    if diary_line:
        return "CHECKPOINT"
    if any(token in lower for token in ("note:", "do ", "when ", "if ")):
        return "CHECKPOINT"
    if any(token in lower for token in ("checkpoint", "end of", "done with", "finished")):
        return "CHECKPOINT"
    return "MANUAL_NOTE"


def is_expected_duplicate(step):
    text = step["text"].lower()
    if text in EXPECTED_DUPLICATE_EXACT:
        return True
    if step["stepType"] in {"TRAVEL", "TRANSPORT", "WITHDRAW", "DEPOSIT", "TALK_TO_NPC", "BUY_SELL"}:
        return True
    if text.startswith(EXPECTED_DUPLICATE_PREFIXES):
        return True
    return text.startswith(("collect ", "take the boat", "take boat", "bank at ", "bank all", "bank anywhere"))


def extract_dialogue_refs(text, npc_refs):
    matches = DIALOG_RE.findall(text)
    if not matches:
        return []

    options = [int(part.strip()) for part in matches[0].strip("()").split(",") if part.strip().isdigit()]
    return [{
        "npcRef": npc_refs[0] if npc_refs else None,
        "promptText": clean_text(text),
        "optionSequence": options,
    }]


def extract_transport_refs(text, location_refs, npc_refs):
    if WITHDRAW_RE.match(text):
        return []
    cleaned = clean_text(text)
    lower = cleaned.lower()
    transports = []
    arrow_match = ROUTE_ARROW_RE.match(cleaned)
    if arrow_match:
        transports.append({
            "type": "teleport",
            "displayName": cleaned,
            "origin": None,
            "destination": location_refs[0] if location_refs else None,
            "objectId": None,
            "npcRef": npc_refs[0] if npc_refs else None,
            "locationRef": location_refs[0] if location_refs else None,
        })

    transport_keywords = {
        "boat": "boat",
        "ship": "ship",
        "charter": "charter",
        "canoe": "canoe",
        "glider": "glider",
        "spirit tree": "spirit_tree",
        "fairy ring": "fairy_ring",
        "teleport": "teleport",
    }
    for keyword, transport_type in transport_keywords.items():
        if keyword in lower:
            transports.append({
                "type": transport_type,
                "displayName": cleaned if arrow_match or keyword in ("teleport", "boat", "ship") else keyword.title(),
                "origin": None,
                "destination": location_refs[0] if location_refs else None,
                "objectId": None,
                "npcRef": npc_refs[0] if npc_refs else None,
                "locationRef": location_refs[0] if location_refs else None,
            })
    return transports


def extract_action_refs(text):
    cleaned = clean_text(text)
    lower = cleaned.lower()
    verbs = ["talk", "speak", "buy", "sell", "withdraw", "deposit", "kill", "mine", "use", "travel", "teleport", "bank", "take", "start", "complete"]
    actions = []
    for verb in verbs:
        if lower.startswith(verb) or f" {verb} " in lower:
            actions.append({
                "verb": verb,
                "target": cleaned,
                "detail": cleaned,
            })
    return actions


def normalize_item(item):
    return {
        "displayName": item["name"],
        "canonicalName": canonical_name(item["name"]),
        "itemIds": [],
        "quantity": item["quantity"],
        "optional": "optional" in item["name"].lower(),
    }


def normalize_quest(quest, alias_map):
    canonical = alias_map.get(quest.lower(), canonical_name(quest))
    return {
        "displayName": quest,
        "canonicalName": canonical,
        "questStateHints": [],
    }


def normalize_npc(npc, alias_map):
    canonical = alias_map.get(npc.lower(), canonical_name(npc))
    return {
        "displayName": npc,
        "canonicalName": canonical,
        "npcIds": [],
        "locationHints": [],
    }


def normalize_location(location, alias_map):
    canonical = alias_map.get(location["name"].lower(), canonical_name(location["name"]))
    world_points = []
    if all(key in location for key in ("x", "y", "z")) and location.get("x") is not None:
        world_points = [{"x": location["x"], "y": location["y"], "z": location["z"]}]
    return {
        "displayName": location["name"],
        "canonicalName": canonical,
        "worldPoints": world_points,
        "areaHints": [],
    }


def unresolved_mentions(step):
    unresolved = []
    bracket_matches = [m.group(1).strip() for m in BRACKET_QUEST_RE.finditer(step["rawText"])]
    actionable_brackets = [
        match for match in bracket_matches
        if not re.match(r'^\d+', match)
        and match.lower() not in ('inventory slots', 'inventory slot', 'inventory spaces')
        and not any(keyword in match.lower() for keyword in NON_QUEST_BRACKET_KEYWORDS)
    ]
    if not step["quests"] and actionable_brackets:
        unresolved.append("Bracketed reference not resolved")
    return unresolved


def normalize_episodes(episodes, alias_tables, overrides):
    diagnostics = {
        "unresolvedQuests": [],
        "unresolvedNpcs": [],
        "unresolvedLocations": [],
        "unresolvedItems": [],
        "ambiguousStepTypes": [],
        "duplicateSteps": [],
    }
    normalized_episodes = []
    seen_step_text = set()

    for episode in episodes:
        normalized_episode = {
            "episodeId": episode["episode"],
            "title": episode["title"],
            "banks": [],
        }
        for bank in episode["banks"]:
            bank_id = bank["bank"]
            normalized_bank = {
                "bankId": bank_id,
                "title": bank["title"],
                "withdrawStepText": next(
                    (step["text"] for step in bank["steps"] if classify_step(step["text"], bool(step.get("items"))) == "WITHDRAW"),
                    None
                ),
                "exitStepText": next(
                    (
                        step["text"] for step in reversed(bank["steps"])
                        if classify_step(step["text"], bool(step.get("items"))) == "DEPOSIT"
                    ),
                    None
                ),
                "transitionNotes": [clean_text(note) for note in bank.get("transitionNotes", []) if clean_text(note)],
                "adviceLines": [clean_text(note) for note in bank.get("adviceLines", []) if clean_text(note)],
                "withdrawItems": [normalize_item(item) for item in bank.get("withdrawItems", [])],
                "steps": [],
            }
            for step in bank["steps"]:
                step_key = step["globalId"]
                step_type = classify_step(step["text"], bool(step.get("items")))
                quest_refs = [normalize_quest(quest, alias_tables["quests"]) for quest in step["quests"]]
                npc_refs = [normalize_npc(npc, alias_tables["npcs"]) for npc in step["npcs"]]
                location_refs = [normalize_location(location, alias_tables["locations"]) for location in step["locations"]]
                item_refs = [normalize_item(item) for item in step["items"]]
                transport_refs = extract_transport_refs(step["text"], location_refs, npc_refs)
                dialogue_refs = extract_dialogue_refs(step["text"], npc_refs)
                action_refs = extract_action_refs(step["text"])
                unresolved = unresolved_mentions(step)

                normalized_step = {
                    "globalId": step["globalId"],
                    "globalIndex": step["globalIndex"],
                    "episodeId": episode["episode"],
                    "bankId": bank_id,
                    "stepIndex": step["stepIndex"],
                    "text": step["text"],
                    "rawText": step["rawText"],
                    "stepType": step_type,
                    "questRefs": quest_refs,
                    "npcRefs": npc_refs,
                    "locationRefs": location_refs,
                    "itemRefs": item_refs,
                    "transportRefs": transport_refs,
                    "dialogueRefs": dialogue_refs,
                    "actionRefs": action_refs,
                    "substeps": step.get("substeps", []),
                    "adviceLines": step.get("adviceLines", []),
                    "unresolvedMentions": unresolved,
                    "notes": overrides.get(step_key, {}).get("notes", []),
                    "tags": overrides.get(step_key, {}).get("tags", []),
                }

                duplicate_candidate = normalized_step["text"].lower()
                if duplicate_candidate in seen_step_text and not is_expected_duplicate(normalized_step):
                    diagnostics["duplicateSteps"].append(step_key)
                seen_step_text.add(duplicate_candidate)
                if step_type == "MANUAL_NOTE" and (quest_refs or npc_refs or location_refs):
                    diagnostics["ambiguousStepTypes"].append(step_key)
                if unresolved:
                    if quest_refs:
                        diagnostics["unresolvedQuests"].append(step_key)
                    if npc_refs:
                        diagnostics["unresolvedNpcs"].append(step_key)
                    if location_refs:
                        diagnostics["unresolvedLocations"].append(step_key)
                    if item_refs:
                        diagnostics["unresolvedItems"].append(step_key)

                if step_key in overrides:
                    normalized_step.update(overrides[step_key])

                normalized_bank["steps"].append(normalized_step)
            normalized_episode["banks"].append(normalized_bank)
        normalized_episodes.append(normalized_episode)

    return normalized_episodes, diagnostics


def print_stats(episodes, total_steps, diagnostics):
    """Print parsing statistics."""
    total_banks = sum(len(ep["banks"]) for ep in episodes)
    quest_steps = sum(
        1 for ep in episodes
        for bank in ep["banks"]
        for step in bank["steps"]
        if step["questRefs"]
    )
    npc_steps = sum(
        1 for ep in episodes
        for bank in ep["banks"]
        for step in bank["steps"]
        if step["npcRefs"]
    )
    loc_steps = sum(
        1 for ep in episodes
        for bank in ep["banks"]
        for step in bank["steps"]
        if step["locationRefs"]
    )

    print(f"\n{'='*60}")
    print(f"B0aty V3 Guide Parser — Results")
    print(f"{'='*60}")
    print(f"Episodes:           {len(episodes)}")
    print(f"Banks:              {total_banks}")
    print(f"Total steps:        {total_steps}")
    print(f"Steps with quests:  {quest_steps}")
    print(f"Steps with NPCs:    {npc_steps}")
    print(f"Steps with locations: {loc_steps}")
    print(f"{'='*60}")

    # Quest breakdown
    all_quests = set()
    for ep in episodes:
        for bank in ep["banks"]:
            for step in bank["steps"]:
                all_quests.update(q["canonicalName"] for q in step["questRefs"])
    print(f"\nUnique quests referenced: {len(all_quests)}")
    for q in sorted(all_quests):
        print(f"  - {q}")

    # NPC breakdown
    all_npcs = set()
    for ep in episodes:
        for bank in ep["banks"]:
            for step in bank["steps"]:
                all_npcs.update(n["canonicalName"] for n in step["npcRefs"])
    print(f"\nUnique NPCs referenced: {len(all_npcs)}")
    print(f"Diagnostics:")
    for key, value in diagnostics.items():
        print(f"  - {key}: {len(value)}")


def main():
    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    resource_dir = os.path.join(project_dir, "src", "main", "resources", "com", "boatyguide")
    raw_dir = os.path.join(project_dir, "data", "raw")
    aliases_dir = os.path.join(project_dir, "data", "aliases")
    overrides_dir = os.path.join(project_dir, "data", "overrides")
    generated_dir = os.path.join(project_dir, "data", "generated")
    cache_path = os.path.join(raw_dir, "guide_v3_raw.txt")
    output_path = os.path.join(resource_dir, "guide_data.json")
    diagnostics_path = os.path.join(generated_dir, "guide_diagnostics.json")
    alias_tables = {
        "quests": load_json_if_exists(os.path.join(aliases_dir, "quests.json"), {}),
        "npcs": load_json_if_exists(os.path.join(aliases_dir, "npcs.json"), {}),
        "locations": load_json_if_exists(os.path.join(aliases_dir, "locations.json"), {}),
    }
    wiki_tables = load_wiki_tables(project_dir)
    overrides = load_json_if_exists(os.path.join(overrides_dir, "steps.json"), {})
    initialize_entity_patterns(wiki_tables)

    # Check for local cached content first
    # Also check if content was already downloaded by the IDE
    local_content_paths = [
        cache_path,
        os.path.join(raw_dir, "guide_v3_raw.txt"),
        os.path.join(script_dir, "guide_raw.md"),
    ]

    content = None
    for path in local_content_paths:
        if os.path.exists(path):
            print(f"Using cached content from {path}")
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            break

    if content is None:
        content = fetch_guide_content(WIKI_URL, cache_path)

    # Parse
    print("Parsing guide content...")
    episodes = parse_guide(content)

    # Assign global indices
    total_steps = assign_global_indices(episodes)

    # Build output
    normalized_episodes, diagnostics = normalize_episodes(episodes, alias_tables, overrides)
    output = {
        "version": "3.0",
        "source": "https://oldschool.runescape.wiki/w/Guide:B0aty_HCIM_Guide_V3",
        "totalSteps": total_steps,
        "diagnostics": diagnostics,
        "episodes": normalized_episodes
    }

    # Write JSON
    os.makedirs(resource_dir, exist_ok=True)
    os.makedirs(generated_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    with open(diagnostics_path, 'w', encoding='utf-8') as f:
        json.dump(diagnostics, f, indent=2, ensure_ascii=False)

    print(f"\nWrote guide data to {output_path}")
    print_stats(normalized_episodes, total_steps, diagnostics)

    full_size = os.path.getsize(output_path)
    print(f"\nFull JSON:    {full_size:,} bytes")


if __name__ == '__main__':
    main()
