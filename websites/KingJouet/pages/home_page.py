# websites/KingJouet/pages/home_page.py
from websites.common.base_page import BasePage
from utils.logger import get_logger
from utils.helpers import wait_random_time
from websites.KingJouet.config import BASE_URL, CART_URL, SELECTORS, TIMEOUTS

class HomePage(BasePage):
    """
    Page d'accueil du site King Jouet.
    Permet de gérer les interactions de base comme accepter les cookies,
    fermer les popups et naviguer dans le menu principal.
    """
    
    def __init__(self, page):
        """
        Initialise la page d'accueil.
        
        Args:
            page: L'instance de Page Playwright
        """
        super().__init__(page, BASE_URL)
        self.logger = get_logger(self.__class__.__name__)
    
    def navigate(self):
        """
        Accède à la page d'accueil et gère les popups initiaux.
        
        Returns:
            self: Pour permettre le chaînage des méthodes
        """
        self.logger.info(f"Navigation vers la page d'accueil: {BASE_URL}")
        super().navigate(BASE_URL)
        self.handle_cookie_consent()
        self.close_popups()
        return self
    
    def handle_cookie_consent(self):
        """
        Accepte la bannière de consentement des cookies si elle est présente.
        
        Returns:
            bool: True si la bannière a été acceptée, False sinon
        """
        self.logger.info("Vérification de la présence de la bannière de cookies")
        
        # Vérifie si le bouton d'acceptation des cookies est présent
        if self.is_visible(SELECTORS["cookie_accept_button"], timeout=5000):
            self.logger.info("Bannière de cookies détectée, acceptation...")
            self.click(SELECTORS["cookie_accept_button"])
            wait_random_time(1.0, 2.0)  # Attendre que la bannière disparaisse
            return True
        else:
            self.logger.info("Pas de bannière de cookies détectée")
            return False
    
    def close_popups(self):
        """
        Ferme toutes les popups qui pourraient apparaître lors de la navigation.
        
        Returns:
            int: Nombre de popups fermées
        """
        self.logger.info("Vérification des popups")
        count = 0
        
        # Vérifie si un bouton de fermeture de popup est présent
        if self.is_visible(SELECTORS["popup_close_button"], timeout=5000):
            self.logger.info("Popup détectée, fermeture...")
            self.click(SELECTORS["popup_close_button"])
            wait_random_time(0.5, 1.5)
            count += 1
        
        return count
    
    def search_product(self, keyword):
        """
        Effectue une recherche de produit.
        
        Args:
            keyword: Mot-clé à rechercher
        
        Returns:
            SearchPage: Instance de la page de résultats de recherche
        """
        self.logger.info(f"Recherche de produit avec le mot-clé: {keyword}")
        
        # S'assurer que le champ de recherche est visible
        self.wait_for_selector(SELECTORS["search_input"])
        
        # Remplir le champ de recherche
        self.fill(SELECTORS["search_input"], keyword)
        wait_random_time(0.5, 1.0)
        
        # Cliquer sur le bouton de recherche
        self.click(SELECTORS["search_button"])
        
        # Attendre que la navigation soit terminée
        self.wait_for_navigation(timeout=TIMEOUTS["search_results"])
        
        # Importer ici pour éviter les imports circulaires
        from websites.KingJouet.pages.search_page import SearchPage
        return SearchPage(self.page)
    
    def go_to_login(self):
        """
        Navigue vers la page de connexion.
        
        Returns:
            LoginPage: Instance de la page de connexion
        """
        self.logger.info("Navigation vers la page de connexion")
        self.click(SELECTORS["account-button"])
        
        # Attendre que la navigation soit terminée
        self.wait_for_navigation()
        
        # Importer ici pour éviter les imports circulaires
        from websites.KingJouet.pages.login_page import LoginPage
        return LoginPage(self.page)
    
    def go_to_cart(self):
        """
        Navigue vers le panier.
        
        Returns:
            CartPage: Instance de la page du panier
        """
        self.logger.info("Navigation vers le panier")
        # Naviguer directement vers l'URL du panier pour éviter les problèmes de click
        super().navigate(CART_URL)
        
        # Importer ici pour éviter les imports circulaires
        from websites.KingJouet.pages.cart_page import CartPage
        return CartPage(self.page)
    
    def is_logged_in(self):
        """
        Vérifie si l'utilisateur est connecté.
        
        Returns:
            bool: True si l'utilisateur est connecté, False sinon
        """
        # On pourrait vérifier un élément spécifique qui n'apparaît que lorsqu'on est connecté
        # Par exemple, vérifier si le texte "Mon compte" est visible
        self.logger.info("Vérification du statut de connexion")
        # Cette implémentation nécessiterait de connaître précisément le sélecteur pour un utilisateur connecté
        # return self.is_visible("selector_for_logged_in_user")
        
        # Pour l'instant, retournons False par défaut
        return False