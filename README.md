# S & J — App de 6 meses

## Ejecutarla en Windows
1. Descomprime esta carpeta.
2. Abre Terminal / PowerShell dentro de la carpeta.
3. Ejecuta:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

También puedes hacer doble clic en `INICIAR_APP.bat` si Python ya está instalado.

## Código de entrada
La pantalla inicial usa la fecha de novios como código:

**13 / 03 / 2026**

## Fotos incluidas
Los recuerdos que compartiste están en `assets/moments/`, organizados por lugar/salida.
Los videos MOV/HEVC fueron convertidos a MP4 H.264 para que se reproduzcan mejor en navegador.

## Fotos que agregue bb
Dentro de la sección **Álbum**, bb puede subir fotos nuevas y asignarlas a una salida existente o al álbum general.
La app guarda esas fotos en `assets/bb_uploads/` y la información en `data/bb_memories.json`.

### Importante para publicarla en Internet
Este sistema de guardado funciona bien localmente o en un servidor con disco persistente. En Streamlit Community Cloud los archivos subidos pueden perderse al reiniciar/republicar la app. Cuando quieras dejarla en Internet de forma definitiva, conviene conectar esta sección a **Supabase Storage + base de datos** para que las fotos y respuestas de bb permanezcan guardadas.

## Cosas que podemos afinar después
- Fecha real de cada salida.
- Ubicación exacta de TopGolf y de la primera salida como novios.
- Frases específicas para cada recuerdo.
- Carta final.
- Las 10 razones.
- Preguntas.
- Agregar música, audio o una sorpresa especial para el 13 de septiembre.
