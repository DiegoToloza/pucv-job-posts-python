from datetime import datetime
from classes.job import Job
from utils.enums import Position, Website
from utils.fetch import trabajando_fetch
from typing import List, Optional

class TrabajandoSpider:
    def __init__(self):
        self.base_url = 'https://www.trabajando.cl/api/searchjob?orden=RANKING'
        self.offer_base_url = 'https://www.trabajando.cl/api/ofertas/'
        self.job_base_url = 'https://www.trabajando.cl/trabajo-empleo/'
        self.headers = {
            'Referer': 'https://www.trabajando.cl/trabajo-empleo'
        }

    def run(self) -> List[Job]:
        all_jobs: List[Job] = []

        for position in Position:
            pages = self.get_pages(position)
            offers = [url for page in pages for url in self.get_offers(page)]
            jobs = [job for url in offers for job in [self.get_job(url, position)] if job is not None]

            all_jobs.extend(jobs)

        return all_jobs

    def get_career_query(self, position: Position) -> str:
    # Como PUBLICISTA y otros no están definidos en tu enum, devolvemos string vacío
        return ''


    def get_pages(self, position: Position) -> List[str]:
        url = f"{self.base_url}&palabraClave={position.value}&{self.get_career_query(position)}"
        data = trabajando_fetch(url, self.headers)
        if data is None:
            return []

        total = data.get("cantidadPaginas", 0)
        return [f"{url}&pagina={i + 1}" for i in range(total)]

    def get_offers(self, page: str) -> List[str]:
        data = trabajando_fetch(page, self.headers)
        if data is None:
            return []

        return [f"{self.offer_base_url}{o['idOferta']}" for o in data.get("ofertas", [])]

    def get_job(self, url: str, position: Position) -> Optional[Job]:
        data = trabajando_fetch(url, self.headers)
        if data is None:
            return None

        encoded_position = position.value.replace(" ", "%20")
        product_url = f"{self.job_base_url}{encoded_position}/trabajo/{data['idOferta']}"

        job = Job(
            title=data.get("nombreCargo", "Sin título"),
            company=data.get("nombreEmpresaFantasia", "Sin empresa"),
            url=product_url,
            published_at=datetime.utcnow(),  # Esto se sobreescribe luego en set_trabajando_data
            position=position,
            website=Website.TRABAJANDO,
        )

        job.set_trabajando_data(data)
        return job
