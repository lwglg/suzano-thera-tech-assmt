# Avaliação Técnica | Suzand/Thera Consulting | *Bounded Contexts* e Serviços

## Índice de conteúdo

<!-- TOC -->

- [Avaliação Técnica | Suzand/Thera Consulting | Bounded Contexts e Serviços](#avalia%C3%A7%C3%A3o-t%C3%A9cnica--suzandthera-consulting--bounded-contexts-e-servi%C3%A7os)
    - [Índice de conteúdo](#%C3%ADndice-de-conte%C3%BAdo)
    - [Especificações do escopos](#especifica%C3%A7%C3%B5es-do-escopos)
    - [O que deseja fazer?](#o-que-deseja-fazer)

<!-- /TOC -->


## Especificações do escopos

Aqui cada escopo e seus atributos posteriormente serão referidos à serviços específicos:

<table>
    <tr>
        <th>Nome do escopo</th>
        <th>Responsabilidades</th>
        <th>Agregado/entidades centrais</th>
        <th>Estados típicos</th>
    </tr>
    <tr>
        <td>Identity & Access</td>
        <td>
            - Cadastro lógico do usuário na plataforma;<br/>
            - Vinculação com identidade externa;<br/>
            - Papéis e permissões;<br/>
            - Emissão/validação de claims para autorização;<br/>
            - Estado de acesso do usuário.
        </td>
        <td>
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
        <td>
            - Criação da solicitação;<br/>
            - Captura de justificativa e metadados;<br/>
            - Controle do status da solicitação;<br/>
            - Associação entre solicitante, moderador e decisão.
        </td>
        <td>- AccessRequest</td>
        <td>
            - PENDING<br/>
            - UNDER_REVIEW<br/>
            - APPROVED<br/>
            - REJECTED<br/>
            - CANCELLED<br/>
            - EXPIRED
        </td>
    </tr> 
    <tr>
        <td> Moderation</td>
        <td>
            - Verificar se o ator possui permissão de moderação;<br/>
            - Registrar decisão;<br/>
            - Garantir regras como segregação de função;<br/>
            - Disparar eventos de aprovação/rejeição.<br/>
        </td>
        <td>
            - ModerationDecision<br/>
            - ModerationAssignment (opcional, se houver distribuição de fila)
        </td>
        <td></td>
    </tr> 
    <tr>
        <td>Provisioning</td>
        <td>
            - Após aprovação, provisionar acesso interno;<br/>
            - Atribuir automaticamente a função padrão;<br/>
            - Opcionalmente sincronizar grupo/papel em Entra ID e SailPoint;<br/>
            - Confirmar sucesso ou falha do provisionamento.<br/>
        </td>
        <td>
            - ProvisioningTask;<br/>
            - DefaultRolePolicy.<br/>
        </td>
        <td></td>
    </tr>
    <tr>
        <td>Audit</td>
        <td>
            - Registrar eventos de negócio e técnicos;<br/>
            - Associar operação, ator, alvo, correlação e timestamps;<br/>
            - Apoiar trilha forense e compliance.<br/>
        </td>
        <td>
            - AuditLog.<br/>
        </td>
        <td></td>
    </tr> 
</table>

--- 

##  O que deseja fazer?

- [Voltar ao topo](#índice-de-conteúdo)
- [Voltar à raíz](../README.md)
- [Visão de arquitetura](./architecture-specs.md);
- [Fluxo de negócio](./event-oriented-flow-specs.md);