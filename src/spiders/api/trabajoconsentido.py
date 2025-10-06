# spiders/api/trabajoconsentido.py
from datetime import datetime
from typing import List, Optional
from classes.job import Job
from utils.enums import Website, Position
from utils.fetch import trabajo_con_sentido_fetch

class TrabajoConSentidoSpider:
    BASE_URL = "https://api.trabajoconsentido.com/offers"
    OFFER_BASE_URL = "https://api.trabajoconsentido.com/offers/slug"
    JOB_BASE_URL = "https://listado.trabajoconsentido.com/trabajos/"

    def __init__(self):
        self.headers = {}

    # ---------- Public API ----------
    def run(self) -> List[Job]:
        jobs: List[Job] = []
        for position in Position:
            for offer_url in self.get_offer_urls(position):
                job = self.get_job(offer_url, position)
                if job:
                    jobs.append(job)
        return jobs

    def get_offer_urls(self, position: Position) -> List[str]:
        """
        Intenta con tag=posición. Si no hay resultados, cae a sin filtros.
        Devuelve URLs de detalle ya formadas: {OFFER_BASE_URL}/{slug}
        """
        urls = self._fetch_offer_urls(self._list_url(position))
        if urls:
            return urls
        # Fallback sin filtro por si el sitio no reconoce el tag
        return self._fetch_offer_urls(self.BASE_URL)

    def get_job(self, detail_url: str, position: Position) -> Optional[Job]:
        data = trabajo_con_sentido_fetch(detail_url, self.headers)
        if not data:
            return None

        offer = ((data.get("content") or {}).get("offer") or {})
        slug = offer.get("slug")
        if not slug:
            return None

        product_url = f"{self.JOB_BASE_URL}{slug}"
        job = Job(
            title=offer.get("title", ""),
            company=(offer.get("organization") or {}).get("name", ""),
            url=product_url,
            published_at=datetime.utcnow(),  # será sobreescrita por set_trabajo_con_sentido_data
            position=position,
            website=Website.TRABAJO_CON_SENTIDO,
        )
        job.set_trabajo_con_sentido_data(offer)
        return job

    # ---------- Internos ----------
    def _list_url(self, position: Position) -> str:
        return f"{self.BASE_URL}?tags={position.value.replace(' ', ',')}"

    def _fetch_offer_urls(self, page_url: str) -> List[str]:
        data = trabajo_con_sentido_fetch(page_url, self.headers)
        offers = (data or {}).get("content", {}).get("offers", []) or []
        return [f"{self.OFFER_BASE_URL}/{o['slug']}" for o in offers if isinstance(o, dict) and o.get("slug")]
