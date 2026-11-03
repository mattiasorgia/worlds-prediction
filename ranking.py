"""Power ranking finale: Elo dei team corretto dal clutch factor dei giocatori.

Il punteggio di clutch della squadra è la somma dei punteggi dei cinque
titolari; ogni punto vale CONVERSIONE_ELO punti di Elo. Il risultato è il
rating che alimenta la simulazione.

Output: output/power_ranking.csv, models/elo_finali.joblib.
"""
import joblib
import pandas as pd

from common import (
    MODELS,
    OUT,
    QUALIFIED_PLAYERS,
    QUALIFIED_TEAMS,
    load_year,
    player_rows,
)

CONVERSIONE_ELO = 25
SOGLIA_CLUTCH = 0.1


def roster_2026(df_2026: pd.DataFrame) -> pd.DataFrame:
    """Coppie (team, giocatore, ruolo) dei titolari qualificati ai Worlds."""
    roster = player_rows(df_2026)
    roster = roster[
        roster["teamname"].isin(QUALIFIED_TEAMS)
        & roster["playername"].isin(QUALIFIED_PLAYERS)
    ]
    return roster[["teamname", "playername", "position"]].drop_duplicates()


def unisci_clutch(roster: pd.DataFrame, clutch: pd.DataFrame) -> pd.DataFrame:
    """Aggancia a ogni titolare il suo punteggio di clutch (0 se sconosciuto)."""
    piatto = clutch.reset_index()[["playername", "position", "Final_Clutch_Score"]]
    unito = roster.merge(piatto, on=["playername", "position"], how="left")
    unito["Final_Clutch_Score"] = unito["Final_Clutch_Score"].fillna(0.0)
    return unito.sort_values(["teamname", "position"])


def etichetta(score: float) -> str:
    if score > SOGLIA_CLUTCH:
        return "CLUTCH"
    if score < -SOGLIA_CLUTCH:
        return "CHOKE"
    return "NEUTRO (o rookie)"


def stampa_roster(roster: pd.DataFrame) -> None:
    print("=======================================================")
    print("ROSTER WORLDS 2026 E RELATIVO CLUTCH/CHOKE FACTOR")
    print("=======================================================")
    for team in QUALIFIED_TEAMS:
        squadra = roster[roster["teamname"] == team]
        if squadra.empty:
            continue
        print(f"\n[{team}]")
        for _, riga in squadra.iterrows():
            score = riga["Final_Clutch_Score"]
            print(
                f"  {riga['position']:<5} | {riga['playername']:<15} | "
                f"Punteggio: {score:>+6.2f}  {etichetta(score)}"
            )


def power_ranking(elo_base: dict, roster: pd.DataFrame) -> pd.DataFrame:
    """Elo finale = Elo base + (clutch della squadra x CONVERSIONE_ELO)."""
    clutch_team = roster.groupby("teamname")["Final_Clutch_Score"].sum()

    righe = []
    for team, base in elo_base.items():
        if team not in QUALIFIED_TEAMS:
            continue
        score = clutch_team.get(team, 0.0)
        bonus = score * CONVERSIONE_ELO
        righe.append({
            "team": team,
            "base_elo": base,
            "clutch_score": score,
            "bonus_elo": bonus,
            "final_elo": base + bonus,
        })

    return (
        pd.DataFrame(righe)
        .sort_values("final_elo", ascending=False)
        .reset_index(drop=True)
    )


def main() -> pd.DataFrame:
    elo_base = joblib.load(MODELS / "elo_base.joblib")
    clutch = joblib.load(MODELS / "clutch.joblib")

    roster = unisci_clutch(roster_2026(load_year(2026)), clutch)
    stampa_roster(roster)

    ranking = power_ranking(elo_base, roster)
    ranking.to_csv(OUT / "power_ranking.csv", index=False)
    joblib.dump(dict(zip(ranking["team"], ranking["final_elo"])), MODELS / "elo_finali.joblib")

    print("\n================================================================")
    print("POWER RANKING DEFINITIVO (Base Elo + Player Clutch Factor)")
    print("================================================================")
    for posizione, riga in enumerate(ranking.itertuples(), 1):
        segno = "+" if riga.bonus_elo > 0 else ""
        print(
            f"{posizione:02d}. {riga.team:<20} | Base: {riga.base_elo:.1f} | "
            f"Clutch: {segno}{riga.clutch_score:.2f} ({segno}{riga.bonus_elo:.1f} Elo) | "
            f"ELO FINALE: {riga.final_elo:.1f}"
        )
    return ranking


if __name__ == "__main__":
    main()
