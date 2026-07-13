with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\window_utils.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the exact pattern around "Try 4 error"
idx = content.find('Try 4 error')
if idx >= 0:
    # Show context
    print('Found at:', idx)
    context = content[idx-200:idx+100]
    print(repr(context))
    
    # The issue is: two "except Exception:" blocks back to back
    # Need to remove one "except Exception:\n                        continue" pair
    # The pattern is: "except Exception:\n                        continue\n                    except Exception:\n                        continue\n            except Exception as e:"
    # Should become: "except Exception:\n                        continue\n            except Exception as e:"
    
    old = '''                    except Exception:
                        continue
                    except Exception:
                        continue
            except Exception as e:'''
    
    new = '''                    except Exception:
                        continue
            except Exception as e:'''
    
    if old in content:
        content = content.replace(old, new)
        with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\window_utils.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print('Fixed!')
    else:
        print('Pattern not found exactly')
        # Show more context
        print('Context around error:')
        print(repr(content[idx-300:idx+50]))
else:
    print('Try 4 error not found')