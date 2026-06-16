# Avaliação Técnica | Suzano/Thera Consulting | Entidades de Domínio

## Índice de conteúdo

<!-- TOC -->

- [Avaliação Técnica | Suzano/Thera Consulting | Entidades de Domínio](#avalia%C3%A7%C3%A3o-t%C3%A9cnica--suzanothera-consulting--entidades-de-dom%C3%ADnio)
    - [Índice de conteúdo](#%C3%ADndice-de-conte%C3%BAdo)
    - [Detalhamento](#detalhamento)
    - [Modelo entidade-relacionamento](#modelo-entidade-relacionamento)
        - [ER lógico sugerido](#er-l%C3%B3gico-sugerido)
    - [O que deseja fazer?](#o-que-deseja-fazer)

<!-- /TOC -->

## Detalhamento

A seguir, a descrição de cada entidade principal.

<table>
    <tr>
        <th>Nome da entidade</th>
        <th>Descrição</th>
        <th>Atributos principais</th>
        <th>Responsabilidades</th>
    </tr>
    <tr>
        <td>User</td>
        <td>Representa o usuário da plataforma, seja solicitante, moderador ou administrador.</td>
        <td>
            - id <br/>
            - email <br/>
            - fullName <br/>
            - status (PENDINGACCESS, ACTIVE, REJECTED, BLOCKED, INACTIVE) <br/>
            - createdAt <br/>
            - updatedAt <br/>
            - lastLoginAt <br/>
        </td>
        <td>
            - identificar o ator principal do sistema; <br/>
            - manter o estado de acesso; <br/>
            - associar papéis e identidades externas. <br/>
        </td>
    </tr>
    <tr>
        <td>ExternalIdentityLink</td>
        <td>Representa o vínculo do usuário com identidades em provedores externos.</td>
        <td>
            - id <br/>
            - userId <br/>
            - provider (ENTRAID, SAILPOINT) <br/>
            - externalId <br/>
            - externalUsername <br/>
            - syncStatus <br/>
            - lastSyncedAt <br/>
        </td>
        <td>
            - relacionar identidade interna com identidades externas;; <br/>
            - rastrear sincronização com Entra ID e SailPoint. <br/>
        </td>
    </tr>
    <tr>
        <td>Role</td>
        <td>Representa uma função/perfil de acesso.</td>
        <td>
            - id <br/>
            - code (ex.: BASICUSER, MODERATOR, ADMIN) <br/>
            - name <br/>
            - description <br/>
            - isDefault <br/>
            - createdAt <br/>
        </td>
        <td>
            - Agrupar permissões; <br/>
            - definir a função padrão atribuída após aprovação. <br/>
        </td>
    </tr>
    <tr>
        <td>Permission</td>
        <td>Representa uma permissão atômica do sistema.</td>
        <td>
            - id <br/>
            - code (ex.: accessrequest:approve) <br/>
            - description <br/>
        </td>
        <td>
            - Permitir autorização granular; <br/>
            - Compor papéis. <br/>
        </td>
    </tr>
    <tr>
        <td>RolePermission</td>
        <td>Entidade de associação entre papel e permissão.</td>
        <td>
            - roleId <br/>
            - permissionId <br/>
        </td>
        <td>
            - Mapear autorização baseada em RBAC. <br/>
        </td>
    </tr>
    <tr>
        <td>UserRole</td>
        <td>Entidade de associação entre usuário e papel.</td>
        <td>
            - id <br/>
            - userId <br/>
            - roleId <br/>
            - assignedByUserId <br/>
            - assignmentReason <br/>
            - assignedAt <br/>
            - revokedAt <br/>
        </td>
        <td>
            - Registrar atribuição de papéis; <br/>
            - Manter evidência de quem concedeu o papel. <br/>
        </td>
    </tr>
    <tr>
        <td>AccessRequest</td>
        <td>Representa a solicitação de acesso submetida pelo usuário.</td>
        <td>
            - id <br/>
            - requesterUserId <br/>
            - requestedEmail <br/>
            - justification <br/>
            - status <br/>
            - submittedAt <br/>
            - reviewStartedAt <br/>
            - resolvedAt <br/>
            - resolutionReason <br/>
            - currentModeratorUserId <br/>
            - correlationId <br/>
        </td>
        <td>
            - centralizar o ciclo de vida da solicitação; <br/>
            - armazenar contexto da análise; <br/>
            - servir como raiz do agregado de solicitação. <br/>
        </td>
    </tr>
    <tr>
        <td>ModerationDecision</td>
        <td>Representa a decisão formal do moderador sobre uma solicitação.</td>
        <td>
            - id <br/>
            - accessRequestId <br/>
            - moderatorUserId <br/>
            - decision (APPROVED, REJECTED) <br/>
            - reason <br/>
            - decidedAt <br/>
        </td>
        <td>
            - Registrar a decisão imutável do moderador; <br/>
            - Garantir trilha auditável da análise. <br/>
        </td>
    </tr>
    <tr>
        <td>ProvisioningTask</td>
        <td>Representa o processo de provisionamento disparado após aprovação.</td>
        <td>
            - id <br/>
            - accessRequestId <br/>
            - userId <br/>
            - status (PENDING, INPROGRESS, COMPLETED, FAILED) <br/>
            - startedAt <br/>
            - finishedAt <br/>
            - errorCode <br/>
            - errorMessage <br/>
            - retryCount <br/>
        </td>
        <td>
            - Rastrear a execução técnica do provisionamento; <br/>
            - Permitir retentativas e suporte operacional. <br/>
        </td>
    </tr>
    <tr>
        <td>AuditLog</td>
        <td>Representa o registro auditável de uma operação.</td>
        <td>
            - id <br/>
            - eventType <br/>
            - entityType <br/>
            - entityId <br/>
            - actorUserId <br/>
            - subjectUserId <br/>
            - correlationId <br/>
            - causationId <br/>
            - payload <br/>
            - createdAt <br/>
            - ipAddress <br/>
            - userAgent <br/>
        </td>
        <td>
            - Registrar ações de negócio e integração; <br/>
            - Suportar auditoria, investigação e compliance. <br/>
        </td>
    </tr>
    <tr>
        <td>Notification</td>
        <td>Representa uma notificação a ser entregue ou já entregue.</td>
        <td>
            - id <br/>
            - userId <br/>
            - type <br/>
            - channel <br/>
            - status <br/>
            - payload <br/>
            - sentAt <br/>
        </td>
        <td>
            - Comunicar mudança de status da solicitação; <br/>
            - Manter evidência de entrega lógica. <br/>
        </td>
    </tr>
</table>


> **Observação**
> 
> Concernente à entidade `Notification`, haja vista que não é necessariamente do escopo dessa investigação técnica já definir o tipo de serviço que irá prover o envio de notificações, e.g. servidor SMTP para e-mail, API do WhatsApp para notificações PUSH, são incluídos na entidade apenas os atributos que estabelecem um vínculo com quem está recendo, sendo o atributo `channel` assumido aqui como arbitrário para a posterio definição do canal de envio de notificações.


## Modelo entidade-relacionamento

Primeiro, a visão conceitual.

```mermaid
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
```

### ER lógico sugerido

Abaixo está uma forma de modelar as tabelas principais com cardinalidades mais claras.

| Entidade              | Relacionamentos principais                                                                 |
|-----------------------|--------------------------------------------------------------------------------------------|
| `Users`               | 1:N com `AccessRequests`, 1:N com `UserRoles` , 1:N com `ExternalIdentityLinks`            |
| `AccessRequests`      | N:1 com `Users` (requester), 1:0..1 com `ModerationDecisions`, 1:N com `ProvisioningTasks` |
| `ModerationDecisions` | N:1 com `accessrequests`, N:1 com `Users` (moderator)                                      |
| `Eoles`                 | 1:N com `UserRoles`, N:N com `Permissions` via ``RolePermissions`                       |
| `AuditLogs`             | N:1 com `Users` como ator e como alvo                                                  |
| `Notifications`         | N:1 com `Users`                                                                        |
| `ExternalIdentityLinks` | N:1 com `Users`                                                                        |


---

## O que deseja fazer?

- [Voltar ao topo](#índice-de-conteúdo)
- [Voltar à raíz](../README.md)
- [Fluxo de negócio](./event-oriented-flow-specs.md)
- [Casos de uso](./use-cases-specs.md)
