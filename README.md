# 👁️ PRECISION VISION — Neuro-Orthoptic AI Platform

Plataforma HealthTech avançada para análise ortóptica inteligente, rastreamento ocular de alta precisão, modelagem biométrica craniana e processamento clínico em tempo real utilizando Inteligência Artificial, visão computacional e geometria espacial 3D.

---

# 🚀 Visão Geral

O PRECISION VISION foi desenvolvido como uma infraestrutura moderna de neuro-ortóptica digital capaz de executar:

- Eye tracking binocular em tempo real
- Reconstrução geométrica da direção visual
- Estimativa biomecânica craniana adaptativa
- Calibração polinomial não-linear da superfície visual
- Correção dinâmica do eixo visual
- Detecção computadorizada de estrabismo
- Telemetria clínica de alta frequência
- Processamento temporal sincronizado
- Pipeline assíncrono de baixa latência
- Consolidação diagnóstica automatizada
- Replay clínico longitudinal auditável
- Infraestrutura SaaS escalável para HealthTech

---

# 🧠 Principais Recursos da Engine

## ✅ Eye Tracking Binocular 3D

Reconstrução vetorial da direção visual de ambos os olhos utilizando:

- MediaPipe FaceMesh
- SolvePnP
- Interseção geométrica raio-esfera
- Álgebra linear espacial
- Vetores normalizados em espaço craniano
- Correção biomecânica adaptativa

---

## ✅ Modelagem Craniana Adaptativa

Sistema antropométrico dinâmico que:

- Escala automaticamente o modelo facial
- Ajusta virtualmente o tamanho ocular
- Compensa diferenças morfológicas
- Corrige distorções volumétricas
- Reduz erro geométrico entre faixas etárias

---

## ✅ Calibração Não-Linear da Superfície Visual

Engine matemática baseada em:

- Regressão polinomial bivariada
- Ridge Regression
- Regularização de Tikhonov
- Correção do ângulo kappa
- Correção espacial dinâmica do gaze

Modelo matemático:

```math
f(h,v)=c0+c1h+c2v+c3h²+c4hv+c5v²
```

Com penalização Alpha contra:

- Overfitting periférico
- Instabilidades geométricas
- Drift espacial em excentricidades elevadas

---

## ✅ Pipeline Temporal Inteligente

Sistema temporal de precisão clínica:

- Timestamp binário embutido nos frames
- Aquisição temporal sincronizada
- Processamento assíncrono
- Métrica de latência interna
- Suavização temporal via Kalman
- Cache da matriz intrínseca da câmera
- Compensação temporal dinâmica
- Gating temporal clínico
- Reconstrução temporal auditável

---

## ✅ Replay Clínico Longitudinal

Arquitetura preparada para auditoria científica:

- Persistência temporal das sessões
- Rastreabilidade matemática
- Assinatura de engine_version
- Histórico de modelos estatísticos
- Consolidação determinística
- Compatibilidade futura com replay clínico

Exemplo:

```text
11.1.0|ridge_v2_spatial_bcea
```

---

## ✅ Confidence Score Clínico

Cálculo matemático de confiabilidade baseado em:

- Pitch craniano
- Yaw craniano
- Velocidade cefálica
- Velocidade palpebral
- Distância do paciente
- Integridade geométrica facial
- Estabilidade temporal
- Penalização biomecânica angular
- Dinâmica fisiológica de piscadas

---

## ✅ BCEA — Bivariate Contour Ellipse Area

Medição estatística da estabilidade real da fixação ocular:

- Área elíptica de dispersão do gaze
- Correlação espacial X/Y
- Excentricidade da fixação
- Detecção de instabilidade foveal
- Triagem de nistagmos sutis
- Segmentação temporal por posição diagnóstica

---

## ✅ Máquina de Estados Clínica

Orquestrador SaMD preparado para ambiente regulatório:

Estados suportados:

```text
INITIALIZED
CALIBRATING
TRACKING
CONSOLIDATING
FINISHED
ABORTED
ERROR
```

Capacidades:

- Controle estrito do exame
- Temporal gating
- Segmentação diagnóstica
- Encerramento auditável
- Timeout automático
- Abort manual do operador

---

## ✅ Engine Assíncrona de Alta Performance

Infraestrutura otimizada para:

- WebSocket binário híbrido
- Processamento cooperativo
- Backpressure inteligente
- Streaming temporal sincronizado
- Desacoplamento de protocolo
- Escalabilidade horizontal
- Conversão em Isolates (Flutter)
- Alta taxa de transferência

---

# 🏗️ Arquitetura da Plataforma

```text
 ┌──────────────────────────────────────────┐
 │       Flutter / React Web               │
 │ UI Clínica • Dashboard • Tracking UI    │
 └──────────────────┬──────────────────────┘
                    │
                    ▼
      ┌────────────────────────────────┐
      │      Laravel API Gateway       │
      │ Auth • SaaS • Billing • ACL    │
      └────────────────┬───────────────┘
                       │
                       ▼
 ┌──────────────────────────────────────────────┐
 │      FastAPI Neuro-Orthoptic Engine          │
 │ IA • Tracking • Geometry • Telemetry         │
 └───────────────┬──────────────────────────────┘
                 │
     ┌───────────┼───────────────────────┐
     ▼           ▼                       ▼
┌──────────┐ ┌──────────┐         ┌──────────┐
│MediaPipe │ │ OpenCV   │         │ NumPy    │
│ FaceMesh │ │ Vision   │         │ Algebra  │
└──────────┘ └──────────┘         └──────────┘
                 │
                 ▼
┌──────────────────────────────────────────────┐
│      Clinical Intelligence Layer             │
│ BCEA • Kalman • Ridge • Spatial Models       │
└────────────────┬─────────────────────────────┘
                 │
      ┌──────────┼───────────────┐
      ▼          ▼               ▼
 ┌────────┐ ┌────────┐ ┌────────────────┐
 │ Redis  │ │ MySQL  │ │ Qdrant Vector │
 │ Cache  │ │ SaaS   │ │ Clinical AI   │
 └────────┘ └────────┘ └────────────────┘
```

