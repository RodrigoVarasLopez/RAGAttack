# ✨🛡️ RAG Attack 🛡️✨

Aplicación web creada con Streamlit que permite consultar y sobrescribir fácilmente Vector Stores utilizando la API de OpenAI. Ideal para sistemas basados en RAG (Retrieval-Augmented Generation).

## 📋 Características

- **Consultar Vector Stores existentes** mediante lenguaje natural.
- **Sobrescribir y actualizar Vector Stores** mediante carga directa de archivos Excel.
- Interfaz sencilla e intuitiva.

## ⚙️ Requisitos previos

- Python 3.8 o superior
- Cuenta en [OpenAI](https://platform.openai.com/) con acceso a la API y clave válida

## 🚀 Instalación

1. Clona este repositorio:

```bash
git clone <url-del-repositorio>
cd <nombre-del-repositorio>
```

2. Instala las dependencias:

```bash
pip install streamlit openai pandas openpyxl
```

## 🛠️ Configuración

- Prepara tu clave API desde [OpenAI](https://platform.openai.com/api-keys).
- La clave API se te solicitará desde la interfaz de usuario al iniciar la aplicación.

## 💻 Ejecutar la aplicación

```bash
streamlit run rag_attack.py
```

Se abrirá automáticamente una nueva ventana en tu navegador predeterminado en la dirección `http://localhost:8501`.

## 📖 Uso de la aplicación

1. Ingresa tu **API KEY de OpenAI** en el campo correspondiente del panel lateral.
2. Selecciona una **Vector Store existente** del menú desplegable.
3. Escribe tu consulta en lenguaje natural y haz clic en `🚀 Realizar Consulta`.
4. Si deseas sobrescribir una Vector Store existente, carga tu archivo Excel usando el cargador proporcionado y haz clic en `♻️ Sobrescribir Vector Store`.

## 📂 Formato del archivo Excel para sobrescritura

Tu archivo Excel debe tener un formato claro con columnas relevantes según tu información. Se recomienda una estructura donde cada fila represente un registro a almacenar en la Vector Store.

**Ejemplo:**

| titulo | contenido  |
|--------|------------|
| Receta | Ingredientes y preparación |

## 🧑‍💻 Autor

Creado y mantenido por [Tu Nombre](https://github.com/tuusuario).

## 📜 Licencia

Este proyecto está bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.

