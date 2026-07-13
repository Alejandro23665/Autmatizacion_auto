with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\window_utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The exact pattern with correct indentation
old = '''                            except Exception:
                                continue
                    except Exception:
                        continue
            except Exception as e:'''

new = '''                            except Exception:
                                continue
            except Exception as e:'''

if old in content:
    content = content.replace(old, new)
    with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\window_utils.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed!')
else:
    print('Pattern not found')