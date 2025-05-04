# websites/KingJouet/pages/search_page.py
from websites.common.base_page import BasePage
from utils.logger import get_logger
from utils.helpers import wait_random_time, parse_price, clean_text
from websites.KingJouet.config import SELECTORS, TIMEOUTS

class SearchPage(BasePage):
    """
    Page de résultats de recherche du site King Jouet.
    Permet de parcourir les résultats, filtrer et accéder aux produits.
    """
    
    def __init__(self, page):
        """
        Initialise la page de résultats de recherche.
        
        Args:
            page: L'instance de Page Playwright
        """
        # Pas besoin d'URL spécifique car on y accède via la recherche
        super().__init__(page)
        self.logger = get_logger(self.__class__.__name__)
    
    def get_results_count(self):
        """
        Récupère le nombre de résultats trouvés.
        
        Returns:
            int: Nombre de résultats, 0 si aucun résultat ou erreur
        """
        try:
            # On suppose qu'il y a un élément qui contient le nombre de résultats
            # À adapter selon la structure réelle du site
            results_selector = ".ais-Stats-text"  # À vérifier
            if self.is_visible(results_selector):
                text = self.get_text(results_selector)
                # Extraire le nombre de la chaîne (par exemple "123 résultats trouvés")
                import re
                match = re.search(r'(\d+)', text)
                if match:
                    return int(match.group(1))
            return 0
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération du nombre de résultats: {str(e)}")
            return 0
    
    def get_product_items(self):
        """
        Récupère tous les éléments de produit dans les résultats de recherche.
        
        Returns:
            list: Liste des éléments de produit, liste vide en cas d'erreur
        """
        try:
            # On attend que les produits soient chargés
            self.wait_for_selector(SELECTORS["product_items"], timeout=TIMEOUTS["search_results"])
            
            # Sélectionner tous les éléments de produit
            product_selector = ".product" # ou le sélecteur approprié
            return self.page.query_selector_all(product_selector)
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des éléments de produit: {str(e)}")
            return []
    
    def get_products_info(self, limit=10):
        """
        Extrait les informations des produits à partir des résultats de recherche.
        
        Args:
            limit: Nombre maximum de produits à extraire
        
        Returns:
            list: Liste de dictionnaires contenant les informations des produits
        """
        products = []
        product_elements = self.get_product_items()
        
        for i, element in enumerate(product_elements[:limit]):
            try:
                # Sélectionner les éléments dans le contexte de ce produit
                name_element = element.query_selector(SELECTORS["product_name"])
                price_euros_element = element.query_selector(SELECTORS["product_price_euros"])
                price_cents_element = element.query_selector(SELECTORS["product_price_cents"])
                availability_element = element.query_selector(SELECTORS["product_availability"])
                
                # Extraire les informations
                name = clean_text(name_element.text_content()) if name_element else "Nom inconnu"
                
                # Extraire et formater le prix
                price_text = ""
                if price_euros_element:
                    price_text += price_euros_element.text_content() or ""
                if price_cents_element:
                    price_text += "," + (price_cents_element.text_content() or "0")
                
                try:
                    price = parse_price(price_text)
                except ValueError:
                    price = 0.0
                
                # Vérifier la disponibilité
                availability = "En stock" if availability_element else "Non disponible"
                
                # URL du produit
                product_url = element.query_selector("a")
                url = product_url.get_attribute("href") if product_url else None
                
                # Ajouter les informations du produit à la liste
                products.append({
                    "name": name,
                    "price": price,
                    "availability": availability,
                    "url": url
                })
                
            except Exception as e:
                self.logger.warning(f"Erreur lors de l'extraction des informations du produit {i}: {str(e)}")
        
        return products
 
    def open_product(self, index=0):
        """
        Ouvre un produit à partir des résultats de recherche.
        
        Args:
            index: Index du produit à ouvrir (0 pour le premier)
        
        Returns:
            ProductPage: Instance de la page du produit
        """
        self.logger.info(f"Ouverture du produit à l'index: {index}")
        
        try:
            # Récupérer tous les éléments de produit
            product_elements = self.get_product_items()
            
            if index >= len(product_elements):
                self.logger.error(f"Index de produit {index} hors limites (max: {len(product_elements) - 1})")
                raise IndexError(f"Index de produit {index} hors limites")
            
            # Trouver le lien du produit
            product_link = product_elements[index].query_selector("a")
            if not product_link:
                raise Exception("Lien du produit non trouvé")
            
            # Cliquer sur le lien du produit
            product_link.click()
            
            # Attendre que la page du produit soit chargée
            self.wait_for_navigation(timeout=TIMEOUTS["page_load"])
            
            # Importer ici pour éviter les imports circulaires
            from websites.KingJouet.pages.product_page import ProductPage
            return ProductPage(self.page)
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ouverture du produit: {str(e)}")
            # Si une erreur se produit, prendre une capture d'écran
            self.take_screenshot(f"open_product_error_{index}")
            # Réessayer avec le premier produit si l'index n'est pas 0
            if index != 0:
                self.logger.info("Tentative d'ouverture du premier produit à la place")
                return self.open_product(0)
            else:
                raise