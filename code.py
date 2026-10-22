import pandas as pd
import math
import numpy as np
from sklearn.preprocessing import StandardScaler

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
    'LØS'
]

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
    "369", "Tian", "Creme", "JackeyLove", "Zhuo",
    # IG
    "TheShy", "Wei", "Rookie", "Jiaqi", "Meiko",
    # G2
    "BrokenBlade", "SkewMond", "Caps", "Hans Sama", "Labrov",
    # KOI
    "Myrwn", "Elyoya", "Jojopyun", "Supa", "Alvaro",
    # KC
    "Canna", "Yike", "kyeahoo", "Caliste", "Busio",
    # TL
    "Morgan", "Josedeodo", "Quid", "Yeon", "CoreJJ",
    # Lyon
    "Dhokla", "Inspired", "Saint", "Berserker", "Isles",
    # TSW
    "Pun", "Hizto", "Dire", "Eddie", "Bie",
    # CFO
    "Rest", "Shad0w", "Pout", "Doggo", "Kino",
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
    'csdiffat15',
    'teamkills'
]


df_teams_2026 = df_teams_2026[colonne_utili]
df_players_2026 = df_players_2026[colonne_utili]

df_teams_storico = df_teams_storico[colonne_utili]
df_players_storico = df_players_storico[colonne_utili]

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


player_stats = [
    'league',                     
    'position',     
    'playername',
    'vspm',              
    'kills', 'deaths', 'assists', 'teamkills',
    'dpm',          
    'damageshare',  
    'earned gpm',   
    'cspm',         
    'golddiffat15', 
    'xpdiffat15',   
    'csdiffat15'   
]

df_players_choke = df_players_storico[player_stats].copy()
leghe_domestiche = ['LCK', 'LPL', 'LEC', 'LCS', 'LCP', 'CBLOL', 'LTA', 'LTA N']

def assegna_torneo(lega):
    if lega == 'WLDs':
        return 'Worlds'
    elif lega in leghe_domestiche:
        return 'Regular Season'
    else:
        return 'Altro'

df_players_choke['torneo_binario'] = df_players_choke['league'].apply(assegna_torneo)
df_players_choke = df_players_choke[df_players_choke['torneo_binario'] != 'Altro']

# Prima di calcolare la pivot, eliminiamo tutto il rumore ('Altro')
df_players_choke = df_players_choke[df_players_choke['torneo_binario'] != 'Altro']

df_players_choke['kda'] = (df_players_choke['kills'] + df_players_choke['assists']) / df_players_choke['deaths'].replace(0, 1)
df_players_choke['kp'] = (df_players_choke['kills'] + df_players_choke['assists']) / df_players_choke['teamkills'].replace(0, 1)
df_players_choke = df_players_choke.fillna(0)

scaler = StandardScaler()
metriche_da_scalare = ['dpm', 'kda', 'golddiffat15', 'csdiffat15', 'vspm', 'kp']

df_players_choke[metriche_da_scalare] = scaler.fit_transform(df_players_choke[metriche_da_scalare])
stats_mean = df_players_choke.groupby(['playername', 'position', 'torneo_binario'])[metriche_da_scalare].mean().reset_index()
pivot_stats = stats_mean.pivot(index=['playername', 'position'], columns='torneo_binario', values=metriche_da_scalare)
pivot_stats = pivot_stats.dropna()

choke_factors = pd.DataFrame(index=pivot_stats.index)
for metrica in metriche_da_scalare:
    choke_factors[f'diff_{metrica}'] = pivot_stats[(metrica, 'Worlds')] - pivot_stats[(metrica, 'Regular Season')]

def calcola_clutch_score_finale(row):
    pos = row.name[1] # Recupera la 'position' dall'indice
    
    if pos == 'adc':
        return row['diff_golddiffat15'] + row['diff_csdiffat15'] + row['diff_dpm'] + row['diff_kda']
    elif pos == 'sup':
        return row['diff_vspm'] + row['diff_kp']
    elif pos == 'jng':
        return row['diff_kp'] + row['diff_golddiffat15'] + row['diff_kda']
    elif pos == 'top':
        return row['diff_golddiffat15'] + row['diff_csdiffat15']
    elif pos == 'mid':
        return row['diff_dpm'] + row['diff_kp'] + row['diff_kda'] + row['diff_golddiffat15'] + row['diff_csdiffat15']
    return 0

choke_factors['Final_Clutch_Score'] = choke_factors.apply(calcola_clutch_score_finale, axis=1)
choke_factors['Absolute_Diff'] = choke_factors['Final_Clutch_Score'].abs()
top_oscillazioni = choke_factors.sort_values(by='Absolute_Diff', ascending=False)

