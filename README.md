# 👁️ PRECISION VISION

## OLHAR. PRECISÃO. EVOLUÇÃO.

Plataforma avançada de engenharia biomédica para avaliação ortóptica digital, rastreamento ocular inteligente e análise clínica assistida por Inteligência Artificial.

O Precision Vision combina visão computacional, biometria ocular, modelagem geométrica tridimensional e processamento temporal para transformar dados de vídeo em métricas clínicas objetivas, auditáveis e reproduzíveis.

Projetado sob princípios compatíveis com a evolução para SaMD (Software as a Medical Device), o ecossistema busca democratizar tecnologias avançadas de análise ortóptica, reduzindo dependência de equipamentos proprietários e ampliando o acesso à medicina digital de precisão.

---

# 🚀 Visão Geral

O Precision Vision foi desenvolvido para criar uma infraestrutura moderna de neuro-ortóptica digital capaz de executar:

* Rastreamento ocular binocular em tempo real
* Reconstrução tridimensional da direção visual
* Estimativa biomecânica craniana adaptativa
* Correção dinâmica do eixo visual
* Telemetria clínica de alta frequência
* Processamento temporal sincronizado
* Persistência auditável de sessões clínicas
* Consolidação biométrica automatizada
* Arquitetura SaaS para aplicações HealthTech

---

# 📌 Estado Atual do Projeto

## ✅ Implementado

### Core Biométrico

* MediaPipe FaceMesh
* OpenCV
* Reconstrução de vetor de olhar
* Estimativa de pose craniana
* Filtro temporal
* Processamento assíncrono
* Telemetria clínica em tempo real

### Analytics

* BCEA (Bivariate Contour Ellipse Area)
* Índice de instabilidade de fixação
* Estimativa de desvio prismático
* Métricas biométricas de estabilidade ocular

### Infraestrutura

* FastAPI
* SQLAlchemy 2.0 Async
* SQLite
* Docker
* Docker Compose
* Arquitetura Monorepo

### Aplicações

* Flutter Profissional
* Flutter Paciente
* Painel Administrativo React

### Sprint Clínica Atual

* ClinicalPacket Architecture
* Examination Controller
* Gatekeeper Clínico
* Checklist Pré-Exame
* Streaming Clínico Reativo

---

## ⏳ Em Desenvolvimento

* Dashboard Clínico Avançado
* Replay de Sessões
* Auditoria Clínica
* Exportação Científica
* Vetorização Clínica

---

## 🔬 Roadmap Futuro

* HL7/FHIR
* Exportação DICOM
* Deep Learning
* Vision Transformers
* IA Preditiva
* Clusterização GPU
* Edge AI
* Certificação SaMD
* Integração Hospitalar

---

# 🧠 Principais Recursos da Engine

## Eye Tracking Binocular 3D

Reconstrução vetorial da direção visual utilizando:

* MediaPipe FaceMesh
* OpenCV
* Álgebra Linear
* Geometria Espacial 3D
* Vetores Normalizados
* Modelagem Craniana Adaptativa

---

## Modelagem Craniana Adaptativa

Sistema antropométrico dinâmico capaz de:

* Escalar automaticamente o modelo facial
* Ajustar virtualmente parâmetros anatômicos
* Compensar diferenças morfológicas
* Reduzir distorções geométricas
* Melhorar estabilidade do gaze tracking

---

## Pipeline Temporal Inteligente

Sistema temporal projetado para ambiente clínico:

* Timestamp embutido nos frames
* Sincronização temporal
* Processamento assíncrono
* Suavização temporal
* Controle de latência
* Reconstrução temporal auditável

---

## BCEA — Bivariate Contour Ellipse Area

Métrica estatística para avaliação da estabilidade de fixação:

* Dispersão espacial X/Y
* Correlação de Pearson
* Estabilidade foveal
* Monitoramento longitudinal
* Triagem de instabilidades oculares

Fórmula utilizada:

BCEA = 2πkσxσy√(1−ρ²)

---

## Desvio Prismático

Estimativa quantitativa baseada na diferença angular entre:

* Vetor de olhar
* Alvo clínico

