import requests
import base64
import os
from ..models import models

class WhatsAppService:
    def __init__(self, church: models.Church):
        self.api_url = church.evolution_api_url
        self.api_key = church.evolution_api_key
        self.instance = church.evolution_instance_name
        self.headers = {"apikey": self.api_key, "Content-Type": "application/json"}

    def send_text(self, phone: str, message: str):
        if not self.api_url or not self.instance: return False
        
        endpoint = f"{self.api_url}/message/sendText/{self.instance}"
        payload = {"number": phone, "text": message}
        
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            return response.status_code == 201
        except Exception as e:
            print(f"Erro WhatsApp: {e}")
            return False

    def send_image(self, phone: str, caption: str, image_path: str):
        if not self.api_url or not self.instance: return False

        endpoint = f"{self.api_url}/message/sendMedia/{self.instance}"
        
        with open(image_path, "rb") as f:
            base64_img = base64.b64encode(f.read()).decode('utf-8')

        payload = {
            "number": phone,
            "mediaMessage": {
                "mediatype": "image",
                "caption": caption,
                "media": base64_img
            }
        }

        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            return response.status_code == 201
        except Exception as e:
            print(f"Erro WhatsApp Imagem: {e}")
            return False
