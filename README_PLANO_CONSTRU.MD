# Plano de Execução do Projeto: Interface Gráfica com Agentes de IA e Supabase

Este plano visa orientar o desenvolvimento do projeto, focando em uma progressão lógica e destacando etapas cruciais para o sucesso da implementação utilizando claude code.

---

## Fluxo de Execução Geral do Projeto:

1.  **Fundação (Backend e Autenticação):** Estabelecer a comunicação com o supabase e criar a estrutura básica de autenticação de usuários.
2.  **Núcleo da Interface Gráfica (Janelas Essenciais):** Desenvolver as janelas primárias para navegação e funcionalidades básicas.
3.  **Funcionalidade de Gravação e Histórico:** Implementar a gravação de reuniões, transcrição e visualização do histórico.
4.  **Integração dos Agentes de IA (auralis):** Construir a lógica dos agentes e a interface de interação com auralis.
5.  **Conexão Frontend-Backend (Agentes):** Estabelecer a comunicação entre a interface gráfica e os módulos dos agentes de ia, considerando a arquitetura distribuída.
6.  **Implementação de Scripts de Carga de Dados:** Desenvolver os scripts para popular as bases de conhecimento e histórico.
7.  **Refinamentos e Testes Abrangentes:** Otimizar, testar todas as funcionalidades e garantir a robustez do sistema.

---

## Plano de Implementação Detalhado:

**Fase 1: Configuração do Ambiente e Base de Dados (supabase)**

* **AÇÃO 1.1:** Configuração da Conexão Python-Supabase.
    * **PRIORIZAR:** Estabelecer a comunicação inicial com o supabase, considerando como instruções de conhecimento para essa implementações as orientações contidas no arquivo @README_MCP.MD
    * Criar um módulo `supabase_handler.py` (ou similar) para centralizar as funções de crud e consultas.
    * Implementar funções específicas para criptografia/hash de senhas (usando bibliotecas como bcrypt) antes de armazenar no banco.

* **AÇÃO 1.2:** Definição dos Esquemas das Tabelas no supabase.
    * **EXECUTAR PRIMEIRO:** Estruturar as tabelas `login_user`, `base_conhecimento`, e `historico_reunioes` no supabase. Considerar todas as colunas mencionadas e pensar em indexações para otimizar consultas futuras.
    * **IMPORTANTE - SEGURANÇA:** A coluna de senha na tabela `login_user` deve armazenar senhas criptografadas usando hash seguro (ex: bcrypt, argon2). Nunca armazenar senhas em texto plano no Supabase.
    * Gerar e aplicar os scripts sql no sql editor do supabase para criar as tabelas.
    * **AÇÃO INICIAL:** Criar um usuário administrativo inicial com nome de usuário "admin" e senha "admin123" (esta senha deve ser armazenada já criptografada no banco). Este usuário servirá para testes iniciais do sistema.

**Fase 2: Interface Gráfica - Autenticação e Navegação Inicial**

* **AÇÃO 2.1:** Desenvolvimento da janela 0 (Login).
    * **EXECUTAR PRIMEIRO:** Criar a interface com campos para usuário, senha e botão "confirmar".
    * **DIMENSÕES DA INTERFACE:** Definir o tamanho base da aplicação como 960x720 pixels para todas as janelas, garantindo consistência visual.
    * Implementar a lógica de autenticação:
        * Receber usuário e senha do formulário
        * Fazer hash da senha inserida usando o mesmo algoritmo usado no armazenamento
        * Comparar com o hash armazenado na tabela `login_user` no supabase
        * Direcionar para a janela 1 em caso de sucesso
    * **NOTA FUTURA:** Preparar estrutura para futuramente adicionar funcionalidade de criação de novos usuários, onde as senhas serão igualmente criptografadas antes do armazenamento.
* **AÇÃO 2.2:** Desenvolvimento da janela 1 (Página Inicial).
    * Criar a interface com os botões: "histórico", "iniciar" e "auralis".
    * Manter as dimensões de 960x720 pixels.
    * Implementar a navegação para as respectivas janelas (ainda que estas não estejam totalmente funcionais).

