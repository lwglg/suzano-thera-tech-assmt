# Avaliação Técnica | Suzano/Thera Consulting | Aspectos de segurança

## Índice de conteúdo

<!-- TOC -->

- [Avaliação Técnica | Suzano/Thera Consulting | Aspectos de segurança](#avalia%C3%A7%C3%A3o-t%C3%A9cnica--suzanothera-consulting--aspectos-de-seguran%C3%A7a)
    - [Índice de conteúdo](#%C3%ADndice-de-conte%C3%BAdo)
    - [Introdução](#introdu%C3%A7%C3%A3o)
        - [Riscos associados à camada de autenticação e autorização](#riscos-associados-%C3%A0-camada-de-autentica%C3%A7%C3%A3o-e-autoriza%C3%A7%C3%A3o)
            - [Camada de autenticação e OAuth2 / Entra ID](#camada-de-autentica%C3%A7%C3%A3o-e-oauth2--entra-id)
            - [Camada de autorização e uso do JWT](#camada-de-autoriza%C3%A7%C3%A3o-e-uso-do-jwt)
        - [Riscos associados ao modelo de papéis e permissões](#riscos-associados-ao-modelo-de-pap%C3%A9is-e-permiss%C3%B5es)
            - [Camada de moderação de requisições de acessos](#camada-de-modera%C3%A7%C3%A3o-de-requisi%C3%A7%C3%B5es-de-acessos)
            - [Provisionamento automático de identidade papéis e permissões](#provisionamento-autom%C3%A1tico-de-identidade-pap%C3%A9is-e-permiss%C3%B5es)
        - [Riscos associados à integrações com serviços externos](#riscos-associados-%C3%A0-integra%C3%A7%C3%B5es-com-servi%C3%A7os-externos)
            - [Integrações externas Sailpoint & Entra ID](#integra%C3%A7%C3%B5es-externas-sailpoint--entra-id)
        - [Riscos associados à camada de persistência de dados DB relacional](#riscos-associados-%C3%A0-camada-de-persist%C3%AAncia-de-dados-db-relacional)
        - [Riscos associados ao mecanismo de auditoria logging de eventos](#riscos-associados-ao-mecanismo-de-auditoria-logging-de-eventos)
        - [Riscos de natureza genérica](#riscos-de-natureza-gen%C3%A9rica)
    - [O que deseja fazer?](#o-que-deseja-fazer)

<!-- /TOC -->

## Introdução

De posse de todos os elementos de modelagem da plataforma de gerenciamento de acessos, estamos em condições de apontar possíveis pontos nos quais a plataforma pode ser vulnerávei, i.e. é feito aqui um esquadrinhamento mais detalhado de vulnerabilidades que a arquitetura proposta pode possuir.

O que segue agora é apenas uma listagem de pontos de risco, nas camadas pertinentes do caso de uso principal, que carecem de uma investigação posterior mais profunda e.g. a aplicação de um modelo STRIDE de avaliação de ameaças, da qual já emana uma estratégia de mitigação de riscos mais confiável.

### Riscos associados à camada de autenticação e autorização

#### Camada de autenticação e OAuth2 / Entra ID

- **Roubo de Tokens / Phishing / Ataques de Consentimento OAuth**: Os invasores podem usar phishing para obter códigos de autorização ou tokens de atualização de usuários por meio de aplicativos maliciosos ou páginas de login falsas do Entra ID. Tokens comprometidos concedem acesso à plataforma (e potencialmente a outros serviços da Microsoft).
- **Validação Inadequada de Tokens**: A falha na validação do público-alvo (aud), emissor (iss), assinatura, expiração ou declarações específicas do Entra ID pode permitir tokens falsificados ou reutilizados.
- **Tokens Opacos vs. Tokens JWT**: O Entra ID pode retornar tokens opacos em alguns fluxos, levando a erros de manipulação ou lógica de validação incorreta.
- **Ausência de Parâmetro PKCE ou de Estado**: No fluxo de código de autorização, isso possibilita ataques CSRF ou de interceptação de código.
- **Tokens de Atualização de Longa Duração**: Sem rotação adequada, revogação ou com tempo de vida curto, tokens de atualização roubados fornecem acesso persistente.

#### Camada de autorização e uso do JWT

- Uso indevido de JWT / Configuração fraca: Algoritmo de assinatura insuficiente (por exemplo, não permitir nenhum), segredo/chave fraca, expiração (exp) ausente ou não validação de nbf/iat. Incorporação de declarações excessivamente permissivas (funções/permissões) pode levar à escalada de privilégios se os tokens forem adulterados.
- Armazenamento de JWT no lado do cliente: Se armazenado de forma insegura (localStorage vs. cookies HttpOnly), vulnerável a ataques XSS.
- Controle de acesso quebrado: Falha na revalidação de permissões em cada solicitação (dependendo exclusivamente de funções JWT incorporadas) após alterações no banco de dados.
- Referências diretas a objetos inseguras (IDOR): Moderadores ou usuários acessando solicitações/usuários por ID sem verificações adequadas de propriedade/permissão.

### Riscos associados ao modelo de papéis e permissões

#### Camada de moderação de requisições de acessos

- **Abuso de privilégios de moderador**: Um moderador comprometido ou malicioso pode aprovar solicitações maliciosas ou atribuir permissões excessivas.
- **Burla da moderação**: Condições de corrida, validação ausente ou chamadas diretas à API que criam/aprovam solicitações sem as devidas verificações.
- **Falsificação de solicitações/Spam**: Envio de solicitações não autenticadas ou com validação fraca, resultando em ataques de negação de serviço (DoS) ou ruído na fila de moderação.
- **Acúmulo de privilégios**: Usuários aprovados acumulando permissões ao longo do tempo se solicitações/funções antigas não forem removidas.

#### Provisionamento automático de identidade (papéis e permissões)

- **Role padrão excessivamente permissivo**: Se um role conceder mais acessos do que o pretendido (por exemplo, endpoints sensíveis), os novos usuários expõem imediatamente a plataforma a riscos.
- **Condições de tempo/corrida**: Durante a aprovação, se a atribuição de função e o provisionamento do Sailpoint não forem atômicos (dentro de uma transação Sequelize), falhas parciais podem deixar os usuários em estados inconsistentes.
- **Ausência do princípio do menor privilégio**: Atribuição automática sem escopo específico de contexto.

### Riscos associados à integrações com serviços externos

#### Integrações externas (Sailpoint & Entra ID)

- **Exposição de credenciais da API**: Segredos do cliente Sailpoint ou credenciais do aplicativo Entra ID comprometidos permitem que invasores provisionem identidades ou consultem usuários.
- **Provisionamento inconsistente**: Falhas na sincronização do Sailpoint podem criar contas órfãs ou permissões incompatíveis entre os sistemas.
- **Riscos na cadeia de suprimentos/terceiros**: Vulnerabilidades no Entra ID ou no Sailpoint (ou em suas bibliotecas de cliente) afetam a plataforma.

### Riscos associados à camada de persistência de dados (DB relacional)

- **Injeção SQL**: Embora o Sequelize, por exemplo, utilize consultas parametrizadas, consultas brutas ou sanitização inadequada ainda representam riscos.
- **Exposição de dados**: Campos sensíveis (por exemplo, logs de auditoria com informações pessoais identificáveis, detalhes do usuário) não criptografados adequadamente em repouso ou expostos por meio de consultas mal configuradas.
- **Ausência de validação de entrada/limitação de taxa**: Em endpoints de solicitação de acesso ou moderação, levando a injeção, DoS ou força bruta.
- **Gerenciamento de sessão/token**: Ausência de lista de revogação de tokens (lista negra) para contas desativadas ou comprometidas.

### Riscos associados ao mecanismo de auditoria (logging de eventos)

- **Registros incompletos ou adulteráveis**: Se os registros não forem imutáveis, protegidos ou estiverem faltando campos críticos (ator, alvo, estado antes/depois, IP, carimbo de data/hora), as investigações se tornam não confiáveis.
- **Falsificação de registros**: Validação insuficiente ao gravar entradas na tabela `AuditLog`.
- **Problemas de desempenho/armazenamento**: Registro excessivo levando ao esgotamento do armazenamento ou à perda de registros durante períodos de alta carga.

### Riscos de natureza genérica

- **XSS, CSRF, configuração incorreta de CORS**: Especialmente relevante para o frontend que interage com fluxos OAuth e APIs.
- **Vulnerabilidades de dependência**: Assumindo que se utilize na implementação uma stack sobre Node.js, e.g. NestJS, Sequelize, JWT, o estado de desatualização destas bibliotecas ou e suas subsidiárias pode ser superposto às vulnerabilidades da plataforma.
- **Ameaças internas e separação de funções**: Moderadores com permissões sobrepostas às dos administradores.
- **Conformidade e privacidade de dados**: Manuseio inadequado de dados pessoais durante o provisionamento/sincronização com o Sailpoint/Entra ID (GDPR, etc.), i.e. não conformidade com a LGPD.
- **Negação de serviço (DoS/DDoS)**: Volume descontrolado de solicitações de acesso ou grande volume de chamadas ao Sailpoint/Entra.

---
## O que deseja fazer?
- [Voltar ao topo](#ìndice-do-conteúdo)
- [Voltar à raiz](../README.md)
- [Casos de uso](./use-cases-specs.md)
- [Aspectos de escalabilidade](./scalability-specs.md)
