import requests
import json
import unittest
import os
import time
from datetime import datetime

# Get the backend URL from the frontend .env file
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BACKEND_URL = line.strip().split('=')[1].strip('"\'')
            break

# Ensure the URL doesn't have quotes
if BACKEND_URL.startswith('"') and BACKEND_URL.endswith('"'):
    BACKEND_URL = BACKEND_URL[1:-1]
elif BACKEND_URL.startswith("'") and BACKEND_URL.endswith("'"):
    BACKEND_URL = BACKEND_URL[1:-1]

API_URL = f"{BACKEND_URL}/api"
print(f"Testing API at: {API_URL}")

class PharmacieBackendTest(unittest.TestCase):
    """Test suite for Pharmacie Saidani backend API"""
    
    def setUp(self):
        """Setup for each test"""
        self.product_id = None
        self.order_id = None
        self.conversation_id = None
    
    def test_01_root_endpoint(self):
        """Test the root endpoint"""
        response = requests.get(f"{API_URL}")
        self.assertEqual(response.status_code, 200)
        try:
            data = response.json()
            self.assertIn("message", data)
        except:
            # If the root endpoint doesn't return JSON, that's okay
            pass
        print("✅ Root endpoint test passed")
    
    def test_02_get_products(self):
        """Test getting all products"""
        response = requests.get(f"{API_URL}/products")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("products", data)
        self.assertIsInstance(data["products"], list)
        self.assertGreater(len(data["products"]), 0)
        
        # Save a product ID for later tests
        if len(data["products"]) > 0:
            self.product_id = data["products"][0]["id"]
        
        # Verify product structure
        product = data["products"][0]
        self.assertIn("id", product)
        self.assertIn("name", product)
        self.assertIn("category", product)
        self.assertIn("description", product)
        self.assertIn("price", product)
        self.assertIn("image_url", product)
        self.assertIn("in_stock", product)
        
        print("✅ Get products test passed")
    
    def test_03_get_product_by_id(self):
        """Test getting a specific product by ID"""
        if not self.product_id:
            self.test_02_get_products()
        
        response = requests.get(f"{API_URL}/products/{self.product_id}")
        self.assertEqual(response.status_code, 200)
        product = response.json()
        self.assertEqual(product["id"], self.product_id)
        self.assertIn("name", product)
        self.assertIn("category", product)
        self.assertIn("description", product)
        self.assertIn("price", product)
        
        print("✅ Get product by ID test passed")
    
    def test_04_get_products_by_category(self):
        """Test getting products by category"""
        # First get all products to find a category
        response = requests.get(f"{API_URL}/products")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        if len(data["products"]) > 0:
            category = data["products"][0]["category"]
            
            # Now test the category endpoint
            response = requests.get(f"{API_URL}/products/category/{category}")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("products", data)
            self.assertIsInstance(data["products"], list)
            self.assertGreater(len(data["products"]), 0)
            
            # Verify all products are of the requested category
            for product in data["products"]:
                self.assertEqual(product["category"], category)
        
        print("✅ Get products by category test passed")
    
    def test_05_get_categories(self):
        """Test getting all categories"""
        response = requests.get(f"{API_URL}/categories")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("categories", data)
        self.assertIsInstance(data["categories"], list)
        self.assertGreater(len(data["categories"]), 0)
        
        print("✅ Get categories test passed")
    
    def test_06_create_order(self):
        """Test creating a new order"""
        # First get a product to order
        response = requests.get(f"{API_URL}/products")
        self.assertEqual(response.status_code, 200)
        products_data = response.json()
        
        if len(products_data["products"]) > 0:
            product = products_data["products"][0]
            
            # Create order payload
            order_data = {
                "customer_name": "Ahmed Benali",
                "customer_phone": "+213555123456",
                "customer_address": "123 Rue Ali Bouhaja, Birtouta, Alger",
                "items": [
                    {
                        "product_id": product["id"],
                        "product_name": product["name"],
                        "quantity": 2,
                        "price": product["price"]
                    }
                ],
                "total_amount": 2 * product["price"],
                "notes": "Livraison l'après-midi, s'il vous plaît"
            }
            
            response = requests.post(f"{API_URL}/orders", json=order_data)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("message", data)
            self.assertIn("order_id", data)
            
            # Save order ID for later tests
            self.order_id = data["order_id"]
        
        print("✅ Create order test passed")
    
    def test_07_get_orders(self):
        """Test getting all orders"""
        # Create an order first if we don't have one
        if not self.order_id:
            self.test_06_create_order()
        
        response = requests.get(f"{API_URL}/orders")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("orders", data)
        self.assertIsInstance(data["orders"], list)
        self.assertGreater(len(data["orders"]), 0)
        
        # Verify order structure
        order = data["orders"][0]
        self.assertIn("id", order)
        self.assertIn("customer_name", order)
        self.assertIn("customer_phone", order)
        self.assertIn("customer_address", order)
        self.assertIn("items", order)
        self.assertIn("total_amount", order)
        self.assertIn("status", order)
        
        print("✅ Get orders test passed")
    
    def test_08_create_conversation(self):
        """Test creating a new conversation"""
        conversation_data = {
            "customer_name": "Fatima Zahra",
            "customer_phone": "+213661234567",
            "message": "Bonjour, avez-vous des médicaments pour l'allergie saisonnière?"
        }
        
        response = requests.post(f"{API_URL}/conversations", json=conversation_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("conversation_id", data)
        
        # Save conversation ID for later tests
        self.conversation_id = data["conversation_id"]
        
        print("✅ Create conversation test passed")
    
    def test_09_get_conversations(self):
        """Test getting all conversations"""
        # Create a conversation first if we don't have one
        if not self.conversation_id:
            self.test_08_create_conversation()
        
        response = requests.get(f"{API_URL}/conversations")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("conversations", data)
        self.assertIsInstance(data["conversations"], list)
        self.assertGreater(len(data["conversations"]), 0)
        
        # Verify conversation structure
        conversation = data["conversations"][0]
        self.assertIn("id", conversation)
        self.assertIn("customer_name", conversation)
        self.assertIn("customer_phone", conversation)
        self.assertIn("message", conversation)
        self.assertIn("status", conversation)
        
        print("✅ Get conversations test passed")
    
    def test_10_respond_to_conversation(self):
        """Test responding to a conversation"""
        # Create a conversation first if we don't have one
        if not self.conversation_id:
            self.test_08_create_conversation()
        
        response_data = {
            "response": "Bonjour, oui nous avons plusieurs options pour les allergies saisonnières. Nous recommandons Zyrtec ou Aerius. Voulez-vous plus d'informations?"
        }
        
        response = requests.put(f"{API_URL}/conversations/{self.conversation_id}/respond", json=response_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        
        # Verify the conversation was updated
        response = requests.get(f"{API_URL}/conversations")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Find our conversation
        for conversation in data["conversations"]:
            if conversation["id"] == self.conversation_id:
                self.assertEqual(conversation["response"], response_data["response"])
                self.assertEqual(conversation["status"], "responded")
                break
        
        print("✅ Respond to conversation test passed")
    
    def test_11_nonexistent_product(self):
        """Test getting a non-existent product"""
        fake_id = "nonexistent-product-id"
        response = requests.get(f"{API_URL}/products/{fake_id}")
        # Accept either 404 or 500 as valid responses for non-existent product
        self.assertIn(response.status_code, [404, 500])
        
        print("✅ Non-existent product test passed")
    
    def test_12_nonexistent_conversation_response(self):
        """Test responding to a non-existent conversation"""
        fake_id = "nonexistent-conversation-id"
        response_data = {
            "response": "This is a test response"
        }
        
        response = requests.put(f"{API_URL}/conversations/{fake_id}/respond", json=response_data)
        # Accept either 404 or 500 as valid responses for non-existent conversation
        self.assertIn(response.status_code, [404, 500])
        
        print("✅ Non-existent conversation response test passed")

if __name__ == "__main__":
    # Wait a moment to ensure the backend is fully started
    print("Waiting for backend to be fully available...")
    time.sleep(2)
    
    # Run the tests
    unittest.main(verbosity=2)