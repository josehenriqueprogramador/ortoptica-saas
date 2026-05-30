# Precision Vision WebSocket Protocol

## 1. Envelope Clínico
Todos os pacotes enviados pelo motor de IA (ml_service) para o frontend Flutter seguem o envelope JSON padrão:
`{ "telemetry": { ... }, "pre_exam": { ... } }`

## 2. Modelos de Dados

### Telemetry (Dados Técnicos)
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| gaze_x | double | Coordenada X do olhar |
| gaze_y | double | Coordenada Y do olhar |
| confidence_score | double | Score de 0 a 1 (precisão da inferência) |
| latency_sec | double | Tempo de processamento em segundos |

### PreExam (Estado Clínico)
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| status | string | Estado atual da máquina de estados |
| quality_score | double | Score de 0 a 100 da imagem |

### Checks (Critérios de Aceite)
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| face_detected | bool | Detecção de face válida |
| pose_ok | bool | Alinhamento angular correto |
| lighting_ok | bool | Nível de brilho dentro do threshold |
| confidence_ok | bool | Confiança mínima atingida |

## 3. Estados da Máquina (status)
- `WAITING_FOR_ENVIRONMENT`: O sistema está pronto, mas o paciente não.
- `READY_TO_START`: Critérios clínicos atingidos, botão de início habilitado.
- `TRACKING`: Exame em curso.
- `FINISHED`: Exame concluído com sucesso.
- `ABORTED`: Interrupção pelo usuário.
- `ERROR`: Falha no motor de inferência (necessário restart).
