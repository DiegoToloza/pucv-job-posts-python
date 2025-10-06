from __future__ import annotations

import os
import csv
from datetime import datetime
from typing import List, Dict, Any
from enum import Enum

from spiders.api.linkedin import LinkedInSpider
from spiders.api.laborum import LaborumSpider
from spiders.api.trabajando import TrabajandoSpider
from spiders.api.trabajoconsentido import TrabajoConSentidoSpider

SPIDER_REGISTRY = {
    "linkedin": LinkedInSpider,
    "laborum": LaborumSpider,
    "trabajando": TrabajandoSpider,
    "trabajoconsentido": TrabajoConSentidoSpider,
}

CSV_FIELDS = [
    "title",
    "company",
    "location",
    "position",
    "website",
    "type_",
    "modality",
    "salary",
    "remote",
    "isPractice",
    "published_at",
    "url",
    "description",
]

def to_scalar(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, Enum):
        return v.value
    if isinstance(v, datetime):
        # ISO 8601; evita problemas de comas/separadores en CSV
        return v.isoformat(timespec="seconds")
    return str(v)

def job_to_row(job) -> Dict[str, str]:
    d: Dict[str, Any] = job.to_dict() if hasattr(job, "to_dict") else job.__dict__
    row = {}
    for f in CSV_FIELDS:
        row[f] = to_scalar(d.get(f))
    return row

def run_spider(name: str) -> List:
    cls = SPIDER_REGISTRY[name]
    spider = cls()
    return spider.run() or []

def main():
    # SPIDERS=linkedin,laborum,trabajando,trabajoconsentido
    spiders_env = os.getenv("SPIDERS", "linkedin,laborum,trabajando,trabajoconsentido")
    spider_names = [s.strip().lower() for s in spiders_env.split(",") if s.strip()]
    csv_path = os.getenv("CSV_PATH", "jobs_export.csv")
    dedup = os.getenv("DEDUP", "1").lower() in ("1", "true", "yes")

    all_jobs: List = []
    for name in spider_names:
        if name not in SPIDER_REGISTRY:
            print(f"Skip '{name}': no registrado")
            continue
        try:
            jobs = run_spider(name)
            print(f"{name}: {len(jobs)} ofertas")
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"{name}: error -> {e}")

    if dedup:
        uniq: Dict[str, Any] = {}
        for j in all_jobs:
            key = getattr(j, "url", None) or (hasattr(j, "to_dict") and j.to_dict().get("url"))
            if key:
                uniq[key] = j
        all_jobs = list(uniq.values())

    rows = [job_to_row(j) for j in all_jobs]

    os.makedirs(os.path.dirname(csv_path) or ".", exist_ok=True)
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"CSV: {csv_path} ({len(rows)} filas)")

if __name__ == "__main__":
    main()