roster_2026 = df_players_2026[df_players_2026['teamname'].isin(qualified_teams)]

roster_2026 = roster_2026[['teamname', 'playername', 'position']].drop_duplicates()


choke_df_flat = choke_factors.reset_index()[['playername', 'position', 'Final_Clutch_Score']]

roster_con_score = pd.merge(roster_2026, choke_df_flat, on=['playername', 'position'], how='left')

roster_con_score['Final_Clutch_Score'] = roster_con_score['Final_Clutch_Score'].fillna(0.0)

roster_con_score = roster_con_score.sort_values(by=['teamname', 'position'])

print("\n=======================================================")
print("ROSTER WORLDS 2026 E RELATIVO CLUTCH/CHOKE FACTOR 🌍")
print("=======================================================")

for team in qualified_teams:
    team_roster = roster_con_score[roster_con_score['teamname'] == team]
    
    if team_roster.empty:
        continue
        
    print(f"\n[{team}]")
    for _, row in team_roster.iterrows():
        giocatore = row['playername']
        ruolo = row['position']
        score = row['Final_Clutch_Score']
        
        if score > 0.1:
            esito = "CLUTCH"
        elif score < -0.1:
            esito = "CHOKE"
        else:
            esito = "NEUTRO (o Rookie)"
            
        print(f"  {ruolo:<5} | {giocatore:<15} | Punteggio: {score:>+6.2f}  {esito}")


team_clutch_scores = roster_con_score.groupby('teamname')['Final_Clutch_Score'].sum()
CONVERSIONE_ELO = 25

power_ranking_aggiustato = {}

for team, base_elo in power_ranking_worlds.items():
    
    score_squadra = team_clutch_scores.get(team, 0.0)
    
    bonus_malus = score_squadra * CONVERSIONE_ELO

    elo_finale = base_elo + bonus_malus

    power_ranking_aggiustato[team] = {
        'Base_Elo': base_elo,
        'Team_Clutch_Score': score_squadra,
        'Bonus': bonus_malus,
        'Final_Elo': elo_finale
    }

ranking_ordinato = sorted(power_ranking_aggiustato.items(), key=lambda x: x[1]['Final_Elo'], reverse=True)

print("\n================================================================")
print("POWER RANKING DEFINITIVO (Base Elo + Player Clutch Factor)")
print("================================================================")

for posizione, (team, dati) in enumerate(ranking_ordinato, 1):
    base = dati['Base_Elo']
    bonus = dati['Bonus']
    finale = dati['Final_Elo']
    score_sq = dati['Team_Clutch_Score']

    segno = "+" if bonus > 0 else ""
    
    print(f"{posizione:02d}. {team:<20} | Base: {base:.1f} | Clutch: {segno}{score_sq:.2f} ({segno}{bonus:.1f} Elo) | ELO FINALE: {finale:.1f}")


import random
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Mappatura degli Elo finali
elo_finali = {dati[0]: dati[1]['Final_Elo'] for dati in ranking_ordinato}

def probabilita_vittoria(team_a, team_b, formato=1):
    """Calcola la probabilità di vittoria a seconda del formato (Bo1, Bo3, Bo5)"""
    elo_a = elo_finali.get(team_a, 1500)
    elo_b = elo_finali.get(team_b, 1500)
    
    # Formula Elo base (singola partita)
    prob_a = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
    
    if formato == 3:
        # Probabilità di vincere un Bo3
        prob_a = (prob_a ** 2) * (3 - 2 * prob_a)
    elif formato == 5:
        # Probabilità di vincere un Bo5
        prob_a = (prob_a ** 3) * (10 - 15 * prob_a + 6 * (prob_a ** 2))
        
    return prob_a

def simula_partita(team_a, team_b, formato=1):
    prob_a = probabilita_vittoria(team_a, team_b, formato)
    return (team_a, team_b) if random.random() < prob_a else (team_b, team_a)

def simula_round(lista_team, formato=1):
    """Accoppia i team a due a due e restituisce vincenti e perdenti"""
    random.shuffle(lista_team) # Sorteggio casuale
    vincenti, perdenti = [], []
    for i in range(0, len(lista_team), 2):
        vincitore, perdente = simula_partita(lista_team[i], lista_team[i+1], formato)
        vincenti.append(vincitore)
        perdenti.append(perdente)
    return vincenti, perdenti

