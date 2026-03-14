with open("tools.txt", "r", encoding="utf-16le") as f:
    text = f.read()
with open("tools_utf8.txt", "w", encoding="utf-8") as f:
    f.write(text)
