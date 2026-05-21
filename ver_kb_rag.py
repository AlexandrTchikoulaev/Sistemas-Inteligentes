"""
Mostra a base de conhecimento RAG construída a partir dos ficheiros Prolog.
Uso: python ver_kb_rag.py
     python ver_kb_rag.py | more       (com paginação)
     python ver_kb_rag.py regra        (filtrar por palavra)
"""
import sys
from chatbot_server import construir_conhecimento, KB_A, KB_B

docs = construir_conhecimento(KB_A, KB_B)

filtro = sys.argv[1].lower() if len(sys.argv) > 1 else ""

print(f"\n{'='*65}")
print(f"  BASE DE CONHECIMENTO RAG  —  {len(docs)} documentos")
print(f"  Fontes: base_conhecimento_a.pl + base_conhecimento_b.pl")
if filtro:
    print(f"  Filtro: '{filtro}'")
print(f"{'='*65}\n")

count = 0
for i, doc in enumerate(docs, 1):
    if filtro and filtro not in doc.lower():
        continue
    count += 1
    print(f"[{i:02d}] {doc}")
    print()

if filtro:
    print(f"--- {count} documento(s) com '{filtro}' ---")
