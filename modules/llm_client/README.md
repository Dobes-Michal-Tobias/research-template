# module: llm_client

Optional module — copy this folder's contents into `src/` of a project that
calls an LLM API (default: Groq). Keeps API calls, retries and rate-limit
handling out of notebooks.

## Contents

- `llm_client.py` — thin `GroqClient` wrapper: `.complete(prompt)` /
  `.complete_batch(prompts, out_csv)` with incremental CSV logging + resume
  support (via `src/io_utils`), so a long batch job can be interrupted and
  resumed without redoing finished requests or losing partial progress.
- `.env.example` — copy to project root as `.env` and fill in your key.
  `src/config.py` already loads `.env` via `python-dotenv`.

## How to pull just this module

```bash
git clone --no-checkout https://github.com/<you>/research-template.git tmp_template
cd tmp_template
git sparse-checkout init --cone
git sparse-checkout set modules/llm_client
git checkout
# copy modules/llm_client/llm_client.py into your project's src/
# copy modules/llm_client/.env.example into your project root, rename to .env
```

## Usage sketch

```python
from llm_client import GroqClient

client = GroqClient(model="llama-3.3-70b-versatile")
answer = client.complete("Classify the sentiment of: ...")

client.complete_batch(prompts, out_csv=DATA_PROCESSED / "llm_outputs.csv", id_column="prompt_id")
```

Swap to another OpenAI-compatible provider by changing `base_url` /
`api_key_env` in `GroqClient.__init__` — the rest of the interface stays
the same.