---

# 🌐 Arquitetura do Protocolo Binário

```text
Cliente Camera Stream
        │
        ▼
┌────────────────────────────┐
│ Binary WebSocket Transport │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ [8 Bytes Timestamp Double] │
├────────────────────────────┤
│ JPEG Binary Frame Payload  │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ MedicalPacketDecoder       │
│ Temporal Reconstruction    │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ Neuro-Orthoptic Processing │
└─────────────┬──────────────┘
              │
              ▼
┌────────────────────────────┐
│ JSON Clinical Telemetry    │
│ Confidence • Angles • Sync │
└────────────────────────────┘
```

---

# 📂 Estrutura do Monorepo

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
│   │   └── main.py
│   │
│   ├── protocols/
│   ├── tracking/
│   ├── services/
│   └── telemetry.py
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
- Python
- FastAPI
- Laravel
- Redis
- MySQL
- Qdrant

## Inteligência Artificial & Visão Computacional
- MediaPipe
- OpenCV
- NumPy
- Álgebra Linear
- SolvePnP
- Ridge Regression
- Filtros de Kalman
- Geometria 3D
- Temporal Synchronization

## Frontend
- Flutter
- React
- Vite
- TailwindCSS

## Infraestrutura
- Docker
- Docker Compose
- WebSocket
- AsyncIO
- Containers Linux

---

# 📡 Pipeline Clínico de Tracking

```text
Captura de Frame
        ↓
Timestamp Binário
        ↓
Sincronização Temporal
        ↓
Detecção Facial
        ↓
Reconstrução Craniana 3D
        ↓
Estimativa de Pose
        ↓
Reconstrução Vetorial Ocular
        ↓
Interseção Raio-Esfera
        ↓
Correção Não-Linear
        ↓
Filtragem Temporal
        ↓
Confidence Score
        ↓
BCEA
        ↓
Prism Diopters
        ↓
Consolidação Diagnóstica
```

---

# 🩺 Aplicações Clínicas

- Estrabismo
- Exotropia
- Esotropia
- Ambliopia
- Nistagmo
- Neurologia ocular
- Reabilitação visual
- Eye tracking assistivo
- Neurociência cognitiva
- Telemedicina oftalmológica
- Estudos biométricos
- Monitoramento longitudinal

---

# 📊 Recursos Computacionais

## Performance
- WebSocket binário otimizado
- Backpressure inteligente
- Cache de inversão matricial
- SolvePnP acelerado
- Downscale adaptativo
- Processamento assíncrono
- Conversão paralela em Isolates
- Pipeline cooperativo

## Matemática
- Ridge Regression
- Regularização de Tikhonov
- Vetores normalizados
- Geometria espacial
- BCEA
- Pearson Correlation
- Tracking temporal

## Clínica
- Confidence Score
- Telemetria sincronizada
- Penalização cinética cefálica
- Dinâmica fisiológica de piscada
- Temporal gating
- Replay clínico

---

# 🔬 Roadmap Futuro

- Deep Learning Pipeline
- Vision Transformers
- Heatmaps oculares
- Dashboard clínico avançado
- Replay visual de sessões
- Exportação DICOM
- Integração HL7/FHIR
- Multi-paciente
- Clusterização GPU
- Inferência Edge AI
- Integração hospitalar

---

# 🐳 Infraestrutura Docker

## Inicialização do Ecossistema

```bash
docker compose up --build
```

---

## Serviços Ativos

- FastAPI Neuro-Orthoptic Engine
- Laravel Gateway
- React Admin Dashboard
- Redis
- MySQL
- Qdrant
- Workers Assíncronos

---

# 🧪 Teste E2E do Orquestrador Clínico

## 1. Health Check

```bash
curl http://localhost:8000/health
```

---

## 2. Inicializar Sessão

```bash
curl -X POST http://localhost:8000/clinical/session/start \
-H "Content-Type: application/json" \
-d '{
  "patient_id": 1,
  "orthoptist_id": 10
}'
```

---

## 3. Transicionar Posição Ortóptica

```bash
curl -X POST http://localhost:8000/clinical/session/target/transition \
-H "Content-Type: application/json" \
-d '{
  "session_id": "SEU_UUID",
  "position_name": "PPO"
}'
```

---

## 4. Consolidar Sessão

```bash
curl -X POST http://localhost:8000/clinical/session/consolidate \
-H "Content-Type: application/json" \
-d '{
  "session_id": "SEU_UUID"
}'
```

---

# 👨‍💻 Autor

## José Henrique Jardim

Desenvolvedor Full Stack • Computer Vision • Data Science • AI Engineering

---

# 🌐 Contatos

## LinkedIn

```text
https://linkedin.com/in/jose-jardim-764143247
```

## YouTube

```text
https://youtube.com/@caminho_do_codigo
```

---

# 📜 Licença

Projeto proprietário em desenvolvimento experimental para pesquisa, engenharia clínica computacional e inovação HealthTech.

© 2026 José Henrique Jardim
