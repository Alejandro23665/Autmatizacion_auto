with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\window_utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The exact pattern from the file
old = '''                            except Exception:
                                continue
                    except Exception:
                        continue
            except Exception as e:
                logger.info(f"Try 4 error: {e}")

            # ===== TRY 5: Deep search entire window ====='''

new = '''                            except Exception:
                                continue
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
    print('Pattern not found')
    idx = content.find('Try 4 error')
    if idx >= 0:
        print('Context:', repr(content[idx-200:idx+100]))