## **Instalación y Configuración**:

1. **Clonar el Repositorio**: Clona el repositorio del proyecto desde GitHub usando el siguiente comando:

    ```bash
    git clone https://github.com/yoezequiel/FarmaGo.git
    ```

2. **Crear un Entorno Virtual (Opcional)**: Se recomienda crear un entorno virtual para aislar las dependencias del proyecto. Desde la raíz del proyecto, ejecuta el siguiente comando:

    ```bash
    python -m venv .venv
    ```

3. **Activar el Entorno Virtual (Opcional)**: En sistemas Windows, ejecuta:

    ```bash
    .env\Scripts\activate
    ```

    En sistemas basados en Unix, ejecuta:

    ```bash
    source .env/bin/activate
    ```

4. **Instalar Dependencias**: Una vez que el entorno virtual está activado, instala las dependencias del proyecto desde el archivo "requirements.txt":

    ```bash
    pip install -r requirements.txt
    ```

5. **Definir las Variables de Entorno**:

    ```python
    # config.py

    # Variable de entorno para la clave secreta de la aplicación Flask
    SECRET_KEY = "tu_clave_secreta_aqui"

    # Variable de entorno para el access_token de mercado pago
    access_token = "tu_access_token_aqui"
    ```

    Reemplaza "tu_clave_secreta_aqui" y "tu_access_token_aqui" con los valores reales que deseas utilizar para SECRET_KEY y ACCESS_TOKEN respectivamente.

6. **Agregar "config.py" al .gitignore**: Para mantener segura la información confidencial, asegúrate de agregar "config.py" al archivo ".gitignore" para que no se incluya en el control de versiones.
7. **Ejecutar la Aplicación**: Finalmente, ejecuta la aplicación Flask con el siguiente comando:

    ```bash
    python3 app.py
    ```

    La aplicación estará disponible en **[http://localhost:5000](http://localhost:5000/)** por defecto.
