from classes.job import Job
from utils.enums import Position, Website
from utils.fetch import laborum_fetch
from typing import List
from datetime import datetime

class LaborumSpider:
    def __init__(self):
        self.base_url = 'https://www.laborum.cl/api/avisos/searchV2'
        self.job_base_url = 'https://www.laborum.cl/empleos/'

        self.headers = {
            'Referer': 'https://www.laborum.cl/empleos-busqueda.html?recientes=true',
            'X-Site-Id': 'BMCL',
            'Content-Type': 'application/json'
        }

    def run(self) -> List[Job]:
        all_jobs: List[Job] = []

        for position in Position:
            pages = self.get_pages(position)
            for page in pages:
                jobs = self.get_jobs(position, page)
                all_jobs.extend(jobs)

        return all_jobs

    def get_pages(self, position: Position) -> List[int]:
        body = {'query': position.value, 'pagina': 1}
        data = laborum_fetch(self.base_url, self.headers, body)
        if data is None:
            return []

        total_pages = -(-data["totalSearched"] // data["size"])
        return list(range(1, total_pages + 1))

    def get_jobs(self, position: Position, page: int) -> List[Job]:
        body = {'query': position.value, 'pagina': page}
        data = laborum_fetch(self.base_url, self.headers, body)
        if data is None or "content" not in data:
            return []

        jobs = []
        for c in data["content"]:
            product_url = f"{self.job_base_url}{c['id']}"

            # Manejo seguro de empresa
            empresa = c.get("empresa", {})
            if isinstance(empresa, dict):
                company = empresa.get("nombre", "Sin empresa")
            else:
                company = str(empresa) or "Sin empresa"

            # Crear objeto Job con campos obligatorios
            job = Job(
                title=c.get("titulo", "Sin título"),
                company=company,
                url=product_url,
                published_at=datetime.utcnow(),  # se actualizará en set_laborum_data si corresponde
                position=position,
                website=Website.LABORUM,
            )

            # Enriquecer datos desde el JSON
            job.set_laborum_data(c)
            jobs.append(job)

        return jobs
