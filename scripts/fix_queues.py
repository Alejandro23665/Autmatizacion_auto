with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\queues.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The old code block to replace - from "for i in range(auto_count + 1):" to "return True, detected_count"
old = '''        boleta_window = None
        
        for i in range(auto_count + 1):
            if i == 0:
                logger.info('Procesando boleta 1/{} (primera)'.format(auto_count))
                try:
                    boleta_window = wait_for_title_change_pattern(app, BOLETA_TITLE_PATTERN, timeout=timeout, exclude_handles=[])
                    logger.info('Primera boleta cargada: "{}"'.format(boleta_window.window_text()))
                except WindowNotFoundError:
                    logger.warning('Titulo no cambio al patron esperado, verificando ventana principal...')
                    main_title = main_window.window_text()
                    import re
                    if re.search(BOLETA_TITLE_PATTERN, main_title, re.IGNORECASE):
                        logger.info('Primera boleta ya cargada: "{}"'.format(main_title))
                        boleta_window = main_window
                    else:
                        logger.error('No se detecto carga de primera boleta')
                        return False
            else:
                logger.info('Procesando boleta {}/{}'.format(i+1, auto_count))
                try:
                    boleta_window = wait_for_title_change_pattern(app, BOLETA_TITLE_PATTERN, timeout=timeout, exclude_handles=[])
                    logger.info('Boleta {} cargada: "{}"'.format(i+1, boleta_window.window_text()))
                except WindowNotFoundError:
                    logger.error('No se detecto carga de boleta {}'.format(i+1))
                    return False
            
            # ===== NUEVO: Detectar y manejar modal de error =====
            logger.info(f"DEBUG: Verificando modal de error en boleta {i+1}")
            error_detected, error_modal = detect_error_modal(app, main_window)
            logger.info(f"DEBUG: detect_error_modal returned: error_detected={error_detected}")
            if error_detected:
                logger.info('Modal de error detectado en boleta {} - manejando...'.format(i+1))
                
                # 1. Click en Cancelar en el modal
                if not click_cancelar_modal(error_modal):
                    logger.error('No se pudo hacer click en Cancelar')
                    return False
                time.sleep(0.5)
                
                # 2. Click en 80% izquierda (evita boletas centradas)
                if not click_80_percent_left(boleta_window):
                    logger.error('No se pudo hacer click 80% izquierda')
                    return False
                time.sleep(0.5)
                
                # 3. Seleccionar "Verificación Javier" en ComboBox "Fases disponibles" + Aceptar
                if not select_fase_verificacion_javier(boleta_window):
                    logger.error('No se pudo seleccionar Verificación Javier')
                    return False
                time.sleep(0.5)
                
                logger.info('Boleta con error procesada, continuando al siguiente lote')
                continue  # Pasar al siguiente lote
            # =====================================================
            
            logger.info('Enviando Ctrl+L en boleta {}...'.format(i+1))
            try:
                boleta_window.type_keys('^l')
                logger.info('Ctrl+L enviado en boleta {}'.format(i+1))
            except Exception as e:
                logger.error('Fallo Ctrl+L en boleta {}: {}'.format(i+1, e))
                return False
            
            logger.info('Esperando 0.5 segundo...')
            time.sleep(0.5)
        
        logger.info('Loop completado. Cerrando aplicacion...')
        try:
            boleta_window.close()
            logger.info('Aplicacion cerrada')
        except Exception as e:
            logger.warning('Error cerrando app: {}'.format(e))
            try:
                boleta_window.type_keys('%{F4}')
            except Exception:
                pass
        
        return True, detected_count
    
    except Exception as e:
        logger.error('Error en loop AUTO: {}'.format(e))
        return False, detected_count

def select_auto_queue_and_open_boleta"""

new = '''        boleta_window = None
        
        i = 0
        processed_count = 0
        
        while i < auto_count:
            # Check if should stop
            if should_stop and should_stop():
                logger.info('Proceso detenido por usuario en boleta {}'.format(i+1))
                return False, processed_count
            
            # Log remaining boletas
            logger.info('Procesando boleta {}/{} (quedan {})'.format(i+1, auto_count, auto_count - i - 1))
            
            if i == 0:
                logger.info('Procesando boleta 1/{} (primera)'.format(auto_count))
                try:
                    boleta_window = wait_for_title_change_pattern(app, BOLETA_TITLE_PATTERN, timeout=timeout, exclude_handles=[], should_stop=lambda: not is_running)
                    logger.info('Primera boleta cargada: "{}"'.format(boleta_window.window_text()))
                except WindowNotFoundError:
                    logger.warning('Titulo no cambio al patron esperado, verificando ventana principal...')
                    main_title = main_window.window_text()
                    import re
                    if re.search(BOLETA_TITLE_PATTERN, main_title, re.IGNORECASE):
                        logger.info('Primera boleta ya cargada: "{}"'.format(main_title))
                        boleta_window = main_window
                    else:
                        logger.error('No se detecto carga de primera boleta')
                        return False, processed_count
            else:
                logger.info('Procesando boleta {}/{}'.format(i+1, auto_count))
                try:
                    boleta_window = wait_for_title_change_pattern(app, BOLETA_TITLE_PATTERN, timeout=timeout, exclude_handles=[], should_stop=lambda: not is_running)
                    logger.info('Boleta {} cargada: "{}"'.format(i+1, boleta_window.window_text()))
                except WindowNotFoundError:
                    logger.error('No se detecto carga de boleta {}'.format(i+1))
                    return False, processed_count
            
            # ===== NUEVO: Detectar y manejar modal de error =====
            logger.info(f"DEBUG: Verificando modal de error en boleta {i+1}")
            error_detected, error_modal = detect_error_modal(app, main_window)
            logger.info(f"DEBUG: detect_error_modal returned: error_detected={error_detected}")
            if error_detected:
                logger.info('Modal de error detectado en boleta {} - manejando...'.format(i+1))
                
                # 1. Click en Cancelar en el modal
                if not click_cancelar_modal(error_modal):
                    logger.error('No se pudo hacer click en Cancelar')
                    return False, processed_count
                time.sleep(0.5)
                
                # 2. Click en 80% izquierda (evita boletas centradas)
                if not click_80_percent_left(boleta_window):
                    logger.error('No se pudo hacer click 80% izquierda')
                    return False, processed_count
                time.sleep(0.5)
                
                # 3. Seleccionar "Verificación Javier" en ComboBox "Fases disponibles" + Aceptar
                if not select_fase_verificacion_javier(boleta_window):
                    logger.error('No se pudo seleccionar Verificación Javier')
                    return False, processed_count
                time.sleep(1)
                
                logger.info('Boleta con error procesada, continuando al siguiente lote')
                # i NO se incrementa aqui - solo se incrementa al hacer Ctrl+L o click Aceptar
                continue  # Pasar al siguiente lote
            # =====================================================
            
            logger.info('Enviando Ctrl+L en boleta {}...'.format(i+1))
            try:
                boleta_window.type_keys('^l')
                logger.info('Ctrl+L enviado en boleta {} (quedan {})'.format(i+1, auto_count - i - 1))
            except Exception as e:
                logger.error('Fallo Ctrl+L en boleta {}: {}'.format(i+1, e))
                return False, processed_count
            
            processed_count += 1
            i += 1
            
            logger.info('Esperando 1.5 segundos...')
            # Check for stop during sleep
            for _ in range(15):
                if should_stop and should_stop():
                    logger.info('Proceso detenido por usuario durante espera')
                    return False, processed_count
                time.sleep(0.1)
        
        logger.info('Loop completado. Cerrando aplicacion...')
        try:
            boleta_window.close()
            logger.info('Aplicacion cerrada')
        except Exception as e:
            logger.warning('Error cerrando app: {}'.format(e))
            try:
                boleta_window.type_keys('%{F4}')
            except Exception:
                pass
        
        return True, processed_count
    
    except Exception as e:
        logger.error('Error en loop AUTO: {}'.format(e))
        return False, processed_count

def select_auto_queue_and_open_boleta"""

with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\queues.py', 'w', encoding='utf-8') as f:
    f.write(content.replace(old, new))

print('Done!')