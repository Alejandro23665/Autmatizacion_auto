import re
import time
import logging
from typing import Optional, Dict, Any, List, Tuple
from pywinauto import Application, WindowSpecification
from pywinauto.timings import TimeoutError as PywinautoTimeoutError

logger = logging.getLogger(__name__)


class WindowNotFoundError(Exception):
    pass


class ButtonNotFoundError(Exception):
    pass


# Patr\u00f3n simplificado sin acentos problem\u00e1ticos
BOLETA_TITLE_PATTERN = r'Proyecto_Consorcio.*FlexiCapture 12.*Estaci.n de verificaci.n.*\d{2}-\d{2}-\d{4}_\d+'


def wait_for_window(
    app: Application,
    title_re: str,
    timeout: int = 30,
    backend: str = 'uia'
) -> WindowSpecification:
    start = time.time()
    pattern = re.compile(title_re, re.IGNORECASE)
    
    while time.time() - start < timeout:
        try:
            for window in app.windows():
                if pattern.search(window.window_text()):
                    return window
        except Exception:
            pass
        time.sleep(0.5)
    
    raise WindowNotFoundError(f'Ventana con t\u00edtulo matching \'{title_re}\' no encontrada en {timeout}s')


def wait_for_title_change(
    app: Application,
    title_re: str,
    timeout: int = 15
) -> WindowSpecification:
    start = time.time()
    pattern = re.compile(title_re, re.IGNORECASE)
    
    while time.time() - start < timeout:
        try:
            for window in app.windows():
                title = window.window_text()
                if pattern.search(title):
                    return window
        except Exception:
            pass
        time.sleep(0.5)
    
    raise WindowNotFoundError(f'T\u00edtulo matching \'{title_re}\' no apareci\u00f3 en {timeout}s')


def wait_for_title_change_pattern(
    app: Application,
    title_pattern_re: str,
    timeout: int = 40,
    exclude_handles: list = None
) -> WindowSpecification:
    if exclude_handles is None:
        exclude_handles = []
    
    start = time.time()
    pattern = re.compile(title_pattern_re, re.IGNORECASE)
    
    while time.time() - start < timeout:
        try:
            for window in app.windows():
                if window.handle in exclude_handles:
                    continue
                title = window.window_text()
                if pattern.search(title):
                    return window
        except Exception:
            pass
        time.sleep(0.5)
    
    raise WindowNotFoundError(f'T\u00edtulo matching patr\u00f3n \'{title_pattern_re}\' no apareci\u00f3 en {timeout}s')


def find_window_by_title_re(app: Application, title_re: str) -> Optional[WindowSpecification]:
    pattern = re.compile(title_re, re.IGNORECASE)
    try:
        for window in app.windows():
            if pattern.search(window.window_text()):
                return window
    except Exception:
        pass
    return None


def find_child_window(parent: WindowSpecification, title_re: str, control_types: tuple = None) -> Optional[WindowSpecification]:
    pattern = re.compile(title_re, re.IGNORECASE)
    
    if control_types is None:
        control_types = ('window', 'custom', 'pane', 'group', 'panel', 'tabitem', 'tab')
    
    try:
        for child in parent.descendants():
            try:
                ctrl_type = child.element_info.control_type
                if ctrl_type and ctrl_type.lower() in control_types:
                    text = child.window_text()
                    if pattern.search(text):
                        return child
            except Exception:
                continue
    except Exception:
        pass
    
    return None


def find_table(window: WindowSpecification, control_types: tuple = None) -> Optional[WindowSpecification]:
    if control_types is None:
        control_types = ('table', 'listview', 'datagrid', 'grid', 'list', 'custom', 'pane')
    
    try:
        for child in window.descendants():
            try:
                ctrl_type = child.element_info.control_type
                if ctrl_type and ctrl_type.lower() in control_types:
                    has_items = False
                    for sub in child.descendants():
                        try:
                            sub_type = sub.element_info.control_type
                            if sub_type and sub_type.lower() in ('listitem', 'row', 'dataitem', 'custom'):
                                has_items = True
                                break
                        except Exception:
                            continue
                    if has_items:
                        return child
            except Exception:
                continue
    except Exception:
        pass
    
    return None


