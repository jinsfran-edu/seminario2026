# Seminario de actualización 2026

Repositorio con notebooks

## Contenido

- `Repaso.ipynb`: notebook de repaso.
- `requirements.txt`: dependencias de Python.

## Requisitos

- Python 3.10+ recomendado.
- VS Code con extension de Jupyter

## Instalacion

1. Crear entorno virtual:

   ```powershell
   python -m venv .venv
   ```

2. Activar entorno virtual (PowerShell):

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Instalar dependencias:

   ```powershell
   pip install -r requirements.txt
   ```

## Uso

1. Abrir el proyecto en VS Code.
2. Abrir un notebook como `Repaso.ipynb`.
3. Seleccionar el kernel de `.venv`.
4. Ejecutar las celdas del notebook.

## Notas

- Si agregas nuevas librerias, actualiza `requirements.txt`.
- Si el kernel no aparece, reinicia VS Code o selecciona manualmente el interprete de `.venv`.
