cd build/ntag224
pandoc "NT2H2421G0.docx" -t markdown -o "NT2H2421G0-pandoc.md" --wrap=none --extract-media="."
uv run ../../convert_emf.py
uv run ../../analyze_image.py