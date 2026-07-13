with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\window_utils.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove the orphaned except at index 623 (line 624)
# Line 624 (index 623): "            except Exception as e:"
# Line 625 (index 624): "                logger.info(f\"Try 4 error: {e}\")"
# These are the orphaned except at indent 12

# First check current state
print("Line 624 (idx 623):", repr(lines[623]))
print("Line 625 (idx 624):", repr(lines[624]))
print("Line 626 (idx 625):", repr(lines[625]))

# Remove the orphaned except (2 lines: except... and logger.info...)
# Index 623: "            except Exception as e:\n"
# Index 624: "                logger.info(f\"Try 4 error: {e}\")\n"
# We need to remove both

if 'except Exception as e:' in lines[623]:
    del lines[623]  # except line
    del lines[623]  # logger line (was 624, now 623 after first deletion)
    print("Removed orphaned except block")

# Now we need to add a proper except for the outer try at line 599 (index 598)
# The outer try starts at index 598 (line 599), indent 8
# We need to add except after the for loop, before the "# ===== TRY 5" comment
# The for loop ends around index 622-623 (before the orphaned except)
# The "# ===== TRY 5" is now at index 624 (was 626 before deletion)

# Find the index of "# ===== TRY 5" comment
try5_idx = None
for i, line in enumerate(lines):
    if 'TRY 5' in line:
        try5_idx = i
        break

print(f"TRY 5 index: {try5_idx}")

# Insert the except for outer try just before TRY 5 comment, at indent 8
if try5_idx:
    # The outer try is at indent 8 (8 spaces)
    except_block = [
        '        except Exception as e:\n',
        '            logger.info(f"Try 4 error: {e}")\n',
        '\n'
    ]
    for i, bline in enumerate(except_block):
        lines.insert(try5_idx + i, bline)
    print("Added proper except for outer try")

with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\window_utils.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Fixed!')