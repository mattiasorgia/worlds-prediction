"""Grafici delle probabilità stimate dalla simulazione.

Legge output/probabilita.csv (prodotto da montecarlo.py) e salva il confronto
tra probabilità di passare lo Swiss stage e di vincere il titolo.

Output: output/probabilita_worlds.png.
"""
import matplotlib.pyplot as plt
import pandas as pd

from common import OUT

COLORE_TOP8 = "#4c72b0"
COLORE_WIN = "#55a868"


def carica() -> pd.DataFrame:
    path = OUT / "probabilita.csv"
    if not path.exists():
        raise FileNotFoundError(
            "output/probabilita.csv non esiste: esegui prima `python montecarlo.py`."
        )
    return pd.read_csv(path)


def grafico(df: pd.DataFrame) -> None:
    df = df.sort_values("win_pct", ascending=True)

    fig, (ax_top8, ax_win) = plt.subplots(
        1, 2, figsize=(14, 6), sharey=True, gridspec_kw={"width_ratios": [1, 1]}
    )

    ax_top8.barh(df["team"], df["top8_pct"], color=COLORE_TOP8)
    ax_top8.set_title("Probabilità di passare lo Swiss stage")
    ax_top8.set_xlabel("Probabilità (%)")
    ax_top8.set_xlim(0, 100)

    ax_win.barh(df["team"], df["win_pct"], color=COLORE_WIN)
    ax_win.set_title("Probabilità di vincere i Worlds 2026")
    ax_win.set_xlabel("Probabilità (%)")
    ax_win.set_xlim(0, max(df["win_pct"].max() * 1.15, 1))

    for asse, colonna in ((ax_top8, "top8_pct"), (ax_win, "win_pct")):
        for barra, valore in zip(asse.patches, df[colonna]):
            asse.text(
                barra.get_width(), barra.get_y() + barra.get_height() / 2,
                f" {valore:.1f}%", va="center", fontsize=8,
            )

    fig.suptitle("Worlds 2026 - Modello Elo + Clutch Factor")
    fig.tight_layout()
    fig.savefig(OUT / "probabilita_worlds.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Salvato {OUT / 'probabilita_worlds.png'}")


if __name__ == "__main__":
    grafico(carica())