def find_boleta_table(main_window: WindowSpecification, timeout: int = 10) -> Optional[WindowSpecification]:
    start = time.time()
    while time.time() - start < timeout:
        for child in main_window.descendants():
            try:
                ctrl_type = child.element_info.control_type
                if ctrl_type and ctrl_type.lower() in ('table', 'listview', 'datagrid', 'grid', 'list', 'custom', 'pane', 'tree'):
                    has_rows = False
                    for sub in child.descendants():
                        try:
                            sub_type = sub.element_info.control_type
                            if sub_type and sub_type.lower() in ('listitem', 'row', 'dataitem', 'custom', 'treeitem', 'group'):
                                text = sub.window_text().strip()
                                if text:
                                    has_rows = True
                                    break
                        except Exception:
                            continue
                    
                    if has_rows:
                        return child
            except Exception:
                continue
        time.sleep(0.5)
    
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


def get_table_rows_with_cells(table: WindowSpecification) -> List[List[str]]:
    result = []
    rows = get_table_rows(table)
    
    for row in rows:
        cells = []
        try:
            for child in row.descendants():
                try:
                    ctrl_type = child.element_info.control_type
                    if ctrl_type and ctrl_type.lower() in ('text', 'edit', 'custom', 'dataitem', 'static'):
                        text = child.window_text()
                        if text is not None:
                            cells.append(text.strip())
                except Exception:
                    continue
        except Exception:
            pass
        
        if cells:
            result.append(cells)
    
    return result


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


def get_cell_object(row: WindowSpecification, col_index: int) -> Optional[WindowSpecification]:
    cell_types = ('text', 'edit', 'custom', 'dataitem', 'static')
    
    try:
        cells = []
        for child in row.descendants():
            try:
                ctrl_type = child.element_info.control_type
                if ctrl_type and ctrl_type.lower() in cell_types:
                    text = child.window_text()
                    if text is not None:
                        cells.append(child)
            except Exception:
                continue
        
        if 0 <= col_index < len(cells):
            return cells[col_index]
    except Exception:
        pass
    
    return None


def get_cell_font_color(cell: WindowSpecification) -> Optional[Tuple[int, int, int]]:
    try:
        font = cell.element_info.font
        if font:
            color = font.color
            if color:
                return (color.red, color.green, color.blue)
    except Exception:
        pass
    
    try:
        import win32gui
        hwnd = cell.handle
        hdc = win32gui.GetDC(hwnd)
        color_ref = win32gui.GetTextColor(hdc)
        win32gui.ReleaseDC(hwnd, hdc)
        r = color_ref & 0xFF
        g = (color_ref >> 8) & 0xFF
        b = (color_ref >> 16) & 0xFF
        return (r, g, b)
    except Exception:
        pass
    
    return None


def is_cell_green_verified(cell: WindowSpecification) -> bool:
    try:
        text = cell.window_text().strip()
        if text != 'Verificado':
            return False
        
        color = get_cell_font_color(cell)
        if color is None:
            return True
        
        r, g, b = color
        return g > 100 and g > r and g > b and r < 120 and b < 120
    except Exception:
        return False


def wait_for_boleta_load(app: Application, main_window: WindowSpecification, timeout: int = 10, retries: int = 3) -> Optional[WindowSpecification]:
    for attempt in range(retries):
        start = time.time()
        while time.time() - start < timeout:
            boleta_table = find_boleta_table(main_window)
            if boleta_table:
                rows = get_table_rows(boleta_table)
                if rows and len(rows) > 0:
                    return boleta_table
            time.sleep(0.5)
        
        if attempt < retries - 1:
            time.sleep(1)
    
    return None


def find_row_by_col_text(table: WindowSpecification, col_index: int, target_text: str, exact: bool = True, timeout: int = 10) -> Optional[WindowSpecification]:
    pattern = re.compile(re.escape(target_text), re.IGNORECASE) if not exact else None
    
    start = time.time()
    while time.time() - start < timeout:
        rows = get_table_rows(table)
        for row in rows:
            cell_text = get_cell_text(row, col_index)
            if exact:
                if cell_text == target_text:
                    return row
            else:
                if pattern and pattern.search(cell_text):
                    return row
        time.sleep(0.5)
    return None


def click_button(window: WindowSpecification, button_text_re: str) -> bool:
    pattern = re.compile(button_text_re, re.IGNORECASE)
    
    try:
        for child in window.descendants():
            try:
                if child.element_info.control_type and child.element_info.control_type.lower() == 'button':
                    text = child.window_text()
                    if pattern.search(text):
                        child.click()
                        return True
            except Exception:
                continue
    except Exception:
        pass
    
    try:
        for child in window.descendants():
            try:
                auto_id = child.element_info.automation_id
                if auto_id and auto_id.lower() in ('ok', 'accept', 'btnok', 'btnaccept', '1'):
                    if pattern.search(child.window_text()) or True:
                        child.click()
                        return True
            except Exception:
                continue
    except Exception:
        pass
    
    raise ButtonNotFoundError(f'Bot\u00f3n con texto matching \'{button_text_re}\' no encontrado en ventana \'{window.window_text()}\'')


