# Build script for data sheets
# Requires: pandoc, uv

# Process NTAG224
cd build/ntag224
uv run ../../pdf2docx_acrobat.py "NT2H2421G0.pdf" "NT2H2421G0.docx"
# Convert docx to markdown and extract images
pandoc "NT2H2421G0.docx" -t markdown -o "pandoc.md" --wrap=none --extract-media="."
# Post-process files
uv run ../../convert_emf.py
uv run ../../analyze_image.py
uv run ../../merge_images.py --output_md="../../ds/NT2H2421G0.md"
uv run split_md.py ds/NT2H2421G0.md --level 2