**Fase 3: Funcionalidade de Gravação de Reuniões**

* **AÇÃO 3.1:** Desenvolvimento da janela 3 (Dados Pré-Gravação).
    * Criar a interface com campos para título (preenchível) e exibição automática de usuário, área e data/hora.
    * Puxar dados do usuário logado (da `login_user` via supabase ou de uma sessão local após login).
    * Implementar botões "confirmar" (leva à janela 4) e "cancelar" (volta à janela 1).
* **AÇÃO 3.2:** Desenvolvimento da janela 4 (Gravação).
    * **IMPORTANTE:** Implementar a lógica de gravação de áudio.
    * Adicionar timer, botões "pausar" (com tela de status e botão "retomar"), "finalizar" (com confirmação) e "cancelar" (com confirmação e exclusão).
* **AÇÃO 3.3:** Transcrição e Armazenamento.
    * **PRIORIZAR:** Ao finalizar a gravação, implementar a chamada à api da openai para transcrição do áudio.
    * **IMPORTANTE:** Desenvolver estrategia para lidar com áudios longos (superiores a 21mb), como segmentação do áudio antes do envio para a openai ou uso de modelos/apis que suportem arquivos maiores/streaming, se disponíveis e viáveis.
    * Salvar a transcrição completa e os metadados (título, data, usuário, área etc.) na tabela `historico_reunioes` do supabase.
    * Implementar a exclusão do arquivo de áudio local após a transcrição e salvamento bem-sucedidos.

**Fase 4: Funcionalidade de Histórico de Reuniões**

* **AÇÃO 4.1:** Desenvolvimento da janela 2 (Histórico).
    * Criar a interface para listagem das reuniões.
    * **IMPORTANTE:** Consultar a tabela `historico_reunioes` no supabase e exibir os dados no formato "título - data - responsável".
    * Implementar a funcionalidade de clique em uma reunião para exibir a transcrição completa e detalhes formatados.
        * **DESAFIO CHAVE:** Garantir que, mesmo com dados armazenados em rag/embeddings no futuro, a visualização aqui apresente a transcrição completa e coerente, remontando as informações necessárias.
    * Adicionar botão "voltar" para a janela 1.

**Fase 5: Desenvolvimento dos Agentes de IA**

* **AÇÃO 5.1:** Estruturação dos Módulos dos Agentes.
    * **PRIORIZAR:** Criar os arquivos `.py` separados para cada agente: `agente_orquestrador.py`, `agente_brainstorm.py`, `agente_consulta_inteligente.py`.
    * Definir a estrutura básica de cada agente, pensando na facilidade de manutenção dos prompts e na lógica de entrada/saída.
* **AÇÃO 5.2:** Desenvolvimento do `agente_orquestrador.py`.
    * Implementar a lógica inicial de interpretação da pergunta e direcionamento (ainda que para stubs dos agentes especializados).
* **AÇÃO 5.3:** Desenvolvimento do `agente_consulta_inteligente.py`.
    * Implementar a capacidade de buscar informações nas bases `base_conhecimento` e `historico_reunioes` no supabase.
    * **IMPORTANTE:** Começar a pensar na implementação da busca semântica avançada.
* **AÇÃO 5.4:** Desenvolvimento do `agente_brainstorm.py`.
    * Implementar a lógica para geração de ideias e soluções, com capacidade de referenciar reuniões.
* **AÇÃO 5.5:** Comunicação Inter-Agentes.
    * **IMPORTANTE:** Definir e implementar o método de comunicação entre o orquestrador e os agentes especializados. Considerar a arquitetura futura com o "core" da ia em um servidor. Pode ser via chamadas de função, uma api interna simples, ou um sistema de mensageria leve, dependendo da complexidade prevista por claude.

**Fase 6: Interface e Funcionalidade auralis (IA)**

* **AÇÃO 6.1:** Desenvolvimento da janela 5 (Interação com auralis).
    * Criar a interface com botão "perguntar", campo de visualização da conversa (estilo chat) e botão "voltar".
