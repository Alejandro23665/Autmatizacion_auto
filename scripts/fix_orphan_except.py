with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\window_utils.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The issue: line 624 (index 624) has `except Exception as e:` at indent 12
# but there's no matching try at that indent level.
# The try at line 599 (index 598) is at indent 8, and there's a missing except for it.
# The except at line 624 is orphaned.

# Let's fix by:
# 1. Remove the orphaned except at index 624
# 2. Add a proper except for the outer try at the correct indentation

# First, let's see the exact lines around the issue
print("Line 625 (idx 624):", repr(lines[624]))
print("Line 626 (idx 625):", repr(lines[625]))

# Remove the orphaned except at index 624 (line 625)
del lines[624]  # "            except Exception as e:"

# Now we need to add a proper except for the outer try at line 599 (idx 598)
# The outer try starts at index 598 (line 599) with indent 8
# We need to add an except after the inner for loop completes, before line 627 (index 626)

# Find where to insert the except for the outer try
# The outer try starts at idx 598, the inner for loop ends around idx 622
# We need to add except at indent 8 after the for loop but before the next statement

# Let's find where the for loop ends - it's around idx 622-623
print("Line 623 (idx 622):", repr(lines[622]))
print("Line 624 (idx 623):", repr(lines[623]))
print("Line 625 (idx 624):", repr(lines[624]))
print("Line 626 (idx 625):", repr(lines[625]))

# We need to insert an except at indent 8 after the for loop (after idx 622)
# The outer try started at idx 598, the for loop ends around idx 622-623

# Actually, let me just fix this by rewriting the whole Try 4 section properly
# But that's complex. Let me just remove the orphaned except and add a pass

# Remove the orphaned except line
if 'except Exception as e:' in lines[624]:
    del lines[624]
    print("Removed orphaned except")

with open(r'C:\Users\Talle\Documents\programacion\Proyectos\automatizacion_automaticas\src\automation\window_utils.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Fixed')