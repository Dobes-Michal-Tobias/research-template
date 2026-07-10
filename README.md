# research-template

Personal project template for computational-linguistics / NLP / CompSocSci /
social-data-science research projects. Based on
[Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/),
trimmed down and adapted for solo research work with notebooks + a shared
`src/` package.

Czech version: [README.cs.md](README.cs.md)

## Why this exists

Research projects in this space differ a lot (sometimes an ML classifier,
sometimes LLM API calls, sometimes network analysis), so this template keeps
the **core minimal** (paths, plotting style, incremental-CSV/progress-bar
helpers) and puts domain-specific code in [`modules/`](modules/) that you
cherry-pick per project instead of dragging along unused dependencies.

Full conventions/standards are in `principles.md` — generated locally after
setup (see below), not committed to normal history (see "principles.md" note
below).

## Quickstart

1. Click **"Use this template"** on GitHub (or `git clone` this repo) to
   start a new project.
2. Run the setup script from the project root:
   ```powershell
   .\scripts\setup_env.ps1          # Windows
   ```
   ```bash
   ./scripts/setup_env.sh           # macOS/Linux
   ```
   This creates `.venv`, installs `requirements.txt`, and registers a
   Jupyter kernel named after the project folder.
3. Copy `.env.example` to `.env` if you need API keys (created
   automatically by the setup script if present).
4. Pull in any [`modules/`](modules/) your project actually needs (see
   below) and start from `notebooks/`.

## Structure

```
data/           raw/ interim/ processed/ external/  — gitignored
notebooks/      orchestration notebooks — logic lives in src/, not here
src/            core reusable code (config.py, viz.py, io_utils.py)
modules/        optional domain-specific code, pulled in per project
models/         trained model artifacts — gitignored
reports/figures/  saved plots — gitignored
scripts/        environment setup scripts
```

## Core modules (always included)

- `src/config.py` — project paths (`DATA_RAW`, `MODELS_DIR`, ...), loads
  `.env`, defines `RANDOM_SEED`.
- `src/viz.py` — shared seaborn/matplotlib style (`set_style()`), consistent
  palette, `save_fig()`. Intentionally light on pre-built chart types —
  add plotting functions here as a project actually needs them, instead of
  a huge unused chart library.
- `src/io_utils.py` — `append_row_csv()` (incremental, crash-safe logging),
  `iter_progress()` (tqdm wrapper), `already_done_ids()` (resume long jobs).

## Optional modules (pull in what you need)

| Module | What it's for |
|---|---|
| [`modules/ml_model`](modules/ml_model) | OOP model wrapper (`BaseModel`/`SklearnModel`), training loop with logging, F1/Precision/Recall/AUPRC metrics |
| [`modules/llm_client`](modules/llm_client) | Groq API client with retries + resumable batch calls, `.env.example` |
| [`modules/network_viz`](modules/network_viz) | networkx graph plotting matching the project's color palette |

Each has its own `README.md` with a sparse-checkout command to grab just
that folder, e.g.:

```bash
git clone --no-checkout https://github.com/<you>/research-template.git tmp
cd tmp && git sparse-checkout init --cone && git sparse-checkout set modules/ml_model
git checkout
```

Then copy the files you need into your project's `src/`.

## Conventions (short version)

- Notebooks orchestrate; logic lives in `.py` files.
- All plots go through `src/viz.py`, default seaborn style.
- Long-running loops: progress bar + incremental CSV writes, always.
- Every trained classifier reports F1, Precision, Recall, AUPRC.
- `data/`, `models/`, `reports/figures/` are gitignored; `.env` holds
  secrets and is gitignored too (commit `.env.example` instead).

Full detail and rationale: `principles.md` (present in the repo but
gitignored going forward — see the note at the top of that file).

## License

MIT — see [LICENSE](LICENSE). Change if a given project needs something else.
