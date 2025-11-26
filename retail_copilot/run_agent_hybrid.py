import json
import click
from agent.graph_hybrid import RetailAgent


@click.command()
@click.option("--batch", required=True, type=str, help="Input JSONL batch file")
@click.option("--out", required=True, type=str, help="Output JSONL file path")
def run(batch: str, out: str):
    with open(batch, "r", encoding="utf-8") as f:
        items = [json.loads(line) for line in f if line.strip()]

    agent = RetailAgent(db_path="data/northwind.sqlite", docs_path="docs")

    outputs = []
    for it in items:
        result = agent.run_one(it)
        outputs.append(result)

    # write outputs to JSONL
    with open(out, "w", encoding="utf-8") as f:
        for r in outputs:
            f.write(json.dumps(r) + "\n")

    print(f"Wrote {len(outputs)} outputs to {out}")


if __name__ == "__main__":
    run()
