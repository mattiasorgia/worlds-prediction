# Worlds 2026: previsione del vincitore con Elo e clutch factor

Modello probabilistico per i Worlds di League of Legends 2026. I rating Elo dei
team sono costruiti sulle partite dell'anno in corso, corretti con un "clutch
factor" che misura quanto ogni giocatore rende di più o di meno nei tornei
internazionali, e infine usati per simulare il torneo 10.000 volte: Swiss stage
e bracket a eliminazione, con le regole di sorteggio reali.

Il progetto è una simulazione Monte Carlo guidata da
rating Elo. La parte statistica sta nella stima del clutch factor, che confronta
le statistiche normalizzate di ogni giocatore ai Worlds e in regular season.

## Risultati in breve

- **Favorito: Gen.G**, 39,7% di probabilità di vincere il titolo e 97,8% di
  passare lo Swiss stage. Elo finale 1883,5, il più alto del torneo.
- **Bilibili Gaming** 22,9%, **T1** 16,4%, **Hanwha Life Esports** 16,1%: quattro
  squadre si giocano quasi tutto il titolo (95,2% complessivo).
- **Il clutch factor sposta la griglia più dell'Elo.** Anyone's Legend guadagna
  45,7 punti di Elo (Shanks +1,23 e Kael +0,55) e sale dall'8° al 6° posto. In
  senso opposto G2 Esports perde 53,7 punti e scende dal 6° al 9°.
- Chi non ha storico ai Worlds parte da un clutch factor neutro (0,00), quindi
  spesso il segnale arriva solo dai giocatori esperti.

## Dati

