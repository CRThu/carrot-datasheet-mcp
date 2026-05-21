cd build/ntag224
pandoc "NT2H2421G0.docx" -t markdown -o "pandoc.md" --wrap=none --extract-media="."
uv run ../../convert_emf.py
uv run ../../analyze_image.py
uv run ../../merge_images.py --output_md="../../ds/NT2H2421G0.md"


cd build/fm434
pandoc "FM434.docx" -t markdown -o "pandoc.md" --wrap=none --extract-media="."
uv run ../../convert_emf.py
uv run ../../analyze_image.py
uv run ../../merge_images.py --output_md="../../ds/fm434.md"