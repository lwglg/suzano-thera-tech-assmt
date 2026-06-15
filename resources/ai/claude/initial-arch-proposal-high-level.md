User:

Considere uma possível arquitetura orientada a eventos (eventos de domínio + broker de mensagens) para implementar uma plataforma web cujo principal caso de uso seja o acesso de um usuário a uma plataforma com backend construído sobre Node.js (Next.js + Nest.js + Sequelize + PostgreSQL + NATS) que possui integração com as APIs externas do Microsoft Entra ID e Sailpoint IdentityNow. Observe que essa solicitação de acesso do usuário precisa ser moderada por outro usuário existente, com direitos de moderação. Caso a solicitação seja concedida, uma função padrão com permissões (básicas) deve ser automaticamente atribuída ao novo usuário. O esquema de autenticação utilizado nesta plataforma é o OAuth2, com tokens JWT para autenticação e autorização, como funções e permissões. Todo o processo deve ser auditável, registrando logs de todas as operações e associando os usuários envolvidos a elas.

De posse da arquitetura, gere também a descrição de cada entidade de domínio, os diagramas de casos de uso, diagramas de sequência (aprovação e rejeição de solicitação por moderador), assim como diagraamas de entidade-relacionamento.

Assistant:

Abaixo está uma proposta de arquitetura orientada a eventos para esse cenário, com foco em:

• solicitação de acesso feita por um usuário externo/candidato;
• moderação por um usuário com permissão de moderador;
• provisionamento automático de função padrão após aprovação;
• integração com Microsoft Entra ID e SailPoint IdentityNow;
• autenticação/autorização com OAuth2 + JWT;
• auditabilidade ponta a ponta com trilha de logs e usuários envolvidos.

Vou estruturar em:

visão da arquitetura;
bounded contexts e serviços;
fluxo orientado a eventos;
entidades de domínio;
casos de uso;
diagramas de sequência;
diagrama ER;
observações de implementação em Next.js + Nest.js + Sequelize + PostgreSQL + NATS.

Visão geral da arquitetura

A solução pode ser organizada em uma arquitetura modular orientada a eventos, mantendo consistência transacional local por serviço e propagando mudanças de estado via eventos de domínio publicados no NATS.

Princípios adotados
• Fonte de verdade local: cada módulo mantém seu próprio modelo de domínio e persiste em PostgreSQL.
• Eventos de domínio: mudanças relevantes do negócio são emitidas como eventos.
• Integrações externas desacopladas: Microsoft Entra ID e SailPoint IdentityNow são consumidos por adaptadores/serviços de integração.
• Auditabilidade first-class: toda ação relevante gera registro auditável.
• Segurança por identidade e autorização: OAuth2 + JWT com claims de usuário, papéis e permissões.
• Idempotência e resiliência: consumidores de eventos devem tolerar reentrega e falhas temporárias.

Componentes principais

Uma divisão prática seria:

| Componente | Responsabilidade principal |
|---|---|
| Next.js Web App | UI, login, abertura de solicitação, tela de moderação, consulta de status |
| API Gateway / BFF | Entrada HTTP principal, agregação de respostas, validação de JWT |
| Identity & Access Service | Usuários, papéis, permissões, claims JWT, vínculo com Entra ID/SailPoint |
| Access Request Service | Gestão do ciclo de vida da solicitação de acesso |
| Moderation Service | Regras e ações de aprovação/rejeição por moderadores |
| Provisioning Service | Atribuição automática de função padrão e efetivação de acesso |
| Integration Service | Integrações com Microsoft Entra ID e SailPoint IdentityNow |
| Audit Service | Persistência e consulta de trilha de auditoria |
| Notification Service | E-mails/notificações de status |
| NATS | Broker de eventos e mensagens assíncronas |
| PostgreSQL | Persistência relacional |
| Observability Stack | Logs estruturados, métricas, tracing |

Diagrama da arquitetura

