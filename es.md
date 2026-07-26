# PC Time Tracker

Cronómetro de tiempo de escritorio ligero para Windows. Cuenta cuánto tiempo pasas frente al PC, con pausa automática por inactividad, objetivo diario configurable e historial de 7 días.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## Características

- 🕒 Gran temporizador de la sesión actual + total del día
- ⏸ Botones **Iniciar / Pausar / Reiniciar**
- 😴 **Pausa automática** por inactividad — umbral ajustable (10…3600 s)
- 🎯 **Objetivo diario** configurable (1–24 h) con barra de progreso
- 📊 **Historial de 7 días** con barras de progreso por día
- 🪟 Opción "Siempre visible"
- 💾 Guardado automático cada 10 segundos y al cerrar — las sesiones sobreviven a un reinicio
- 🎨 Tema oscuro, fuentes Consolas / Segoe UI
- 🌐 **10 idiomas de interfaz** — English (predeterminado), Русский, 中文, Español, Français, Deutsch, Português, 日本語, 한국어, العربية

## Captura de pantalla

![PC Time Tracker](screenshot.png)

## Instalación y ejecución

Requiere **Python 3.10+** con el módulo `tkinter` (incluido por defecto en Windows).

```bash
python pc_time_tracker.py
```

También funciona con doble clic si `.py` está asociado con Python.

## Dónde se guardan los datos

Toda la configuración y el historial viven en un único archivo JSON:

```
%APPDATA%\PCTimeTracker\data.json
```

## Licencia

MIT
