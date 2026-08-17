"""
Author: Grayson Olin
File: matchAnalysis.py
Language: Python 3.10
Date Created: 7/24/2025
Last Modified: 1/3/2026
----------------------------------------------
A statistical analysis of CS2 matches
"""
from collections import namedtuple
from dataclasses import dataclass
import duckdb
import numpy as np
import pandas as pd
import warnings

@dataclass
class TotalDamages:
    steam_id: str
    total_health_dmg_dealt: int
    total_health_dmg_received: int
    total_armor_dmg_dealt: int
    total_armor_dmg_received: int
    total_combined_dmg_dealt: int
    total_combined_dmg_received: int

    def __str__(self):
        string_print = f"\n Total Health \n\t DMG Dealt: {self.total_health_dmg_dealt} | DMG Received: {self.total_health_dmg_received} \
        \n Total Armor \n\t DMG Dealt: {self.total_armor_dmg_dealt} | DMG Received: {self.total_armor_dmg_received} \
        \n Total Combined \n\t DMG Dealt: {self.total_combined_dmg_dealt} | DMG Received: {self.total_combined_dmg_received}"
        return string_print

@dataclass
class Player:
    name: str
    steam_id: str
    team: str
    avg_de: float
    damages: TotalDamages
    round_damages: dict
    round_de: dict

    def __str__(self):
        string_print = f"Name: {self.name} \n Steam ID: {self.steam_id} \n Team: {self.team} \n Avg. DE: {self.avg_de} \n Damages: {self.damages.__str__()} \
            \n Round Damages: {self.round_damages} \n Round DE: {self.round_de}"
        return string_print

@dataclass
class Team:
    name: str
    avg_de: float
    round_de: dict

    def update_avg(self, de):
        self.avg_de += de
    
    def update_round_de(self, rde):
        for r in self.round_de.keys():
            self.round_de[r] += rde[r]
    
    def __str__(self):
        string_print = f"Name: {self.name} \n\t Avg. DE: {self.avg_de} \n\t Round DE: {self.round_de}"
        return string_print

def init_player(playerLst):
    players = []

    for i in playerLst:
        name = i[0]
        steam_id = str(i[1])
        team = i[2]
        avg_de = 0
        damages = TotalDamages(steam_id, 0, 0, 0, 0, 0, 0)
        round_damages = {
            "dealt": {},
            "received": {}
        }
        round_de = {}
        players.append(Player(name=name, steam_id=steam_id, team=team, avg_de=avg_de, damages=damages, round_damages=round_damages, round_de=round_de))

    return players

def get_player(players, id):
    for player in players:
        if player.steam_id == id:
            return player

def dmg_eff(dealt, rec):
    if dealt == 0:
        z = -100
    else:
        z = 1 - (rec/dealt)

    j = rec - dealt - z

    if rec == 0:
        k = (z-j)/100
    else:
        k = (z - j) / rec

    return k

def de_other(dealt, rec):
    delta = dealt - rec
    if dealt == 0:
        de = delta/100
    else:
        de = delta / dealt

    return de

def de_nomap(dealt, rec):
    if dealt == 0:
        de = -100
    else:
        de = 1 - rec/dealt
    return de

def de_correct(dealt, rec):
    # this suggests that damage received is the cost input
    # where the damage dealt is the cost output
    # as opposed to the other formulae which suggest the opposite
    if rec == 0:
        de = -100
    else:
        de = 1 - dealt/rec
    return de

def funtime(dealt, rec):
    if dealt == 0 or rec == 0:
        if dealt == 0 and rec == 0:
            de = 0
        elif dealt == 0:
            de = -rec
        else:
            de = dealt
    else:
        de = (dealt**2 - rec**2)/(dealt*rec)
    return de

def funtime2(dealt, rec):
    de = (1 + (dealt**2 - rec**2))/(1 + dealt*rec)
    return de

def to_txt(filename, players):
    with open(filename, "w") as file:
        for player in players:
            player_print = player.__str__() + "\n"
            file.write(player_print)
    return 0

def get_match_checksums(df):
    checksums = list(df.groupby('match_checksum').groups)
    return checksums

def split_by_round(df, round):
    round_df = df[df["round_number"] == round]
    return round_df

def load_rounds(df, players):
    rounds = np.sort(df["round_number"].unique())
    for round in rounds:
        round_df = split_by_round(df, round)
        attacker_id_list = round_df["attacker_steam_id"].unique().tolist()
        victim_id_list = round_df["victim_steam_id"].unique().tolist()

        for player in players:
            player_steam_id = int(player.steam_id)

            if player_steam_id in attacker_id_list:
                as_attacker_df = round_df[round_df["attacker_steam_id"] == player_steam_id]
                dealt_match_round_sum = as_attacker_df.groupby("match_checksum").sum()
                dealt = dealt_match_round_sum["health_damage"].tolist()
                player.round_damages["dealt"][f"{round}"] = dealt

            if player_steam_id in victim_id_list:
                as_victim_df = round_df[round_df["victim_steam_id"] == player_steam_id]
                received_match_round_sum = as_victim_df.groupby("match_checksum").sum()
                received = received_match_round_sum["health_damage"].tolist()
                player.round_damages["received"][f"{round}"] = received
    return 0

def avg_of_players(players):
    size = len(players)
    total = 0

    for player in players:
        total += player.avg_de
    if size != 0 :
        avg = total/size
        print("\n" + f"Number of players: {size}" + "\n" + f"Average of all players: {avg}" + "\n")
    else:
        print("Divide by zero error")

    return 0

