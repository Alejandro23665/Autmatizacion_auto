# Automatizacion Autos - ABBYY FlexiCapture Auto Boletas

Interfaz gráfica para automatizar el envío de boletas 100% verificadas en ABBYY FlexiCapture 12 Verification Station.

## Descripción

Esta aplicación automatiza el proceso de:
1. Lanzar ABBYY FlexiCapture Verification Station
2. Abrir el proyecto configurado
3. Seleccionar la cola AUTO
4. Procesar todas las boletas de la cola:
   - Detectar modales de error
   - Enviar a etapa "Verificación Javier"
   - Continuar con la siguiente boleta

## Instalación

### Opción 1: Desarrollo (Python)
```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python gui_v2.py
```

### Opción 2: Ejecutable (Windows)
```bash
# Instalar PyInstaller
pip install pyinstaller

# Compilar
pyinstaller gui.spec

# El ejecutable estará en dist/Automatizacion_Autos.exe
```

## Uso

1. Ejecutar la aplicación
2. Clic en **"Iniciar Envio"**
3. La aplicación:
   - Abre ABBYY FlexiCapture
   - Abre el proyecto configurado
   - Selecciona la cola AUTO
   - Procesa cada boleta automáticamente
   - Maneja errores enviando a "Verificación Javier"
4. Ver el progreso en la interfaz
5. Clic en **"Detener"** para cancelar

## Configuración

La aplicación usa por defecto:
- **Ejecutable**: `C:\Program Files\ABBYY FlexiCapture 12 Stations\FlexiCapture.exe`
- **Proyecto**: `http://3.233.5.132/Proyecto_Consorcio`
- **Cola**: AUTO
- **Fase destino**: Verificación Javier

Para cambiar la configuración, editar `src/automation/launch_app.py` (constante `EXE_PATH`).

## Flujo de Automatización

```
Iniciar → Diálogos modo/proyecto → Ventana principal
    ↓
Seleccionar fila AUTO → Click DERECHO (20% izq) → Menú "Contexto"
    ↓
Click IZQUIERDO "Enviar a etapa..." → Ventana "Enviar tarea a etapa"
    ↓
ComboBox "Fases disponibles" → Seleccionar "Verificación Javier" → Click "Aceptar"
    ↓
Siguiente boleta → Repetir hasta completar
```

## Logs

La interfaz muestra logs en tiempo real con timestamps:
- Progreso de cada paso
- Detección de errores
- Acciones realizadas

## Requisitos

- Windows 10/11
- ABBYY FlexiCapture 12 Verification Station instalado
- Python 3.8+ (solo para desarrollo)
- Acceso al servidor del proyecto (http://3.233.5.132/Proyecto_Consorcio)

## Estructura del Proyecto

```
automatizacion_automaticas/
├── gui_v2.py          # Interfaz gráfica principal
├── gui.spec           # Spec PyInstaller
├── requirements.txt   # Dependencias Python
├── src/
│   └── automation/
│       ├── __init__.py
│       ├── launch_app.py      # Lanza app y maneja diálogos
│       ├── window_utils.py    # Utilidades UI (detectar modales, clicks)
│       ├── dialogs.py         # Manejo diálogos modo/proyecto
│       └── queues.py          # Lógica colas AUTO + loop procesamiento
└── dist/
    └── Automatizacion_Autos.exe  (después de compilar)
```

## Compilación para Distribución

```bash
# Instalar PyInstaller
pip install pyinstaller

# Compilar
pyinstaller gui.spec

# El ejecutable estará en:
dist/Automatizacion_Autos.exe
```

## Solución de Problemas

### Error "No se encontró tabla de colas"
- Verificar que el proyecto esté abierto correctamente
- Aumentar timeout en `src/automation/queues.py`

### Error "Modal no detectado"
- Verificar que el título del modal sea exactamente: "ABBYY FlexiCapture 12 (Estación de verificación)"
- Los botones deben ser: Sí, No, Cancelar

### Error "ComboBox 'Fases disponibles' no encontrado"
- Verificar que la ventana "Enviar tarea a etapa" se abra correctamente
- El ComboBox debe tener texto "Fases disponibles:"

### App se cierra inesperadamente
- Ejecutar desde consola para ver logs: `Automatizacion_Autos.exe`
- Verificar que ABBYY esté instalado en la ruta por defecto

## Licencia

Uso interno - Empresa de automatización.