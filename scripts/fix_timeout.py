with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\queues.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("logger.info('Esperando 5 segundos...')", "logger.info('Esperando 1 segundo...')")
content = content.replace('time.sleep(5)', 'time.sleep(1)')

with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\queues.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')