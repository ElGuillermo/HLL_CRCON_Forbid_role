"""
automod_forbid_role

A plugin for HLL CRCON (https://github.com/MarechJ/hll_rcon_tool)
that blocks role(s) access to defined players.

Source : https://github.com/ElGuillermo

Feel free to use/modify/distribute, as long as you keep this note in your code
"""

import logging
from time import sleep
from typing import Literal
import discord
from rcon.rcon import Rcon
from rcon.settings import SERVER_INFO
from rcon.utils import get_server_number
from custom_tools.automod_forbid_role_config import *
from custom_tools.common_functions import (
    CLAN_URL,
    DISCORD_EMBED_AUTHOR_URL,
    DISCORD_EMBED_AUTHOR_ICON_URL,
    discord_embed_send,
    get_avatar_url,
    get_external_profile_url
)
from custom_tools.common_translations import TRANSL


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

        # Check if enabled
        server_number = int(get_server_number())
        if not SERVER_CONFIG[server_number - 1][1]:
            return
        discord_webhook = SERVER_CONFIG[server_number - 1][0]

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

        # Create and send discord embed
        webhook = discord.SyncWebhook.from_url(discord_webhook)
        embed = discord.Embed(
            title=soldier_name,
            url=get_external_profile_url(soldier_id, soldier_name),
            description=embed_desc_txt,
            color=embed_color
        )
        embed.set_author(
            name=BOT_NAME,
            url=DISCORD_EMBED_AUTHOR_URL,
            icon_url=DISCORD_EMBED_AUTHOR_ICON_URL
        )
        embed.set_thumbnail(url=get_avatar_url(soldier_id))

        discord_embed_send(embed, webhook)


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
