from datetime import datetime
from typing import Optional
from bs4 import BeautifulSoup
from utils.enums import Position, Website, Modality, JobType

class Job:
    def __init__(
        self,
        title: str,
        company: str,
        url: str,
        published_at: datetime,
        position: Position,
        website: Website,
        modality: Optional[Modality] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
        salary: Optional[str] = None,
        type_: Optional[JobType] = None,
        remote: Optional[bool] = None,
    ):
        self.title = title
        self.company = company
        self.url = url
        self.published_at = published_at
        self.position = position
        self.website = website
        self.modality = modality
        self.location = location
        self.description = description
        self.salary = salary
        self.type_ = type_
        self.remote = remote

    def to_dict(self):
        return self.__dict__


    def set_practice(self):
        if not self.title:
            return

        normalized = (
            self.title.lower()
            .replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
        )

        words = normalized.split()
        self.isPractice = any(word in {"practica", "practicas", "practicante"} for word in words)


    def set_laborum_data(self, data: dict):
        self.title = data.get("titulo")
        self.company = data.get("empresa")
        self.location = data.get("localizacion")
        self.description = data.get("detalle")

        d, m, y = data.get("fechaPublicacion", "01-01-2000").split("-")
        self.published_at = datetime.strptime(f"{y}-{m}-{d}", "%Y-%m-%d")

        if data.get("tipoTrabajo") == "Full-time":
            self.type_ = JobType.FULLTIME
        else:
            self.type_ = JobType.PARTTIME

        match data.get("modalidadTrabajo"):
            case "Presencial":
                self.modality = Modality.PRESENCIAL
            case "Híbrido":
                self.modality = Modality.HIBRIDO
            case "Remoto":
                self.modality = Modality.REMOTO

        self.set_practice()


    def set_trabajando_data(self, data: dict):
        self.title = data.get("nombreCargo")
        self.company = data.get("nombreEmpresaFantasia")
        self.location = data.get("ubicacion", {}).get("direccion")
        self.description = f"{data.get('descripcionOferta')}\n{data.get('requisitosMinimos')}"

        self.published_at = datetime.strptime(data.get("fechaPublicacionFormatoIngles", "2000-01-01"), "%Y-%m-%d")

        if data.get("nombreJornada") == "Part Time":
            self.type_ = JobType.PARTTIME
        else:
            self.type_ = JobType.FULLTIME

        jornada = data.get("nombreJornada", "")
        if jornada == "Jornada Completa":
            self.modality = Modality.PRESENCIAL
        elif jornada == "Mixta (Teletrabajo + Presencial)":
            self.modality = Modality.HIBRIDO
        elif jornada == "Teletrabajo":
            self.modality = Modality.REMOTO
        else:
            self.modality = Modality.PRESENCIAL

        self.set_practice()


    def set_trabajo_con_sentido_data(self, data: dict):
        self.title = data.get("title")
        self.company = data.get("organization", {}).get("name")
        self.location = data.get("city")
        self.description = data.get("description")

        self.published_at = datetime.strptime(data.get("moderatedAt", "").split("T")[0], "%Y-%m-%d")

        if data.get("workingDay") == "Completa":
            self.type_ = JobType.FULLTIME
        else:
            self.type_ = JobType.PARTTIME

        match data.get("workingMode"):
            case "Presencial":
                self.modality = Modality.PRESENCIAL
            case "Semi-presencial":
                self.modality = Modality.HIBRIDO
            case "Remoto":
                self.modality = Modality.REMOTO

        self.set_practice()


    def set_linkedin_html(self, html: str, date: datetime, modality: Modality):
        self.published_at = date
        self.modality = modality

        soup = BeautifulSoup(html, "html.parser")

        # Título, empresa, ubicación
        title_el = soup.select_one(".top-card-layout__title")
        self.title = title_el.text.strip() if title_el else None

        org = soup.select_one("a.topcard__org-name-link, .topcard__org-name-link")
        self.company = org.text.strip() if org else None

        loc = soup.select_one(".topcard__flavor.topcard__flavor--bullet")
        self.location = loc.text.strip() if loc else None

        
        items = soup.select(".description__job-criteria-text.description__job-criteria-text--criteria")
        if len(items) > 1:
            type_text = items[1].get_text(strip=True)
            self.type_ = JobType.PARTTIME if type_text in {"Media jornada", "Voluntario"} else JobType.FULLTIME

        # Mantener HTML en la descripción 
        desc_tag = soup.select_one(".description__text--rich .show-more-less-html__markup")
        self.description = desc_tag.decode_contents() if desc_tag else None

        self.set_practice()


