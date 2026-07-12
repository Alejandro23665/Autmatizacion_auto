import re
import time
from typing import Optional, Dict, Any, List, Tuple
from pywinauto import Application, WindowSpecification
from pywinauto.timings import TimeoutError as PywinautoTimeoutError


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
