import os
from pathlib import Path
from html import escape

def gerar_documentacao():
    base = Path.cwd()
    saida = base / 'ortoptica_saas_docs.html'
    
    # Configurações de ignorados
    ignore_ext = {'.json', '.pyc', '.env', '.sqlite', '.log', '.html', '.md'}
    ignore_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.venv', 'env', 'dist', 'build', 'static', 'uploads', 'tmp'}

    html_head = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Documentação Ortoptica SaaS</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; line-height: 1.6; color: #333; }
        pre { background: #f4f4f4; padding: 15px; border-radius: 5px; overflow: auto; border: 1px solid #ddd; }
        h1 { color: #2c3e50; }
        h3 { color: #e67e22; margin-top: 30px; border-bottom: 2px solid #eee; }
        nav { background: #f9f9f9; padding: 15px; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <h1>Projeto: Ortoptica SaaS</h1>
    <h2>Índice</h2>
    <nav><ul>"""

    html_body = "</ul></nav><h2>Conteúdo dos Arquivos</h2>"
    files_count = 0

    for root, dirs, files in os.walk(base):
        # Filtra diretórios em tempo real
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        for file in files:
            if any(file.endswith(ext) for ext in ignore_ext):
                continue
            
            file_path = Path(root) / file
            rel_path = str(file_path.relative_to(base))
            anchor = rel_path.replace(os.sep, '_').replace('.', '_')
            
            try:
                content = file_path.read_text(encoding='utf-8')
                if len(content) > 500000:
                    content = content[:500000] + '\n\n... [TRUNCADO POR EXCESSO DE TAMANHO] ...'
                
                html_head += f'<li><a href="#{anchor}">{escape(rel_path)}</a></li>'
                html_body += f'<h3 id="{anchor}">{escape(rel_path)}</h3><pre>{escape(content)}</pre>'
                files_count += 1
            except Exception as e:
                html_head += f'<li>{escape(rel_path)} [Erro: {escape(str(e))}]</li>'

    full_html = html_head + html_body + "</body></html>"
    
    saida.write_text(full_html, encoding='utf-8')
    print(f"Sucesso! Documentação gerada em: {saida}")
    print(f"Total de arquivos processados: {files_count}")

if __name__ == "__main__":
    gerar_documentacao()
