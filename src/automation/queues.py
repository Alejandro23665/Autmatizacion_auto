import time
import logging
import re
from typing import Optional, List, Tuple
from pywinauto import Application, WindowSpecification
from .window_utils import (
    find_child_window, get_table_rows, get_cell_text, find_row_by_col_text,
    click_row, send_enter, get_window_info, wait_for_window,
    wait_for_title_change_pattern, WindowNotFoundError, ButtonNotFoundError,
    find_table, find_boleta_table, get_table_rows_with_cells,
    get_cell_object, is_cell_green_verified, wait_for_boleta_load,
    get_cell_font_color, BOLETA_TITLE_PATTERN,
    detect_error_modal, click_cancelar_modal, click_80_percent_left, select_fase_verificacion_javier
)

logger = logging.getLogger(__name__)


def find_queue_table(main_window: WindowSpecification, timeout: int = 15) -> Optional[WindowSpecification]:
    control_types = ('table', 'listview', 'datagrid', 'grid', 'list', 'custom', 'pane', 'tree')
    
    start = time.time()
    while time.time() - start < timeout:
        for ctrl_type in control_types:
            try:
                table = find_child_window(main_window, r'.*', control_types=(ctrl_type,))
                if table:
                    rows = get_table_rows(table)
                    if rows:
                        logger.info(f'Tabla de colas encontrada: tipo={ctrl_type}, filas={len(rows)}')
                        return table
            except Exception:
                continue
        time.sleep(0.5)
    
    logger.warning('No se encontr\u00f3 tabla de colas con filas')
    return None


def get_table_rows(table: WindowSpecification) -> List[WindowSpecification]:
    row_types = ('listitem', 'row', 'dataitem', 'custom', 'treeitem', 'group')
    rows = []
    
    try:
        for child in table.descendants():
            try:
                ctrl_type = child.element_info.control_type
                if ctrl_type and ctrl_type.lower() in row_types:
                    text = child.window_text()
                    if text and text.strip():
                        rows.append(child)
            except Exception:
                continue
    except Exception:
        pass
    
    return rows


def get_cell_text(row: WindowSpecification, col_index: int) -> str:
    cell_types = ('text', 'edit', 'custom', 'dataitem', 'static')
    
    try:
        cells = []
        for child in row.descendants():
            try:
                ctrl_type = child.element_info.control_type
                if ctrl_type and ctrl_type.lower() in cell_types:
                    text = child.window_text()
                    if text is not None:
                        cells.append(text.strip())
            except Exception:
                continue
        
        if 0 <= col_index < len(cells):
            return cells[col_index]
    except Exception:
        pass
    
    return ''


def find_auto_row(table: WindowSpecification, timeout: int = 10) -> Optional[WindowSpecification]:
    start = time.time()
    while time.time() - start < timeout:
        rows = get_table_rows(table)
        for row in rows:
            cell_text = get_cell_text(row, 0)
            if cell_text.upper() == 'AUTO':
                logger.info(f'Fila AUTO encontrada: \"{cell_text}\"')
                return row
        time.sleep(0.5)
    
    logger.warning('Fila AUTO no encontrada en la tabla de colas')
    return None


