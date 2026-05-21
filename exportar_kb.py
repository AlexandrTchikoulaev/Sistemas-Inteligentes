"""
Exporta a base de conhecimento RAG do chatbot para kb_chatbot.txt.
Usa exactamente a mesma função construir_conhecimento() do chatbot_server.py.

Uso: python exportar_kb.py
"""
from chatbot_server import construir_conhecimento, KB_A, KB_B

docs = construir_conhecimento(KB_A, KB_B)

output = "BASE DE CONHECIMENTO RAG — SNS24 CHATBOT\n"
output += "Gerado automaticamente a partir de base_conhecimento_a.pl + base_conhecimento_b.pl\n"
output += "=" * 60 + "\n\n"

for i, doc in enumerate(docs, 1):
    output += f"[{i}]\n{doc}\n\n" + "-" * 60 + "\n\n"

with open("kb_chatbot.txt", "w", encoding="utf-8") as f:
    f.write(output)

print(f"Exportado: kb_chatbot.txt ({len(docs)} documentos)")
