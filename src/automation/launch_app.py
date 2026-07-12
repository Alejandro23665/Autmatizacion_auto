import time
import logging
from typing import Tuple
from pywinauto import Application

from .window_utils import wait_for_window, get_window_info, WindowNotFoundError, wait_for_title_change
from .dialogs import handle_mode_selection_dialog, handle_open_project_window, wait_for_main_verification_window
from .queues import select_auto_queue_and_open_boleta, post_boleta_action, process_auto_queue_loop, find_queue_table, find_auto_row, get_cell_text

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

EXE_PATH = r'C:\\Program Files\\ABBYY FlexiCapture 12 Stations\\FlexiCapture.exe'


def launch_verification_station(
    exe_path: str = EXE_PATH,
    timeout_main_window: int = 60,
    timeout_dialogs: int = 30,
    timeout_project_window: int = 15,
    timeout_queue_selection: int = 40,
    backend: str = 'uia'
) -> Tuple[Application, object]:
    '''
    Flujo completo Tareas 1+2+3+4+5:
    1. Inicia proceso
    2. Diálogo 'Seleccionar modo' -> Click 'Aceptar'
    3. Ventana principal 'Estación de verificación'
    4. Ventana hija 'Abrir proyecto' -> Click 'Aceptar'
    5. Espera título URL proyecto
    6. Lee recuento AUTO (columna 3)
    7. Loop: Click AUTO + Ctrl+G + Alt+G (1ra) -> esperar boleta -> Ctrl+L + 5s x N boletas
    8. Cerrar app al final
    
    Returns:
        (app, main_window)
    '''
    # 1. Iniciar aplicación
    logger.info(f'Iniciando: {exe_path}')
    app = Application(backend=backend).start(exe_path)
    time.sleep(2)
    
    # 2. Diálogo de selección de modo
    try:
        handle_mode_selection_dialog(app, timeout=timeout_dialogs)
        time.sleep(1)
    except WindowNotFoundError:
        logger.warning('Diálogo de selección de modo no encontrado, continuando...')
    except Exception as e:
        logger.warning(f'Error en diálogo de modo: {e}, continuando...')
    
    # 3. Esperar ventana principal de verificación
    logger.info('Esperando ventana principal...')
    main_window = wait_for_main_verification_window(app, timeout=timeout_main_window)
    logger.info(f'Ventana principal encontrada: {main_window.window_text()}')
    
    # 4. Manejar ventana hija \"Abrir proyecto\" dentro de la ventana principal
    try:
        handle_open_project_window(main_window, timeout=timeout_project_window)
        time.sleep(2)
        logger.info('Ventana Abrir proyecto manejada')
    except Exception as e:
        logger.warning(f'Error/aviso en ventana Abrir proyecto: {e}')
    
    # 5. Esperar a que el título cambie a la URL del proyecto (confirmación de carga)
    logger.info('Esperando confirmación de carga de proyecto (cambio de título)...')
    try:
        main_window = wait_for_title_change(app, r'http://3\.233\.5\.132/Proyecto_Consorcio|Proyecto_Consorcio', timeout=15)
        logger.info(f'Proyecto cargado. Título: {main_window.window_text()}')
    except WindowNotFoundError:
        logger.warning('Título no cambió a URL del proyecto, pero continuando...')
    
    # 6. NUEVO: Leer recuento AUTO y procesar loop completo
    logger.info('Buscando tabla de colas y fila AUTO...')
    table = find_queue_table(main_window, timeout=15)
    if not table:
        logger.error('No se pudo encontrar la tabla de colas')
        return app, main_window
    
    auto_row = find_auto_row(table, timeout=10)
    if not auto_row:
        logger.error('No se encontró la fila AUTO')
        return app, main_window
    
    # Leer recuento (columna 3)
    recuento_text = get_cell_text(auto_row, 3)
    logger.info(f'Cantidad de AUTO (Recuento tareas con forma): {recuento_text}')
    print(f'Cantidad de AUTO: {recuento_text}')
    
    try:
        auto_count = int(recuento_text.strip())
    except ValueError:
        logger.error(f'No se pudo parsear el recuento: {recuento_text}')
        return app, main_window
    
    if auto_count <= 0:
        logger.warning('Recuento AUTO es 0 o negativo, no hay boletas para procesar')
        return app, main_window
    
    logger.info(f'Iniciando loop AUTO para {auto_count} boletas...')
    success = process_auto_queue_loop(main_window, app, auto_count, timeout=timeout_queue_selection)
    
    if success:
        logger.info('Loop AUTO completado exitosamente')
    else:
        logger.warning('Loop AUTO fallo')
    
    return app, main_window


def launch_and_get_info(
    exe_path: str = EXE_PATH,
    timeout_main_window: int = 60,
    timeout_dialogs: int = 30,
    timeout_project_window: int = 15,
    timeout_queue_selection: int = 40,
    backend: str = 'uia'
) -> dict:
    '''
    Lanza la app completa y retorna información de la ventana principal.
    '''
    app, main_window = launch_verification_station(
        exe_path=exe_path,
        timeout_main_window=timeout_main_window,
        timeout_dialogs=timeout_dialogs,
        timeout_project_window=timeout_project_window,
        timeout_queue_selection=timeout_queue_selection,
        backend=backend
    )
    
    info = get_window_info(main_window)
    info['app_pid'] = app.process
    info['main_window_title'] = main_window.window_text()
    return info


if __name__ == '__main__':
    import sys
    sys.path.insert(0, 'src')
    
    print('Iniciando ABBYY FlexiCapture Verification Station...')
    try:
        info = launch_and_get_info()
        print('\\n=== RESULTADO ===')
        for k, v in info.items():
            if k not in ('rect',):
                print(f'  {k}: {v}')
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)