def click_button_in_container(container: WindowSpecification, button_text_re: str) -> bool:
    pattern = re.compile(button_text_re, re.IGNORECASE)
    
    try:
        for child in container.descendants():
            try:
                if child.element_info.control_type and child.element_info.control_type.lower() == 'button':
                    text = child.window_text()
                    if pattern.search(text):
                        child.click()
                        return True
            except Exception:
                continue
    except Exception:
        pass
    
    raise ButtonNotFoundError(f'Bot\u00f3n \'{button_text_re}\' no encontrado en contenedor \'{container.window_text()}\'')


def click_row(row: WindowSpecification, button: str = 'right') -> bool:
    try:
        if button.lower() == 'right':
            row.click_input(button='right')
        else:
            row.click_input(button='left')
        return True
    except Exception:
        try:
            if button.lower() == 'right':
                row.type_keys('+{F10}')
            else:
                row.click()
            return True
        except Exception:
            pass
    return False


def send_enter(target: WindowSpecification) -> bool:
    try:
        target.type_keys('{ENTER}')
        return True
    except Exception:
        try:
            from pywinauto import Application
            app = Application(backend='uia').connect(handle=target.handle)
            app.type_keys('{ENTER}')
            return True
        except Exception:
            pass
    return False


def get_window_info(window: WindowSpecification) -> Dict[str, Any]:
    try:
        rect = window.rectangle()
        return {
            'handle': window.handle,
            'title': window.window_text(),
            'class_name': window.class_name(),
            'rect': {'left': rect.left, 'top': rect.top, 'right': rect.right, 'bottom': rect.bottom},
            'width': rect.width(),
            'height': rect.height(),
        }
    except Exception as e:
        return {'error': str(e)}


def wait_for_window_close(window: WindowSpecification, timeout: int = 10) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        try:
            if not window.exists():
                return True
        except Exception:
            return True
        time.sleep(0.5)
    return False


def detect_error_modal(app: Application, main_window: WindowSpecification = None) -> tuple:
    """
    Detecta si hay un modal de error abierto.
    Título esperado exacto: 'ABBYY FlexiCapture 12 (Estación de verificación)'
    El modal es un diálogo con botones Sí/No/Cancelar.
    Retorna (True, modal_window) si se encuentra, (False, None) si no.
    """
    try:
        # Buscar en ventanas top-level de la app
        logger.info(f"DEBUG detect_error_modal: Checking {len(app.windows())} top-level windows")
        for window in app.windows():
            try:
                title = window.window_text()
                logger.info(f"DEBUG: Checking window: '{title}' (len={len(title)})")
                # El modal tiene título EXACTO sin prefijo http://
                if title == 'ABBYY FlexiCapture 12 (Estación de verificación)' or \
                   (not title.startswith('http://') and 'ABBYY FlexiCapture 12' in title and 'Estación de verificación' in title and len(title) < 60):
                    # Verificar que tiene botones Sí/No/Cancelar
                    buttons = []
                    for child in window.descendants():
                        try:
                            if child.element_info.control_type and child.element_info.control_type.lower() == 'button':
                                text = child.window_text().strip().lower()
                                if text in ('sí', 'si', 'yes', 'no', 'cancelar', 'cancel'):
                                    buttons.append(text)
                        except Exception:
                            continue
                    if len(buttons) >= 2:
                        logger.info(f"Modal de error detectado: '{title}' - Botones: {buttons}")
                        return True, window
            except Exception as e:
                logger.info(f"DEBUG: Error checking window: {e}")
                continue
        
        # Si no se encontró en top-level, buscar en hijos de la ventana principal
        if main_window:
            try:
                for child in main_window.descendants():
                    try:
                        ctrl_type = child.element_info.control_type
                        if ctrl_type and ctrl_type.lower() in ('window', 'dialog', 'pane'):
                            title = child.window_text()
                            if title == 'ABBYY FlexiCapture 12 (Estación de verificación)' or \
                               (not title.startswith('http://') and 'ABBYY FlexiCapture 12' in title and 'Estación de verificación' in title and len(title) < 60):
                                buttons = []
                                for sub in child.descendants():
                                    try:
                                        if sub.element_info.control_type and sub.element_info.control_type.lower() == 'button':
                                            text = sub.window_text().strip().lower()
                                            if text in ('sí', 'si', 'yes', 'no', 'cancelar', 'cancel'):
                                                buttons.append(text)
                                    except Exception:
                                        continue
                                if len(buttons) >= 2:
                                    logger.info(f"Modal de error detectado (hijo): '{title}' - Botones: {buttons}")
                                    return True, child
                    except Exception:
                        continue
            except Exception as e:
                logger.info(f"DEBUG: Error searching children: {e}")
    except Exception as e:
        logger.info(f"Error detectando modal: {e}")
    return False, None


