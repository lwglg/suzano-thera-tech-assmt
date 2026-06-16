# Avaliação Técnica | Suzano/Thera Consulting

Aqui encontra-se redigida a modelagem da solução de software em núvem que visa servir uma plataforma de gestão moderada de acessos de usuários, integrada às plataformas Microsoft Entra ID e SailPoint IdentityNow.

Todos os aspectos arquitetônicos e de casos de uso, à luz da especificação das condições de fronteiras iniciais, informados neste [documento](../resources/docs/pdf/Avaliação%20Técnica%20para%20Desenvolvedores%20Back%20Full.pdf), serão explorados em diferentes seções deste documento.

## Índice de conteúdo

<!-- TOC -->

- [Avaliação Técnica | Suzano/Thera Consulting](#avalia%C3%A7%C3%A3o-t%C3%A9cnica--suzanothera-consulting)
    - [Índice de conteúdo](#%C3%ADndice-de-conte%C3%BAdo)
    - [Introdução](#introdu%C3%A7%C3%A3o)
    - [Responsável técnico](#respons%C3%A1vel-t%C3%A9cnico)
    - [O que deseja fazer?](#o-que-deseja-fazer)

<!-- /TOC -->

##  Introdução

Como já supracitado, este sistema tem como função principal moderar a requisição de acessos para novos usuários, em um contexto corporativo e.g. à suite de ferramentas de software de uma empresa, através de um processo de moderação, a priori, por usuários já existentes (cadastrados) na base de dados do sistema e que possuem privilégios necessários para tal. De modo também à gerenciar a camada de autenticação e autenticação de novos usuários, existirão integrações desta plataforma às seguintes soluções:

- [Microsoft Entra ID](https://learn.microsoft.com/en-us/entra/identity/): Será responsável por lidar com a camada de autenticação, isto é sob o esquema OAuth2, i.e. 
- [SailPoint IdentityNow](https://documentation.sailpoint.com/): Considerando que a criação de identidades será feita pelo Entra ID, a **governança** por outro lado será feita via interface do IdentityNow.

Com efeito, serão exploradas as diferentes nuances de modelagem desse sistema, consolidadas em uma proposta de arquitetura orientada a eventos para esse cenário, com foco em:

- solicitação de acesso feita por um usuário externo/candidato;
- moderação por um usuário com permissão de moderador;
- provisionamento automático de função padrão após aprovação;
- integração com Microsoft Entra ID e SailPoint IdentityNow;
- autenticação/autorização com OAuth2 + JWT;
- auditabilidade ponta a ponta com trilha de logs e usuários envolvidos.

A estrutura dessa proposta será segmentada em diferentes seções:

- [Visão da arquitetura](./sections/architecture-specs.md);
- [Bounded contexts e serviços](./sections/bounded-context-services-specs.md);
- [Fluxo de negócio](./sections/event-oriented-flow-specs.md);
- [Entidades de domínio](./sections/domain-entities-specs.md);
- [Casos de uso](./sections/use-cases-specs.md);
- [Análise de riscos](./sections/risk-assessment-specs.md);
- [Aspectos de escalabilidade](./sections/scalability-specs.md).
- [Observações de implementação](./sections/implementation-specs.md).

De posse de todo esse esquadrinhamento, as fases seguintes naturais, as quais não serão comtempladas nesse material, seriam:

- Definição de uma estrutura lógico-organizacional para implementar a base de código, i.e. padrão de projeto (_design pattern_);
- Escolha da(s) linguagem(ns) de programação e dos SDKs necessários para a implementação das camadas de abstração inerentes ao padrão de projeto escolhido e também para os diferentes tipos de integração com serviços e interfaces externos.

## Responsável técnico

Qualquer dúvida ou sugestão pode ser comunicada à Guilherme Lima Gonçalves. Os meios pelos quais isso pode ser feito são:

- Email: [lwglguilherme@gmail.com](mailto:lwglguilherme@gmail.com?subject=Contato | Avaliação Técnica | Suzano/Thera Consulting)
- Telefone: +55 51 9 8199 9952 ([WhatsApp](https://wa.me/5551981999952) | [Telegram](https://t.me/lwglg))
- LinkedIn: [https://linkedin.com/in/guligon90]

---

##  O que deseja fazer?

- [Voltar ao topo](#índice-de-conteúdo)
- [Visão da arquitetura](./sections/architecture-specs.md)
