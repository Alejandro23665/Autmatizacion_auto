with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\window_utils.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix: Remove the duplicate except block at line 624-625
# Lines 624-625 (0-indexed: 623-624) are the problematic except block
# Line 624 (index 623): "            except Exception:"
# Line 625 (index 624): "                continue"

# Check the current state
print(f"Line 623 (idx 623): {lines[623].rstrip()}")
print(f"Line 624 (idx 624): {lines[624].rstrip()}")
print(f"Line 625 (idx 625): {lines[625].rstrip()}")
print(f"Line 626 (idx 626): {lines[626].rstrip()}")

# Remove lines 624-625 (indices 623-624)
# The problematic lines are:
# idx 623: "            except Exception:"
# idx 624: "                continue"

# Actually looking at the output, lines are:
# 624:             except Exception:
# 625:                 continue
# 626:         except Exception as e:
# So indices 623 and 624 are the problematic ones

# Remove them
del lines[623]  # "            except Exception:"
del lines[623]  # "                continue" (was idx 624, now 623 after first deletion)

with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\window_utils.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Fixed - removed duplicate except block')