* **AÇÃO 6.2:** Gravação da Pergunta e Interação.
    * Ao clicar em "perguntar", direcionar para a janela 6 (ou um estado/modal na janela 5) para gravação de áudio da pergunta.
    * **IMPORTANTE:** Implementar a transcrição da pergunta via openai e envio para o `agente_orquestrador`.
    * Exibir a pergunta transcrita e a resposta do agente na janela de conversa.
    * Implementar a interface visual interativa para feedback de "auralis ouvindo/processando".
* **AÇÃO 6.3:** Gerenciamento de Memória Local de auralis.
    * **PRIORIZAR:** Implementar o armazenamento local do histórico da conversa da janela 5 na pasta `auralis_memoria` (escolher formato de arquivo adequado, ex: json, txt).
    * Garantir que este histórico seja usado como contexto para interações subsequentes na mesma sessão.
    * **IMPORTANTE:** Implementar a exclusão do arquivo em `auralis_memoria` e limpeza do campo de visualização ao retornar para a janela 1.

**Fase 7: Scripts de Carga de Dados no Supabase**

* **AÇÃO 7.1:** Desenvolvimento do `imput_base_conhecimento.py`.
    * Criar script para ler arquivos `.txt` da pasta local `update_conhecimento` e inseri-los na tabela `base_conhecimento` do supabase, considerando a lógica de rag/chunks e identificação do título do arquivo original.
    * **PREPARAÇÃO DE TESTES:** Para fins de teste inicial, preparar pelo menos 2 arquivos .txt de exemplo na pasta `update_conhecimento` com conteúdo relevante para testar a funcionalidade de carga.
* **AÇÃO 7.2:** Desenvolvimento do `imput_historico_reunioes.py`.
    * Similar ao anterior, mas para a pasta `update_historico` e a tabela `historico_reunioes`. (Nota: Este script pode ser menos usado se o histórico for primariamente populado via gravações da interface).
    * **PREPARAÇÃO DE TESTES:** Preparar também 2 arquivos .txt de exemplo na pasta `update_historico` para testar a carga inicial de dados históricos.

**Fase 8: Integração, Testes e Refinamentos Finais**

* **AÇÃO 8.1:** Integração Frontend (GUI) - Backend (Agentes de IA).
    * **EXECUTAR PRIMEIRO nesta fase:** Implementar o método de conexão (api, sockets, etc.) entre a interface gráfica (que pode estar em outra máquina) e os módulos dos agentes de ia. A transcrição de áudio ocorre no frontend.
* **AÇÃO 8.2:** Testes Funcionais.
    * Testar todas as janelas, botões e fluxos de usuário.
    * **TESTE DE AUTENTICAÇÃO:** Verificar o login com usuário "admin" e senha "admin123", confirmando que a autenticação com senha criptografada funciona corretamente.
    * Verificar a correta gravação, transcrição e armazenamento de reuniões.
    * Testar a interação com auralis, incluindo a memória contextual e a precisão das respostas dos agentes.
    * **IMPORTANTE:** Testar a busca semântica e a capacidade de lidar com variações (ex: "mateus estivau" vs "matheus estival").
    * Testar a carga de dados usando os arquivos .txt de exemplo preparados nas pastas `update_conhecimento` e `update_historico`.
* **AÇÃO 8.3:** Implementação de Logs e Fallback.
    * Adicionar logs detalhados para facilitar o debugging.
    * Implementar mecanismos de fallback gracioso para casos de falha na api da openai, supabase ou outros componentes.
* **AÇÃO 8.4:** Revisão e Documentação.
    * Revisar todo o código, adicionar comentários em português explicando funções e utilizações.
    * Garantir que os arquivos `.py` estejam bem separados por funcionalidade.
    * Documentar claramente o processo de criptografia de senhas e as considerações de segurança implementadas.
* **AÇÃO 8.5:** Considerações de Desempenho.
    * Avaliar e otimizar o desempenho, especialmente no processamento de áudios e consultas ao supabase.
    * Implementar caching inteligente, se aplicável e viável.

crie uma pasta com o nome EXEC_FASES_CLAUDE