Este diagrama mostra a visão macro dos componentes.

``mermaid
flowchart LR
    U[Usuario Solicitante] --> FE[Next.js Web App]
    M[Moderador] --> FE

    FE --> GW[API Gateway / BFF]
    GW --> IAS[Identity & Access Service]
    GW --> ARS[Access Request Service]
    GW --> MS[Moderation Service]

    IAS --> PG[(PostgreSQL)]
    ARS --> PG
    MS --> PG
    PS[Provisioning Service] --> PG
    AUD[Audit Service] --> PG
    IS[Integration Service] --> PG

    ARS <--> NATS[NATS]
    MS <--> NATS
    PS <--> NATS
    IAS <--> NATS
    AUD <--> NATS
    NS[Notification Service] <--> NATS
    IS <--> NATS

    IS --> ENTRA[Microsoft Entra ID API]
    IS --> SP[SailPoint IdentityNow API]
`

Bounded contexts e responsabilidades
Identity & Access

Responsável por:

• cadastro lógico do usuário na plataforma;
• vinculação com identidade externa;
• papéis e permissões;
• emissão/validação de claims para autorização;
• estado de acesso do usuário.

Agregados centrais
• User
• Role
• Permission
• UserRole
• ExternalIdentityLink

Access Request

Responsável por:

• criação da solicitação;
• captura de justificativa e metadados;
• controle do status da solicitação;
• associação entre solicitante, moderador e decisão.

Agregado central
• AccessRequest

Estados típicos:

• PENDING
• UNDERREVIEW
• APPROVED
• REJECTED
• CANCELLED
• EXPIRED

Moderation

Responsável por:

• verificar se o ator possui permissão de moderação;
• registrar decisão;
• garantir regras como segregação de função;
• disparar eventos de aprovação/rejeição.

Agregado/entidades associadas
• ModerationDecision
• ModerationAssignment (opcional, se houver distribuição de fila)

Provisioning

Responsável por:

• após aprovação, provisionar acesso interno;
• atribuir automaticamente a função padrão;
• opcionalmente sincronizar grupo/papel em Entra ID e SailPoint;
• confirmar sucesso ou falha do provisionamento.

Agregado/entidades associadas
• ProvisioningTask
• DefaultRolePolicy

Audit

Responsável por:

• registrar eventos de negócio e técnicos;
• associar operação, ator, alvo, correlação e timestamps;
• apoiar trilha forense e compliance.

Entidade central
• AuditLog

Fluxo de negócio orientado a eventos
Fluxo principal de aprovação
Usuário autenticado ou pré-identificado inicia uma solicitação de acesso.
O Access Request Service valida regras básicas e grava a solicitação.
É emitido o evento AccessRequestSubmitted.
O Moderation Service recebe o evento e disponibiliza a solicitação para moderadores.
Um moderador aprova a solicitação.
O Moderation Service persiste a decisão e publica AccessRequestApproved.
O Provisioning Service consome o evento e:
   - garante existência/vínculo do usuário;
   - atribui a função padrão;
   - opcionalmente sincroniza Entra ID / SailPoint.
Após sucesso, publica UserProvisioned e/ou DefaultRoleAssigned.
O Identity & Access Service atualiza o estado de acesso do usuário.
O Audit Service registra todo o encadeamento.
O Notification Service envia confirmação ao solicitante e, se necessário, ao moderador.

Fluxo principal de rejeição
Solicitação fica pendente de moderação.
Moderador rejeita e informa motivo.
Moderation Service registra a decisão e publica AccessRequestRejected.
Access Request Service atualiza o status final.
Audit Service registra a rejeição.
Notification Service comunica o solicitante.

Eventos de domínio sugeridos

Os eventos devem ser pequenos, versionados e carregarem IDs de correlação.

| Evento | Quando ocorre | Consumidores principais |
|---|---|---|
| AccessRequestSubmitted | Solicitação criada | Moderation, Audit, Notification |
| AccessRequestMarkedUnderReview | Solicitação assumida para análise | Audit |
| AccessRequestApproved | Moderador aprovou | Provisioning, Audit, Notification |
| AccessRequestRejected | Moderador rejeitou | Access Request, Audit, Notification |
| UserProvisioningStarted | Provisionamento iniciado | Audit |
| DefaultRoleAssigned | Função padrão atribuída | Identity & Access, Audit |
| ExternalIdentitySynchronized | Sincronização com Entra/SailPoint concluída | Audit |
| UserProvisioned | Usuário pronto para acesso | Identity & Access, Notification, Audit |
| ProvisioningFailed | Falha no provisionamento | Audit, Notification, suporte operacional |
| AuditLogRequested | Opcional, para pipeline de auditoria | Audit |

Exemplo de payload de evento

`json
{
  "eventId": "evt01JXYZ...",
  "eventType": "AccessRequestApproved",
  "eventVersion": 1,
  "occurredAt": "2026-06-15T13:45:00Z",
  "correlationId": "corr01JXYZ...",
  "causationId": "cmd01JXYZ...",
  "actor": {
    "userId": "usrmod123",
    "type": "MODERATOR"
  },
  "subject": {
    "userId": "usrreq999"
  },
  "data": {
    "accessRequestId": "ar456",
    "decisionId": "md789",
    "approvedBy": "usrmod123",
    "defaultRoleCode": "BASICUSER"
  }
}
`

Estratégias importantes para consistência
Outbox Pattern

Como há PostgreSQL e NATS, recomendo fortemente usar Transactional Outbox:

• a transação grava:
  - a mudança de estado da entidade;
  - o registro na tabela outboxevents.
• um publicador assíncrono lê a outbox e publica no NATS.
• após sucesso, marca o evento como publicado.

Isso evita o problema clássico de:

• gravar no banco e falhar ao publicar no broker;
• publicar no broker e falhar ao gravar no banco.

Idempotência

Consumidores devem registrar eventid processados em tabela própria, por exemplo:

• messageconsumption
• chave única por consumername + eventid

Assim, reprocessemento não duplica:

• atribuição de papéis;
• criação de logs;
• chamadas externas.

Sagas / Process Manager

Para a parte de provisionamento, faz sentido um process manager simples:

• disparado por AccessRequestApproved;
• acompanha:
  - criação/ativação do usuário;
  - atribuição da função padrão;
  - sincronização com Entra ID;
  - sincronização com SailPoint;
• conclui com UserProvisioned ou ProvisioningFailed.

Modelo de autenticação e autorização
OAuth2 + JWT

O fluxo pode ser:

• autenticação do usuário por Microsoft Entra ID como provedor de identidade;
• backend valida o token recebido;
• plataforma emite ou enriquece uma sessão/token próprio com claims internas, se necessário;
• autorização baseada em:
  - sub
  - email
  - roles
  - permissions
  - tenant se existir multi-tenant
  - moderator=true ou permissão específica.

Claims recomendadas

`json
{
  "sub": "usr123",
  "email": "user@empresa.com",
  "roles": ["BASICUSER"],
  "permissions": [
    "accessrequest:create",
    "accessrequest:read:self"
  ],
  "externalIds": {
    "entraObjectId": "xxxx",
    "sailpointIdentityId": "yyyy"
  },
  "iat": 1710000000,
  "exp": 1710003600,
  "iss": "plataforma.exemplo",
  "aud": "plataforma-web"
}
`

Permissões mínimas sugeridas

| Papel | Permissões |
|---|---|
| REQUESTER | accessrequest:create, accessrequest:read:self |
| MODERATOR | accessrequest:read:any, accessrequest:approve, accessrequest:reject |
| BASICUSER | permissões básicas da plataforma após aprovação |
| ADMIN | gestão de papéis, políticas, auditoria avançada |

Entidades de domínio

A seguir, a descrição de cada entidade principal.

User

Representa o usuário da plataforma, seja solicitante, moderador ou administrador.

Atributos principais:

• id
• email
• fullName
• status (PENDINGACCESS, ACTIVE, REJECTED, BLOCKED, INACTIVE)
• createdAt
• updatedAt
• lastLoginAt

Responsabilidades:

• identificar o ator principal do sistema;
• manter o estado de acesso;
• associar papéis e identidades externas.

ExternalIdentityLink

Representa o vínculo do usuário com identidades em provedores externos.

Atributos principais:

• id
• userId
• provider (ENTRAID, SAILPOINT)
• externalId
• externalUsername
• syncStatus
• lastSyncedAt

Responsabilidades:

• relacionar identidade interna com identidades externas;
• rastrear sincronização com Entra ID e SailPoint.

Role

Representa uma função/perfil de acesso.

Atributos principais:

• id
• code (ex.: BASICUSER, MODERATOR, ADMIN)
• name
• description
• isDefault
• createdAt

Responsabilidades:

• agrupar permissões;
• definir a função padrão atribuída após aprovação.

Permission

Representa uma permissão atômica do sistema.

Atributos principais:

• id
• code (ex.: accessrequest:approve)
• description

Responsabilidades:

• permitir autorização granular;
• compor papéis.

RolePermission

Entidade de associação entre papel e permissão.

Atributos principais:

• roleId
• permissionId

Responsabilidades:

• mapear autorização baseada em RBAC.

UserRole

Entidade de associação entre usuário e papel.

Atributos principais:

• id
• userId
• roleId
• assignedByUserId
• assignmentReason
• assignedAt
• revokedAt

Responsabilidades:

• registrar atribuição de papéis;
• manter evidência de quem concedeu o papel.

AccessRequest

Representa a solicitação de acesso submetida pelo usuário.

Atributos principais:

• id
• requesterUserId
• requestedEmail
• justification
• status
• submittedAt
• reviewStartedAt
• resolvedAt
• resolutionReason
• currentModeratorUserId
• correlationId

Responsabilidades:

• centralizar o ciclo de vida da solicitação;
• armazenar contexto da análise;
• servir como raiz do agregado de solicitação.

ModerationDecision

Representa a decisão formal do moderador sobre uma solicitação.

Atributos principais:

• id
• accessRequestId
• moderatorUserId
• decision (APPROVED, REJECTED)
• reason
• decidedAt

Responsabilidades:

• registrar a decisão imutável do moderador;
• garantir trilha auditável da análise.

ProvisioningTask

Representa o processo de provisionamento disparado após aprovação.

Atributos principais:

• id
• accessRequestId
• userId
• status (PENDING, INPROGRESS, COMPLETED, FAILED)
• startedAt
• finishedAt
• errorCode
• errorMessage
• retryCount

Responsabilidades:

• rastrear a execução técnica do provisionamento;
• permitir retentativas e suporte operacional.

AuditLog

Representa o registro auditável de uma operação.

Atributos principais:

• id
• eventType
• entityType
• entityId
• actorUserId
• subjectUserId
• correlationId
• causationId
• payload
• createdAt
• ipAddress
• userAgent

Responsabilidades:

• registrar ações de negócio e integração;
• suportar auditoria, investigação e compliance.

Notification

Representa uma notificação a ser entregue ou já entregue.

Atributos principais:

• id
• userId
• type
• channel
• status
• payload
• sentAt

Responsabilidades:

• comunicar mudança de status da solicitação;
• manter evidência de entrega lógica.

Regras de negócio essenciais
Regras de solicitação
• Um usuário não deve possuir mais de uma solicitação pendente ao mesmo tempo.
• Solicitações devem ter justificativa mínima.
• E-mail do solicitante deve ser válido e, idealmente, compatível com domínio permitido.

Regras de moderação
• Apenas usuários com permissão accessrequest:approve ou accessrequest:reject podem decidir.
• Moderador não pode aprovar a própria solicitação, se isso for política da organização.
• Toda rejeição deve conter motivo.
• Decisão de moderação é final para aquela solicitação, salvo reabertura explícita.

Regras de provisionamento
• Aprovação deve disparar atribuição da função padrão exatamente uma vez.
• Atribuição de papel deve ser idempotente.
• Falha em integração externa não deve corromper o estado interno; deve gerar estado compensável ou pendência operacional.

Regras de auditoria
• Toda ação crítica deve gerar log:
  - criação de solicitação;
  - início de análise;
  - aprovação;
  - rejeição;
  - atribuição de papel;
  - sincronização externa;
  - falhas.

Casos de uso
Principais casos de uso do sistema
Autenticar usuário
Submeter solicitação de acesso
Consultar status da solicitação
Listar solicitações pendentes para moderação
Aprovar solicitação
Rejeitar solicitação
Atribuir função padrão automaticamente
Sincronizar identidade com Entra ID
Sincronizar identidade com SailPoint IdentityNow
Consultar trilha de auditoria

Diagrama de casos de uso

`mermaid
flowchart LR
    requester[Usuario Solicitante]
    moderator[Moderador]
    admin[Administrador]
    entra[Microsoft Entra ID]
    sailpoint[SailPoint IdentityNow]

    subgraph Sistema[Plataforma de Acesso]
        uc1((Autenticar usuario))
        uc2((Submeter solicitacao de acesso))
        uc3((Consultar status da solicitacao))
        uc4((Listar solicitacoes pendentes))
        uc5((Aprovar solicitacao))
        uc6((Rejeitar solicitacao))
        uc7((Atribuir funcao padrao))
        uc8((Sincronizar identidade Entra ID))
        uc9((Sincronizar identidade SailPoint))
        uc10((Consultar auditoria))
    end

    requester --> uc1
    requester --> uc2
    requester --> uc3

    moderator --> uc1
    moderator --> uc4
    moderator --> uc5
    moderator --> uc6

    admin --> uc10

    uc1 --> entra
    uc8 --> entra
    uc9 --> sailpoint

    uc5 --> uc7
    uc7 --> uc8
    uc7 --> uc9
