# Tienda Apple Flask

Proyecto completo en Flask con conexión a MongoDB Atlas, panel admin y despliegue listo para Render y GitHub.

## 🚀 Instalación local

```bash
pip install -r requirements.txt
python app.py
```

## 🌐 Configurar Mongo Atlas

1. Crear un cluster en MongoDB Atlas.
2. En **Network Access**, permitir acceso desde 0.0.0.0/0.
3. Obtener tu URI de conexión:
   ```
   mongodb+srv://usuario:password@cluster.mongodb.net/tienda
   ```
4. Guardar como variable de entorno:
   ```
   export MONGO_URI="TU_URI"
   ```

## 🛠 Despliegue en Render

1. Subir proyecto a GitHub.
2. Crear nuevo servicio Web en Render.
3. Elegir repo.
4. Configurar:
   - **Runtime**: Python 3
   - **Start Command**: `gunicorn app:app`
   - Variables de entorno:
     - `MONGO_URI` = tu cadena
     - `ADMIN_PASSWORD` = la clave del panel admin

5. Deploy.

## 📦 Estructura

- app.py
- templates/
- static/
- requirements.txt
- Procfile
- README.md
