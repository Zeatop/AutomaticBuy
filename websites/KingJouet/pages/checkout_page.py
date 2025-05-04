# websites/KingJouet/pages/checkout_page.py
from websites.common.base_page import BasePage
from utils.logger import get_logger
from utils.helpers import wait_random_time
from websites.KingJouet.config import SELECTORS, TIMEOUTS

class CheckoutPage(BasePage):
    """
    Page de paiement du site King Jouet.
    Permet de finaliser la commande en fournissant les informations de livraison et de paiement.
    """
    
    def __init__(self, page):
        """
        Initialise la page de paiement.
        
        Args:
            page: L'instance de Page Playwright
        """
        super().__init__(page)
        self.logger = get_logger(self.__class__.__name__)
        self.current_step = self._determine_current_step()
    
    def _determine_current_step(self):
        """
        Détermine l'étape actuelle du processus de paiement.
        
        Returns:
            str: Étape actuelle ('identification', 'livraison', 'paiement', 'confirmation')
        """
        # À adapter selon la structure du site
        if "identification" in self.page.url:
            return "identification"
        elif "livraison" in self.page.url:
            return "livraison"
        elif "paiement" in self.page.url:
            return "paiement"
        elif "confirmation" in self.page.url:
            return "confirmation"
        else:
            return "unknown"
    
    def select_delivery_option(self, option_index=0):
        """
        Sélectionne une option de livraison.
        
        Args:
            option_index: Index de l'option à sélectionner (0 pour la première)
        
        Returns:
            bool: True si la sélection a réussi, False sinon
        """
        self.logger.info(f"Sélection de l'option de livraison {option_index}")
        
        try:
            # Vérifier que nous sommes à l'étape de livraison
            if self.current_step != "livraison":
                self.logger.warning(f"Étape actuelle ({self.current_step}) n'est pas 'livraison'")
                return False
            
            # Sélectionner toutes les options de livraison
            delivery_options = self.page.query_selector_all(SELECTORS["delivery_options"])
            
            if option_index >= len(delivery_options):
                self.logger.error(f"Index d'option {option_index} hors limites (max: {len(delivery_options) - 1})")
                return False
            
            # Sélectionner l'option de livraison
            delivery_options[option_index].click()
            wait_random_time(0.5, 1.0)
            
            # Cliquer sur le bouton de confirmation (pour passer à l'étape suivante)
            self.click(SELECTORS["proceed_to_checkout"])
            
            # Attendre que la page suivante soit chargée
            self.wait_for_navigation(timeout=TIMEOUTS["checkout_step"])
            
            # Mettre à jour l'étape actuelle
            self.current_step = self._determine_current_step()
            
            return self.current_step == "paiement"
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sélection de l'option de livraison: {str(e)}")
            self.take_screenshot("select_delivery_option_error")
            return False
    
    def fill_payment_info(self, card_owner, card_number, expiry_date, security_code):
        """
        Remplit les informations de paiement.
        
        Args:
            card_owner: Nom du titulaire de la carte
            card_number: Numéro de la carte
            expiry_date: Date d'expiration (format MM/YY)
            security_code: Code de sécurité (CVV)
        
        Returns:
            bool: True si le remplissage a réussi, False sinon
        """
        self.logger.info(f"Remplissage des informations de paiement pour {card_owner}")
        
        try:
            # Vérifier que nous sommes à l'étape de paiement
            if self.current_step != "paiement":
                self.logger.warning(f"Étape actuelle ({self.current_step}) n'est pas 'paiement'")
                return False
            
            # Remplir les champs de paiement
            self.fill(SELECTORS["card_owner"], card_owner)
            wait_random_time(0.5, 1.0)
            
            # Champs spéciaux pour le numéro de carte, ils sont souvent dans des iframes
            # Note: Une implémentation complète nécessiterait de gérer les iframes, ce qui est plus complexe
            # Pour simplifier, nous allons supposer que les champs sont directement accessibles
            
            self.fill(SELECTORS["card_number"], card_number)
            wait_random_time(0.5, 1.0)
            
            self.fill(SELECTORS["card_expiration"], expiry_date)
            wait_random_time(0.5, 1.0)
            
            self.fill(SELECTORS["card_security_code"], security_code)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors du remplissage des informations de paiement: {str(e)}")
            self.take_screenshot("fill_payment_info_error")
            return False
    
    def place_order(self):
        """
        Finalise la commande en cliquant sur le bouton de commande.
        NOTE: Cette méthode effectue réellement l'achat! À utiliser uniquement pour des tests réels.
        
        Returns:
            bool: True si la commande a été passée, False sinon
        """
        self.logger.info("Finalisation de la commande")
        
        try:
            # Vérifier que nous sommes à l'étape de paiement
            if self.current_step != "paiement":
                self.logger.warning(f"Étape actuelle ({self.current_step}) n'est pas 'paiement'")
                return False
            
            # Cliquer sur le bouton de commande
            self.click(SELECTORS["place_order_button"])
            
            # Attendre que la page de confirmation soit chargée
            self.wait_for_navigation(timeout=TIMEOUTS["checkout_step"])
            
            # Mettre à jour l'étape actuelle
            self.current_step = self._determine_current_step()
            
            # Vérifier si nous sommes sur la page de confirmation
            return self.current_step == "confirmation"
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la finalisation de la commande: {str(e)}")
            self.take_screenshot("place_order_error")
            return False
    
    def is_order_confirmed(self):
        """
        Vérifie si la commande a été confirmée.
        
        Returns:
            bool: True si la commande est confirmée, False sinon
        """
        return self.current_step == "confirmation"
    
    def get_order_number(self):
        """
        Récupère le numéro de commande après confirmation.
        
        Returns:
            str: Numéro de commande, ou chaîne vide si non disponible
        """
        self.logger.info("Récupération du numéro de commande")
        
        try:
            # Vérifier que nous sommes à l'étape de confirmation
            if self.current_step != "confirmation":
                self.logger.warning(f"Étape actuelle ({self.current_step}) n'est pas 'confirmation'")
                return ""
            
            # Sélectionner l'élément contenant le numéro de commande
            # À adapter selon la structure du site
            order_number_selector = ".order-number"  # À vérifier
            
            if self.is_visible(order_number_selector):
                order_number_text = self.get_text(order_number_selector)
                
                # Extraire le numéro de commande du texte (par exemple "Commande n°123456")
                import re
                match = re.search(r'\d+', order_number_text)
                if match:
                    return match.group(0)
            
            return ""
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du numéro de commande: {str(e)}")
            return ""
    
    def go_to_home(self):
        """
        Retourne à la page d'accueil après avoir finalisé ou annulé la commande.
        
        Returns:
            HomePage: Instance de la page d'accueil
        """
        self.logger.info("Retour à la page d'accueil")
        
        try:
            # Cliquer sur le logo pour retourner à l'accueil
            self.click(SELECTORS["logo"])
            self.wait_for_navigation()
            
            # Importer ici pour éviter les imports circulaires
            from websites.KingJouet.pages.home_page import HomePage
            return HomePage(self.page)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du retour à la page d'accueil: {str(e)}")
            # Naviguer directement vers l'URL de la page d'accueil
            from websites.KingJouet.config import BASE_URL
            super().navigate(BASE_URL)
            
            from websites.KingJouet.pages.home_page import HomePage
            return HomePage(self.page)