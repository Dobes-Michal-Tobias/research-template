# Principles — how projects built from this template work

This file is intentionally **not tracked by normal git workflow**
(`principles.md` is in `.gitignore`) — it's a personal standard, not
project content. It shipped once into this template via `git add -f`;
future edits to it won't show up in `git status`/`git add .` unless you
force-add again. Treat it as a living cheat-sheet you read, not something
you commit changes to per-project.

## Structure (Cookiecutter Data Science, trimmed)

```
data/           raw/ interim/ processed/ external/ — gitignored, never committed
notebooks/      orchestration only — no logic lives here
src/            core reusable code: config.py, viz.py, io_utils.py
modules/        optional, domain-specific code — cherry-pick per project
models/         trained model artifacts — gitignored
reports/figures/  saved plots — gitignored
scripts/        one-off setup scripts (venv, kernel)
```

## Notebook = orchestrator, src/modules = logic

Notebooks call functions defined in `src/`/`modules/` and display results.
No pandas transformations, model definitions, or plotting internals
directly in notebook cells — that all belongs in a `.py` file so it's
reusable, testable, and diffable. A notebook cell should mostly look like:

```python
from src.viz import plot_barplot
ax = plot_barplot(df, x="category", y="score")
```

## Visualization

- Default library: **seaborn** (+ matplotlib), one shared style set via
  `src.viz.set_style()`, called once per notebook.
- All plotting functions live in `src/viz.py` (or a project-specific
  submodule for a large project). Don't inline `plt.plot(...)` calls in
  notebooks.
- Leave room for other viz needs without forcing them into `viz.py`
  unconditionally: interactive libraries (plotly/bokeh) or graph drawing
  (`modules/network_viz`) get their own functions/files, but should still
  reuse the same color palette (`src.viz.PALETTE`) so the project's figures
  look like one consistent set.
- Save figures via `src.viz.save_fig()` into `reports/figures/`, don't
  scatter `plt.savefig()` calls with ad-hoc paths.

## Code style

Pythonic, reusable, clean:
- functions over copy-pasted cells; classes when there's real shared state
  (see `modules/ml_model/model.py` for the OOP pattern used for models)
- type hints on public functions
- no premature abstraction — three similar lines beat a speculative helper
- comments only for non-obvious *why*, not *what*

## Long-running loops: write incrementally, show progress

Any loop that takes more than a few seconds (training, API calls, batch
processing) must:
1. show a progress bar — `src.io_utils.iter_progress()` (wraps `tqdm`)
2. append each result to its output CSV as it's produced —
   `src.io_utils.append_row_csv()` — so a crash/interrupt doesn't lose
   completed work
3. support resuming — check `src.io_utils.already_done_ids()` before
   redoing work already present in the output file

See `modules/llm_client/llm_client.py::complete_batch` and
`modules/ml_model/train_loop.py` for the pattern.

## ML model evaluation

Every trained classifier gets logged with, at minimum:
**F1, precision, recall, AUPRC** (`modules/ml_model/metrics.py`). Binary by
default; for multiclass use `average="macro"` and
`multiclass_average_precision()`. Always follow up training with a results
plot (`modules/ml_model/train_loop.py::plot_results`) — a metrics table
alone isn't enough, compare runs visually.

## Data & secrets

- `data/`, `models/`, `reports/figures/` are gitignored — never commit
  research data or trained weights. `.gitkeep` files keep the empty
  directory structure trackable.
- Secrets (API keys) go in `.env` (gitignored), loaded via
  `src/config.py`'s `load_dotenv()`. Commit `.env.example` with dummy
  values instead.

## Environment

- Plain `venv` + `requirements.txt` (no poetry/conda) — keep it simple and
  identical across projects.
- Run `scripts/setup_env.ps1` (Windows) or `scripts/setup_env.sh`
  (mac/Linux) once per project: creates `.venv`, installs requirements,
  registers a Jupyter kernel **named after the project folder** (not the
  generic "Python 3") so the right environment is obvious in VS Code /
  Jupyter's kernel picker.

## Modules — pulling only what a project needs

`modules/` holds domain-specific code that not every project needs
(`ml_model`, `llm_client`, `network_viz`, ...). Rather than bloating every
new project with unused code, cherry-pick via sparse-checkout:

```bash
git clone --no-checkout https://github.com/<you>/research-template.git tmp
cd tmp && git sparse-checkout init --cone && git sparse-checkout set modules/ml_model
git checkout
# copy modules/ml_model/* into your new project's src/
```

Add a new `modules/<name>/` + its own `README.md` whenever a pattern
repeats across ≥2 projects — that's the signal it belongs in the template
instead of being reprompted/copy-pasted each time.
