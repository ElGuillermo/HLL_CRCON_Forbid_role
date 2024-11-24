"""
automod_forbid_role_config.py

A plugin for HLL CRCON (https://github.com/MarechJ/hll_rcon_tool)
that filters (kick) players based upon their language.

Source : https://github.com/ElGuillermo

Feel free to use/modify/distribute, as long as you keep this note in your code
"""

# True : only logs - no real message sent / no real punition applied)
# Value : True or False
TEST_MODE = False

# The script can work without any Discord output
# False : the only output would be the log file (as set in config/supervisord.conf)
USE_DISCORD = True

# Dedicated Discord's channel webhook
# ServerNumber, Webhook, Enabled
SERVER_CONFIG = [
    ["https://discord.com/api/webhooks/...", True],  # Server 1
    ["https://discord.com/api/webhooks/...", False],  # Server 2
    ["https://discord.com/api/webhooks/...", False],  # Server 3
    ["https://discord.com/api/webhooks/...", False],  # Server 4
    ["https://discord.com/api/webhooks/...", False],  # Server 5
    ["https://discord.com/api/webhooks/...", False],  # Server 6
    ["https://discord.com/api/webhooks/...", False],  # Server 7
    ["https://discord.com/api/webhooks/...", False],  # Server 8
    ["https://discord.com/api/webhooks/...", False],  # Server 9
    ["https://discord.com/api/webhooks/...", False]  # Server 10
]

# Discord embeds strings translations
# Available : 0 for english, 1 for french, 2 for german
LANG = 0

# Define the guys and the roles they can't play
# action : Choose either "warning" (or "message"), "punish" or "kick"
# note : "punish" will report failures as long as the player isn't alive on map
OBSERVED_PLAYERS = [
    # {
    #     "id": "76561198051234560",  # someGuy
    #     "roles": ["armycommander", "officer],
    #     "reason": "Toxic",
    #     "action": "punish"
    # },
    # {
    #     "id": "76561198354123456",  # SomeOtherGuy
    #     "roles": ["armycommander"],
    #     "reason": "No voice comm",
    #     "action": "punish"
    # }
]


# Miscellaneous (you don't have to change these)
# ----------------------------------------------

# {} replace values in this order :
# pseudo (str), role (str), reason (str), clan url (automatic)
# ie : "Sorry, {} !\n\nYou can't play\n'{}'\non this server.\n\nReason: {}\n\nContact: {}"
WARNING_MSG = (
    "(Message automatique)\n\n"
    "Attention, {} !\n\n"
    "Tu joues\n\n"
    "{}\n\n"
    "alors que cela t'est interdit sur ce serveur.\n\n"
    "Raison :\n"
    "{}\n\n"
    "Réclamations :\n{}"
)

# {} replace values in this order :
# pseudo (str), role (str)
# ie : "Sorry, {} !\n\nYou can't play\n'{}'\non this server.\n\nReason: {}\n\nContact: {}"
PUNISH_MSG = (
    "\n(Message automatique)\n\n"
    "Désolé, {} !\n\n"
    "Tu as été puni parce que tu joues\n\n"
    "{}\n\n"
    "alors que cela t'est interdit sur ce serveur.\n\n"
    "Raison :\n"
    "{}\n\n"
    "Réclamations :\n{}\n\n"
)

# Bot name that will be displayed in CRCON "audit logs" and Discord embeds
BOT_NAME = "CRCON_forbid_role"

# The interval between watch turns (in seconds)
# Recommended : as the stats must be gathered for all the players,
#               requiring some amount of data from the game server,
#               you may encounter slowdowns if done too frequently.
# Default : 60
WATCH_INTERVAL_SECS = 60
