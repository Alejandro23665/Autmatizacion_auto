with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\window_utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find exact location
idx = content.find('Try 4 error')
if idx >= 0:
    # Get the exact bytes around it
    context = content[idx-200:idx+100]
    print('CONTEXT:')
    print(repr(context))
    print()
    
    # Check the exact line structure
    for i, ch in enumerate(context):
        if ch == '\n':
            print(f'[{i}] LF')
        elif ch == ' ':
            pass
        elif ch == '\t':
            print(f'[{i}] TAB')
        else:
            print(f'[{i}] {ch}')

# The fix - replace the two 'continue' lines with one
# Need to match exact whitespace
# The pattern has 12 spaces before 'except Exception:' then 2 lines
# Let's just do a simpler replacement

# Find the line numbers and do line-by-line
lines = content.split('\n')
print('\n--- Line analysis ---')
for i, line in enumerate(lines):
    if 'Try 4 error' in line:
        print(f'Line {i}: {repr(line)}')
    if 'continue' in line and i > 0:
        if 'except Exception:' in lines[i-1]:
            print(f'Line {i-1}: {repr(lines[i-1])}')
            print(f'Line {i}:   {repr(line)}')