def simula_torneo_svizzero(match_round_1):
    team_in_gara = [team for match in match_round_1 for team in match]
    records = {team: {'W': 0, 'L': 0} for team in team_in_gara}
    
    # Usiamo tre liste separate per mantenere il record ai fini del sorteggio
    pool_3_0, pool_3_1, pool_3_2 = [], [], []
    
    # Round 1 (Bo1)
    for t1, t2 in match_round_1:
        v, p = simula_partita(t1, t2, formato=1)
        records[v]['W'] += 1; records[p]['L'] += 1
        
    # Round 2 (Bo1)
    pool_1_0 = [t for t, r in records.items() if r['W']==1 and r['L']==0]
    pool_0_1 = [t for t, r in records.items() if r['W']==0 and r['L']==1]
    
    v, p = simula_round(pool_1_0, formato=1); [records[t].update({'W': 2}) for t in v]; [records[t].update({'L': 1}) for t in p]
    v, p = simula_round(pool_0_1, formato=1); [records[t].update({'W': 1}) for t in v]; [records[t].update({'L': 2}) for t in p]
    
    # Round 3
    pool_2_0 = [t for t, r in records.items() if r['W']==2 and r['L']==0] # Qualificazione (Bo3)
    pool_1_1 = [t for t, r in records.items() if r['W']==1 and r['L']==1] # Sopravvivenza (Bo1)
    pool_0_2 = [t for t, r in records.items() if r['W']==0 and r['L']==2] # Eliminazione (Bo3)
    
    v, p = simula_round(pool_2_0, formato=3); pool_3_0.extend(v); [records[t].update({'L': 1}) for t in p]
    v, p = simula_round(pool_0_2, formato=3); [records[t].update({'W': 1}) for t in v] 
    v, p = simula_round(pool_1_1, formato=1); [records[t].update({'W': 2}) for t in v]; [records[t].update({'L': 2}) for t in p]
    
    # Round 4 (Tutti Bo3)
    pool_2_1 = [t for t, r in records.items() if r['W']==2 and r['L']==1]
    pool_1_2 = [t for t, r in records.items() if r['W']==1 and r['L']==2]
    
    v, p = simula_round(pool_2_1, formato=3); pool_3_1.extend(v); [records[t].update({'L': 2}) for t in p]
    v, p = simula_round(pool_1_2, formato=3); [records[t].update({'W': 2}) for t in v]
    
    # Round 5 (Tutti Bo3)
    pool_2_2 = [t for t, r in records.items() if r['W']==2 and r['L']==2]
    v, p = simula_round(pool_2_2, formato=3); pool_3_2.extend(v)
    
    return pool_3_0, pool_3_1, pool_3_2

def simula_knockout(qual_3_0, qual_3_1, qual_3_2):
    """Simula il bracket in base alle regole ufficiali di sorteggio dei Worlds"""
    
    # 1. Shuffle casuale delle urne per simulare le palline estratte
    q_30 = random.sample(qual_3_0, 2)
    q_31 = random.sample(qual_3_1, 3)
    q_32 = random.sample(qual_3_2, 3)
    
    # 2. Regola d'oro: I due 3-0 pescano obbligatoriamente due 3-2
    qf_a_30 = (q_30[0], q_32[0])
    qf_b_30 = (q_30[1], q_32[1])
    
    # 3. Il rimanente 3-2 pesca obbligatoriamente un 3-1
    qf_c_31_vs_32 = (q_31[0], q_32[2])
    
    # 4. I due rimanenti 3-1 giocano per forza tra loro
    qf_d_31_vs_31 = (q_31[1], q_31[2])
    
    # 5. Costruzione Bracket (Lato SX e Lato DX)
    # I due match che contengono i 3-0 vengono forzati su lati opposti
    altri_match = [qf_c_31_vs_32, qf_d_31_vs_31]
    random.shuffle(altri_match)
    
    lato_sx = [qf_a_30, altri_match[0]]
    lato_dx = [qf_b_30, altri_match[1]]
    
    # --- QUARTI DI FINALE (Bo5) ---
    vincitori_qf_sx = [simula_partita(m[0], m[1], formato=5)[0] for m in lato_sx]
    vincitori_qf_dx = [simula_partita(m[0], m[1], formato=5)[0] for m in lato_dx]
    
    # --- SEMIFINALI (Bo5) ---
    vincente_semi_sx = simula_partita(vincitori_qf_sx[0], vincitori_qf_sx[1], formato=5)[0]
    vincente_semi_dx = simula_partita(vincitori_qf_dx[0], vincitori_qf_dx[1], formato=5)[0]
    
    # --- FINALE (Bo5) ---
    campione = simula_partita(vincente_semi_sx, vincente_semi_dx, formato=5)[0]
    
    return campione

