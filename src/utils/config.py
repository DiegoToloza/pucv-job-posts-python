from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")


# --- login opcional ---
LINKEDIN_USER = os.getenv("LINKEDIN_USER", "")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")

# --- búsqueda ---
# Si LINKEDIN_KEYWORDS está vacío, el spider usa Position.value (enum)
LINKEDIN_KEYWORDS = os.getenv("LINKEDIN_KEYWORDS", "")

# Lugar: puede ser string ("Chile", "Santiago Metropolitan") o geoId numérico
LINKEDIN_LOCATION = os.getenv("LINKEDIN_LOCATION", "Chile")

# Último N segundos de publicaciones
# 86400 = 24h, 14400 = 4h, 604800 = 7d
LINKEDIN_F_TPR_SECONDS = int(os.getenv("LINKEDIN_F_TPR_SECONDS", "86400"))

# Páginas máximas (25 resultados por página)
LINKEDIN_MAX_PAGES = int(os.getenv("LINKEDIN_MAX_PAGES", "6"))

# --- otros opcionales ---
LINKEDIN_MIN_PUNCTUATION = int(os.getenv("LINKEDIN_MIN_PUNCTUATION", "0"))
EMAIL_SENT = os.getenv("EMAIL_SENT", "")
