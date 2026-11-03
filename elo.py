"""Rating Elo dei team, calcolati sulle partite del 2026.

Il rating parte da un valore legato alla lega di appartenenza e viene
aggiornato partita per partita, in ordine cronologico. Il fattore K cambia con
il contesto: un match di regular season muove l'Elo molto meno di un playoff o
di un torneo internazionale.

Output: models/elo_base.joblib (dict team -> Elo).
"""
import joblib

import pandas as pd

from common import MODELS, QUALIFIED_TEAMS, REGIONAL_WEIGHTS, load_year, team_rows

K_MSI = 72
K_EWC = 32
K_SPRING = 4
K_SPRING_PLAYOFFS = 12
K_SUMMER = 16
K_SUMMER_PLAYOFFS = 80
K_DEFAULT = 16


def probabilita_attesa(elo_a: float, elo_b: float) -> float:
    """Probabilità che A batta B in una singola partita."""
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))


def aggiorna_elo(elo_a: float, elo_b: float, vittoria_a: int, k: float = 32):
    """Restituisce i nuovi Elo dopo una partita (vittoria_a = 1 se vince A)."""
    attesa_a = probabilita_attesa(elo_a, elo_b)
    nuovo_a = elo_a + k * (vittoria_a - attesa_a)
    nuovo_b = elo_b + k * ((1 - vittoria_a) - (1 - attesa_a))
    return nuovo_a, nuovo_b


def k_factor(lega: str, split: str, playoffs: bool) -> float:
    """Quanto pesa una partita, in base a torneo, split e fase."""
    if lega == "MSI":
        return K_MSI
    if lega == "EWC":
        return K_EWC
    split = str(split).lower()
    if "spring" in split:
        return K_SPRING_PLAYOFFS if playoffs else K_SPRING
    if "summer" in split:
        return K_SUMMER_PLAYOFFS if playoffs else K_SUMMER
    return K_DEFAULT


def calcola_rating(df_2026: pd.DataFrame) -> dict:
    """Elo finale di ogni team dopo tutte le partite del 2026."""
    df = team_rows(df_2026)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    lega_del_team = df.groupby("teamname")["league"].first()
    elo = {
        team: REGIONAL_WEIGHTS.get(lega_del_team.get(team, "Unknown"), 1200)
        for team in df["teamname"].unique()
    }

    for _, partita in df.groupby("gameid"):
        if len(partita) != 2:
            continue

        t1, t2 = partita.iloc[0], partita.iloc[1]
        nome_t1, nome_t2 = t1["teamname"], t2["teamname"]

        k = k_factor(t1["league"], t1["split"], t1["playoffs"] == 1)
        elo[nome_t1], elo[nome_t2] = aggiorna_elo(
            elo[nome_t1], elo[nome_t2], t1["result"], k=k
        )

    return elo


def main() -> dict:
    ratings = calcola_rating(load_year(2026))
    joblib.dump(ratings, MODELS / "elo_base.joblib")

    ranking = {t: ratings[t] for t in QUALIFIED_TEAMS if t in ratings}
    ordinato = sorted(ranking.items(), key=lambda item: item[1], reverse=True)

    print("--- POWER RANKING WORLDS 2026 (Base Elo) ---")
    for posizione, (team, elo) in enumerate(ordinato, 1):
        print(f"{posizione}. {team}: {elo:.1f}")
    return ratings


if __name__ == "__main__":
    main()
