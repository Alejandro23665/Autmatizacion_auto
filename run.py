import sys
sys.path.insert(0, 'src')

from automation.launch_app import launch_verification_station

if __name__ == '__main__':
    print('=== Iniciando flujo completo ABBYY FlexiCapture ===')
    try:
        app, main_window = launch_verification_station()
        print('=== Flujo completado ===')
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