def process_auto_queue_loop(main_window, app, auto_count, timeout=120):
    """
    Procesa N boletas de la cola AUTO en loop:
    - Iteracion 1: Click AUTO + Ctrl+G + Alt+G (una vez) -> esperar boleta -> Ctrl+L -> 5s
    - Iteraciones 2..N: esperar cambio de titulo -> Ctrl+L -> 5s
    - Al final: cerrar app
    """
    logger.info('=== LOOP AUTO: Procesando {} boletas ==='.format(auto_count))
    
    table = find_queue_table(main_window, timeout=15)
    if not table:
        logger.error('No se pudo encontrar la tabla de colas')
        return False
    
    auto_row = find_auto_row(table, timeout=10)
    if not auto_row:
        logger.error('No se encontro la fila AUTO')
        return False
    
    try:
        logger.info('Click izquierdo en fila AUTO...')
        if not click_row(auto_row, button="left"):
            logger.error('Fallo click izquierdo en fila AUTO')
            return False
        
        import time
        time.sleep(0.5)
        
        logger.info('Enviando Ctrl+G para abrir primera boleta...')
        try:
            auto_row.type_keys('^g')
        except Exception as e:
            logger.error('Fallo envio de Ctrl+G: {}'.format(e))
            return False
        
        time.sleep(0.5)
        
        logger.info('Enviando Alt+G para carga automatica de lotes...')
        try:
            # Enviar Alt+G a la ventana principal (app level) porque el foco cambia tras Ctrl+G
            main_window.type_keys('%g')
        except Exception as e:
            logger.error('Fallo envio de Alt+G: {}'.format(e))
            return False
        
        boleta_window = None
        
        for i in range(auto_count):
            if i == 0:
                logger.info('Procesando boleta 1/{} (primera)'.format(auto_count))
                try:
                    boleta_window = wait_for_title_change_pattern(app, BOLETA_TITLE_PATTERN, timeout=timeout, exclude_handles=[])
                    logger.info('Primera boleta cargada: "{}"'.format(boleta_window.window_text()))
                except WindowNotFoundError:
                    logger.warning('Titulo no cambio al patron esperado, verificando ventana principal...')
                    main_title = main_window.window_text()
                    import re
                    if re.search(BOLETA_TITLE_PATTERN, main_title, re.IGNORECASE):
                        logger.info('Primera boleta ya cargada: "{}"'.format(main_title))
                        boleta_window = main_window
                    else:
                        logger.error('No se detecto carga de primera boleta')
                        return False
            else:
                logger.info('Procesando boleta {}/{}'.format(i+1, auto_count))
                try:
                    boleta_window = wait_for_title_change_pattern(app, BOLETA_TITLE_PATTERN, timeout=timeout, exclude_handles=[])
                    logger.info('Boleta {} cargada: "{}"'.format(i+1, boleta_window.window_text()))
                except WindowNotFoundError:
                    logger.error('No se detecto carga de boleta {}'.format(i+1))
                    return False
            
            # ===== NUEVO: Detectar y manejar modal de error =====
            logger.info(f"DEBUG: Verificando modal de error en boleta {i+1}")
            error_detected, error_modal = detect_error_modal(app, main_window)
            logger.info(f"DEBUG: detect_error_modal returned: error_detected={error_detected}")
            if error_detected:
                logger.info('Modal de error detectado en boleta {} - manejando...'.format(i+1))
                
                # 1. Click en Cancelar en el modal
                if not click_cancelar_modal(error_modal):
                    logger.error('No se pudo hacer click en Cancelar')
                    return False
                time.sleep(0.5)
                
                # 2. Click en 80% izquierda (evita boletas centradas)
                if not click_80_percent_left(boleta_window):
                    logger.error('No se pudo hacer click 80% izquierda')
                    return False
                time.sleep(0.5)
                
                # 3. Seleccionar "Verificación Javier" en ComboBox "Fases disponibles" + Aceptar
                if not select_fase_verificacion_javier(boleta_window):
                    logger.error('No se pudo seleccionar Verificación Javier')
                    return False
                time.sleep(1)
                
                logger.info('Boleta con error procesada, continuando al siguiente lote')
                continue  # Pasar al siguiente lote
            # =====================================================
            
            logger.info('Enviando Ctrl+L en boleta {}...'.format(i+1))
            try:
                boleta_window.type_keys('^l')
                logger.info('Ctrl+L enviado en boleta {}'.format(i+1))
            except Exception as e:
                logger.error('Fallo Ctrl+L en boleta {}: {}'.format(i+1, e))
                return False
            
            logger.info('Esperando 1 segundo...')
            time.sleep(1)
        
        logger.info('Loop completado. Cerrando aplicacion...')
        try:
            boleta_window.close()
            logger.info('Aplicacion cerrada')
        except Exception as e:
            logger.warning('Error cerrando app: {}'.format(e))
            try:
                boleta_window.type_keys('%{F4}')
            except Exception:
                pass
        
        return True
        
    except Exception as e:
        logger.error('Error en loop AUTO: {}'.format(e))
        return False


