import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from automation.launch_app import launch_verification_station, launch_and_get_info


def test_full_flow():
    print('=' * 70)
    print('TEST COMPLETO: Tareas 1+2+3+4 (Loop AUTO + Verificacion)')
    print('=' * 70)
    
    try:
        info = launch_and_get_info(
            timeout_main_window=60,
            timeout_dialogs=30,
            timeout_project_window=15,
            timeout_queue_selection=40
        )
        
        print('\n' + '=' * 70)
        print('RESULTADO FINAL:')
        print('=' * 70)
        print(f'  App PID: {info.get(\"app_pid\")}')
        print(f'  Main Window: {info.get(\"main_window_title\")}')
        print(f'  Main Handle: {info.get(\"handle\")}')
        print(f'  Main Size: {info.get(\"width\")}x{info.get(\"height\")}')
        
        if info.get('boleta_window'):
            bw = info['boleta_window']
            print(f'\n  BOLETA ABIERTA:')
            print(f'    Titulo: {info.get(\"boleta_title\")}')
            print(f'    Handle: {bw.get(\"handle\")}')
            print(f'    Size: {bw.get(\"width\")}x{bw.get(\"height\")}')
        else:
            print(f'\n  NO SE ABRIO BOLETA')
            print(f'    Titulo: {info.get(\"boleta_title\")}')
        
        print('\n[OK] Test completado')
        print('La aplicacion queda abierta para inspeccion manual.')
        print('Manteniendo la app abierta por 15 segundos...')
        time.sleep(15)
        
        return True
        
    except Exception as e:
        print(f'\n[ERROR] {e}')
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_full_flow()
    sys.exit(0 if success else 1)
