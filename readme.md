# Thesis RAG API

Backend asíncrono construido con FastAPI y SQLAlchemy para soportar flujos de Recuperación Aumentada por Generación (RAG). El objetivo es gestionar clientes, usuarios, conversaciones y documentos que nutren a un motor RAG, dejando preparada la capa de persistencia y la API base para futuros módulos de ingestión y consulta.

## Características principales
- API REST con FastAPI lista para desplegarse (p. ej. Railway) con middleware CORS abierto para integraciones rápidas.
- Conexión asíncrona a MySQL mediante SQLAlchemy 2.x y el driver `asyncmy`, con creación automática de tablas al iniciar.
- Modelado inicial de entidades clave: clientes, usuarios, chats, detalles de chat y documentos, pensado para trazar la interacción completa con el sistema RAG.
- Estructura modular (`controllers`, `services`, `schemas`, `shared`, `util`) para separar responsabilidad y facilitar la evolución futura.

## Estructura del proyecto
```
├── app
│   ├── controllers/        # Routers de FastAPI (pendientes de implementación)
│   ├── db/
│   │   ├── base.py         # Declarative Base y mixins comunes
│   │   ├── session.py      # Configuración del motor Async SQLAlchemy
│   │   └── loadModels.py   # Registro de modelos en la metadata
│   ├── models/             # Tablas SQLAlchemy (Users, Clients, Chats, etc.)
│   ├── schemas/            # Pydantic DTOs para requests/responses
│   ├── services/           # Lógica de negocio (reservado)
│   ├── shared/             # Utilidades compartidas (p. ej. respuestas estándar)
│   └── util/               # Helpers generales
├── main.py                  # Punto de entrada FastAPI
├── requirements.txt         # Dependencias del proyecto
└── readme.md                # Documentación del proyecto
```

## Requisitos previos
- Python 3.10 o superior.
- Servidor MySQL/MariaDB accesible (se recomienda versión 8.x o MySQL compatible).
- (Opcional) `virtualenv` o `conda` para aislar dependencias.

## Variables de entorno
Configura un archivo `.env` en la raíz del proyecto o exporta las variables antes de ejecutar la aplicación.

| Variable      | Descripción                                 | Valor por defecto |
|---------------|----------------------------------------------|-------------------|
| `DB_USER`     | Usuario de la base de datos                  | `root`            |
| `DB_PASSWORD` | Contraseña del usuario                       | `` (vacío)        |
| `DB_HOST`     | Host o IP del servidor MySQL                 | `127.0.0.1`       |
| `DB_PORT`     | Puerto del servidor MySQL                    | `3306`            |
| `DB_NAME`     | Base de datos donde se crearán las tablas    | `rag_db`          |

Ejemplo de `.env`:
```dotenv
DB_USER=rag_user
DB_PASSWORD=super_secreto
DB_HOST=localhost
DB_PORT=3306
DB_NAME=rag_db
```

## Instalación
```bash
# 1. Clonar el repositorio
# git clone <URL_del_repositorio>
cd RAG_v1

# 2. (Opcional) Crear y activar un entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

## Puesta en marcha
```bash
# Ejecutar la API con recarga automática
uvicorn main:app --reload

# Si prefieres cargar variables desde .env usando uvicorn >= 0.17:
uvicorn main:app --reload --env-file .env
```

Al iniciar, FastAPI intentará crear las tablas definidas en `app/models` si no existen. Puedes validar el servicio visitando `http://localhost:8000/health` o abrir la documentación interactiva en `http://localhost:8000/docs`.

## Modelado de datos
Las entidades disponibles cubren los elementos base del ecosistema RAG:
- `Clients`: organización o empresa dueña de la información y usuarios.
- `Users`: usuarios finales asociados a cada cliente.
- `Chats`: histórico de conversaciones (prompt/respuesta) con el asistente.
- `ChatDetails`: mensajes ordenados que componen cada chat (usuario, sistema, asistente).
- `Documents`: corpus y metadatos de las fuentes utilizadas para la recuperación.
- `TableXClients`: tabla auxiliar para vincular configuraciones adicionales por cliente.

Todas las tablas heredan de `TimestampMixin`, que incluye columnas de alta (`createDate`), actualización (`updateDate`) y un flag lógico (`swt`).

## Endpoints disponibles
Por ahora se encuentra expuesto únicamente el endpoint de salud:
- `GET /health` → `{ "ok": true }`

Los routers de negocio (ingestión, consulta, administración) se añadirán en `app/controllers` a medida que avanza el desarrollo.

## Próximos pasos sugeridos
- Implementar controladores y servicios para CRUD de clientes, usuarios y documentos.
- Integrar el pipeline RAG (vector store, embeddings, consumo del LLM) utilizando las dependencias ya declaradas (`faiss-cpu`, `sentence-transformers`, `transformers`, etc.).
- Configurar migraciones con Alembic para gestionar cambios en el esquema.
- Añadir pruebas automatizadas y scripts de inicialización de datos.

## Licencia
Todavía no se ha definido una licencia para este proyecto. Añade el archivo `LICENSE` correspondiente cuando se tome una decisión.
