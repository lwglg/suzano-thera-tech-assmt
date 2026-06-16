# Avaliação Técnica | Suzano/Thera Consulting | Aspectos de Escalabilidade

## Índice do conteúdo

<!-- TOC -->

- [Avaliação Técnica | Suzano/Thera Consulting | Aspectos de Escalabilidade](#avalia%C3%A7%C3%A3o-t%C3%A9cnica--suzanothera-consulting--aspectos-de-escalabilidade)
    - [Índice do conteúdo](#%C3%ADndice-do-conte%C3%BAdo)
    - [Preliminares](#preliminares)
    - [Cenário](#cen%C3%A1rio)
    - [Objetivos de escalabilidade](#objetivos-de-escalabilidade)
    - [Arquitetura](#arquitetura)
        - [Componentes-chave a serem escalados por camada](#componentes-chave-a-serem-escalados-por-camada)
            - [NATS JetStream não "plain NATS":](#nats-jetstream-n%C3%A3o-plain-nats)
            - [Backend NestJS Autoscaled:](#backend-nestjs-autoscaled)
            - [PostgreSQL:](#postgresql)
            - [Redis como cache + armazenamento de sessão:](#redis-como-cache--armazenamento-de-sess%C3%A3o)
    - [Mecanismos de escalabilidade](#mecanismos-de-escalabilidade)
    - [Fluxo de requisição do usuário otimizado para escalabilidade](#fluxo-de-requisi%C3%A7%C3%A3o-do-usu%C3%A1rio-otimizado-para-escalabilidade)
    - [Monitoramento, observabilidade e alta disponibilidade](#monitoramento-observabilidade-e-alta-disponibilidade)
    - [Cronograma de implementação](#cronograma-de-implementa%C3%A7%C3%A3o)
    - [Custos](#custos)
    - [O que deseja fazer?](#o-que-deseja-fazer)

<!-- /TOC -->

## Preliminares

Para efeito de quantificação de carga de requisições e das métricas resultantes dessa quantificação, levando-se já em consideração as integrações com serviços externos, fixam-se aqui algumas plataformas que podem potencialmente compor essa solução de software, i.e. seriam de escolha do autor dessa documentação, haja vista que o mesmo já trabalhou com as mesmas em experiências pregressas:

- **SGBD (banco de dados)**: PostgreSQL como sistema de gerenciamento de banco de dados relacionais;
- **Message broker**: NATS Streaming Service, como barramento de mensageria, i.e. transmissão e recepção de dados de eventos.
- **Front-end**: Node.js como _runtime engine_, usando Next.js como framework para construção da SPA que serve a UI de gerenciamento de acessos;
- **Back-end**: Node.js como _runtime engine_, usando NestJS como framework de construção dos serviços, usando em particular Sequelize para a implementação da camada de persistências de dados (DB PostgreSQL);

## Cenário

Suponhamos 100.000 usuários registrados simultâneos ou no total, com solicitações de acesso ativas, alterações contínuas de função/permissão e alto volume de atividade de auditoria/log. Com efeito, as características-chave da carga total seriam:

- Taxa de solicitações moderada a alta (0,5–2% de solicitações de acesso diárias ou 50–200 novas solicitações por segundo durante os picos).
- Picos de tráfego devido à moderação humana (os moderadores podem revisar de 10 a 50 solicitações por minuto).
- Tráfego externo de IAM com picos de tráfego (chamadas à API do Entra ID / Sailpoint IdentityNow durante atribuições de função).
- Necessidade de registro de auditoria em tempo real e validação de JWT.
- Volume de mensagens NATS: ~100 mil eventos/dia (criação, aprovação, concessão, atribuição de função, enriquecimento de auditoria).

## Objetivos de escalabilidade

- Suporte a 100 mil usuários com latência de ponta a ponta inferior a 200 ms para solicitações de acesso e alterações de função.
- Alcance de 99,99% de tempo de atividade com failover automático.
- Manutenção de total auditabilidade e escalabilidade linear.
- Minimização de custos operacionais, aproveitando a infraestrutura existente de Node.js, PostgreSQL e NATS.

## Arquitetura

Abaixo é esquematizado somente o encadeamento lógico dos elementos que compoem a plataforma, que são passíveis de serem escalados:

```shell
text[Frontend: Next.js SPA]          [Backend: NestJS (Autoscaled)]     [External IAM]
  │                                │                                │
  ├─ OAuth2 PKCE (Entra ID / Sailpoint) ──────────────────────────────►
  │                                │                                │
  ├─ Domain Events (NATS) ──────────────────────────────► [NATS Cluster]
  │                                                       │ (JetStream)
  └─ User Access Flow (Moderate + Auto-Role) ───────────► [NATS Consumer]
                                                                 │
                                                   [PostgreSQL Cluster]
                                                      └─ Read Replicas + Citus
                                                         (for 100k users)
```

### Componentes-chave a serem escalados (por camada)


#### NATS JetStream (não "_plain_ NATS"):
- **Cluster**: replicado (3 a 5 nós) com alta disponibilidade baseada em Raft (Raft-based HA).
- **_Streams_**: `solicitações de acesso de usuário`, `atribuições de função`, `eventos de auditoria`.
- **Retenção**: 30 dias, idade máxima de 1 ano.
- **_Deliver all_**: sim.

#### Backend NestJS (Autoscaled):
- Escalador automático horizontal de pods (HPA) baseado no comprimento da fila do consumidor NATS + uso do pool de conexões do PostgreSQL.
- Consumidores: 4 a 6 por fluxo (para paralelismo).
- Processadores de eventos: async/await com BullMQ (fila Redis) para contrapressão e idempotência.

#### PostgreSQL:
- Primário + 3 réplicas de leitura.
- Particionado (sharding) por `userId` (extensão Citus) para tabelas de usuário/função.
- Tabelas particionadas para logs de auditoria (por data). - Pool de conexões (PgBouncer) + arquivamento de WAL.

#### Redis (como cache + armazenamento de sessão):

- Cache para validação de JWT, verificador de código PKCE (de curta duração), funções de usuário e limitação de taxa.
- Armazenamento de sessão para solicitações de acesso do usuário (TTL de 5 minutos).

IAM externo: Tratar como "caixa preta" – nenhuma alteração necessária. Usar políticas de repetição e _circuit brakers_ no NestJS.

## Mecanismos de escalabilidade

- **NATS**: Adicione nós horizontalmente; o JetStream processa mais de 1 milhão de mensagens por segundo por nó.
- **NestJS HPA**: Escale para 20 a 30 réplicas com base na profundidade da fila.
- **PostgreSQL**: Adicione réplicas sob demanda; o Citus fragmenta 100 mil linhas de usuário em 4 a 8 shards.
- **Redis**: Clusterize com 3 a 5 nós para obter tempos de cache inferiores a 1 ms.
- **Caminhos com uso intensivo de assincronia (atribuição de funções, enriquecimento de auditoria)**: Mova para tarefas em segundo plano (BullMQ) para que o frontend permaneça responsivo.

## Fluxo de requisição do usuário (otimizado para escalabilidade)

- 1. Usuário (Next.js SPA) – Login PKCE + JWT.
- 2. O frontend emite o evento `AccessRequestSubmitted` (autenticado).
- 3. O consumidor NATS (NestJS) valida a transação com o PostgreSQL e emite o evento `AccessRequestApproved` somente após a moderação humana.
- 4. Após a aprovação: chamada síncrona para Entra ID/Sailpoint + atualização do PostgreSQL + evento `DefaultRoleAssigned`.
- 5. Todas as etapas são registradas com ID do usuário, ID do moderador, ID do evento e carimbo de data/hora.
- 6. O JWT é atualizado/emitido via cache Redis.

Isso mantém a etapa de moderação (humana) de acessos síncrona (crítica para a segurança), enquanto torna o restante totalmente assíncrono e escalável.

## Monitoramento, observabilidade e alta disponibilidade

- **Métricas**: Prometheus + Grafana (atraso do consumidor NATS, atraso da replicação do PostgreSQL, taxa de acertos do Redis, taxa de transferência de eventos).
- **Rastreamento**: OpenTelemetry + Jaeger (rastreamento de requisições de ponta a ponta entre frontend, NestJS, NATS e PostgreSQL).
- **Alertas**: Fila de consumidores NATS > 1.000; Pool de conexões PostgreSQL > 90%; Taxa de erros IAM externa > 5%.
- **NATS**: Cluster de 3 nós com eleição automática de líder.
- **PostgreSQL**: Replicação síncrona + PITR.
- **Redis**: Redis Sentinel ou Cluster com 3 nós.
- **Multirregião (se necessário)**: Streaming de eventos com NATS ou Kafka como fallback.

## Cronograma de implementação

Estimado de 6 (seis) a 8 (oito) semanas, assumindo uma plataforma já estavelmente implementada. Segue abaixo a granularidade:

- **Semanas 1 a 2**: Adicionar NATS JetStream, Redis e particionamento Citus.
- **Semanas 3 a 4**: Converter consumidores para jobs assíncronos do BullMQ + políticas HPA.
- **Semanas 5 a 6**: Adicionar monitoramento Prometheus + OpenTelemetry.
- **Semanas 7 a 8**: Teste de carga (k6 + 100 mil usuários simulados), ajustes e implementação em produção.

## Custos 

Impacto estimado no custo (mensal): aproximadamente de **US$ 800,00 a US$ 2.000,00 (ou R$ 4.079,52 a R$ 10.198,80) extras**, considerando escalonamento automático do provedor de nuvem, com nós adicionais de NATS/PostgreSQL – linear com o tráfego.

Esta proposta preserva a auditabilidade original, o controle de moderação humana, o OAuth2/PKCE e as integrações externas de IAM, ao mesmo tempo que escala perfeitamente para 100.000 usuários. O núcleo orientado a eventos torna-se vantajoso, i.e. possibilita criar mais consumidores e réplicas sem alterar a lógica de negócios.

---

## O que deseja fazer?

- [Voltar ao topo](#índice-do-conteúdo)
- [Voltar à raíz](../main.md)
- [Análise de risco](./risk-assessment-specs.md)