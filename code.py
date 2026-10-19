import pandas as pd
import math

qualified_teams = [
    # LCK (Korea)
    "Gen.G", "Hanwha Life Esports", "T1", "Dplus Kia",
    # LPL (Cina)
    "Anyone's Legend", "Bilibili Gaming", "Top Esports", "Invictus Gaming",
    # LEC (Europa)
    "G2 Esports", "Movistar KOI", "Karmine Corp",
    # LCS (Nord America)
    "Team Liquid", "LYON",
    # LCP (Asia Pacifico)
    "Team Secret Whales", "CTBC Flying Oyster",
    # CBLOL (Brasile/Americhe)
    "LOS"
]

# Lista dei giocatori qualificati (5 per team)
qualified_players = [
    # Gen.G
    "Kiin", "Canyon", "Chovy", "Ruler", "Duro",
    # Hanwha Life
    "Zeus", "Kanavi", "Zeka", "Gumayusi", "Delight",
    # T1
    "Doran", "Oner", "Faker", "Peyz", "Keria",
    # Dplus KIA
    "Siwoo", "Lucid", "ShowMaker", "Smash", "Career",
    # AL
    "Breathe", "Tarzan", "Shanks", "Hope", "Kael",
    # BLG
    "Bin", "Xun", "Knight", "Viper", "ON",
    # TES
    "369", "Tian", "Creme", "Jackeylove", "Zhuo",
    # IG
    "TheShy", "Wei", "Rookie", "Jiaqi", "Meiko",
    # G2
    "BrokenBlade", "SkewMond", "Caps", "Hans Sama", "Labrov",
    # KOI
    "Myrwn", "Elyoya", "Jojopyun", "Supa", "Alvaro",
    # KC
    "Canna", "Yike", "Kyeahoo", "Caliste", "Busio",
    # TL
    "Morgan", "Josedeodo", "Quid", "Yeon", "CoreJJ",
    # Lyon
    "Dhokla", "Inspired", "Saint", "Berserker", "Isles",
    # TSW
    "Pun", "Hitzo", "Dire", "Eddie", "Bie",
    # CFO
    "Rest", "Shad0w", "POUT", "Doggo", "Kino",
    # LOS
    "Zest", "Curse", "Feisty", "Duduhh", "Ackerman"
]

df_2026 = pd.read_csv("2026_LoL_esports_match_data_from_OraclesElixir.csv", low_memory=False)
df_2025 = pd.read_csv("2025_LoL_esports_match_data_from_OraclesElixir.csv", low_memory=False)
df_2024 = pd.read_csv("2024_LoL_esports_match_data_from_OraclesElixir.csv", low_memory=False)
df_2023 = pd.read_csv("2023_LoL_esports_match_data_from_OraclesElixir.csv", low_memory=False)

df_storico = pd.concat([df_2023, df_2024, df_2025], ignore_index=True)

columns = list(df_2026.columns)

df_teams_2026 = df_2026[
    (df_2026['position'] == 'team') & 
    (df_2026['teamname'].isin(qualified_teams))
]

df_players_2026 = df_2026[
    (df_2026['position'] != 'team') & 
    (df_2026['playername'].isin(qualified_players))
]

df_teams_storico = df_storico[
    (df_storico['position'] == 'team') & 
    (df_storico['teamname'].isin(qualified_teams))
]

df_players_storico = df_storico[
    (df_storico['position'] != 'team') & 
    (df_storico['teamname'].isin(qualified_teams))
]


colonne_utili = [
    
    'gameid',       
    'date',         
    'league',       
    'split',        
    'playoffs',     
    'gamelength',   
    'position',     
    'playername',   
    'teamname',     
    'champion',     
    'result',       
    'firstblood',   
    'team kpm',     
    'dragons',      
    'barons',       
    'towers',       
    'vspm',         
    'gspd',         
    'kills', 'deaths', 'assists', 
    'dpm',          
    'damageshare',  
    'earned gpm',   
    'cspm',         
    'golddiffat15', 
    'xpdiffat15',   
    'csdiffat15'   
]

