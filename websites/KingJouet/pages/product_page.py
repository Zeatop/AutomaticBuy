# websites/KingJouet/pages/product_page.py
from websites.common.base_page import BasePage
from utils.logger import get_logger
from utils.helpers import wait_random_time, parse_price, clean_text
from websites.KingJouet.config import SELECTORS, TIMEOUTS

class ProductPage(BasePage):
    """
    Page de produit du site King Jouet.
    Permet de consulter les détails d'un produit et de l'ajouter au panier.
    """
    
    def __init__(self, page):
        """
        Initialise la page de produit.
        
        Args:
            page: L'instance de Page Playwright
        """
        super().__init__(page)
        self.logger = get_logger(self.__class__.__name__)
    
    def get_product_info(self):
        """
        Récupère les informations détaillées du produit.
        
        Returns:
            dict: Informations du produit (nom, prix, disponibilité, etc.)
        """
        self.logger.info("Récupération des informations du produit")
        
        try:
            # Nom du produit
            title = clean_text(self.get_text(SELECTORS["product_title"]))
            
            # Prix du produit
            price_euros = self.get_text(SELECTORS["product_price_detail_euros"])
            price_cents = self.get_text(SELECTORS["product_price_detail_cents"])
            price_text = f"{price_euros},{price_cents}" if price_cents else price_euros
            
            try:
                price = parse_price(price_text)
            except ValueError:
                price = 0.0
            
            # Disponibilité
            is_available = self.is_visible(SELECTORS["add_to_cart_button"]) or self.is_visible(SELECTORS["add_to_cart_preco_button"])
            availability_status = "En stock" if is_available else "Non disponible"
            
            # URL du produit
            product_url = self.page.url
            
            # Récupérer la référence du produit (à adapter selon le site)
            reference_selector = ".reference"  # À vérifier
            reference = clean_text(self.get_text(reference_selector, ""))
            
            return {
                "name": title,
                "price": price,
                "availability": availability_status,
                "url": product_url,
                "reference": reference
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des informations du produit: {str(e)}")
            self.take_screenshot("product_info_error")
            return {
                "name": "Erreur",
                "price": 0.0,
                "availability": "Erreur",
                "url": self.page.url,
                "reference": ""
            }
    
    def add_to_cart(self, quantity=1):
        """
        Ajoute le produit au panier.
        
        Args:
            quantity: Quantité à ajouter (par défaut 1)
        
        Returns:
            bool: True si l'ajout a réussi, False sinon
        """
        self.logger.info(f"Ajout du produit au panier (quantité: {quantity})")
        
        try:
            # Vérifier si le produit est disponible
            if self.is_visible(SELECTORS["add_to_cart_button"]):
                add_button = SELECTORS["add_to_cart_button"]
            elif self.is_visible(SELECTORS["add_to_cart_preco_button"]):
                add_button = SELECTORS["add_to_cart_preco_button"]
            else:
                self.logger.warning("Bouton d'ajout au panier non trouvé, produit probablement non disponible")
                return False
            
            # Si la quantité est supérieure à 1, modifier la quantité (si possible)
            if quantity > 1:
                # Chercher un champ de quantité (à adapter selon le site)
                quantity_input = "#quantity"  # À vérifier
                if self.is_visible(quantity_input):
                    self.fill(quantity_input, str(quantity))
            
            # Cliquer sur le bouton d'ajout au panier
            self.click(add_button)
            
            # Attendre que le produit soit ajouté au panier
            # Cela peut déclencher une popup de confirmation ou une mise à jour du panier
            wait_random_time(1.0, 2.0)
            
            # Vérifier si l'ajout a réussi (à adapter selon le comportement du site)
            # Par exemple, vérifier si une notification de succès est affichée
            success_notification = ".success-message"  # À vérifier
            return self.is_visible(success_notification, timeout=TIMEOUTS["add_to_cart"])
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout au panier: {str(e)}")
            self.take_screenshot("add_to_cart_error")
            return False
    
    def go_to_cart(self):
        """
        Navigue vers le panier après avoir ajouté un produit.
        
        Returns:
            CartPage: Instance de la page du panier
        """
        self.logger.info("Navigation vers le panier")
        
        try:
            # Chercher un bouton "Voir le panier" qui pourrait apparaître après l'ajout
            view_cart_button = ".view-cart-button"  # À vérifier
            
            if self.is_visible(view_cart_button):
                self.click(view_cart_button)
            else:
                # Si pas de bouton spécifique, naviguer directement vers l'URL du panier
                from websites.KingJouet.config import CART_URL
                super().navigate(CART_URL)
            
            # Attendre que la page du panier soit chargée
            self.wait_for_navigation()
            
            # Importer ici pour éviter les imports circulaires
            from websites.KingJouet.pages.cart_page import CartPage
            return CartPage(self.page)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la navigation vers le panier: {str(e)}")
            self.take_screenshot("go_to_cart_error")
            # Malgré l'erreur, essayer de créer une instance de CartPage
            from websites.KingJouet.pages.cart_page import CartPage
            return CartPage(self.page)