def click_cancelar_modal(modal: WindowSpecification) -> bool:
    """Click en botón Cancelar del modal de error."""
    try:
        for child in modal.descendants():
            try:
                if child.element_info.control_type and child.element_info.control_type.lower() == 'button':
                    text = child.window_text().strip().lower()
                    if text in ('cancelar', 'cancel'):
                        child.click()
                        logger.info("Click en Cancelar del modal")
                        return True
            except Exception:
                continue
    except Exception as e:
        logger.error(f"Error click Cancelar: {e}")
    return False


def click_80_percent_left(window: WindowSpecification) -> bool:
    """
    Click DERECHO en 20% desde la izquierda (80% desde borde izquierdo, 50% desde arriba).
    Es un click DERECHO para abrir el menú contextual con 'Fases disponibles'.
    """
    try:
        rect = window.rectangle()
        x = rect.left + int(rect.width() * 0.2)
        y = rect.top + int(rect.height() * 0.5)
        window.click_input(button='right', coords=(x, y))
        logger.info(f"Click DERECHO 80% izquierda en ({x}, {y})")
        return True
    except Exception as e:
        logger.error(f"Error click DERECHO 80% izquierda: {e}")
        return False


def select_fase_verificacion_javier(window: WindowSpecification) -> bool:
    """
    Flujo correcto (click DERECHO abre menú 'Contexto'):
    1. El menú contextual 'Contexto' ya está abierto (se abrió con click derecho)
    2. Click IZQUIERDO en 'Enviar a etapa' en el menú
    3. Se abre ventana hija 'Enviar tarea a etapa'
    4. En esa ventana: buscar 'Fases disponibles' -> click 'Verificación Javier' -> Click 'Aceptar'
    """
    try:
        logger.info("DEBUG: Buscando menú contextual 'Contexto' y opción 'Enviar a etapa'...")
        
        # Buscar en ventanas top-level (popup menus) el menú "Contexto"
        from pywinauto import Application
        app = Application(backend='uia').connect(handle=window.handle)
        
        # Buscar el menú contextual "Contexto"
        for popup in app.windows():
            try:
                title = popup.window_text()
                ctrl_type = popup.element_info.control_type
                logger.info(f"DEBUG: Ventana popup: '{title}' type={ctrl_type}")
                
                if ctrl_type and ctrl_type.lower() in ('menu', 'popup') and title:
                    logger.info(f"DEBUG: Popup menu encontrado: '{title}' type={ctrl_type}")
                    
                    # Buscar "Enviar a etapa" en el menú
                    for child in popup.descendants():
                        try:
                            text = child.window_text().strip()
                            if 'enviar' in text.lower() and 'etapa' in text.lower():
                                logger.info(f"Encontrado 'Enviar a etapa': '{child.window_text()}'")
                                # Click IZQUIERDO en "Enviar a etapa"
                                child.click_input()
                                logger.info("Click IZQUIERDO en 'Enviar a etapa'")
                                time.sleep(0.5)
                                break
                        except Exception:
                            continue
            except Exception:
                continue
        
        # Esperar a que se abra la ventana hija "Enviar tarea a etapa"
        time.sleep(0.5)
        