# --- ESECUZIONE ---
match_primo_turno = [
    ("Gen.G",'Invictus Gaming'),
    ("Bilibili Gaming","Movistar KOI"),
    ("T1","LØS"),
    ("Hanwha Life Esports","Top Esports"),
    ("Dplus Kia", "G2 Esports"),
    ("Anyone's Legend", "Karmine Corp"),
    ("LYON", "Team Secret Whales"),
    ("CTBC Flying Oyster", "Team Liquid")
]

# ==========================================
# (Il tuo codice precedente con le funzioni e la lista match_primo_turno arriva fino a qui...)
# ==========================================

N_ITERAZIONI = 10000

# --- 1. INIZIALIZZAZIONE DEI TRACKER ---
teams_in_gara = [team for match in match_primo_turno for team in match]

# Creiamo un dizionario per salvare tutte le statistiche di ogni team
stats_team = {team: {'3-0': 0, '3-1': 0, '3-2': 0, 'Top8': 0, 'Win': 0} for team in teams_in_gara}

print(f"Lancio della Simulazione Monte Carlo ({N_ITERAZIONI} tornei in corso)...")

# --- 2. CICLO MONTE CARLO ---
for _ in range(N_ITERAZIONI):
    # Simula lo Swiss e recupera i team divisi per Record
    pool_3_0, pool_3_1, pool_3_2 = simula_torneo_svizzero(match_primo_turno)
    
    # Aggiorniamo le statistiche di qualificazione
    for t in pool_3_0:
        stats_team[t]['3-0'] += 1
        stats_team[t]['Top8'] += 1
    for t in pool_3_1:
        stats_team[t]['3-1'] += 1
        stats_team[t]['Top8'] += 1
    for t in pool_3_2:
        stats_team[t]['3-2'] += 1
        stats_team[t]['Top8'] += 1
        
    # Simula il Knockout con le regole ufficiali di piazzamento
    campione = simula_knockout(pool_3_0, pool_3_1, pool_3_2)
    
    # Aggiorna il contatore del vincitore finale
    stats_team[campione]['Win'] += 1


# --- 3. STAMPA DELLA DASHBOARD FINALE ---
print("\n=======================================================================================")
print(f" 📊 PROBABILITÀ DI QUALIFICAZIONE SWISS STAGE & VITTORIA FINALE ({N_ITERAZIONI} run) 📊")
print("=======================================================================================")
print(f"{'Team':<20} | {'Top 8 (Qual.)':<13} | {'3-0':<7} | {'3-1':<7} | {'3-2':<7} | {'Vincitore'}")
print("-" * 87)

# Ordiniamo i team per probabilità decrescente di arrivare in Top 8
team_ordinati = sorted(stats_team.keys(), key=lambda x: stats_team[x]['Top8'], reverse=True)

for team in team_ordinati:
    # Convertiamo i contatori in percentuali
    p_top8 = (stats_team[team]['Top8'] / N_ITERAZIONI) * 100
    p_3_0 = (stats_team[team]['3-0'] / N_ITERAZIONI) * 100
    p_3_1 = (stats_team[team]['3-1'] / N_ITERAZIONI) * 100
    p_3_2 = (stats_team[team]['3-2'] / N_ITERAZIONI) * 100
    p_win = (stats_team[team]['Win'] / N_ITERAZIONI) * 100
    
    print(f"{team:<20} | {p_top8:>6.2f}%       | {p_3_0:>5.2f}% | {p_3_1:>5.2f}% | {p_3_2:>5.2f}% | {p_win:>6.2f}%")

# (Opzionale) Se vuoi mantenere il grafico a barre per il vincitore:
import matplotlib.pyplot as plt
import seaborn as sns

team_names_plot = [t for t in team_ordinati if stats_team[t]['Win'] > 0]
win_probs_plot = [(stats_team[t]['Win'] / N_ITERAZIONI) * 100 for t in team_names_plot]

plt.figure(figsize=(12, 6))
sns.barplot(x=win_probs_plot, y=team_names_plot, palette="viridis")
plt.title(f"Probabilità di Vincere i Worlds 2026 (Modello Elo + Choke Factor)\nSimulazione Monte Carlo: {N_ITERAZIONI} iterazioni")
plt.xlabel("Probabilità di Vittoria (%)")
plt.ylabel("Team")
plt.tight_layout()
plt.show()