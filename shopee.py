import time
import hashlib
import json
import requests
import re

class Shopee():

    def __init__(self, app_id, secret):
        self.secret = secret
        self.app_id = app_id
        # Url da api
        self.api_url = "https://open-api.affiliate.shopee.com.br/graphql"

    # Verifica se a url é encurtada
    def is_short_url(self, url):
        return bool(re.match(r"https://s\.shopee\.com\.br/\w+$", url))

    # Extrai a url original
    def get_link_original(self, url_encurtada):
        response = requests.head(url_encurtada, allow_redirects=True)
        return response.url

    # Extrai o id do produto na url
    def extract_product_id(self, url):
        match = re.search(r'(\d+)\?', url)
        if match:
            return match.group(1)
        match = re.search(r"https://shopee\.com\.br/product/\d+/(\d+)", url)
        if match:
            return match.group(1)
        return None

    # Gera a assinaruta para o uso da api
    def generate_signature(self, app_id: str, secret: str, payload: str, timestamp: int) -> str:
        signature_string = f"{app_id}{timestamp}{payload}{secret}"
        return hashlib.sha256(signature_string.encode('utf-8')).hexdigest()

    # Extrai as informações do produto
    def get_item_details(self, item_id: int) -> dict:
    
        query = f"""
        {{
            productOfferV2(itemId: {item_id}) {{
                nodes {{
                    productName
                    imageUrl
                    price
                    shopName
                    productLink
                    commissionRate
                    priceDiscountRate
                    priceMax
                    priceMin
                    offerLink
                }}
            }}
        }}
        """
        payload = json.dumps({"query": query})
        timestamp = int(time.time())
        signature = self.generate_signature(self.app_id, self.secret, payload, timestamp)

        headers = {
            "Authorization": f"SHA256 Credential={self.app_id}, Timestamp={timestamp}, Signature={signature}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.api_url, headers=headers, data=payload)
            response.raise_for_status()
            data = response.json()
            item = data.get("data", {}).get("productOfferV2", {}).get("nodes", [{}])[0]
            return {
                "productName": item.get("productName"),
                "imageUrl": item.get("imageUrl"),
                "price": item.get("price"),
                "shopName": item.get("shopName"),
                "productLink": item.get("productLink"),
                "commissionRate": item.get("commissionRate"),
                "priceDiscountRate": item.get("priceDiscountRate"),
                "priceMax": item.get("priceMax"),
                "priceMin": item.get("priceMin"),
                "offerLink": item.get("offerLink"),
            }
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar detalhes do produto com id {item_id}: {e}")
            return {}


if __name__ == "__main__":
    app_id = "seu_appid"
    senha = "sua_chave"

    sh=Shopee(app_id=app_id, secret=senha)
    link = "link_do_produto"

    # Verifica se o link é encurtado, se sim, extrai o link completo
    if(sh.is_short_url(link)):
        link = sh.get_link_original(link)
    
    # Extrai o id do produto através do link completo
    item_id = sh.extract_product_id(link)
    
    # Extrair as informações do produto
    item_details = sh.get_item_details(item_id)

    print(json.dumps(item_details, indent=4, ensure_ascii=False))
