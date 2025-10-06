from enum import Enum

class Website(str, Enum):
    LABORUM = "laborum"
    TRABAJANDO = "trabajando"
    TRABAJO_CON_SENTIDO = "trabajoconsentido"
    LINKEDIN = "linkedin"

class Modality(str, Enum):
    REMOTO = "remoto"
    HIBRIDO = "hibrido"
    PRESENCIAL = "presencial"

class Position(str, Enum):
    BACKEND = "backend"
    FRONTEND = "frontend"
    FULLSTACK = "fullstack"
    DEVOPS = "devops"
    QA = "qa"
    DATA = "data"
    MOBILE = "mobile"
    PRODUCT_MANAGER = "product_manager"
    DESIGNER = "designer"

class JobType(str, Enum):
    FULLTIME = "full-time"
    PARTTIME = "part-time"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
