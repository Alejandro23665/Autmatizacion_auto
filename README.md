# Automatización Boletas AUTO - ABBYY FlexiCapture 12

Aplicación de escritorio para automatizar el envío de boletas 100% verificadas en ABBYY FlexiCapture 12 Verification Station.

## 📋 Descripción

Esta aplicación automatiza el envío de boletas en la cola **AUTO** de ABBYY FlexiCapture 12 Verification Station para el proyecto **Proyecto_Consorcio** (http://3.233.5.132/Proyecto_Consorcio).

### Flujo de trabajo automatizado:

1. **Inicia ABBYY FlexiCapture Verification Station**
2. Maneja el diálogo "Seleccionar modo" → Click "Aceptar"
3. Espera ventana principal "Estación de verificación"
4. Maneja ventana hija "Abrir proyecto" → Click "Aceptar"
3. Espera título URL del proyecto (confirmación de carga)
4. **Busca tabla de colas y fila AUTO**
5. **Lee recuento de boletas AUTO (columna 3: "Recuento de las tareas con forma")**
4. **Loop por cada boleta:**
   - Click fila AUTO + `Ctrl+G` + `Alt+G` (primera vez)
   - Espera carga de boleta (cambio de título)
   - Detecta modal de error (Si/No/Cancelar) → Click "Cancelar"
   - Click derecho 80% izquierda → menú "Enviar a etapa"
   - Click "Enviar a etapa..." → Ventana "Enviar tarea a etapa"
   - ComboBox "Fases disponibles" → Seleccionar "Verificación Javier"
   - Click "Aceptar"
   - `Ctrl+L` → Esperar 1.5s
   - Repetir para siguiente boleta
5. Cerrar aplicación al finalizar

## 🚀 Instalación y Uso

### Requisitos previos
- Windows 10/11
- ABBYY FlexiCapture 12 Stations instalado en `C:\Program Files\ABBYY FlexiCapture 12 Stations\FlexiCapture.exe`
- Acceso al servidor: http://3.233.5.132/Proyecto_Consorcio
- Usuario con permisos en "Verificación Javier"

### Opción A: Ejecutable portable (Recomendado)
```bash
# Solo copiar y ejecutar
dist/Automatizacion_Autos.exe
```

### Opción B: Desarrollo / Python
```bash
# 1. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar
python main.py
```

### Dependencias
```txt
pywinauto>=0.6.8
pywin32>=306
```

## 🏗️ Estructura del Proyecto

```
automatizacion_automaticas/
├── main.py                 # Entry point (dev + bundled)
├── gui_v2.py               # Interfaz gráfica Tkinter
├── gui.spec                # Config PyInstaller
├── requirements.txt        # Dependencias Python
├── gui.spec                # Config PyInstaller
├── README.md               # Este archivo
├── dist/
│   └── Automatizacion_Autos.exe    # Ejecutable compilado
├── src/
│   └── automation/
│       ├── __init__.py
│       ├── launch_app.py   # Orquestador principal
│       ├── queues.py       # Loop AUTO + manejo errores
│       ├── window_utils.py # Utilidades UIA/PyWinAuto
│       └── dialogs.py      # Manejo de diálogos
└── scripts/                # Scripts de debug/test
```

## 🖥️ Interfaz Gráfica

La GUI (`gui_v2.py`) incluye:
- **Estado**: Muestra estado actual (Listo/Iniciando/Procesando/Detenido)
- **Contador**: "Boletas AUTO: X" - muestra cantidad detectada
- **Barra de progreso**: Indeterminada durante procesamiento
- **Botones**: 
  - **Iniciar Automatización** - Inicia hilo de trabajo
  - **Detener** - Detiene procesamiento actual
- **Log en tiempo real**: Timestamps + mensajes detallados

### Controles
| Botón | Acción |
|-------|--------|
| **Iniciar Automatización** | Lanza hilo background, deshabilita botón inicio |
| **Detener** | Establece flag `is_running=False`, detiene loop actual |

## 🔄 Flujo Técnico Detallado

### 1. Lanzamiento (`launch_app.py`)
```python
launch_verification_station() -> (app, main_window)
```
1. `Application().start(FlexiCapture.exe)`
2. Dialog "Seleccionar modo" → Click "Aceptar"
3. Espera ventana "Estación de verificación"
4. Dialog "Abrir proyecto" → Click "Aceptar"
5. Espera título URL proyecto

### 2. Loop AUTO (`queues.py` - `process_auto_queue_loop`)
```python
def process_auto_queue_loop(main_window, app, auto_count=0, timeout=120, should_stop=None)
```
**Parámetros:**
- `main_window`: Ventana principal UIA
- `app`: Aplicación PyWinAuto
- `auto_count`: 0 = auto-detectar desde columna 3
- `should_stop`: Callable que retorna True para detener

**Flujo por boleta:**
```
1. Boleta 1: Click fila AUTO + Ctrl+G + Alt+G → espera título boleta
2. N>1: Espera cambio título (nueva boleta cargada)
3. Detectar modal error (Sí/No/Cancelar) → Click "Cancelar"
4. Click derecho 80% izquierda → Menú "Enviar a etapa"
3. Click "Enviar a etapa..." → Ventana "Enviar tarea a etapa"
4. ComboBox "Fases disponibles" → "Verificación Javier" → Click "Aceptar"
4. Ctrl+L → Esperar 1.5s
5. Repetir hasta completar N boletas
```

### Manejo de Errores (Modales)
```
Modal "ABBYY FlexiCapture 12 (Estación de verificación)"
Botones: [Sí] [No] [Cancelar]
→ Click "Cancelar"
→ Click derecho 80% izq → "Enviar a etapa..."
→ Click "Enviar a etapa..." → Ventana "Enviar tarea a etapa"
→ ComboBox "Fases disponibles" → "Verificación Javier" → Click "Aceptar"
```

## 📦 Compilación (PyInstaller)

```bash
# Instalar PyInstaller
pip install pyinstaller

# Compilar usando spec
pyinstaller --clean gui.spec

# O con comando directo
pyinstaller --clean gui.spec

# Salida: dist/Automatizacion_Autos.exe
```

### Configuración `gui.spec`
```python
# Incluye src/automation como datos
datas=[('src/automation', 'src/automation')]

# Hidden imports para pywinauto/comtypes
hiddenimports=[
    'pywinauto', 'pywinauto.controls', 'pywinauto.timings',
    'comtypes', 'comtypes.client', 'comtypes.gen'
]

# Sin consola (GUI only)
console=False
```

## 📁 Archivos de Configuración

### `gui.spec` - PyInstaller Spec
```python
# Incluye src/automation como datos
datas=[('src/automation', 'src/automation')]

# Hidden imports para pywinauto/comtypes
hiddenimports=[
    'pywinauto', 'pywinauto.controls', 'pywinauto.timings',
    'comtypes', 'comtypes.client', 'comtypes.gen',
]
```

### `gui.spec` (entry point alternativo)
```python
# Entry point alternativo usando gui_v2.py directamente
```

## 🐛 Debug y Logs

### Logs en tiempo real (GUI)
- Timestamp: `[HH:MM:SS] mensaje`
- Niveles: INFO, WARNING, ERROR
- Scroll automático

### Logs en consola (desarrollo)
```bash
python main.py
```

### Logs de depuración disponibles
- `DEBUG: Verificando modal de error en boleta X`
- `DEBUG: detect_error_modal returned: error_detected=True`
- `DEBUG: Popup window found: 'Contexto' type=Menu`

### Archivos de debug en `scripts/`
```
debug_boleta.py          # Debug tabla boletas
debug_boleta_table.py    # Debug tabla detallada
test_launch.py           # Test launch app
test_task2.py            # Test tarea 2
test_task4.py            # Test tarea 4
```

## 🔧 Solución de Problemas

### Error: "No se encontró tabla de colas"
- Verificar que el proyecto esté cargado (título URL visible)
- Aumentar timeout en `find_queue_table`

### Error: "No se encontró fila AUTO"
- Verificar que existe fila con texto "AUTO" en columna 0
- Verificar que la tabla tiene filas visibles

### Error: "Modal de error no detectado"
- Verificar título exacto: "ABBYY FlexiCapture 12 (Estación de verificación)"
- Verificar botones: "Sí", "No", "Cancelar"

### Error: "ComboBox 'Fases disponibles' no encontrado"
- Verificar que ventana "Enviar tarea a etapa" esté activa
- Buscar ComboBox/ListBox con items "Verificación Javier"

### App no responde / Se cuelga
- Verificar timeouts en `wait_for_title_change_pattern`
- Revisar `wait_for_title_change_pattern` en `window_utils.py`

## 📦 Distribución

### Archivos a distribuir
```
Automatizacion_Autos.exe     # Ejecutable principal (14 MB)
README.md                    # Documentación (opcional)
```

### Requisitos en máquina destino
- Windows 10/11
- ABBYY FlexiCapture 12 Stations instalado
- Mismo path: `C:\Program Files\ABBYY FlexiCapture 12 Stations\FlexiCapture.exe`
- Conexión a http://3.233.5.132/Proyecto_Consorcio

## 📝 Licencia y Uso

**Uso interno - Empresa de automatización**

Proyecto desarrollado para automatización interna de procesos de verificación en ABBYY FlexiCapture 12.

---

## 📚 Referencias Técnicas

- **PyWinAuto**: https://github.com/pywinauto/pywinauto
- **UI Automation (UIA)**: Microsoft UI Automation
- **ABBYY FlexiCapture 12 SDK**: Documentación oficial ABBYY

---

*Última actualización: Julio 2026*
*Versión: 1.0.0*