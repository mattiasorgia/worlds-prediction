"""Clutch/Choke factor: quanto un giocatore cambia rendimento ai Worlds.

Per ogni giocatore si confrontano le statistiche normalizzate nei match di
Worlds e in regular season. La differenza, pesata per ruolo, diventa un unico
punteggio: positivo = rende di più nei tornei internazionali (clutch),
negativo = cala (choke).

Output: models/clutch.joblib (DataFrame con una riga per giocatore e ruolo).
"""
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

from common import (
    DOMESTIC_LEAGUES,
    MODELS,
    PLAYER_STATS,
    QUALIFIED_TEAMS,
    load_history,
    player_rows,
)

METRICHE = ["dpm", "kda", "golddiffat15", "csdiffat15", "vspm", "kp"]

# Ogni ruolo è valutato sulle metriche che contano davvero per quel ruolo.
METRICHE_PER_RUOLO = {
    "adc": ["diff_golddiffat15", "diff_csdiffat15", "diff_dpm", "diff_kda"],
    "sup": ["diff_vspm", "diff_kp"],
    "jng": ["diff_kp", "diff_golddiffat15", "diff_kda"],
    "top": ["diff_golddiffat15", "diff_csdiffat15"],
    "mid": ["diff_dpm", "diff_kp", "diff_kda", "diff_golddiffat15", "diff_csdiffat15"],
}


def etichetta_torneo(lega: str) -> str:
    """Riduce la lega a 'Worlds', 'Regular Season' o 'Altro'."""
    if lega == "WLDs":
        return "Worlds"
    if lega in DOMESTIC_LEAGUES:
        return "Regular Season"
    return "Altro"


def calcola_clutch(history: pd.DataFrame) -> pd.DataFrame:
    """Punteggio di clutch per (giocatore, ruolo)."""
    df = player_rows(history)
    # Solo le partite dei team qualificati: è il contesto che ci interessa.
    df = df[df["teamname"].isin(QUALIFIED_TEAMS)][PLAYER_STATS].copy()

    df["torneo_binario"] = df["league"].apply(etichetta_torneo)
    df = df[df["torneo_binario"] != "Altro"]

    df["kda"] = (df["kills"] + df["assists"]) / df["deaths"].replace(0, 1)
    df["kp"] = (df["kills"] + df["assists"]) / df["teamkills"].replace(0, 1)
    df = df.fillna(0)

    # Le metriche sono su scale diverse: si standardizzano prima di sommarle.
    df[METRICHE] = StandardScaler().fit_transform(df[METRICHE])

    medie = (
        df.groupby(["playername", "position", "torneo_binario"])[METRICHE]
        .mean()
        .reset_index()
    )
    pivot = medie.pivot(
        index=["playername", "position"], columns="torneo_binario", values=METRICHE
    )
    # Servono entrambi i contesti, altrimenti la differenza non ha senso.
    pivot = pivot.dropna()

    clutch = pd.DataFrame(index=pivot.index)
    for metrica in METRICHE:
        clutch[f"diff_{metrica}"] = (
            pivot[(metrica, "Worlds")] - pivot[(metrica, "Regular Season")]
        )

    clutch["Final_Clutch_Score"] = [
        clutch.loc[idx, METRICHE_PER_RUOLO.get(idx[1], [])].sum()
        for idx in clutch.index
    ]
    return clutch


def main() -> pd.DataFrame:
    clutch = calcola_clutch(load_history())
    joblib.dump(clutch, MODELS / "clutch.joblib")

    top = (
        clutch.assign(Absolute_Diff=clutch["Final_Clutch_Score"].abs())
        .sort_values("Absolute_Diff", ascending=False)
        .head(10)[["Final_Clutch_Score"]]
    )
    print("--- CLUTCH/CHOKE FACTOR: le 10 oscillazioni più forti ---")
    for (giocatore, ruolo), riga in top.iterrows():
        print(f"{ruolo:<4} | {giocatore:<15} | {riga['Final_Clutch_Score']:>+6.2f}")

    print(f"\nGiocatori con entrambi i contesti: {len(clutch)}")
    return clutch


if __name__ == "__main__":
    main()
