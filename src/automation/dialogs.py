import time
import logging
from typing import Optional
from pywinauto import Application, WindowSpecification
from .window_utils import wait_for_window, click_button, find_window_by_title_re, find_child_window, click_button_in_container, ButtonNotFoundError, WindowNotFoundError

logger = logging.getLogger(__name__)


def handle_mode_selection_dialog(app: Application, timeout: int = 30) -> WindowSpecification:
    '''
    Maneja el diálogo de selección de modo de FlexiCapture.
    Título: 'Seleccionar modo de FlexiCapture'
    Click en botón 'Aceptar'
    '''
    logger.info('Esperando diálogo: Seleccionar modo de FlexiCapture')
    mode_window = wait_for_window(app, r'Seleccionar.*modo.*FlexiCapture|FlexiCapture.*modo|FlexiCapture.*station|Mode.*selection', timeout=timeout)
    logger.info(f'Diálogo encontrado: {mode_window.window_text()}')
    
    click_button(mode_window, r'Aceptar|OK')
    logger.info('Click en Aceptar (diálogo modo)')
    
    return mode_window


def handle_open_project_window(main_window: WindowSpecification, timeout: int = 15) -> bool:
    '''
    Maneja la ventana hija \"Abrir proyecto\" DENTRO de la ventana principal.
    - Busca ventana hija con título \"Abrir proyecto\"
    - Click en botón \"Aceptar\" (auto_id=1) dentro de esa ventana
    - Retorna True si se manejó, False si no se encontró
    '''
    logger = logging.getLogger(__name__)
    
    logger.info('Buscando ventana hija \"Abrir proyecto\" en ventana principal...')
    
    start = time.time()
    project_window = None
    
    while time.time() - start < timeout:
        project_window = find_child_window(main_window, r'Abrir.*proyecto|Open.*project', control_types=('window', 'custom', 'pane', 'group', 'panel'))
        if project_window:
            logger.info(f'Ventana hija encontrada: {project_window.window_text()} (tipo: {project_window.element_info.control_type})')
            break
        time.sleep(0.5)
    
    if not project_window:
        logger.info('Ventana \"Abrir proyecto\" no encontrada (quizás ya cargó el proyecto)')
        return False
    
    # Click en 'Aceptar' dentro de la ventana hija
    try:
        click_button_in_container(project_window, r'Aceptar|OK')
        logger.info('Click en Aceptar (ventana Abrir proyecto)')
    except ButtonNotFoundError as e:
        logger.warning(f'No se encontró botón Aceptar: {e}')
        return False
    
    # Esperar a que se cierre y cambie el título
    time.sleep(2)
    
    return True


def wait_for_main_verification_window(app: Application, timeout: int = 60) -> WindowSpecification:
    '''
    Espera a que aparezca la ventana principal de la Estación de Verificación.
    Título esperado: 'ABBYY FlexiCapture 12 (Estación de verificación)'
    '''
    logger.info('Esperando ventana principal de Estación de Verificación')
    return wait_for_window(app, r'ABBY.*FlexiCapture.*Estaci[oó]n.*verificaci[oó]n|FlexiCapture.*Verificaci[oó]n', timeout=timeout)


def close_window(window: WindowSpecification) -> bool:
    '''
    Intenta cerrar una ventana usando el botón X o Alt+F4.
    '''
    try:
        window.close()
        return True
    except Exception:
        try:
            window.type_keys('%{F4}')
            return True
        except Exception:
            return False
