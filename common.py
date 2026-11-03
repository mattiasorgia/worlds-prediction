"""Costanti, caricamento dei dati e utilità condivise.

Ogni altro script importa da qui: percorsi, seed, team e giocatori qualificati
ai Worlds 2026, pesi regionali, colonne di Oracle's Elixir e le funzioni che
leggono i CSV. Nessuna logica di modello vive in questo file.
"""
from pathlib import Path

import pandas as pd

SEED = 42
N_ITERAZIONI = 10_000

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output"
MODELS = ROOT / "models"
OUT.mkdir(exist_ok=True)
MODELS.mkdir(exist_ok=True)

QUALIFIED_TEAMS = [
    # LCK (Corea)
    "Gen.G", "Hanwha Life Esports", "T1", "Dplus Kia",
    # LPL (Cina)
    "Anyone's Legend", "Bilibili Gaming", "Top Esports", "Invictus Gaming",
    # LEC (Europa)
    "G2 Esports", "Movistar KOI", "Karmine Corp",
    # LCS (Nord America)
    "Team Liquid", "LYON",
    # LCP (Asia Pacifico)
    "Team Secret Whales", "CTBC Flying Oyster",
    # CBLOL (Brasile)
    "LØS",
]

QUALIFIED_PLAYERS = [
    # Gen.G
    "Kiin", "Canyon", "Chovy", "Ruler", "Duro",
    # Hanwha Life
    "Zeus", "Kanavi", "Zeka", "Gumayusi", "Delight",
    # T1
    "Doran", "Oner", "Faker", "Peyz", "Keria",
    # Dplus KIA
    "Siwoo", "Lucid", "ShowMaker", "Smash", "Career",
    # Anyone's Legend
    "Breathe", "Tarzan", "Shanks", "Hope", "Kael",
    # Bilibili Gaming
    "Bin", "Xun", "Knight", "Viper", "ON",
    # Top Esports
    "369", "Tian", "Creme", "JackeyLove", "Zhuo",
    # Invictus Gaming
    "TheShy", "Wei", "Rookie", "Jiaqi", "Meiko",
    # G2
    "BrokenBlade", "SkewMond", "Caps", "Hans Sama", "Labrov",
    # Movistar KOI
    "Myrwn", "Elyoya", "Jojopyun", "Supa", "Alvaro",
    # Karmine Corp
    "Canna", "Yike", "kyeahoo", "Caliste", "Busio",
    # Team Liquid
    "Morgan", "Josedeodo", "Quid", "Yeon", "CoreJJ",
    # LYON
    "Dhokla", "Inspired", "Saint", "Berserker", "Isles",
    # Team Secret Whales
    "Pun", "Hizto", "Dire", "Eddie", "Bie",
    # CTBC Flying Oyster
    "Rest", "Shad0w", "Pout", "Doggo", "Kino",
    # LØS
    "Zest", "Curse", "Feisty", "Duduhh", "Ackerman",
]

# Elo di partenza per lega: le regioni più forti partono più in alto.
REGIONAL_WEIGHTS = {
    "LCK": 1750,
    "LPL": 1700,
    "LEC": 1450,
    "LCS": 1450,
    "LCP": 1200,
    "CBLOL": 1200,
}

DOMESTIC_LEAGUES = ["LCK", "LPL", "LEC", "LCS", "LCP", "CBLOL", "LTA", "LTA N"]

COLONNE_UTILI = [
    "gameid", "date", "league", "split", "playoffs", "gamelength",
    "position", "playername", "teamname", "champion", "result",
    "firstblood", "team kpm", "dragons", "barons", "towers", "vspm", "gspd",
    "kills", "deaths", "assists", "dpm", "damageshare", "earned gpm", "cspm",
    "golddiffat15", "xpdiffat15", "csdiffat15", "teamkills",
]

PLAYER_STATS = [
    "league", "position", "playername", "vspm",
    "kills", "deaths", "assists", "teamkills",
    "dpm", "damageshare", "earned gpm", "cspm",
    "golddiffat15", "xpdiffat15", "csdiffat15",
]

# Primo turno dello Swiss stage (sorteggio reale).
MATCH_PRIMO_TURNO = [
    ("Gen.G", "Invictus Gaming"),
    ("Bilibili Gaming", "Movistar KOI"),
    ("T1", "LØS"),
    ("Hanwha Life Esports", "Top Esports"),
    ("Dplus Kia", "G2 Esports"),
    ("Anyone's Legend", "Karmine Corp"),
    ("LYON", "Team Secret Whales"),
    ("CTBC Flying Oyster", "Team Liquid"),
]


def load_year(year: int) -> pd.DataFrame:
    """Legge il CSV di Oracle's Elixir per un singolo anno."""
    path = ROOT / f"{year}_LoL_esports_match_data_from_OraclesElixir.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"File mancante: {path.name}. Scaricalo da Oracle's Elixir e mettilo "
            "nella cartella del progetto."
        )
    return pd.read_csv(path, low_memory=False)


def load_history(years=(2023, 2024, 2025)) -> pd.DataFrame:
    """Concatena gli anni passati: la base per i rating Elo e i clutch factor."""
    return pd.concat([load_year(y) for y in years], ignore_index=True)


def team_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Una riga per team e partita."""
    return df[df["position"] == "team"].copy()


def player_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Una riga per giocatore e partita."""
    return df[df["position"] != "team"].copy()
