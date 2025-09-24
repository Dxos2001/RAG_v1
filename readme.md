# Proyecto RAG

Este proyecto implementa un sistema de Recuperación Aumentada por Generación (RAG), combinando técnicas de recuperación de información y modelos de lenguaje para mejorar la precisión y relevancia de las respuestas generadas.

## Características

- Recuperación de documentos relevantes a partir de una consulta.
- Integración con modelos de lenguaje para generación de respuestas.
- Modular y fácil de extender.

## Requisitos

- Python 3.8+
- Instalar dependencias con `pip install -r requirements.txt`

## Instalación

```bash
git clone https://github.com/tu-usuario/rag.git
cd rag
pip install -r requirements.txt
```

## Uso

1. Prepara tu conjunto de documentos.
2. Ejecuta el sistema con:

    ```bash
    python main.py --query "Tu pregunta aquí"
    ```

3. El sistema recuperará información relevante y generará una respuesta.

## Estructura del proyecto

```
├── data/           # Documentos fuente
├── src/            # Código fuente principal
├── requirements.txt
└── readme.md
```

## Contribución

¡Las contribuciones son bienvenidas! Por favor, abre un issue o pull request.

## Licencia

MIT
