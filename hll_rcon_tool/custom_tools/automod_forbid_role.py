"""
automod_forbid_role.py

A plugin for HLL CRCON (https://github.com/MarechJ/hll_rcon_tool)
that blocks role(s) access to defined players.

Source : https://github.com/ElGuillermo

Feel free to use/modify/distribute, as long as you keep this note in your code
"""

import logging
from time import sleep
from typing import Literal
from rcon.rcon import Rcon
from rcon.settings import SERVER_INFO
from custom_tools.custom_common import (
    CLAN_URL,
    get_avatar_url,
    get_external_profile_url,
    send_discord_embed
)
from custom_tools.custom_translations import TRANSL


# Configuration (you must review/change these !)
# -----------------------------------------------------------------------------

# Don't forget you have some parameters to set in 'custom_common.py' too !

# True : only logs - no real message sent / no real punition applied)
# Value : True or False
TEST_MODE = False

# The script can work without any Discord output
# False : the only output would be the log file (as set in config/supervisord.conf)
USE_DISCORD = True

# Dedicated Discord's channel webhook
DISCORD_WEBHOOK = (
    "https://discord.com/api/webhooks/..."
)

# Discord embeds strings translations
# Available : 0 for english, 1 for french, 2 for german
LANG = 0

# The interval between watch turns (in seconds)
# Recommended : as the stats must be gathered for all the players,
#               requiring some amount of data from the game server,
#               you may encounter slowdowns if done too frequently.
# Default : 60
WATCH_INTERVAL_SECS = 40

