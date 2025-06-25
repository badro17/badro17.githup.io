from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
import os
from datetime import datetime
from typing import List, Optional
import uuid

# Initialize FastAPI app
app = FastAPI(title="Pharmacie Saidani API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
client = MongoClient(mongo_url)
db = client.pharmacie_saidani

# Collections
products_collection = db.products
orders_collection = db.orders
conversations_collection = db.conversations

# Pydantic models
class Product(BaseModel):
    id: str
    name: str
    category: str
    description: str
    price: float
    image_url: str
    in_stock: bool = True

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float

class Order(BaseModel):
    id: str
    customer_name: str
    customer_phone: str
    customer_address: str
    items: List[OrderItem]
    total_amount: float
    status: str = "pending"
    created_at: datetime
    notes: Optional[str] = None

class ConversationMessage(BaseModel):
    id: str
    customer_name: str
    customer_phone: str
    message: str
    response: Optional[str] = None
    status: str = "pending"
    created_at: datetime

# Initialize sample products
def initialize_products():
    if products_collection.count_documents({}) == 0:
        sample_products = [
            {
                "id": str(uuid.uuid4()),
                "name": "Paracétamol 500mg",
                "category": "Médicaments",
                "description": "Antalgique et antipyrétique pour soulager la douleur et réduire la fièvre",
                "price": 150.0,
                "image_url": "https://images.unsplash.com/photo-1471864190281-a93a3070b6de",
                "in_stock": True
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Ibuprofène 400mg",
                "category": "Médicaments",
                "description": "Anti-inflammatoire non stéroïdien pour douleurs et inflammations",
                "price": 200.0,
                "image_url": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae",
                "in_stock": True
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Vitamines C 1000mg",
                "category": "Compléments",
                "description": "Complément alimentaire pour renforcer le système immunitaire",
                "price": 800.0,
                "image_url": "https://images.pexels.com/photos/159211/headache-pain-pills-medication-159211.jpeg",
                "in_stock": True
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Crème Hydratante",
                "category": "Cosmétiques",
                "description": "Crème hydratante pour peaux sèches et sensibles",
                "price": 1200.0,
                "image_url": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9",
                "in_stock": True
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Sérum Anti-Âge",
                "category": "Cosmétiques",
                "description": "Sérum anti-âge avec acide hyaluronique",
                "price": 2500.0,
                "image_url": "https://images.pexels.com/photos/3018845/pexels-photo-3018845.jpeg",
                "in_stock": True
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Sirop pour la Toux",
                "category": "Médicaments",
                "description": "Sirop expectorant pour soulager la toux",
                "price": 300.0,
                "image_url": "https://images.unsplash.com/photo-1471864190281-a93a3070b6de",
                "in_stock": True
            }
        ]
        products_collection.insert_many(sample_products)

initialize_products()

# API Routes
@app.get("/")
async def root():
    return {"message": "Pharmacie Saidani API"}

@app.get("/api/products")
async def get_products():
    try:
        products = list(products_collection.find({}, {"_id": 0}))
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    try:
        product = products_collection.find_one({"id": product_id}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/category/{category}")
async def get_products_by_category(category: str):
    try:
        products = list(products_collection.find({"category": category}, {"_id": 0}))
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orders")
async def create_order(order_data: dict):
    try:
        order = {
            "id": str(uuid.uuid4()),
            "customer_name": order_data["customer_name"],
            "customer_phone": order_data["customer_phone"],
            "customer_address": order_data["customer_address"],
            "items": order_data["items"],
            "total_amount": order_data["total_amount"],
            "status": "pending",
            "created_at": datetime.now(),
            "notes": order_data.get("notes", "")
        }
        
        result = orders_collection.insert_one(order)
        return {"message": "Commande créée avec succès", "order_id": order["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders")
async def get_orders():
    try:
        orders = list(orders_collection.find({}, {"_id": 0}).sort("created_at", -1))
        return {"orders": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversations")
async def create_conversation(conversation_data: dict):
    try:
        conversation = {
            "id": str(uuid.uuid4()),
            "customer_name": conversation_data["customer_name"],
            "customer_phone": conversation_data["customer_phone"],
            "message": conversation_data["message"],
            "response": None,
            "status": "pending",
            "created_at": datetime.now()
        }
        
        result = conversations_collection.insert_one(conversation)
        return {"message": "Message envoyé avec succès", "conversation_id": conversation["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations")
async def get_conversations():
    try:
        conversations = list(conversations_collection.find({}, {"_id": 0}).sort("created_at", -1))
        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/conversations/{conversation_id}/respond")
async def respond_to_conversation(conversation_id: str, response_data: dict):
    try:
        result = conversations_collection.update_one(
            {"id": conversation_id},
            {"$set": {
                "response": response_data["response"],
                "status": "responded"
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {"message": "Réponse envoyée avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories():
    try:
        categories = products_collection.distinct("category")
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)