# Buscar la ventana hija "Enviar tarea a etapa" - buscar ventana distinta a main_window
        enviar_window = None
        for w in app.windows():
            try:
                title = w.window_text()
                # Buscar ventana que no sea la main_window y que parezca un diálogo (sin http://)
                # y que tenga palabras clave de "enviar" o "etapa" o "tarea"
                if w.handle != window.handle and title:
                    if not title.startswith('http://'):
                        logger.info(f"  Ventana candidata: '{title}' type={w.element_info.control_type}")
                        # Aceptar cualquier ventana hija que no sea la main y no tenga http://
                        enviar_window = w
                        logger.info(f"Ventana hija encontrada: '{title}'")
                        break
            except Exception:
                continue
        
        if not enviar_window:
            logger.warning("Ventana 'Enviar tarea a etapa' no encontrada en app.windows()")
            # Buscar en hijos de la ventana principal
            logger.info("Buscando en hijos de la ventana principal...")
            for child in window.descendants():
                try:
                    title = child.window_text()
                    ctrl_type = child.element_info.control_type
                    if title and ctrl_type and ctrl_type.lower() in ('window', 'dialog', 'pane'):
                        logger.info(f"  Hijo candidato: '{title}' type={ctrl_type}")
                        if title == 'Enviar tarea a etapa':
                            enviar_window = child
                            logger.info(f"Ventana hija encontrada: '{title}'")
                            break
                except Exception:
                    pass
            
            # Debug: listar TODAS las ventanas en app.windows()
            logger.info("DEBUG: Todas las ventanas en app.windows():")
            for w in app.windows():
                try:
                    logger.info(f"  app.window: handle={w.handle} title='{w.window_text()}' type={w.element_info.control_type} class={w.class_name()} rect={w.rectangle()}")
                except Exception:
                    pass
            
            if not enviar_window:
                return False
        
        logger.info("Ventana 'Enviar tarea a etapa' encontrada, buscando 'Fases disponibles'...")
        
        # En la ventana "Enviar tarea a etapa", buscar "Fases disponibles"
        combo = None
        for child in enviar_window.descendants():
            try:
                ctrl_type = child.element_info.control_type
                text = child.window_text().strip().lower()
                if ctrl_type and ctrl_type.lower() in ('combobox', 'combo', 'splitbutton', 'button', 'menu', 'splitbuttondropdown', 'list'):
                    if 'fase' in text and 'disponible' in text:
                        combo = child
                        logger.info(f"ComboBox 'Fases disponibles' encontrado: {child.window_text()}")
                        break
            except Exception:
                continue
        
        if not combo:
            # Buscar por texto en hijos
            for child in enviar_window.descendants():
                try:
                    text = child.window_text().strip().lower()
                    if 'fase' in text and 'disponible' in text:
                        parent = child.parent()
                        if parent:
                            ctrl_type = parent.element_info.control_type
                            if ctrl_type and ctrl_type.lower() in ('combobox', 'combo', 'list'):
                                combo = parent
                                logger.info(f"ComboBox 'Fases disponibles' encontrado via hijo: {parent.window_text()}")
                                break
                except Exception:
                    continue
        
        if not combo:
            logger.warning("ComboBox 'Fases disponibles' no encontrado en ventana 'Enviar tarea a etapa'")
            # Debug: listar controles
            for child in enviar_window.descendants():
                try:
                    ctrl_type = child.element_info.control_type
                    text = child.window_text().strip()
                    if ctrl_type and text:
                        logger.info(f"DEBUG EnviarWindow: type={ctrl_type}, text='{text[:80]}'")
                except Exception:
                    continue
            return False
        
        # Click para expandir
        combo.click_input()
        time.sleep(0.5)
        
        # Buscar item "Verificación Javier"
        item_found = False
        for child in combo.descendants():
            try:
                text = child.window_text().strip().lower()
                if 'verificación' in text and 'javier' in text:
                    child.click_input()
                    logger.info(f"Seleccionado: {child.window_text()}")
                    item_found = True
                    break
            except Exception:
                continue
        
        if not item_found:
            try:
                combo.type_keys('verificacion javier')
                time.sleep(0.5)
                combo.type_keys('{ENTER}')
                logger.info("Seleccionado via type_keys")
            except Exception:
                logger.warning("No se pudo seleccionar 'Verificación Javier'")
                return False
        
        time.sleep(0.5)
        
        # Click en botón Aceptar en la ventana "Enviar tarea a etapa"
        for child in enviar_window.descendants():
            try:
                if child.element_info.control_type and child.element_info.control_type.lower() == 'button':
                    text = child.window_text().strip().lower()
                    if text in ('aceptar', 'ok', 'accept'):
                        child.click()
                        logger.info("Click en Aceptar en ventana 'Enviar tarea a etapa'")
                        return True
            except Exception:
                continue
        
        logger.warning("Botón Aceptar no encontrado en ventana 'Enviar tarea a etapa'")
        return False
        
    except Exception as e:
        logger.error(f"Error seleccionando fase: {e}")
        return False
