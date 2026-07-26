import re
text = open(r"C:\Users\onefan1\.minimax\workspace\pc_time_tracker\README.md", "r", encoding="utf-8").read()
for i, line in enumerate(text.split("\n")):
    if "10" in line and "language" in line.lower():
        with open(r"C:\Users\onefan1\.minimax\workspace\pc_time_tracker\_peek.txt", "a", encoding="utf-8") as f:
            f.write(f"L{i}: {line}\n")
print("done")