def select_auto_queue_and_open_boleta(main_window: WindowSpecification, app: Application, timeout: int = 40) -> Optional[WindowSpecification]:
    '''
    Click fila AUTO + Ctrl+G para abrir PRIMERA boleta.
    Retorna la ventana principal con t\u00edtulo actualizado (misma ventana).
    '''
    logger.info('=== Seleccionando cola AUTO y abriendo primera boleta ===')
    
    table = find_queue_table(main_window, timeout=15)
    if not table:
        logger.error('No se pudo encontrar la tabla de colas')
        return None
    
    auto_row = find_auto_row(table, timeout=10)
    if not auto_row:
        logger.error('No se encontr\u00f3 la fila AUTO')
        return None
    
    # === NUEVO PASO 4: Leer recuento de AUTO (columna 3) ===
    recuento_text = get_cell_text(auto_row, 3)
    logger.info(f'Cantidad de AUTO (Recuento tareas con forma): {recuento_text}')
    print(f'Cantidad de AUTO: {recuento_text}')
    
    # Click IZQUIERDO en la fila AUTO (selecciona, fondo azul)
    logger.info('Click izquierdo en fila AUTO...')
    if not click_row(auto_row, button='left'):
        logger.error('Fall\u00f3 click izquierdo en fila AUTO')
        return None
    
    time.sleep(0.5)
    
    # Ctrl+G para abrir primera boleta
    logger.info('Enviando Ctrl+G para abrir primera boleta...')
    try:
        auto_row.type_keys('^g')
    except Exception as e:
        logger.error(f'Fall\u00f3 env\u00edo de Ctrl+G: {e}')
        return None
    
    # Esperar que el t\u00edtulo de la ventana principal cambie (misma ventana)
    logger.info('Esperando carga de primera boleta (cambio de t\u00edtulo en ventana principal)...')
    try:
        updated_window = wait_for_title_change_pattern(app, BOLETA_TITLE_PATTERN, timeout=timeout, exclude_handles=[])
        logger.info(f'\u2705 Primera boleta cargada en ventana principal: \"{updated_window.window_text()}\"')
        return updated_window
    except WindowNotFoundError:
        logger.warning('T\u00edtulo no cambi\u00f3 al patr\u00f3n esperado, verificando ventana principal actual...')
        main_title = main_window.window_text()
        if re.search(BOLETA_TITLE_PATTERN, main_title, re.IGNORECASE):
            logger.info(f'\u2705 Primera boleta ya cargada en ventana principal: \"{main_title}\"')
            return main_window
        
        logger.error('No se detect\u00f3 carga de primera boleta')
        return None


def post_boleta_action(boleta_window: WindowSpecification) -> bool:
    '''
    TAREA 3: Acci\u00f3n despu\u00e9s de abrir la boleta
    1. Ctrl+L en la ventana de la boleta
    2. Esperar 10 segundos
    3. Cerrar la aplicaci\u00f3n
    
    Returns:
        True si \u00e9xito, False si falla
    '''
    logger.info('=== TAREA 3: Acci\u00f3n post-boleta ===')
    
    try:
        logger.info('Enviando Ctrl+L...')
        boleta_window.type_keys('^l')
        logger.info('Ctrl+L enviado')
        
        logger.info('Esperando 10 segundos...')
        time.sleep(10)
        
        logger.info('Cerrando aplicaci\u00f3n...')
        boleta_window.close()
        logger.info('Aplicaci\u00f3n cerrada')
        
        return True
        
    except Exception as e:
        logger.error(f'Error en Tarea 3: {e}')
        return False


def find_auto_queue_table(main_window: WindowSpecification) -> Optional[WindowSpecification]:
    return find_table(main_window)