# Manteniamo solo le colonne utili nei dataset correnti e storici
df_teams_2026 = df_teams_2026[colonne_utili]
df_players_2026 = df_players_2026[colonne_utili]

df_teams_storico = df_teams_storico[colonne_utili]
df_players_storico = df_players_storico[colonne_utili]

# Converte la colonna data per facilitare i calcoli temporali (Time-Decay)
df_teams_2026['date'] = pd.to_datetime(df_teams_2026['date'])
df_players_2026['date'] = pd.to_datetime(df_players_2026['date'])

pesi_regionali = {
    'LCK': 1750, 
    'LPL': 1700, 
    'LEC': 1450, 
    'LCS': 1450, 
    'LCP': 1200,
    'CBLOL': 1200
}


def calcola_probabilita(elo_a, elo_b):
    return 1 / (1 + math.pow(10, (elo_b - elo_a) / 400))

def aggiorna_elo(elo_a, elo_b, vittoria_a, k=32):
    prob_a = calcola_probabilita(elo_a, elo_b)
    nuovo_elo_a = elo_a + k * (vittoria_a - prob_a)
    nuovo_elo_b = elo_b + k * ((1 - vittoria_a) - (1 - prob_a))
    return nuovo_elo_a, nuovo_elo_b


df_tutti_team_2026 = df_2026[df_2026['position'] == 'team'].copy()

df_tutti_team_2026['date'] = pd.to_datetime(df_tutti_team_2026['date'])
df_tutti_team_2026 = df_tutti_team_2026.sort_values(by='date')

mappa_leghe = df_tutti_team_2026.groupby('teamname')['league'].first()

tutti_i_team = df_tutti_team_2026['teamname'].unique()
elo_ratings = {}

for team in tutti_i_team:
    lega_del_team = mappa_leghe.get(team, 'Unknown')
    # Se la lega è mappata prende il peso, altrimenti un default di 1200
    elo_iniziale = pesi_regionali.get(lega_del_team, 1200) 
    elo_ratings[team] = elo_iniziale

partite = df_tutti_team_2026.groupby('gameid')

for gameid, dati_partita in partite:
    if len(dati_partita) != 2:
        continue
        
    team1 = dati_partita.iloc[0]
    team2 = dati_partita.iloc[1]
    
    nome_t1 = team1['teamname']
    nome_t2 = team2['teamname']
    risultato_t1 = team1['result']
    
    # Nuove variabili per contestualizzare la partita
    lega_partita = team1['league']
    is_playoffs = team1['playoffs'] == 1
    split_partita = str(team1['split']).lower() # 'spring' o 'summer'
    
    elo_t1 = elo_ratings[nome_t1]
    elo_t2 = elo_ratings[nome_t2]
    
    if lega_partita == 'MSI':
        selettore_K = 72
    elif lega_partita == "EWC":
        selettore_K = 32
    elif 'spring' in split_partita:
        selettore_K = 12 if is_playoffs else 4
    elif 'summer' in split_partita:
        selettore_K = 80 if is_playoffs else 16 
    else:
        selettore_K = 16
        
    nuovo_elo_t1, nuovo_elo_t2 = aggiorna_elo(elo_t1, elo_t2, risultato_t1, k=selettore_K)
    
    elo_ratings[nome_t1] = nuovo_elo_t1
    elo_ratings[nome_t2] = nuovo_elo_t2


power_ranking_worlds = {team: elo_ratings[team] for team in qualified_teams if team in elo_ratings}

power_ranking_ordinato = dict(sorted(power_ranking_worlds.items(), key=lambda item: item[1], reverse=True))

print("--- POWER RANKING WORLDS 2026 (Base Elo) ---")
for posizione, (team, elo) in enumerate(power_ranking_ordinato.items(), 1):
    print(f"{posizione}. {team}: {elo:.1f}")