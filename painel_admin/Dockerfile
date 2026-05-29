# Imagem base estável e leve do Node.js
FROM node:20-slim

WORKDIR /app

# Copia os manifestos de pacotes primeiro para otimizar o cache de camadas do Docker
COPY package.json ./

# Instala as dependências especificadas (React, Lucide, Tailwind, Vite, TypeScript)
RUN npm install

# Copia o restante dos arquivos do painel (src, index.html, configs)
COPY . .

# Expõe a porta padrão do servidor de desenvolvimento do Vite
EXPOSE 5173

# Inicializa o Vite forçando o binding de IP para aceitar requisições de fora do container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
