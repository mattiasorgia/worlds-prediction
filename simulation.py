"""Motore della simulazione: partite, round svizzero e bracket a eliminazione.

Funzioni pure: ricevono il dizionario degli Elo finali e un generatore casuale,
non leggono file e non stampano nulla. Così la simulazione Monte Carlo può
girare migliaia di volte senza toccare il disco.
"""
import random


def probabilita_vittoria(elo_a: float, elo_b: float, formato: int = 1) -> float:
    """Probabilità che A vinca la serie: Bo1, Bo3 o Bo5."""
    p = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))
    if formato == 3:
        return p ** 2 * (3 - 2 * p)
    if formato == 5:
        return p ** 3 * (10 - 15 * p + 6 * p ** 2)
    return p


def simula_partita(team_a, team_b, elo, formato=1, rng=None):
    """Restituisce (vincitore, perdente)."""
    rng = rng or random
    p = probabilita_vittoria(elo.get(team_a, 1500), elo.get(team_b, 1500), formato)
    return (team_a, team_b) if rng.random() < p else (team_b, team_a)


def simula_round(lista_team, elo, formato=1, rng=None):
    """Sorteggia gli accoppiamenti e restituisce vincenti e perdenti."""
    rng = rng or random
    rng.shuffle(lista_team)
    vincenti, perdenti = [], []
    for i in range(0, len(lista_team), 2):
        vincitore, perdente = simula_partita(lista_team[i], lista_team[i + 1], elo, formato, rng)
        vincenti.append(vincitore)
        perdenti.append(perdente)
    return vincenti, perdenti


def simula_torneo_svizzero(match_round_1, elo, rng=None):
    """Swiss stage a cinque round. Restituisce i qualificati divisi per record."""
    rng = rng or random
    team_in_gara = [team for match in match_round_1 for team in match]
    records = {team: {"W": 0, "L": 0} for team in team_in_gara}
    pool_3_0, pool_3_1, pool_3_2 = [], [], []

    # Round 1 (Bo1)
    for t1, t2 in match_round_1:
        vincitore, perdente = simula_partita(t1, t2, elo, formato=1, rng=rng)
        records[vincitore]["W"] += 1
        records[perdente]["L"] += 1

    # Round 2 (Bo1): 1-0 contro 1-0, 0-1 contro 0-1
    pool_1_0 = [t for t, r in records.items() if r["W"] == 1 and r["L"] == 0]
    pool_0_1 = [t for t, r in records.items() if r["W"] == 0 and r["L"] == 1]

    vincenti, perdenti = simula_round(pool_1_0, elo, 1, rng)
    for t in vincenti:
        records[t]["W"] = 2
    for t in perdenti:
        records[t]["L"] = 1
    vincenti, perdenti = simula_round(pool_0_1, elo, 1, rng)
    for t in vincenti:
        records[t]["W"] = 1
    for t in perdenti:
        records[t]["L"] = 2

    # Round 3: 2-0 si qualifica (Bo3), 0-2 è eliminato (Bo3), 1-1 si gioca il resto (Bo1)
    pool_2_0 = [t for t, r in records.items() if r["W"] == 2 and r["L"] == 0]
    pool_1_1 = [t for t, r in records.items() if r["W"] == 1 and r["L"] == 1]
    pool_0_2 = [t for t, r in records.items() if r["W"] == 0 and r["L"] == 2]

    vincenti, perdenti = simula_round(pool_2_0, elo, 3, rng)
    pool_3_0.extend(vincenti)
    for t in perdenti:
        records[t]["L"] = 1
    vincenti, _ = simula_round(pool_0_2, elo, 3, rng)
    for t in vincenti:
        records[t]["W"] = 1
    vincenti, perdenti = simula_round(pool_1_1, elo, 1, rng)
    for t in vincenti:
        records[t]["W"] = 2
    for t in perdenti:
        records[t]["L"] = 2

    # Round 4 (tutti Bo3): 2-1 si qualifica, 1-2 va all'ultima chance
    pool_2_1 = [t for t, r in records.items() if r["W"] == 2 and r["L"] == 1]
    pool_1_2 = [t for t, r in records.items() if r["W"] == 1 and r["L"] == 2]

    vincenti, perdenti = simula_round(pool_2_1, elo, 3, rng)
    pool_3_1.extend(vincenti)
    for t in perdenti:
        records[t]["L"] = 2
    vincenti, _ = simula_round(pool_1_2, elo, 3, rng)
    for t in vincenti:
        records[t]["W"] = 2

    # Round 5 (Bo3): i 2-2 si giocano l'ultimo posto
    pool_2_2 = [t for t, r in records.items() if r["W"] == 2 and r["L"] == 2]
    vincenti, _ = simula_round(pool_2_2, elo, 3, rng)
    pool_3_2.extend(vincenti)

    return pool_3_0, pool_3_1, pool_3_2


def simula_knockout(qual_3_0, qual_3_1, qual_3_2, elo, rng=None):
    """Bracket a eliminazione con le regole di sorteggio ufficiali dei Worlds."""
    rng = rng or random
    sorteggiati_3_0 = rng.sample(qual_3_0, 2)
    sorteggiati_3_1 = rng.sample(qual_3_1, 3)
    sorteggiati_3_2 = rng.sample(qual_3_2, 3)

    # I due 3-0 pescano obbligatoriamente due 3-2
    qf_a = (sorteggiati_3_0[0], sorteggiati_3_2[0])
    qf_b = (sorteggiati_3_0[1], sorteggiati_3_2[1])
    # Il 3-2 rimasto pesca un 3-1
    qf_c = (sorteggiati_3_1[0], sorteggiati_3_2[2])
    # I due 3-1 rimasti si affrontano tra loro
    qf_d = (sorteggiati_3_1[1], sorteggiati_3_1[2])

    # I match con i 3-0 finiscono su lati opposti del bracket
    altri = [qf_c, qf_d]
    rng.shuffle(altri)
    lato_sx = [qf_a, altri[0]]
    lato_dx = [qf_b, altri[1]]

    # Quarti (Bo5)
    vincitori_sx = [simula_partita(m[0], m[1], elo, 5, rng)[0] for m in lato_sx]
    vincitori_dx = [simula_partita(m[0], m[1], elo, 5, rng)[0] for m in lato_dx]

    # Semifinali (Bo5)
    finalista_sx = simula_partita(vincitori_sx[0], vincitori_sx[1], elo, 5, rng)[0]
    finalista_dx = simula_partita(vincitori_dx[0], vincitori_dx[1], elo, 5, rng)[0]

    # Finale (Bo5)
    return simula_partita(finalista_sx, finalista_dx, elo, 5, rng)[0]