`

Diagrama de sequência - aprovação da solicitação

`mermaid
sequenceDiagram
    actor Solicitante
    participant UI as Next.js
    participant API as API Gateway/BFF
    participant ARS as Access Request Service
    participant NATS as NATS
    participant MOD as Moderation Service
    participant PROV as Provisioning Service
    participant IAM as Identity & Access Service
    participant INT as Integration Service
    participant AUD as Audit Service
    participant NOTIF as Notification Service

    Solicitante->>UI: Submete solicitacao de acesso
    UI->>API: POST /access-requests
    API->>ARS: criarSolicitacao()
    ARS->>ARS: persiste AccessRequest(PENDING)
    ARS->>NATS: publica AccessRequestSubmitted
    ARS->>AUD: registrar criacao
    AUD-->>ARS: ok
    API-->>UI: 201 Created

    actor Moderador
    Moderador->>UI: Aprova solicitacao
    UI->>API: POST /access-requests/{id}/approve
    API->>MOD: aprovarSolicitacao()
    MOD->>MOD: valida permissao e registra ModerationDecision
    MOD->>NATS: publica AccessRequestApproved
    MOD->>AUD: registrar aprovacao

    NATS->>PROV: entrega AccessRequestApproved
    PROV->>PROV: cria ProvisioningTask
    PROV->>IAM: atribuir role padrao BASICUSER
    IAM->>IAM: persiste UserRole
    IAM->>NATS: publica DefaultRoleAssigned

    PROV->>INT: sincronizar Entra ID / SailPoint
    INT->>INT: executa integracoes externas
    INT->>NATS: publica ExternalIdentitySynchronized

    PROV->>NATS: publica UserProvisioned
    NATS->>AUD: entrega eventos para auditoria
    NATS->>NOTIF: notificar solicitante sobre aprovacao
