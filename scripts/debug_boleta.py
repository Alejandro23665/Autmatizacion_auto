import sys, time
sys.path.insert(0, r'src')
from pywinauto import Application

EXE_PATH = r'C:\Program Files\ABBYY FlexiCapture 12 Stations\FlexiCapture.exe'
app = Application(backend='uia').start(EXE_PATH)
time.sleep(2)

# Click en diálogo modo
for w in app.windows():
    if 'Seleccionar' in w.window_text() and 'modo' in w.window_text().lower():
        for c in w.descendants():
            if c.element_info.control_type == 'Button' and 'aceptar' in c.window_text().lower():
                c.click()
                break

time.sleep(3)

# Click en Abrir proyecto
for w in app.windows():
    if 'Abrir proyecto' in w.window_text():
        for c in w.descendants():
            if c.element_info.control_type == 'Button' and 'aceptar' in c.window_text().lower():
                c.click()
                break

time.sleep(5)

# Encontrar ventana principal
main = None
for w in app.windows():
    if 'Proyecto_Consorcio' in w.window_text() and 'Estaci' in w.window_text():
        main = w
        break

if main:
    print('Main window:', main.window_text())
    print('Handle:', main.handle)
    
    # Buscar tabla
    for c in main.descendants():
        if c.element_info.control_type in ('Table', 'ListView', 'DataGrid', 'Grid', 'List', 'Custom', 'Pane', 'Tree'):
            rows = [r for r in c.descendants() if r.element_info.control_type in ('ListItem', 'Row', 'Custom', 'TreeItem') and r.window_text().strip()]
            if rows:
                print('Table found:', c.element_info.control_type, '-', c.window_text())
                print('Rows:', len(rows))
                for i, r in enumerate(rows):
                    cells = []
                    for cc in r.descendants():
                        if cc.element_info.control_type in ('Text', 'Edit', 'Custom', 'DataItem', 'Static'):
                            txt = cc.window_text().strip()
                            if txt:
                                cells.append(txt)
                    print(f'  Row {i}: {cells}')
                break
