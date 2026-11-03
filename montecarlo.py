"""Simulazione Monte Carlo dei Worlds 2026.

Ripete il torneo N_ITERAZIONI volte e stima, per ogni team, la probabilità di
passare lo Swiss stage (con il record), e di vincere il titolo.

Output: output/probabilita.csv.
"""
import random

import joblib
import pandas as pd

from common import MATCH_PRIMO_TURNO, MODELS, N_ITERAZIONI, OUT, SEED
from simulation import simula_knockout, simula_torneo_svizzero

RECORD = ["3-0", "3-1", "3-2"]


def simula_tornei(elo: dict, n_iterazioni: int = N_ITERAZIONI, seed: int = SEED) -> dict:
    """Conta quante volte ogni team raggiunge ogni traguardo."""
    rng = random.Random(seed)
    teams = [team for match in MATCH_PRIMO_TURNO for team in match]
    stats = {team: {**{r: 0 for r in RECORD}, "Top8": 0, "Win": 0} for team in teams}

    for _ in range(n_iterazioni):
        pool_3_0, pool_3_1, pool_3_2 = simula_torneo_svizzero(MATCH_PRIMO_TURNO, elo, rng)

        for record, pool in zip(RECORD, (pool_3_0, pool_3_1, pool_3_2)):
            for team in pool:
                stats[team][record] += 1
                stats[team]["Top8"] += 1

        campione = simula_knockout(pool_3_0, pool_3_1, pool_3_2, elo, rng)
        stats[campione]["Win"] += 1

    return stats


def tabella(stats: dict, n_iterazioni: int) -> pd.DataFrame:
    """Converte i contatori in percentuali, ordinando per probabilità di Top 8."""
    righe = [
        {
            "team": team,
            "top8_pct": 100 * s["Top8"] / n_iterazioni,
            "p_3_0": 100 * s["3-0"] / n_iterazioni,
            "p_3_1": 100 * s["3-1"] / n_iterazioni,
            "p_3_2": 100 * s["3-2"] / n_iterazioni,
            "win_pct": 100 * s["Win"] / n_iterazioni,
        }
        for team, s in stats.items()
    ]
    return pd.DataFrame(righe).sort_values("top8_pct", ascending=False).reset_index(drop=True)


def main() -> pd.DataFrame:
    elo = joblib.load(MODELS / "elo_finali.joblib")
    print(f"Lancio della simulazione Monte Carlo ({N_ITERAZIONI} tornei)...")

    risultato = tabella(simula_tornei(elo), N_ITERAZIONI)
    risultato.to_csv(OUT / "probabilita.csv", index=False)

    print("\n" + "=" * 87)
    print(f"PROBABILITÀ DI QUALIFICAZIONE SWISS STAGE & VITTORIA FINALE ({N_ITERAZIONI} run)")
    print("=" * 87)
    print(f"{'Team':<20} | {'Top 8 (Qual.)':<13} | {'3-0':<7} | {'3-1':<7} | {'3-2':<7} | {'Vincitore'}")
    print("-" * 87)
    for riga in risultato.itertuples():
        print(
            f"{riga.team:<20} | {riga.top8_pct:>6.2f}%       | {riga.p_3_0:>5.2f}% | "
            f"{riga.p_3_1:>5.2f}% | {riga.p_3_2:>5.2f}% | {riga.win_pct:>6.2f}%"
        )
    return risultato


if __name__ == "__main__":
    main()
