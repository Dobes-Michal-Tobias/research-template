# research-template

Osobní šablona pro výzkumné projekty z computational linguistics / NLP /
CompSocSci / social data science. Založeno na
[Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/),
zjednodušené pro sólo výzkumnou práci s notebooky + sdíleným `src/` balíčkem.

English version: [README.md](README.md)

## Proč to existuje

Výzkumné projekty v této oblasti se dost liší (někdy ML klasifikátor,
někdy volání LLM API, někdy síťová analýza), takže tahle šablona drží
**jádro minimální** (cesty, styl grafů, pomocné funkce pro inkrementální
CSV zápis a progress bar) a doménově specifický kód dává do
[`modules/`](modules/), odkud si vezmeš jen to, co daný projekt skutečně
potřebuje, místo tažení nepoužitých závislostí.

Kompletní konvence/standardy jsou v `principles.md` — je v repu, ale
gitignorovaný do budoucna (viz poznámka na začátku toho souboru).

## Rychlý start

1. Na GitHubu klikni na **"Use this template"** (nebo `git clone` tohoto
   repa) a založ nový projekt.
2. Spusť setup skript z rootu projektu:
   ```powershell
   .\scripts\setup_env.ps1          # Windows
   ```
   ```bash
   ./scripts/setup_env.sh           # macOS/Linux
   ```
   Vytvoří `.venv`, nainstaluje `requirements.txt` a zaregistruje Jupyter
   kernel pojmenovaný podle složky projektu.
3. Pokud potřebuješ API klíče, zkopíruj `.env.example` do `.env` (setup
   skript to udělá automaticky, pokud soubor existuje).
4. Stáhni si z [`modules/`](modules/) jen to, co projekt potřebuje (viz
   níže), a začni v `notebooks/`.

## Struktura

```
data/           raw/ interim/ processed/ external/  — gitignored
notebooks/      orchestrace — logika je v src/, ne tady
src/            jádro znovupoužitelného kódu (config.py, viz.py, io_utils.py)
modules/        volitelný doménový kód, per-projekt cherry-pick
models/         natrénované modely — gitignored
reports/figures/  uložené grafy — gitignored
scripts/        skripty pro nastavení prostředí
```

## Základní moduly (vždy součástí)

- `src/config.py` — cesty projektu (`DATA_RAW`, `MODELS_DIR`, ...), načítá
  `.env`, definuje `RANDOM_SEED`.
- `src/viz.py` — sdílený seaborn/matplotlib styl (`set_style()`), jednotná
  paleta, `save_fig()`. Záměrně bez velkého množství předpřipravených
  grafů — funkce sem přidávej, až je projekt reálně potřebuje.
- `src/io_utils.py` — `append_row_csv()` (inkrementální, crash-safe zápis),
  `iter_progress()` (obal nad tqdm), `already_done_ids()` (navázání na
  přerušený běh).

## Volitelné moduly (vezmi si, co potřebuješ)

| Modul | K čemu slouží |
|---|---|
| [`modules/ml_model`](modules/ml_model) | OOP obal nad modely (`BaseModel`/`SklearnModel`), trénovací smyčka s logováním, metriky F1/Precision/Recall/AUPRC |
| [`modules/llm_client`](modules/llm_client) | Klient pro Groq API s retry logikou a navazatelnými dávkovými voláními, `.env.example` |
| [`modules/network_viz`](modules/network_viz) | Vykreslování networkx grafů v barvách projektu |

Každý má vlastní `README.md` s příkazem pro sparse-checkout jen dané
složky, např.:

```bash
git clone --no-checkout https://github.com/<ty>/research-template.git tmp
cd tmp && git sparse-checkout init --cone && git sparse-checkout set modules/ml_model
git checkout
```

Pak zkopíruj potřebné soubory do `src/` svého projektu.

## Konvence (stručně)

- Notebook orchestruje, logika je v `.py` souborech.
- Všechny grafy jdou přes `src/viz.py`, výchozí styl seaborn.
- Dlouhé smyčky: vždy progress bar + inkrementální zápis do CSV.
- Každý natrénovaný klasifikátor reportuje F1, Precision, Recall, AUPRC.
- `data/`, `models/`, `reports/figures/` jsou gitignored; `.env` obsahuje
  tajné klíče a je taky gitignored (commituje se jen `.env.example`).

Plné detaily a zdůvodnění: `principles.md` (je v repu, ale do budoucna
gitignorovaný — viz poznámka na začátku toho souboru).

## Licence

MIT — viz [LICENSE](LICENSE). U konkrétního projektu klidně změň, pokud
potřebuješ jinou.