`

Diagrama de sequência - rejeição da solicitação

`mermaid
sequenceDiagram
    actor Moderador
    participant UI as Next.js
    participant API as API Gateway/BFF
    participant MOD as Moderation Service
    participant ARS as Access Request Service
    participant NATS as NATS
    participant AUD as Audit Service
    participant NOTIF as Notification Service

    Moderador->>UI: Rejeita solicitacao com motivo
    UI->>API: POST /access-requests/{id}/reject
    API->>MOD: rejeitarSolicitacao()
    MOD->>MOD: valida permissao e registra ModerationDecision
    MOD->>NATS: publica AccessRequestRejected
    MOD->>AUD: registrar rejeicao

    NATS->>ARS: atualiza status da AccessRequest para REJECTED
    NATS->>AUD: registra evento de negocio
    NATS->>NOTIF: envia notificacao ao solicitante
`

Modelo entidade-relacionamento

Primeiro, a visão conceitual.

`mermaid
erDiagram
    USER ||--o{ ACCESSREQUEST : "submete"
    USER ||--o{ MODERATIONDECISION : "decide"
    ACCESSREQUEST ||--o| MODERATIONDECISION : "possui"
    USER ||--o{ USERROLE : "recebe"
    ROLE ||--o{ USERROLE : "atribui"
    ROLE ||--o{ ROLEPERMISSION : "possui"
    PERMISSION ||--o{ ROLEPERMISSION : "compoe"
    USER ||--o{ EXTERNALIDENTITYLINK : "vincula"
    ACCESSREQUEST ||--o{ PROVISIONINGTASK : "gera"
    USER ||--o{ AUDITLOG : "atuacomoator"
    USER ||--o{ AUDITLOG : "atuacomoalvo"
    USER ||--o{ NOTIFICATION : "recebe"

    USER {
        uuid id PK
        string email
        string fullname
        string status
        datetime createdat
        datetime updatedat
        datetime lastloginat
    }

    ACCESSREQUEST {
        uuid id PK
        uuid requesteruserid FK
        string requestedemail
        string justification
        string status
        uuid currentmoderatoruserid FK
        string correlationid
        datetime submittedat
        datetime reviewstartedat
        datetime resolvedat
        string resolutionreason
    }

    MODERATIONDECISION {
        uuid id PK
        uuid accessrequestid FK
        uuid moderatoruserid FK
        string decision
        string reason
        datetime decidedat
    }

    ROLE {
        uuid id PK
        string code
        string name
        string description
        boolean isdefault
        datetime createdat
    }

    PERMISSION {
        uuid id PK
        string code
        string description
    }

    ROLEPERMISSION {
        uuid roleid FK
        uuid permissionid FK
    }

    USERROLE {
        uuid id PK
        uuid userid FK
        uuid roleid FK
        uuid assignedbyuserid FK
        string assignmentreason
        datetime assignedat
        datetime revokedat
    }

    EXTERNALIDENTITYLINK {
        uuid id PK
        uuid userid FK
        string provider
        string externalid
        string externalusername
        string syncstatus
        datetime lastsyncedat
    }

    PROVISIONINGTASK {
        uuid id PK
        uuid accessrequestid FK
        uuid userid FK
        string status
        int retrycount
        string errorcode
        string errormessage
        datetime startedat
        datetime finishedat
    }

    AUDITLOG {
        uuid id PK
        string eventtype
        string entitytype
        uuid entityid
        uuid actoruserid FK
        uuid subjectuserid FK
        string correlationid
        string causationid
        json payload
        string ipaddress
        string useragent
        datetime createdat
    }

    NOTIFICATION {
        uuid id PK
        uuid userid FK
        string type
        string channel
        string status
        json payload
        datetime sentat
    }
`

ER lógico sugerido

Abaixo está uma forma de modelar as tabelas principais com cardinalidades mais claras.

| Entidade | Relacionamentos principais |
|---|---|
| users | 1:N com accessrequests, 1:N com userroles, 1:N com externalidentitylinks |
| accessrequests | N:1 com users (requester), 1:0..1 com moderationdecisions, 1:N com provisioningtasks |
| moderationdecisions | N:1 com accessrequests, N:1 com users (moderator) |
| roles | 1:N com userroles, N:N com permissions via rolepermissions |
| auditlogs | N:1 com users como ator e como alvo |
| notifications | N:1 com users |
| externalidentitylinks | N:1 com users |

Tópicos de integração com Microsoft Entra ID e SailPoint
Microsoft Entra ID

Pode cumprir dois papéis:

• IdP para autenticação via OAuth2 / OIDC;
• fonte externa de identidade/grupos.

Integrações possíveis
• buscar atributos do usuário após login;
• validar existência do usuário corporativo;
• opcionalmente refletir grupos/papéis da plataforma em grupos do Entra;
• armazenar entraObjectId em externalidentitylinks.

SailPoint IdentityNow

Pode ser usado para:

• governança de identidade;
• trilha de provisionamento;
• sincronização de status de acesso;
• reconciliação de atribuições.

Integrações possíveis
• criar/atualizar vínculo da identidade;
• registrar concessão de acesso;
• registrar revogação futura;
• armazenar identityNowId em externalidentitylinks.

Tópicos de auditoria e observabilidade
Auditabilidade funcional

Toda ação de negócio relevante deve registrar:

• quem executou;
• sobre quem a ação ocorreu;
• o que aconteceu;
• quando aconteceu;
• correlationId da jornada;
• payload mínimo necessário.

Exemplos de eventos auditáveis
• login bem-sucedido;
• login negado;
• solicitação criada;
• solicitação aprovada;
• solicitação rejeitada;
• role padrão atribuída;
• sincronização externa concluída;
• falha de provisionamento.

Logging técnico

Além do AuditLog, usar logs estruturados com:

• traceId
• correlationId
• requestId
• userId
• serviceName
• eventType

Ferramentas comuns:

• Pino no Nest.js;
• OpenTelemetry para tracing;
• Grafana/Loki/Tempo ou ELK.

Estrutura de módulos no Nest.js

Uma organização possível:

`text
src/
  modules/
    auth/
    users/
    roles/
    permissions/
    access-requests/
    moderation/
    provisioning/
    integrations/
      entra/
      sailpoint/
    audit/
    notifications/
    outbox/
    inbox/
  common/
    events/
    guards/
    interceptors/
    persistence/
`

Assuntos NATS sugeridos

Uma convenção simples:

`text
access.request.submitted
access.request.underreview
access.request.approved
access.request.rejected
user.role.defaultassigned
user.provisioning.started
user.provisioned
user.provisioning.failed
identity.external.synchronized
audit.log.created
`

Se quiser versionar no nome:

`text
access.request.approved.v1
`

Exemplo de comandos e eventos
Comandos síncronos HTTP
• POST /access-requests
• GET /access-requests/me
• GET /moderation/access-requests?status=PENDING
• POST /moderation/access-requests/:id/approve
• POST /moderation/access-requests/:id/reject
• GET /audit-logs?correlationId=...

Eventos assíncronos
• AccessRequestSubmitted
• AccessRequestApproved
• AccessRequestRejected
• DefaultRoleAssigned
• UserProvisioned
• ProvisioningFailed

Estados da solicitação

Este diagrama ajuda a visualizar o ciclo de vida de AccessRequest.

`mermaid
stateDiagram-v2
    [] --> PENDING
    PENDING --> UNDERREVIEW : moderador assume
    PENDING --> APPROVED : aprovado diretamente
    PENDING --> REJECTED : rejeitado diretamente
    UNDERREVIEW --> APPROVED : aprovar
    UNDERREVIEW --> REJECTED : rejeitar
    PENDING --> CANCELLED : solicitante cancela
    PENDING --> EXPIRED : expira SLA
    UNDERREVIEW --> EXPIRED : expira SLA
    APPROVED --> []
    REJECTED --> []
    CANCELLED --> []
    EXPIRED --> [*]
`

Sugestão de separação entre eventos de domínio e eventos de integração
Eventos de domínio internos

Usados entre módulos da própria plataforma:

• AccessRequestSubmitted
• ModerationDecisionRecorded
• DefaultRoleAssigned
• UserProvisioned

Eventos de integração

Usados para efeitos externos ou interoperabilidade:

• EntraIdentitySyncRequested
• EntraIdentitySynchronized
• SailPointProvisioningRequested
• SailPointProvisioningCompleted

Isso ajuda a não poluir o núcleo do domínio com detalhes de infraestrutura externa.

Considerações de segurança
• Validar issuer, audience, signature, exp, nbf do JWT.
• Não confiar apenas em papéis vindos do provedor externo sem política local.
• Manter autorização sensível do moderador também no banco interno.
• Registrar IP, user agent e identificadores de sessão para auditoria.
• Aplicar segregação de função para evitar autoaprovação, se exigido.

Recomendação de implementação prática

Para esse stack, a abordagem mais equilibrada costuma ser:

• monorepo com apps Nest.js modulares;
• começar com modular monolith e eventos internos + NATS para integrações assíncronas;
• evoluir para microsserviços apenas se houver necessidade operacional real.

Por que isso faz sentido aqui

Seu domínio tem:
• fluxo bem definido;
• forte necessidade de auditoria;
• integrações externas;
• processamento assíncrono natural.

Mas também tem:
• consistência importante entre solicitação, decisão e provisionamento.

Por isso, um monólito modular com outbox + NATS costuma ser mais simples e robusto do que partir cedo para muitos serviços distribuídos.

Proposta resumida de agregados

| Agregado | Raiz | Objetivo |
|---|---|---|
| Acesso | AccessRequest | controlar solicitação e status |
| Moderação | ModerationDecision ou AccessRequest | formalizar decisão |
| Identidade | User | representar ator/autorização |
| Autorização | Role | agrupar permissões |
| Provisionamento | ProvisioningTask | rastrear concessão técnica |
| Auditoria | AuditLog | evidenciar operações |

Exemplo de sequência de eventos de aprovação
AccessRequestSubmitted
AccessRequestApproved
UserProvisioningStarted
DefaultRoleAssigned
ExternalIdentitySynchronized
UserProvisioned`

Cada evento compartilha o mesmo correlationId.

Conclusão arquitetural

A arquitetura recomendada é uma arquitetura orientada a eventos sobre um núcleo de domínio transacional, com:

• Nest.js como backend modular;
• PostgreSQL para persistência relacional;
• NATS para integração assíncrona e propagação de eventos;
• OAuth2/OIDC + JWT para autenticação/autorização;
• Microsoft Entra ID como IdP e fonte externa de identidade;
• SailPoint IdentityNow como camada de governança/provisionamento complementar;
• AuditLog + Outbox + Idempotência para rastreabilidade e confiabilidade.

Essa combinação atende bem aos requisitos de:
• moderação humana;
• concessão automática de papel padrão;
• integração corporativa de identidade;
• auditabilidade completa.

Próximo refinamento técnico

Um passo lógico seguinte é transformar essa proposta em um documento de arquitetura mais formal, contendo:

• modelo C4 (Contexto, Contêineres e Componentes);
• DDL SQL inicial das tabelas;
• contratos de eventos NATS;
• exemplo de módulos Nest.js com handlers, publishers e consumers;
• matriz RBAC de papéis e permissões.
