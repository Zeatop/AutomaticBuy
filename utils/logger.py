import os
import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from dotenv import load_dotenv

def setup_logger():
    """
    Configure Sentry et le système de journalisation.
    """
    # Chargement des variables d'environnement
    load_dotenv()
    
    # Configuration de base du logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Affichage dans la console
            logging.FileHandler("automation.log")  # Sauvegarde dans un fichier
        ]
    )
    
    # Configuration de Sentry si la DSN est définie
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        # Configurer l'intégration du logging avec Sentry
        sentry_logging = LoggingIntegration(
            level=logging.INFO,        # Niveau minimum capturé par Sentry
            event_level=logging.ERROR  # Niveau pour envoyer des événements à Sentry
        )
        
        # Initialiser Sentry avec la configuration
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[sentry_logging],
            traces_sample_rate=1.0,  # Capturer 100% des traces pour le débogage
            environment=os.getenv("ENVIRONMENT", "development"),
            release=os.getenv("RELEASE", "0.1.0")
        )
        
        # Ajouter les tags via set_tag après l'initialisation
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("application", "automation_achats")
        
        logging.info("Sentry a été configuré avec succès.")
    else:
        logging.warning("SENTRY_DSN n'est pas défini. La journalisation vers Sentry est désactivée.")

def get_logger(name):
    """
    Récupère un logger pour un module spécifique.
    """
    return logging.getLogger(name)