# websites/KingJouet/pages/login_page.py
from websites.common.base_page import BasePage
from utils.logger import get_logger
from utils.helpers import wait_random_time
from websites.KingJouet.config import LOGIN_URL, SELECTORS

class LoginPage(BasePage):
    """
    Page de connexion du site King Jouet.
    Permet de se connecter avec un compte existant.
    """
    
    def __init__(self, page):
        """
        Initialise la page de connexion.
        
        Args:
            page: L'instance de Page Playwright
        """
        super().__init__(page, LOGIN_URL)
        self.logger = get_logger(self.__class__.__name__)
    
    def navigate(self):
        """
        Accède directement à la page de connexion.
        
        Returns:
            self: Pour permettre le chaînage des méthodes
        """
        self.logger.info(f"Navigation directe vers la page de connexion: {LOGIN_URL}")
        super().navigate(LOGIN_URL)
        return self
    
    def login(self, email, password):
        """
        Se connecte avec les identifiants fournis.
        
        Args:
            email: Adresse email du compte
            password: Mot de passe du compte
        
        Returns:
            bool: True si la connexion a réussi, False sinon
        """
        self.logger.info(f"Tentative de connexion avec l'email: {email}")
        
        # Remplir le formulaire de connexion
        self.fill(SELECTORS["email_input"], email)
        wait_random_time(0.5, 1.0)
        self.fill(SELECTORS["password_input"], password)
        wait_random_time(0.5, 1.0)
        
        # Cliquer sur le bouton de connexion
        self.click(SELECTORS["login_button"])
        
        # Attendre la redirection après la connexion
        self.wait_for_navigation()
        
        # Vérifier si la connexion a réussi (par exemple, en vérifiant si un élément spécifique aux utilisateurs connectés est présent)
        # Cela nécessiterait un sélecteur spécifique pour un élément qui n'apparaît que pour les utilisateurs connectés
        # Pour l'instant, nous supposons que si nous ne sommes plus sur la page de connexion, la connexion a réussi
        return "login" not in self.page.url
    
    def is_on_login_page(self):
        """
        Vérifie si nous sommes actuellement sur la page de connexion.
        
        Returns:
            bool: True si nous sommes sur la page de connexion, False sinon
        """
        return "login" in self.page.url

    def go_to_home(self):
        """
        Retourne à la page d'accueil.
        
        Returns:
            HomePage: Instance de la page d'accueil
        """
        self.logger.info("Retour à la page d'accueil")
        self.click(SELECTORS["logo"])
        self.wait_for_navigation()
        
        from websites.KingJouet.pages.home_page import HomePage
        return HomePage(self.page)