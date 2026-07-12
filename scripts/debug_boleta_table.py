import sys, time, re
sys.path.insert(0, r'src')
from pywinauto import Application

EXE_PATH = r'C:\Program Files\ABBYY FlexiCapture 12 Stations\FlexiCapture.exe'

app = Application(backend='uia').start(EXE_PATH)
time.sleep(2)

# Click modo
for w in app.windows():
    if 'Seleccionar' in w.window_text() and 'modo' in w.window_text().lower():
        for c in w.descendants():
            if c.element_info.control_type == 'Button' and 'aceptar' in c.window_text().lower():
                c.click()
                print('Clicked modo Aceptar')
                break
        break

time.sleep(3)

# Esperar y click abrir proyecto
for i in range(20):
    for w in app.windows():
        if 'Abrir proyecto' in w.window_text():
            print('Found Abrir proyecto:', w.window_text())
            for c in w.descendants():
                if c.element_info.control_type == 'Button' and 'aceptar' in c.window_text().lower():
                    c.click()
                    print('Clicked abrir proyecto Aceptar')
                    break
            break
    time.sleep(1)

time.sleep(5)

# Encontrar main window
main = None
for w in app.windows():
    txt = w.window_text()
    if 'Proyecto_Consorcio' in txt and 'Estaci' in txt:
        main = w
        break

if not main:
    print('Main not found, listing all windows:')
    for w in app.windows():
        t = w.window_text()
        if t:
            print(f'  \"{t}\" | class={w.class_name()} | handle={w.handle}')
    exit()

print('Main window:', main.window_text())

# Click AUTO + Ctrl+G
from automation.window_utils import find_table, get_table_rows, get_cell_text, click_row

table = find_table(main)
if table:
    rows = get_table_rows(table)
    for r in rows:
        if get_cell_text(r, 0).upper() == 'AUTO':
            click_row(r, 'left')
            time.sleep(0.5)
            r.type_keys('^g')
            print('Clicked AUTO + Ctrl+G')
            break

time.sleep(5)

print('\n=== Ventanas despues de Ctrl+G ===')
for w in app.windows():
    t = w.window_text()
    if t:
        print(f'  \"{t}\" | class={w.class_name()} | handle={w.handle}')

print('\n=== Descendientes de main (buscando tabla/grid/list) ===')
for c in main.descendants():
    try:
        ctrl = c.element_info.control_type
        txt = c.window_text().strip()
        if ctrl and ctrl.lower() in ('table', 'listview', 'datagrid', 'grid', 'list', 'custom', 'pane', 'tree', 'treeitem'):
            has_kids = len(list(c.descendants())) > 0
            print(f'  {ctrl}: \"{txt[:50]}\" | children={has_kids}')
    except:
        pass

print('\n=== Todos los controles tipo ListItem/Row/DataItem/Custom con texto ===')
for c in main.descendants():
    try:
        ctrl = c.element_info.control_type
        txt = c.window_text().strip()
        if ctrl and ctrl.lower() in ('listitem', 'row', 'dataitem', 'custom', 'treeitem') and txt:
            print(f'  {ctrl}: \"{txt[:80]}\"')
    except:
        pass
