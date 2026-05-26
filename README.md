# 👁️ Neuro-Orthoptic AI SaaS Platform

Plataforma HealthTech avançada para análise ortóptica inteligente, rastreamento ocular de alta precisão, modelagem biométrica craniana e processamento clínico em tempo real utilizando Inteligência Artificial, visão computacional e geometria espacial 3D.

---

# 🚀 Visão Geral

O projeto foi desenvolvido para atuar como uma infraestrutura moderna de neuro-ortóptica digital, capaz de realizar:

- Tracking ocular binocular em tempo real
- Reconstrução geométrica da direção visual
- Estimativa biomecânica craniana adaptativa
- Calibração polinomial não-linear da superfície visual
- Correção dinâmica do eixo visual
- Detecção de estrabismo
- Telemetria clínica de alta frequência
- Pipeline assíncrono de baixa latência
- Processamento temporal sincronizado
- Infraestrutura SaaS escalável para HealthTech

---

# 🧠 Principais Recursos da Engine

## ✅ Eye Tracking Binocular 3D

Reconstrução vetorial da direção visual de ambos os olhos utilizando:

- MediaPipe FaceMesh
- Interseção geométrica raio-esfera
- SolvePnP
- Álgebra linear espacial
- Vetores normalizados em espaço craniano

---

## ✅ Modelagem Craniana Adaptativa

Sistema antropométrico dinâmico que:

- Escala automaticamente o modelo facial
- Ajusta o tamanho ocular conforme a morfologia do paciente
- Corrige distorções volumétricas
- Reduz erro geométrico entre pacientes infantis e adultos

---

## ✅ Calibração Não-Linear da Superfície Visual

Engine matemática baseada em:

- Regressão polinomial bivariada
- Regressão Ridge (Regularização de Tikhonov)
- Compensação dinâmica do ângulo kappa
- Correção espacial do eixo visual

Modelo utilizado:

```math
f(h,v)=c0+c1h+c2v+c3h²+c4hv+c5v²
```

Com penalização Alpha contra overfitting periférico e instabilidades geométricas em excentricidades elevadas do campo visual.

---

## ✅ Pipeline Temporal Inteligente

Sistema de sincronização temporal de alta precisão:

- Timestamp binário embutido no frame
- Processamento assíncrono
- Métrica de latência interna
- Suavização temporal com Kalman
- Cache de matriz intrínseca da câmera
- Compensação temporal dinâmica
- Sincronização cliente-servidor em alta frequência

---

## ✅ Confidence Score Clínico

Cálculo matemático de confiabilidade baseado em:

- Pitch craniano
- Yaw craniano
- Velocidade cinética cefálica e palpebral
- Distância do paciente
- Integridade geométrica facial
- Detecção e dinâmica fisiológica de piscadas
- Estabilidade temporal do tracking
- Penalização biomecânica angular

---

## ✅ Engine Assíncrona de Alta Performance

Infraestrutura otimizada para:

- WebSocket binário híbrido
- Processamento cooperativo
- Alta taxa de transferência
- Redução de overhead
- Escalabilidade horizontal
- Streaming temporal sincronizado

---

# 🏗️ Arquitetura da Plataforma

```text
 ┌──────────────────────────────────────────┐
 │         Flutter / React Web             │
 │  UI Clínica • Dashboard • Tracking UI   │
 └──────────────────┬───────────────────────┘
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
│ Kalman • Ridge Regression • Surface Model    │
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
│ Temporal Synchronization   │
│ Latency Reconstruction     │
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
- Geometria 3D
- Ridge Regression
- Filtros de Kalman
- Temporal Synchronization

## Frontend
- React + Vite
- Flutter
- TailwindCSS

## Infraestrutura
- Docker
- WebSocket
- AsyncIO
- Containers Linux

---

# 📡 Pipeline de Tracking

```text
Captura de Frame
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
Avaliação Clínica
```

---

# 🩺 Possíveis Aplicações Clínicas

- Estrabismo
- Exotropia
- Esotropia
- Ambliopia
- Neurologia ocular
- Reabilitação visual
- Tracking neurocognitivo
- Eye-tracking assistivo
- Telemedicina oftalmológica
- Estudos biométricos

---

# 📊 Métricas da Engine

## Recursos Computacionais
- WebSocket binário otimizado
- Cache de inversão matricial
- SolvePnP EPNP acelerado
- Downscale adaptativo
- Processamento assíncrono

## Recursos Matemáticos
- Ridge Regression
- Regularização de Tikhonov
- Vetores normalizados
- Geometria espacial
- Tracking temporal

## Recursos Clínicos
- Confidence Score
- Telemetria sincronizada
- Dinâmica fisiológica de piscada
- Estimativa biométrica craniana
- Penalização cinética cefálica

---

# 🔬 Roadmap Futuro

- Inferência com Deep Learning
- Modelos Transformer Vision
- Heatmaps oculares
- Dashboard clínico avançado
- Exportação DICOM
- Multi-paciente
- Streaming distribuído
- Clusterização GPU
- Inferência Edge AI
- Integração hospitalar HL7/FHIR

---

# 🐳 Infraestrutura Docker

```bash
docker compose up -d
```

Serviços previstos:

- API Gateway Laravel
- FastAPI AI Engine
- Redis
- MySQL
- Qdrant
- Nginx
- Workers Assíncronos

---

# 👨‍💻 Autor

## José Henrique Jardim

Desenvolvedor Full Stack • Data Science • Computer Vision • AI Engineering

### Contatos

🔗 LinkedIn  
https://linkedin.com/in/jose-jardim-764143247

📺 YouTube  
https://youtube.com/@caminho_do_codigo



---
# 📺 Regra de Negócio

<div align="center">

<a href="https://youtu.be/Oo37ZGVPvNA" target="_blank">
  <img 
    src="https://i.ytimg.com/vi/Oo37ZGVPvNA.jpg"
   alt="Assista no YouTube"
    width="100%"
    style="max-width: 900px; border-radius: 14px; box-shadow: 0px 6px 20px rgba(0,0,0,0.35);"
  >
</a>

</div>

# 📺 Processo de Desenvolvimento

<div align="center">

<a href="https://youtu.be/4j0y1g531aM" target="_blank">
  <img 
    src="https://i.ytimg.com/vi/4j0y1g531aM/maxresdefault.jpg"
    alt="Assista no YouTube"
    width="100%"
    style="max-width: 900px; border-radius: 14px; box-shadow: 0px 6px 20px rgba(0,0,0,0.35);"
  >
</a>

</div>

---

# 📜 Licença

Projeto proprietário em desenvolvimento experimental para pesquisa, engenharia clínica computacional e inovação HealthTech.

© 2026 José Henrique Jardim