Capaz de classificar:

* Exotropia
* Esotropia
* Hipertropia
* Hipotropia
* Ortoforia

---

## Índice de Instabilidade de Fixação

Métrica biométrica baseada em:

* Distância média entre amostras consecutivas
* Variabilidade espacial
* Micro-instabilidade ocular

---

# 🏗️ Arquitetura da Plataforma

```text
┌─────────────────────────────────────┐
│      Flutter / React Frontend       │
│ Aplicativos Clínicos e Dashboard    │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│      FastAPI Neuro-Orthoptic        │
│          Processing Engine          │
└──────────────────┬──────────────────┘
                   │
     ┌─────────────┼─────────────┐
     ▼             ▼             ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│MediaPipe │ │ OpenCV   │ │ NumPy    │
│FaceMesh  │ │ Vision   │ │ Algebra  │
└──────────┘ └──────────┘ └──────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│ Clinical Intelligence Layer         │
│ BCEA • Prism • Stability Analytics  │
└─────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│ SQLAlchemy Async + SQLite           │
│ Clinical Persistence Layer          │
└─────────────────────────────────────┘
```

---

# 📡 Pipeline Clínico

```text
Captura de Frame
        ↓
FaceMesh
        ↓
Pose Craniana
        ↓
Reconstrução Ocular
        ↓
Vetores de Olhar
        ↓
Filtragem Temporal
        ↓
Telemetria
        ↓
Confidence Score
        ↓
BCEA
        ↓
Desvio Prismático
        ↓
Persistência
        ↓
Consolidação Clínica
```

---

# 📂 Estrutura do Projeto

```text
ortoptica_saas/
├── apps/
│   ├── flutter_paciente/
│   └── flutter_profissional/
│
├── backend/
│
├── ml_service/
│   ├── app/
│   │   ├── analytics/
│   │   ├── api/
│   │   ├── session/
│   │   ├── tracking/
│   │   └── main.py
│   │
│   └── database.py
│
├── painel_admin/
│
├── vector_db/
│
├── docker-compose.yml
└── README.md
```

---

# ⚙️ Stack Tecnológica

## Backend

* Python
* FastAPI
* SQLAlchemy 2.0 Async
* SQLite
* AsyncIO

---

## Inteligência Artificial

* MediaPipe
* OpenCV
* NumPy
* Álgebra Linear
* Geometria 3D

---

## Frontend

* Flutter
* React
* Vite
* TypeScript

---

## Infraestrutura

* Docker
* Docker Compose
* WebSocket
* Linux Containers

---

# 🩺 Aplicações Clínicas

* Estrabismo
* Exotropia
* Esotropia
* Ambliopia
* Nistagmo
* Reabilitação Visual
* Neurologia Ocular
* Neurociência Cognitiva
* Telemedicina Oftalmológica
* Estudos Biométricos
* Monitoramento Longitudinal

---

# 🔒 Engenharia e Governança

O projeto segue princípios de:

* Clean Architecture
* Programação Reativa
* Programação Defensiva
* Rastreabilidade Clínica
* Persistência Auditável
* Processamento Assíncrono
* Separação de Responsabilidades
* Escalabilidade Modular

---

# 🐳 Execução Local

## Inicialização

```bash
docker compose up --build
```

---

## Logs

```bash
docker compose logs -f
```

---

## Encerramento

```bash
docker compose down
```

---

# 🧪 Health Check

```bash
curl http://localhost:8000/health
```

---

# 👨‍💻 Autor

## José Henrique Jardim

Desenvolvedor Full Stack
Computer Vision Engineer
Data Science Enthusiast
AI Engineering

---

# 🌐 Contatos

LinkedIn

https://linkedin.com/in/jose-jardim-764143247

YouTube

https://youtube.com/@caminho_do_codigo

---

# 📜 Licença

Projeto proprietário em desenvolvimento experimental para pesquisa, engenharia biomédica, inovação HealthTech e futura evolução para Software as a Medical Device (SaMD).

© 2026 José Henrique Jardim

PRECISION VISION

OLHAR. PRECISÃO. EVOLUÇÃO.
