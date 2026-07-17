"""
Builds a labeled AI-vs-human eval dataset. Not itself under test coverage
(it's a data-prep tool, not production code) — spot-check its output manually.

Takes a JSONL of real, known-human posts (label="human", already sourced —
see eval/data/human_seed.jsonl for the current seed set and its provenance)
and generates one matched AI-written counterpart per human post by prompting
Claude to write in the same subreddit/topic/length, so the AI examples aren't
trivially distinguishable by topic alone. Writes the combined, shuffled
dataset to an output JSONL with a real `label` field on every record.

Usage:
    python eval/build_dataset.py \
        --human-seed eval/data/human_seed.jsonl \
        --out eval/data/sample_labeled_posts.jsonl
"""
import argparse
import json
import os
import random
import sys

import anthropic
from dotenv import load_dotenv

MODEL = "claude-sonnet-5"

GENERATION_SYSTEM_PROMPT = """You are helping build an evaluation dataset for a Reddit AI-text detector by \
writing example AI-generated posts. Given a real Reddit post's subreddit and approximate length, write a \
NEW, DIFFERENT post in the same subreddit's genre and length range. Do not imitate or paraphrase the \
specific story you're shown — invent your own scenario in the same genre. Write it the way someone would \
actually post it: first person, casual Reddit tone, no meta-commentary, no disclaimers, no markdown \
headers. Return only the post text itself, nothing else."""


def load_jsonl(path):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def generate_ai_counterpart(client: anthropic.Anthropic, human_record: dict) -> str:
    word_count = len((human_record.get("title", "") + " " + human_record.get("selftext", "")).split())
    prompt = (
        f"Subreddit: r/{human_record.get('subreddit', 'AITAH')}\n"
        f"Target length: approximately {word_count} words\n\n"
        "Write a new post in this subreddit's style, in the target length range."
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=1200,
        system=GENERATION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    text_block = next((b.text for b in response.content if b.type == "text"), "")
    return text_block.strip()


def build(human_seed_path: str, out_path: str, seed: int = 42):
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY is not set — cannot generate AI counterparts.")
        sys.exit(1)
    client = anthropic.Anthropic(api_key=api_key)

    human_records = load_jsonl(human_seed_path)
    print(f"Loaded {len(human_records)} human seed records from {human_seed_path}")

    combined = []
    for i, human in enumerate(human_records):
        combined.append(human)
        print(f"[{i + 1}/{len(human_records)}] generating AI counterpart for {human['id']}...")
        ai_text = generate_ai_counterpart(client, human)
        combined.append({
            "id": human["id"].replace("human_", "ai_"),
            "title": "",
            "selftext": ai_text,
            "subreddit": human.get("subreddit", "AITAH"),
            "label": "ai",
            "source": f"claude_generated:{MODEL}",
            "notes": [],
            "matched_human_id": human["id"],
        })

    random.Random(seed).shuffle(combined)

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for r in combined:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    n_human = sum(1 for r in combined if r["label"] == "human")
    n_ai = sum(1 for r in combined if r["label"] == "ai")
    print(f"Wrote {len(combined)} records ({n_human} human, {n_ai} ai) to {out_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--human-seed", default="eval/data/human_seed.jsonl")
    parser.add_argument("--out", default="eval/data/labeled_posts.jsonl")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    build(args.human_seed, args.out, args.seed)


if __name__ == "__main__":
    main()
