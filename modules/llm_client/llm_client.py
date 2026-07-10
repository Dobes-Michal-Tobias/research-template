"""Thin wrapper around the Groq API for LLM calls.

Requires `pip install groq` (uncomment in requirements.txt) and a
GROQ_API_KEY in .env (see .env.example).
"""

import os
import time
from pathlib import Path
from typing import Sequence

from groq import Groq

from src.io_utils import already_done_ids, append_row_csv, iter_progress


class GroqClient:
    def __init__(
        self,
        model: str = "llama-3.3-70b-versatile",
        api_key_env: str = "GROQ_API_KEY",
        temperature: float = 0.0,
        max_retries: int = 3,
    ):
        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise RuntimeError(f"{api_key_env} not set — copy .env.example to .env and fill it in.")
        self.client = Groq(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries

    def complete(self, prompt: str, system: str | None = None) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                )
                return response.choices[0].message.content
            except Exception as e:  # rate limits / transient API errors
                last_error = e
                time.sleep(2**attempt)
        raise last_error

    def complete_batch(
        self,
        prompts: dict[str, str],
        out_csv: Path,
        system: str | None = None,
    ) -> None:
        """prompts: {id: prompt_text}. Writes each result to out_csv as it
        arrives and skips ids already present, so an interrupted batch job
        can just be re-run.
        """
        done = already_done_ids(out_csv, id_column="id")
        pending = {pid: p for pid, p in prompts.items() if pid not in done}

        for prompt_id in iter_progress(pending, desc="LLM calls"):
            response = self.complete(pending[prompt_id], system=system)
            append_row_csv(out_csv, {"id": prompt_id, "response": response})
