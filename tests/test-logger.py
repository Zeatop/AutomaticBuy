# test_logger.py
from utils.logger import setup_logger, get_logger

# Configuration du logger
setup_logger()
logger = get_logger(__name__)

def main():
    logger.info("Test de journalisation - Info")
    logger.warning("Test de journalisation - Warning")
    
    # Simuler une erreur pour tester Sentry
    try:
        1 / 0  # Division par zéro pour générer une erreur
    except Exception as e:
        logger.error(f"Une erreur s'est produite: {str(e)}", exc_info=True)
        
    # Test de journalisation avec des données structurées
    user_data = {
        "username": "test_user",
        "action": "login_attempt",
        "status": "success"
    }
    logger.info(f"Action utilisateur: {user_data}")

if __name__ == "__main__":
    main()