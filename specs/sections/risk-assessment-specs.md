# Avaliação Técnica | Suzano/Thera Consulting | Aspectos de segurança

## Índice de conteúdo

<!-- TOC -->

- [Avaliação Técnica | Suzano/Thera Consulting | Aspectos de segurança](#avalia%C3%A7%C3%A3o-t%C3%A9cnica--suzanothera-consulting--aspectos-de-seguran%C3%A7a)
    - [Índice de conteúdo](#%C3%ADndice-de-conte%C3%BAdo)
    - [Introdução](#introdu%C3%A7%C3%A3o)
    - [Análise de riscos high-level](#an%C3%A1lise-de-riscos-high-level)
        - [Riscos associados à camada de autenticação e autorização](#riscos-associados-%C3%A0-camada-de-autentica%C3%A7%C3%A3o-e-autoriza%C3%A7%C3%A3o)
            - [Authentication & OAuth2 / Entra ID Risks](#authentication--oauth2--entra-id-risks)
            - [Authorization & JWT Risks](#authorization--jwt-risks)
        - [Riscos associados ao modelo de papéis e permissões](#riscos-associados-ao-modelo-de-pap%C3%A9is-e-permiss%C3%B5es)
            - [Moderated Access Request Risks](#moderated-access-request-risks)
            - [Automatic Default Role Assignment Risks](#automatic-default-role-assignment-risks)
        - [Riscos associados à integrações com serviços externos](#riscos-associados-%C3%A0-integra%C3%A7%C3%B5es-com-servi%C3%A7os-externos)
            - [External Integrations Sailpoint & Entra ID](#external-integrations-sailpoint--entra-id)
        - [Riscos associados ao SGBD PostgreSQL e também à camada de persistência associada Sequelize + NestJS](#riscos-associados-ao-sgbd-postgresql-e-tamb%C3%A9m-%C3%A0-camada-de-persist%C3%AAncia-associada-sequelize--nestjs)
        - [Riscos associados ao mecanismo de auditoria logging de eventos](#riscos-associados-ao-mecanismo-de-auditoria-logging-de-eventos)
        - [Riscos de natureza genérica](#riscos-de-natureza-gen%C3%A9rica)
    - [Mitigation Recommendations High-Level](#mitigation-recommendations-high-level)
    - [O que deseja fazer?](#o-que-deseja-fazer)

<!-- /TOC -->

## Introdução

De posse de todos os elementos de modelagem da plataforma de gerenciamento de acessos, estamos em condições de apontar possíveis pontos nos quais a plataforma pode ser vulnerávei, i.e. é feito aqui um esquadrinhamento mais detalhado de vulnerabilidades que a arquitetura proposta pode possuir.

## Análise de riscos (high-level)

O que segue agora é apenas uma listagem de pontos de risco, nas camadas pertinentes do caso de uso principal, que carecem de uma investigação posterior mais profunda e.g. a aplicação de um modelo STRIDE de avaliação de ameaças, da qual já emana uma estratégia de mitigação de riscos mais confiável.

### Riscos associados à camada de autenticação e autorização

#### Authentication & OAuth2 / Entra ID Risks

- Token Theft / Phishing / OAuth Consent Attacks: Attackers can phish users to obtain authorization codes or refresh tokens via malicious apps or fake Entra ID login pages. Compromised tokens grant access to the platform (and potentially other Microsoft services).
- Improper Token Validation: Failing to validate audience (aud), issuer (iss), signature, expiration, or Entra ID-specific claims can allow forged or replayed tokens.
- Opaque vs JWT Tokens: Entra ID may return opaque tokens in some flows, leading to mishandling or incorrect validation logic.
- Missing PKCE or State Parameter: In authorization code flow, this enables CSRF or code interception attacks.
- Long-lived Refresh Tokens: Without proper rotation, revocation, or short lifetimes, stolen refresh tokens provide persistent access.

#### Authorization & JWT Risks

- JWT Misuse / Weak Configuration: Insufficient signing algorithm (e.g., allowing none), weak secret/key, missing expiration (exp), or not validating nbf/iat. Overly permissive claims embedding (roles/permissions) can lead to privilege escalation if tokens are tampered with.
- Client-Side JWT Storage: If stored insecurely (localStorage vs HttpOnly cookies), vulnerable to XSS attacks.
- Broken Access Control: Failure to re-validate permissions on every request (relying solely on embedded JWT roles) after changes in the database.
- Insecure Direct Object References (IDOR): Moderators or users accessing requests/users by ID without proper ownership/permission checks.

### Riscos associados ao modelo de papéis e permissões

####  Moderated Access Request Risks

- Moderator Privilege Abuse: A compromised or malicious moderator can approve malicious requests or assign excessive permissions.
- Bypassing Moderation: Race conditions, missing validation, or direct API calls that create/approve requests without proper checks.
- Request Forging / Spam: Unauthenticated or weakly validated request submissions leading to DoS or noise in the moderation queue.
- Privilege Creep: Approved users accumulating permissions over time if old requests/roles are not cleaned up.

#### Automatic Default Role Assignment Risks

- Overly Permissive Default Role: If the "BASIC" role grants more access than intended (e.g., sensitive endpoints), new users immediately expose the platform to risks.
- Timing / Race Conditions: During approval, if role assignment and Sailpoint provisioning are not atomic (within a Sequelize transaction), partial failures can leave users in inconsistent states.
- Lack of Least Privilege: Automatic assignment without context-specific scoping.

### Riscos associados à integrações com serviços externos

#### External Integrations (Sailpoint & Entra ID)

API Credential Exposure: Compromised Sailpoint client secrets or Entra ID app credentials allow attackers to provision identities or query users.
Inconsistent Provisioning: Failures in Sailpoint syncs can create orphaned accounts or mismatched permissions between systems.
Supply Chain / Third-Party Risks: Vulnerabilities in Entra ID or Sailpoint (or their client libraries) affect the platform.

### Riscos associados ao SGBD (PostgreSQL) e também à camada de persistência associada (Sequelize + NestJS)

- SQL Injection: Although Sequelize uses parameterized queries, raw queries or improper sanitization remain risky.
- Data Exposure: Sensitive fields (e.g., audit logs with PII, user details) not properly encrypted at rest or exposed via misconfigured queries.
- Missing Input Validation / Rate Limiting: On access request or moderation endpoints, leading to injection, DoS, or brute-force.
- Session / Token Management: No token revocation list (blacklist) for logout or compromised accounts.

### Riscos associados ao mecanismo de auditoria (logging de eventos)

- Incomplete or Tamperable Logs: If logs are not immutable, protected, or missing critical fields (actor, target, before/after state, IP, timestamp), investigations become unreliable.
- Log Forging: Insufficient validation when writing AUDIT_LOG entries.
- Performance / Storage Issues: Excessive logging leading to storage exhaustion or missing logs during high load.

### Riscos de natureza genérica

- XSS, CSRF, CORS Misconfiguration: Especially relevant for the frontend interacting with OAuth flows and API.
- Dependency Vulnerabilities: Outdated NestJS, Sequelize, JWT libraries, or other npm packages.
- Insider Threats & Separation of Duties: Moderators having overlapping permissions with admins.
- Compliance & Data Privacy: Improper handling of personal data during provisioning/sync with Sailpoint/Entra ID (GDPR, etc.).
- Denial of Service: Uncontrolled access request volume or heavy Sailpoint/Entra calls.


## Mitigation Recommendations (High-Level)

- Use secure OAuth2 libraries with PKCE, validate all tokens strictly (including claims).
- Implement short-lived JWTs + refresh token rotation + blacklist.
- Enforce least privilege, regular access reviews, and SoD (Separation of Duties).
- Use database transactions for approval flows.
- Enable comprehensive, tamper-proof audit logging (e.g., append-only with digital signatures or external SIEM).
- Regular pentests, dependency scanning, and zero-trust principles.
- Monitor Entra ID sign-in logs and Sailpoint events for anomalies.

This is not an exhaustive list — a proper threat model (e.g., STRIDE) and penetration testing tailored to your implementation would reveal more context-specific issues. Let me know if you want a deeper dive into any category or mitigation strategies!

---
## O que deseja fazer?
- [Voltar ao topo](#ìndice-do-conteúdo)
- [Voltar à raiz](../main.md)