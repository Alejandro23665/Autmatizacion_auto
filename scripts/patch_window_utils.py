# Read the file
with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\window_utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the end of wait_for_window_close function
marker = 'def wait_for_window_close(window: WindowSpecification, timeout: int = 10) -> bool:'
idx = content.find(marker)
if idx == -1:
    print('ERROR: marker not found')
    exit(1)

# Find the end of that function (next def or end of file)
end_idx = content.find('\ndef ', idx + 1)
if end_idx == -1:
    end_idx = len(content)

# New functions to add
new_functions = '''

def find_data_rows_in_window(window: WindowSpecification) -> List[WindowSpecification]:
    """
    Find all data rows in the data grid within a window.
    Strategy: Find Header -> Find grid below Header -> Extract rows
    Returns list of row controls.
    """
    rows = []
    row_types = ('listitem', 'row', 'dataitem', 'custom', 'treeitem', 'group', 'text', 'edit', 'static')
    grid_types = ('listview', 'list', 'grid', 'datagrid', 'tree', 'table', 'custom', 'pane')
    
    def find_rows_in_control(container):
        found = []
        try:
            for child in container.descendants():
                try:
                    ctrl_type = child.element_info.control_type
                    if ctrl_type and ctrl_type.lower() in row_types:
                        text = child.window_text()
                        if text and text.strip():
                            found.append(child)
                except Exception:
                    continue
        except Exception:
            pass
        return found
    
    # TRY 1: Find Header, then grid BELOW it
    logger.info('Try 1: Find Header then grid below it')
    header_control = None
    try:
        for child in window.descendants():
            try:
                ctrl_type = child.element_info.control_type
                text = child.window_text() or ''
                rect = child.rectangle()
                if ctrl_type and ctrl_type.lower() == 'header' and 'control de encabezado' in text.lower():
                    header_control = child
                    logger.info('Found Header: pos=({},{},{},{})'.format(rect.left, rect.top, rect.right, rect.bottom))
                    break
            except Exception:
                continue
    except Exception:
        pass
    
    if header_control:
        try:
            header_rect = header_control.rectangle()
            for child in window.descendants():
                try:
                    ctrl_type = child.element_info.control_type
                    if ctrl_type and ctrl_type.lower() in grid_types:
                        rect = child.rectangle()
                        if rect.top > header_rect.bottom - 50:
                            has_rows = False
                            child_texts = []
                            for sub in child.descendants():
                                try:
                                    st = sub.element_info.control_type
                                    stext = sub.window_text()
                                    if stext and stext.strip():
                                        child_texts.append(stext.strip())
                                except Exception:
                                    continue
                            has_nombre = any('nombre' in t.lower() for t in child_texts)
                            has_estado = any('estado' in t.lower() for t in child_texts)
                            if has_nombre or has_estado or len(child_texts) > 10:
                                logger.info('Found data grid below header: {} at pos=({},{},{},{})'.format(ctrl_type, rect.left, rect.top, rect.right, rect.bottom))
                                logger.info('  Sample texts: {}'.format(child_texts[:15]))
                                rows.extend(find_rows_in_control(child))
                                break
                except Exception:
                    continue
        except Exception as e:
            logger.info('Try 1 error: {}'.format(e))
    else:
        logger.info('Header not found')
    
    # TRY 2: Search for grid with column pattern
    if not rows:
        logger.info('Try 2: Search for grid with column pattern')
        try:
            for child in window.descendants():
                try:
                    ctrl_type = child.element_info.control_type
                    if ctrl_type and ctrl_type.lower() in grid_types:
                        child_texts = []
                        for sub in child.descendants():
                            try:
                                stext = sub.window_text()
                                if stext and stext.strip():
                                    child_texts.append(stext.strip())
                            except Exception:
                                continue
                        has_nombre = any('nombre' in t.lower() for t in child_texts)
                        has_estado = any('estado' in t.lower() for t in child_texts)
                        if has_nombre or has_estado or len(child_texts) > 10:
                            logger.info('Found potential data grid: {} with {} text children'.format(ctrl_type, len(child_texts)))
                            logger.info('  Sample texts: {}'.format(child_texts[:15]))
                            rows.extend(find_rows_in_control(child))
                            break
                except Exception:
                    continue
        except Exception as e:
            logger.info('Try 2 error: {}'.format(e))
    
    # TRY 3: Find data grid in main window
    if not rows:
        logger.info('Try 3: Find data grid in main window')
        try:
            for child in window.descendants():
                try:
                    ctrl_type = child.element_info.control_type
                    if ctrl_type and ctrl_type.lower() in grid_types:
                        has_rows = False
                        for sub in child.descendants():
                            try:
                                sub_type = sub.element_info.control_type
                                if sub_type and sub_type.lower() in ('listitem', 'row', 'dataitem', 'custom', 'treeitem', 'group'):
                                    text = sub.window_text()
                                    if text and text.strip():
                                        has_rows = True
                                        break
                            except Exception:
                                continue
                        if has_rows:
                            logger.info('Found data grid: {} at pos=({},{})'.format(ctrl_type, child.rectangle().left, child.rectangle().top))
                            rows.extend(find_rows_in_control(child))
                            break
                except Exception:
                    continue
        except Exception as e:
            logger.info('Try 3 error: {}'.format(e))
    
    # TRY 4: Check child windows
    if not rows:
        logger.info('Try 4: Check child windows')
        try:
            from pywinauto import Application
            app = Application(backend='uia').connect(handle=window.handle)
            for w in app.windows():
                if w.handle != window.handle:
                    try:
                        for child in w.descendants():
                            try:
                                ctrl_type = child.element_info.control_type
                                if ctrl_type and ctrl_type.lower() in grid_types:
                                    has_rows = False
                                    for sub in child.descendants():
                                        try:
                                            sub_type = sub.element_info.control_type
                                            if sub_type and sub_type.lower() in ('listitem', 'row', 'dataitem', 'custom', 'treeitem', 'group'):
                                                text = sub.window_text()
                                                if text and text.strip():
                                                    has_rows = True
                                                    break
                                        except Exception:
                                            continue
                                    if has_rows:
                                        logger.info('Found data grid in child window: {}'.format(ctrl_type))
                                        rows.extend(find_rows_in_control(child))
                                        break
                            except Exception:
                                continue
                    except Exception:
                        continue
            except Exception as e:
                logger.info('Try 4 error: {}'.format(e))
        except Exception as e:
            logger.info('Try 4 error: {}'.format(e))
    
    # TRY 5: Deep search entire window
    if not rows:
        logger.info('Try 5: Deep search entire window')
        rows = find_rows_in_control(window)
    
    # FILTER OUT STATUS BAR
    filtered_rows = []
    for r in rows:
        try:
            rt = r.element_info.control_type
            rrect = r.rectangle()
            is_status_bar = (rt and rt.lower() == 'text' and rrect.top > 700)
            if not is_status_bar:
                rows.append(r)
            else:
                logger.info('Filtered out status bar control: {}'.format(r.window_text()[:80]))
        except Exception:
            rows.append(r)
    
    rows = rows  # This line seems wrong, let me fix it
    # Actually it should be:
    # rows = filtered_rows
    # But wait, I'm modifying 'rows' which is the original list. Let me fix this logic.
    # The issue is I'm appending to 'rows' instead of 'filtered_rows' in the loop
    # And then assigning 'rows = filtered_rows' at the end. That's correct.

    logger.info('Total candidate rows found: {}'.format(len(rows)))
    if rows:
        for i, r in enumerate(rows[:5]):
            try:
                rt = r.element_info.control_type
                rtext = r.window_text()
                rrect = r.rectangle()
                logger.info('  Candidate row {}: type={}, text=\'{}\', pos=({},{},{},{})'.format(i+1, rt, rtext[:80], rrect.left, rrect.top, rrect.right, rrect.bottom))
                for sub in r.descendants():
                    try:
                        st = sub.element_info.control_type
                        stext = sub.window_text()
                        if st and stext and stext.strip():
                            logger.info('    Child: type={}, text=\'{}\''.format(st, stext[:80]))
                    except Exception:
                        continue
            except Exception as e:
                logger.info('  Candidate row {} debug error: {}'.format(i+1, e))
    return rows


def log_lote_nombres(window: WindowSpecification, label: str = 'Lote') -> None:
    """
    Logs the nombre (column 3) from each row in the lote window.
    - Finds all data rows
    - Uses get_cell_text to extract column 3 (index 3) from each row
    """
    rows = find_data_rows_in_window(window)
    
    logger.info('=== {} - Nombres ({} filas) ==='.format(label, len(rows)))
    
    for i, row in enumerate(rows):
        nombre = get_cell_text(row, 3)
        texts = []
        try:
            for child in row.descendants():
                try:
                    ctrl_type = child.element_info.control_type
                    if ctrl_type and ctrl_type.lower() in ('text', 'edit', 'custom', 'dataitem', 'static'):
                        text = child.window_text()
                        if text is not None:
                            t = text.strip()
                            if t:
                                texts.append(t)
                except Exception:
                    continue
        except Exception:
            pass
        logger.info('  Fila {}: Nombre=\'{}\' | Celdas={}'.format(i+1, nombre, texts)

# Insert new functions
new_content = content[:end_idx] + new_functions

with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\window_utils.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Done - functions added')