# Define the guys and the roles they can't play
# action : Choose either "warning" (or "message"), "punish" or "kick"
# note : "punish" will report failures as long as the player isn't alive on map
OBSERVED_PLAYERS = [
#     {
#         "id": "76561123456918684",  # SomeGuy
#         "roles": ["armycommander", "officer", "tankcommander", "spotter"],
#         "reason": "No comms",
#         "action": "punish"
#     },
#     {
#         "id": "76561112345601973",  # SomeOtherGuy
#         "roles": ["armycommander", "officer", "tankcommander", "spotter"],
#         "reason": "Trolling",
#         "action": "punish"
#     }
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


# (End of configuration)
# -----------------------------------------------------------------------------


def filter_players():
    """
    Find the observed players, test if they took a forbidden role
    """
    rcon = Rcon(SERVER_INFO)

    try:
        team_view = rcon.get_team_view()
    except Exception as error:
        logger.error("get_team_view() failed - %s", error)
        return

    for player in OBSERVED_PLAYERS:
        # Team
        for team in ["allies", "axis"]:
            if not team_view.get(team):
                continue

            # Commander
            if (
                team_view[team]["commander"] is not None  # type: ignore
                and team_view[team]["commander"].get("player_id") == player["id"]  # type: ignore
                and "armycommander" in player["roles"]
            ):
                you_cant_take_this_role(
                    rcon=rcon,
                    soldier_name=team_view[team]["commander"].get("name"),  # type: ignore
                    soldier_id=player["id"],
                    soldier_team=team_view[team]["commander"].get("team"),  # type: ignore
                    soldier_unit_name="command",
                    soldier_role="armycommander"
                )

            # Squads
            for squad in team_view[team]["squads"]:  # type: ignore

                # Players
                for soldier in range(len(team_view[team]["squads"][squad]["players"])):  # type: ignore
                    if (
                        team_view[team]["squads"][squad]["players"][soldier].get("player_id") == player["id"] # type: ignore
                        and team_view[team]["squads"][squad]["players"][soldier].get("unit_name") is not None   # type: ignore  # Avoids to observe unassigned players reported as "rifleman"
                        and team_view[team]["squads"][squad]["players"][soldier].get("role") in player["roles"]   # type: ignore
                    ):
                        you_cant_take_this_role(
                            rcon=rcon,
                            soldier_name=team_view[team]["squads"][squad]["players"][soldier].get("name"),  # type: ignore
                            soldier_id=player["id"],
                            soldier_team=team_view[team]["squads"][squad]["players"][soldier].get("team"),  # type: ignore
                            soldier_unit_name=team_view[team]["squads"][squad]["players"][soldier].get("unit_name"),  # type: ignore
                            soldier_role=team_view[team]["squads"][squad]["players"][soldier].get("role"),  # type: ignore
                        )


def you_cant_take_this_role(
    rcon: Rcon,
    soldier_name: str,
    soldier_id: str,
    soldier_team: Literal["allies", "axis"],
    soldier_unit_name: str,
    soldier_role: str,
):
    """
    The player has taken a role he can't play
    """

    soldier_role_translated = TRANSL[soldier_role][LANG]
    soldier_team_translated = TRANSL[soldier_team][LANG]

    for player in OBSERVED_PLAYERS:
        if soldier_id == player["id"]:
            reason: str = player["reason"]
            action: Literal["warning", "message", "punish", "kick"] = player["action"]
            break

    if not TEST_MODE:

        if action in ("warning", "message"):
            warning_message = WARNING_MSG
            custom_warning_message = warning_message.format(
                soldier_name,
                soldier_role_translated,
                reason,
                CLAN_URL
            )
            try:
                rcon.message_player(
                    player_name=soldier_name,
                    player_id=soldier_id,
                    message=custom_warning_message,
                    by=BOT_NAME,
                    # save_message=False  # False by default
                )
                result = TRANSL["success"][LANG]
            except Exception:
                result = TRANSL["failure"][LANG]

        elif action == "punish":
            punish_message = PUNISH_MSG
            custom_punish_message = punish_message.format(
                soldier_name,
                soldier_role_translated,
                reason,
                CLAN_URL
            )
            try:
                rcon.punish(
                    player_name=soldier_name,
                    reason=custom_punish_message,
                    by=BOT_NAME
                )
                result = TRANSL["success"][LANG]
            except Exception:
                result = TRANSL["failure"][LANG]

        elif action == "kick":
            punish_message = PUNISH_MSG
            custom_punish_message = punish_message.format(
                soldier_name,
                soldier_role_translated,
                reason,
                CLAN_URL
            )
            try:
                rcon.kick(
                    player_name=soldier_name,
                    reason=custom_punish_message,
                    by=BOT_NAME,
                    player_id=soldier_id
                )
                result = TRANSL["success"][LANG]
            except Exception:
                result = TRANSL["failure"][LANG]

        else:  # Unknown action
            logger.warning(
                "Error : '%s' action isn't defined. Check your config.",
                action
            )
            result = TRANSL["unknown_action"][LANG]

    else:
        result = TRANSL["testmode"][LANG]

    # Log action
    logger.info(
        "'%s' (%s/%s/%s) - Action : '%s' - Reason : '%s' - Result : %s",
        soldier_name,
        soldier_team,
        soldier_unit_name,
        soldier_role,
        action,
        reason,
        result
    )

    # Discord
    if USE_DISCORD:

        # message
        embed_desc_txt = (
            f"● {soldier_team_translated} / {soldier_unit_name}\n"
            f"{TRANSL['play_as'][LANG]} `{soldier_role_translated}`\n"
            f"{TRANSL['engaged_action'][LANG]} `{action}`\n"
            f"{TRANSL['reason'][LANG]} *\"{reason}\"*\n"
            f"{TRANSL['action_result'][LANG]} {result}"
        )

        # embed color
        if action in ("warning", "message"):
            embed_color = 0xffff00
        elif action == "punish":
            embed_color = 0xff8000
        elif action == "kick":
            embed_color = 0xff0000
        else:
            embed_color = 0xffffff

        send_discord_embed(
            BOT_NAME,
            embed_title=soldier_name,
            embed_title_url=get_external_profile_url(soldier_id, soldier_name),
            steam_avatar_url=get_avatar_url(soldier_id),
            embed_desc_txt=embed_desc_txt,
            embed_color=embed_color,
            discord_webhook=DISCORD_WEBHOOK
        )


# Launching - initial pause : wait to be sure the CRCON is fully started
sleep(60)

logger = logging.getLogger('rcon')

logger.info(
    "\n-------------------------------------------------------------------------------\n"
    "%s (started)\n"
    "-------------------------------------------------------------------------------",
    BOT_NAME
)

if TEST_MODE:
    logger.info(
        "NOTE : Test mode enabled. No real action will be engaged\n"
        "-------------------------------------------------------------------------------"
    )

# Launching and running (infinite loop)
if __name__ == "__main__":
    while True:
        filter_players()
        sleep(WATCH_INTERVAL_SECS)
