# config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Chemins de base
BASE_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

# Créer les répertoires s'ils n'existent pas
for directory in [DATA_DIR, LOGS_DIR, SCREENSHOTS_DIR]:
    directory.mkdir(exist_ok=True)

# Paramètres généraux
DEFAULT_TIMEOUT = 30000  # 30 secondes en millisecondes
DEFAULT_WAIT_TIME = 5000  # 5 secondes en millisecondes
RETRY_COUNT = 3  # Nombre d'essais en cas d'échec
HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"  # Mode sans interface graphique

# Configuration des navigateurs
BROWSER_TYPE = os.getenv("BROWSER_TYPE", "chromium")  # chromium, firefox, webkit
USER_DATA_DIR = BASE_DIR / "browser_data"

# URLs de base des sites (à personnaliser selon vos besoins)
WEBSITES = {
    "site1": {
        "base_url": os.getenv("SITE1_BASE_URL", "https://example1.com"),
        "login_url": os.getenv("SITE1_LOGIN_URL", "https://example1.com/login"),
        "search_url": os.getenv("SITE1_SEARCH_URL", "https://example1.com/search"),
        "cart_url": os.getenv("SITE1_CART_URL", "https://example1.com/cart"),
        "checkout_url": os.getenv("SITE1_CHECKOUT_URL", "https://example1.com/checkout"),
    },
    "site2": {
        "base_url": os.getenv("SITE2_BASE_URL", "https://example2.com"),
        "login_url": os.getenv("SITE2_LOGIN_URL", "https://example2.com/login"),
        "search_url": os.getenv("SITE2_SEARCH_URL", "https://example2.com/search"),
        "cart_url": os.getenv("SITE2_CART_URL", "https://example2.com/cart"),
        "checkout_url": os.getenv("SITE2_CHECKOUT_URL", "https://example2.com/checkout"),
    }
}

# Paramètres d'exécution
RUN_MODE = os.getenv("RUN_MODE", "sequential")  # sequential, parallel
MAX_PARALLEL_RUNS = int(os.getenv("MAX_PARALLEL_RUNS", "2"))

# Paramètres de notification
NOTIFICATION_ENABLED = os.getenv("NOTIFICATION_ENABLED", "False").lower() == "true"
NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "")
NOTIFICATION_SMS = os.getenv("NOTIFICATION_SMS", "")

# Paramètres de journalisation
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "automation.log"