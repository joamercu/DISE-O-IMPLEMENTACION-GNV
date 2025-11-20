import sys
try:
    import PyPDF2
    with open('diagrama gnv.pdf', 'rb') as pdf:
        reader = PyPDF2.PdfReader(pdf)
        for i, page in enumerate(reader.pages):
            print(f"=== Página {i+1} ===")
            print(page.extract_text())
            print()
except ImportError:
    print("PyPDF2 no está instalado")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

