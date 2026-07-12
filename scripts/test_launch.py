import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from automation.launch_app import launch_verification_station, launch_and_get_info
from automation.window_utils import get_window_info


def test_launch():
    print('=' * 60)
    print('TEST: Lanzar ABBYY FlexiCapture Verification Station')
    print('=' * 60)
    
    try:
        # Usar la función que devuelve info
        info = launch_and_get_info(
            timeout_main_window=60,
            timeout_dialogs=30,
            timeout_project_window=15
        )
        
        print('\\nVENTANA PRINCIPAL DETECTADA:')
        print('-' * 40)
        for k, v in info.items():
            print(f'  {k}: {v}')
        
        # Verificar título final
        title = info.get('title', '')
        expected_keywords = ['Proyecto_Consorcio', '3.233.5.132']
        found = any(keyword in title for keyword in expected_keywords)
        
        if found:
            print(f'\\n[OK] Título confirma carga de proyecto: \"{title}\"')
        else:
            print(f'\\n[WARN] Título no contiene URL proyecto: \"{title}\"')
        
        print('\\n[OK] Test completado exitosamente')
        print('La aplicación queda abierta para inspección manual.')
        print('Manteniendo la app abierta por 10 segundos...')
        time.sleep(10)
        
        return True
        
    except Exception as e:
        print(f'\\n[ERROR] {e}')
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_launch()
    sys.exit(0 if success else 1)
