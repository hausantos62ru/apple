from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()

# Obtener URI desde variable de entorno
MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise Exception("ERROR: Debes definir la variable de entorno MONGO_URI")

client = MongoClient(MONGO_URI)
db = client.get_default_database()

products = db["products"]

# Limpiar datos previos
products.delete_many({})
print("Colección limpiada.")

# Lista de productos
seed_data = [
    {
        "title": "iPhone 15 Pro",
        "slug": "iphone-15-pro",
        "price": 1199.00,
        "description": "Construido con titanio de grado aeroespacial, chip A17 Pro, cámara de 48 MP y USB-C.",
        "image_url": "https://www.apple.com/v/iphone-15-pro/a/images/overview/hero/hero_dramatic_endframe__e3uykdujt4a6_large.jpg"
    },
    {
        "title": "iPhone 15",
        "slug": "iphone-15",
        "price": 899.00,
        "description": "Nuevo diseño con bordes redondeados, cámara de 48 MP y chip A16 Bionic.",
        "image_url": "https://www.apple.com/v/iphone-15/a/images/overview/hero/hero_endframe__d8eriaush7u6_large.jpg"
    },
    {
        "title": "MacBook Air M2",
        "slug": "macbook-air-m2",
        "price": 1299.00,
        "description": "Superligera, silenciosa y potente con el chip M2 y 18 horas de batería.",
        "image_url": "https://www.apple.com/v/macbook-air-m2/a/images/overview/design/design__b6sxm9tr9j66_large.jpg"
    },
    {
        "title": "MacBook Pro 14” M3",
        "slug": "macbook-pro-14-m3",
        "price": 1999.00,
        "description": "Pantalla Liquid Retina XDR, chip M3 y rendimiento profesional en un diseño compacto.",
        "image_url": "https://www.apple.com/newsroom/images/product/mac/standard/Apple-MacBook-Pro-14-inch-16-inch-M3-chiplineup-231030_big.jpg.large.jpg"
    },
    {
        "title": "iPad Pro M2",
        "slug": "ipad-pro-m2",
        "price": 1099.00,
        "description": "Pantalla Liquid Retina XDR, chip M2, soporte para Apple Pencil Hover y cámaras Pro.",
        "image_url": "https://www.apple.com/newsroom/images/product/ipad/standard/Apple-announces-iPad-Pro-M2-hero-221018_Full-Bleed-Image.jpg.large.jpg"
    },
    {
        "title": "Apple Watch Series 9",
        "slug": "apple-watch-series-9",
        "price": 399.00,
        "description": "Chip S9, control con doble toque, pantalla súper brillante y seguimiento de salud avanzado.",
        "image_url": "https://www.apple.com/v/apple-watch-series-9/b/images/overview/hero/hero_s9__e9w1j7gxyw2a_large.jpg"
    },
    {
        "title": "AirPods Pro (2da generación)",
        "slug": "airpods-pro-2",
        "price": 249.00,
        "description": "Cancelación de ruido mejorada, audio adaptativo y chip H2 para un sonido superior.",
        "image_url": "https://www.apple.com/v/airpods-pro/a/images/overview/hero__ecv967jz1yq6_large.jpg"
    },
    {
        "title": "Apple TV 4K",
        "slug": "apple-tv-4k",
        "price": 179.00,
        "description": "Resolución 4K HDR, Dolby Atmos y Siri Remote con USB-C.",
        "image_url": "https://www.apple.com/v/apple-tv-4k/b/images/overview/apple_tv_4k__ean1akihq0sy_large.jpg"
    }
]

# Insertar productos
result = products.insert_many(seed_data)
print(f"Productos insertados: {len(result.inserted_ids)}")
