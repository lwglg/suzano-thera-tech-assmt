# Avaliação Técnica | Suzand/Thera Consulting | *Bounded Contexts* e Serviços


<!-- TOC -->

- [Avaliação Técnica | Suzand/Thera Consulting | Bounded Contexts e Serviços](#avalia%C3%A7%C3%A3o-t%C3%A9cnica--suzandthera-consulting--bounded-contexts-e-servi%C3%A7os)
    - [Especificações do escopos](#especifica%C3%A7%C3%B5es-do-escopos)
        - [Moderation](#moderation)
        - [Agregado/entidades associadas](#agregadoentidades-associadas)
        - [Provisioning](#provisioning)
        - [Agregado/entidades associadas](#agregadoentidades-associadas)
        - [Audit](#audit)
        - [Entidade central](#entidade-central)

<!-- /TOC -->


## Especificações do escopos

<table>
    <tr>
        <th>Nome do escopo</th>
        <th>Responsabilidades</th>
        <th>Agregado/entidades centrais</th>
        <th>Estados típicos</th>
    </tr>
    <tr>
        <td>Identity & Access</td>
        <td rowspan="5">
            - Cadastro lógico do usuário na plataforma;<br/>
            - Vinculação com identidade externa;<br/>
            - Papéis e permissões;<br/>
            - Emissão/validação de claims para autorização;<br/>
            - Estado de acesso do usuário.
        </td>
        <td rowspan="5">
            - User <br/>
            - Role <br/>
            - Permission <br/>
            - UserRole <br/>
            - ExternalIdentityLink
        </td>
        <td>N/A</td>
    </tr>
    <tr>
        <td>Access Request</td>
        <td rowspan="6">
            - Criação da solicitação;<br/>
            - Captura de justificativa e metadados;<br/>
            - Controle do status da solicitação;<br/>
            - Associação entre solicitante, moderador e decisão.
        </td>
        <td>
            - AccessRequest
        </td>
        <td rowspan="6">
            - PENDING<br/>
            - UNDER_REVIEW<br/>
            - APPROVED<br/>
            - REJECTED<br/>
            - CANCELLED<br/>
            - EXPIRED
        </td>
    </tr>
</table>




### 3. Moderation
Responsável por:

- verificar se o ator possui permissão de moderação;
- registrar decisão;
- garantir regras como segregação de função;
- disparar eventos de aprovação/rejeição.

### Agregado/entidades associadas

ModerationDecision
ModerationAssignment (opcional, se houver distribuição de fila)

### 4. Provisioning
Responsável por:

- após aprovação, provisionar acesso interno;
- atribuir automaticamente a função padrão;
- opcionalmente sincronizar grupo/papel em Entra ID e SailPoint;
- confirmar sucesso ou falha do provisionamento.

### Agregado/entidades associadas

- ProvisioningTask
- DefaultRolePolicy


### 5. Audit
Responsável por:

- registrar eventos de negócio e técnicos;
- associar operação, ator, alvo, correlação e timestamps;
- apoiar trilha forense e compliance.

### Entidade central
AuditLog