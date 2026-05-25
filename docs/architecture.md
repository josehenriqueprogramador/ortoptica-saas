# 🪐 ARQUITETURA OFICIAL DA HEALTHTECH SAAS

## Fluxo da Plataforma
1. O App Mobile/Web captura quadros via câmera.
2. Os dados de vídeo/imagem batem no `saas_backend` (Laravel) para validação.
3. O Laravel consome o `saas_ml` (FastAPI + MediaPipe), que usa a malha facial refinada.
4. As coordenadas matemáticas da Íris são extraídas para o diagnóstico de estrabismo, nistagmo e fadiga.
5. Padrões complexos e históricos evolutivos de exames são transformados em vetores no `saas_vector` (Qdrant).
