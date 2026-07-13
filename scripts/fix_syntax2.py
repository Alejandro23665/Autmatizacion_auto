with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\window_utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and fix the duplicate except block
old = '''                                continue
                    except Exception:
                        continue
            except Exception as e:
                logger.info(f"Try 4 error: {e}")

            # ===== TRY 5: Deep search entire window ====='''

new = '''                                continue
                        continue
            except Exception as e:
                logger.info(f"Try 4 error: {e}")

            # ===== TRY 5: Deep search entire window ====='''

if old in content:
    content = content.replace(old, new)
    with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\window_utils.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed!')
else:
    print('Pattern not found exactly')
    # Try alternative
    idx = content.find('Try 4 error')
    if idx >= 0:
        print('Context:', repr(content[idx-300:idx+100]))