def summarize_rounds(players):
    for player in players:
        dmgs = player.round_damages
        dealt = dmgs["dealt"]
        rec = dmgs["received"]

        d_keys = [int(a) for a in dealt.keys()]
        r_keys = [int(b) for b in rec.keys()]
        max_d = max(d_keys)
        max_r = max(r_keys)
        max_key = max(max_d, max_r)

        d_sum = [sum(d) for d in dealt.values()]
        r_sum = [sum(r) for r in rec.values()]

        new_dealt = {}
        new_rec = {}
        round_de = {}

        count_d = 0
        count_r = 0

        for m in range(1, max_key + 1):
            m_str = f"{m}"
            if m in d_keys:
                new_dealt[m_str] = d_sum[count_d]
                count_d += 1
            else:
                new_dealt[m_str] = 0
            if m in r_keys:
                new_rec[m_str] = r_sum[count_r]
                count_r += 1
            else:
                new_rec[m_str] = 0
        
        for d in range(1, max_key + 1):
            rd = f"{d}"
            d_dmg = new_dealt[rd]
            r_dmg = new_rec[rd]
            de = funtime(d_dmg, r_dmg)

            round_de[rd] = de
        
        player.round_de = round_de
    return 0

def summarize_team(players):
    teams = {}

    for player in players:
        player_team = player.team
        player_de = player.avg_de
        player_rde = player.round_de

        team_avg = player_de / 5
        team_rde = {}

        for r in player_rde.keys():
            team_rde[r] = player_rde[r] / 5
        
        if player.name == "headtr1ck":
            team_rde["35"] = 0
        
        if player_team not in teams.keys():
            teams[player_team] = Team(name=player_team, avg_de=team_avg, round_de=team_rde)
        else:
            teams[player_team].update_avg(team_avg)
            teams[player_team].update_round_de(team_rde)
    
    for team in teams:
        print(teams[team].__str__())

    return 0

def to_df_to_csv(players):
    name = []
    steam_id = []
    team = []
    damage_dealt = []
    damage_received = []
    damage_efficiency = []

    for player in players:
        name.append(player.name)
        steam_id.append(player.steam_id)
        team.append(player.team)
        damage_dealt.append(player.damages.total_health_dmg_dealt)
        damage_received.append(player.damages.total_health_dmg_received)
        damage_efficiency.append(player.avg_de)
    
    df = pd.DataFrame({"player_name": name, "steam_id": steam_id, "team": team,
    "damage_dealt": damage_dealt, "damage_received": damage_received, 
    "damage_efficiency": damage_efficiency
    })

    df.to_csv("cs2_analysis.csv")
    return 0

def total_avg_de(df, players):
    dmg_eff_mapped = {}
    dmg_eff_basic = {}
    dmg_eff_unmapped = {}
    dmg_eff_correct = {}
    d_funtime = {}

    for row in df.itertuples(index=False):
        attacker_id = str(row[15])
        victim_id = str(row[19])

        attacker = get_player(players, attacker_id)
        victim = get_player(players, victim_id)

        # col 6 -> 11 contain health/armor info therefore 5 -> 10
        health_dmg = row[5]
        armor_dmg = row[6]
        combined_dmg = health_dmg + armor_dmg

        victim_hp = row[7]
        victim_new_hp = row[8]
        victim_armor = row[9]
        victim_new_armor = row[10]
        dmg_received = victim_hp - victim_new_hp
        armor_dmg_received = victim_armor - victim_new_armor
        combined_dmg_received = dmg_received + armor_dmg_received

        if attacker:
            damages = attacker.damages
            damages.total_health_dmg_dealt += health_dmg
            damages.total_armor_dmg_dealt += armor_dmg
            damages.total_combined_dmg_dealt += combined_dmg

        if victim:
            damages = victim.damages
            damages.total_health_dmg_received += dmg_received
            damages.total_armor_dmg_received += armor_dmg_received
            damages.total_combined_dmg_received += combined_dmg_received

    for player in players:
        name = player.name
        dealt = player.damages.total_health_dmg_dealt
        rec = player.damages.total_health_dmg_received
        avg_de = funtime(dealt, rec)
        player.avg_de = avg_de

        dmg_eff_mapped[name] = (dmg_eff(dealt, rec), player.team)
        dmg_eff_basic[name] = (de_other(dealt, rec), player.team)
        dmg_eff_unmapped[name] = (de_nomap(dealt, rec), player.team)
        dmg_eff_correct[name] = (de_correct(dealt, rec), player.team)
        d_funtime[name] = (avg_de, player.team)

    list_of_attackers = list(df.groupby("attacker_steam_id").groups)
    list_of_victims = list(df.groupby("victim_steam_id").groups)
    if 0 in list_of_attackers:
        list_of_attackers.remove(0)  # 0 is damage caused by World
    if list_of_attackers != list_of_victims:
        warnings.warn("Warning: Attacker list is not equal to Victim list.")

    return 0

def main():
    print("Running. . .")

    floc ="Z:/cs_analysis/"
    df = pd.read_csv(floc+"starladderBudapestDamages_202601211525.csv")
    filename = "playerData4.txt"

    # remove knife rounds, if so recorded
    df = df.query("team_name != 'Team A'")
    df = df.query("team_name != 'Team B'")

    checksums_list = get_match_checksums(df)
    list_of_players = list(df.groupby(["name", "steam_id", "team_name"]).groups)

    players = init_player(list_of_players)
    total_avg_de(df, players)
    load_rounds(df, players)
    summarize_rounds(players)

    to_txt(floc+filename, players)

    # avg_of_players(players)

    # to_df_to_csv(players)

    summarize_team(players)

    print("Finished.")
    return 0

if __name__ == "__main__":
    main()