- Fonte: [Oracle's Elixir](https://oracleselixir.com/tools/downloads), file
  `2023`–`2026_LoL_esports_match_data_from_OraclesElixir.csv`, un CSV per anno.
- Ogni riga è un giocatore (o il team aggregato, `position = team`) in una
  partita. Le partite del 2026 servono per l'Elo, quelle 2023-2025 per il clutch
  factor.
- **2026**: usato per calcolare i rating di tutti i team professionistici, quindi
  non conta solo chi è qualificato ai Worlds. I rating partono da un valore
  legato alla lega (LCK 1750, LPL 1700, LEC/LCS 1450, LCP/CBLOL 1200).
- **2023-2025**: filtro sui team qualificati, poi confronto tra le partite di
  Worlds (`WLDs`) e quelle di regular season delle leghe domestiche.

I CSV non sono inclusi (sono circa 80 MB l'uno): scaricali da Oracle's Elixir e
mettili nella cartella principale.

## Struttura del repository

```
common.py          costanti (team e giocatori qualificati, pesi regionali,
                   primo turno dello Swiss, N_ITERAZIONI) e lettura dei CSV
elo.py             rating Elo 2026, con K che dipende da torneo, split e playoff
clutch.py          clutch/choke factor per giocatore, pesato per ruolo
ranking.py         power ranking finale = Elo base + bonus clutch della squadra
simulation.py      motore: probabilità Bo1/Bo3/Bo5, Swiss, bracket (funzioni pure)
montecarlo.py      N simulazioni del torneo, dashboard e tabella delle probabilità
grafici.py         grafico delle probabilità stimate
models/            artefatti intermedi salvati con joblib (non versionati)
output/            power_ranking.csv, probabilita.csv, grafico
```

Ogni script salva il proprio risultato su disco e il successivo lo rilegge,
quindi non si ricalcola tutto a ogni passo. Le fasi costose (lettura dei CSV,
Scaler, Elo) girano una volta sola.

## Come eseguire

```bash
pip install -r requirements.txt

python elo.py           # ~25s: rating Elo 2026
python clutch.py        # ~45s: clutch factor dai CSV 2023-2025
python ranking.py       # power ranking finale
python montecarlo.py    # 10.000 tornei simulati
python grafici.py       # grafico delle probabilità
```

## Metodologia

### 1. Rating Elo

Classico Elo con probabilità attesa $p = 1/(1+10^{(E_b-E_a)/400})$. Il fattore K
dipende dal contesto, così una partita di regular season muove poco il rating e
un playoff molto:

| Contesto | K |
|---|---|
| MSI | 72 |
| EWC | 32 |
| Playoff estivi | 80 |
| Regular season estiva | 16 |
| Playoff primaverili | 12 |
| Regular season primaverile | 4 |
| Altro | 16 |

### 2. Clutch factor

Per ogni giocatore si mediano sei metriche per partita (`dpm`, `kda`,
`golddiffat15`, `csdiffat15`, `vspm`, `kp` — quest'ultima è la kill
participation), dopo averle standardizzate con uno `StandardScaler` per
renderle confrontabili. Si tiene solo chi ha giocato **sia** ai Worlds **sia** in
regular season, e si calcola la differenza Worlds − regular season.

Il punteggio finale somma le metriche che contano per quel ruolo:

| Ruolo | Metriche |
|---|---|
| top | golddiffat15, csdiffat15 |
| jng | kp, golddiffat15, kda |
| mid | dpm, kp, kda, golddiffat15, csdiffat15 |
| adc | golddiffat15, csdiffat15, dpm, kda |
| sup | vspm, kp |

Punteggio > +0,10 è etichettato **CLUTCH**, < −0,10 **CHOKE**, in mezzo neutro.

### 3. Power ranking finale

Il clutch della squadra è la somma dei cinque titolari; ogni punto vale **25
punti di Elo**:

```
Elo finale = Elo base + 25 · (somma clutch dei titolari)
```

### 4. Simulazione

- **Swiss stage**: cinque round, Bo1 nei primi due e Bo3 dal terzo (i 3-0 e gli
  0-2 del terzo round si giocano in Bo3, così come i round 4 e 5). Passano le
  otto squadre con tre vittorie.
- **Bracket**: i due 3-0 pescano obbligatoriamente due 3-2, il 3-2 rimasto pesca
  un 3-1, i due 3-1 rimasti si affrontano tra loro. Quarti, semifinali e finale
  al meglio delle cinque.
- La probabilità di vincere una serie è quella Elo elevata al formato: per un
  Bo3 $p^2(3-2p)$, per un Bo5 $p^3(10-15p+6p^2)$.
- Seed fisso (`SEED = 42`) e 10.000 iterazioni: i numeri sono riproducibili.

## Power ranking finale

| # | Team | Elo base | Clutch | Bonus | Elo finale |
|---|---|---|---|---|---|
| 1 | Gen.G | 1918,5 | −1,40 | −35,0 | 1883,5 |
| 2 | Bilibili Gaming | 1822,2 | +0,98 | +24,5 | 1846,7 |
| 3 | T1 | 1818,9 | +0,23 | +5,7 | 1824,5 |
| 4 | Hanwha Life Esports | 1832,0 | −0,34 | −8,5 | 1823,5 |
| 5 | Dplus Kia | 1765,6 | −0,66 | −16,6 | 1749,0 |
| 6 | Anyone's Legend | 1635,8 | +1,83 | +45,7 | 1681,5 |
| 7 | Team Liquid | 1665,3 | −0,09 | −2,2 | 1663,1 |
| 8 | LYON | 1635,6 | 0,00 | 0,0 | 1635,6 |
| 9 | G2 Esports | 1682,6 | −2,15 | −53,7 | 1628,9 |
| 10 | Karmine Corp | 1629,4 | −1,07 | −26,8 | 1602,6 |
| 11 | Invictus Gaming | 1567,0 | −0,52 | −13,0 | 1554,0 |
| 12 | Movistar KOI | 1555,5 | −0,80 | −19,9 | 1535,6 |
| 13 | Top Esports | 1409,2 | −0,64 | −15,9 | 1393,3 |
| 14 | Team Secret Whales | 1417,0 | −2,05 | −51,4 | 1365,7 |
| 15 | LØS | 1342,8 | 0,00 | 0,0 | 1342,8 |
| 16 | CTBC Flying Oyster | 1194,5 | +1,00 | +25,0 | 1219,5 |

## Probabilità simulate (10.000 tornei)

| Team | Top 8 | 3-0 | 3-1 | 3-2 | Campione |
|---|---|---|---|---|---|
| Gen.G | 97,80% | 44,98% | 38,37% | 14,45% | **39,69%** |
| Bilibili Gaming | 95,45% | 36,54% | 39,19% | 19,72% | 22,94% |
| T1 | 94,69% | 36,00% | 39,08% | 19,61% | 16,43% |
| Hanwha Life Esports | 94,68% | 35,13% | 38,99% | 20,56% | 16,13% |
| Dplus Kia | 82,14% | 15,30% | 34,02% | 32,82% | 3,54% |
| Anyone's Legend | 66,38% | 8,24% | 24,37% | 33,77% | 0,58% |
| Team Liquid | 66,26% | 10,11% | 24,86% | 31,29% | 0,30% |
| LYON | 57,86% | 6,91% | 19,86% | 31,09% | 0,17% |
| G2 Esports | 48,05% | 2,82% | 15,14% | 30,09% | 0,10% |
| Karmine Corp | 41,43% | 2,34% | 12,89% | 26,20% | 0,12% |
| Invictus Gaming | 25,41% | 0,79% | 6,39% | 18,23% | 0,00% |
| Movistar KOI | 21,40% | 0,67% | 5,14% | 15,59% | 0,00% |
| Top Esports | 3,85% | 0,08% | 0,77% | 3,00% | 0,00% |
| Team Secret Whales | 2,75% | 0,06% | 0,43% | 2,26% | 0,00% |
| LØS | 1,64% | 0,03% | 0,42% | 1,19% | 0,00% |
| CTBC Flying Oyster | 0,21% | 0,00% | 0,08% | 0,13% | 0,00% |

Le percentuali di 3-0, 3-1 e 3-2 sono condizionate all'essere passati: sommate
danno la probabilità di Top 8.

## Limiti

- **L'Elo non conosce i roster.** Un team che cambia tre giocatori nell'offseason
  mantiene il rating della stagione precedente; il clutch factor corregge solo in
  parte, e solo per chi ha già giocato ai Worlds.
- **Il clutch factor ha poco campione.** Molti giocatori hanno una sola
  apparizione ai Worlds: il confronto con la regular season è rumoroso, ed è per
  questo che la conversione in Elo è solo 25 punti per unità.
- **Lo Swiss è simulato a regole semplificate.** Non ci sono i vincoli di
  accoppiamento per regione e i rematch sono ammessi.
- **Le probabilità Elo ignorano la forma del momento**, il patch e il vantaggio
  di mappa: sono un modello di forza relativa, non una previsione puntuale.

## Possibili estensioni

- Stimare il clutch factor con un modello gerarchico (shrinkage verso la media)
  invece della differenza grezza, per gestire chi ha pochi match.
- Aggiornare i rating con i risultati dei Worlds a mano a mano che il torneo
  procede, e ricalcolare le probabilità a ogni round.
- Inserire il vantaggio di lato blu/rosso, che sui dati di Oracle's Elixir è
  misurabile e vale qualche punto percentuale.
