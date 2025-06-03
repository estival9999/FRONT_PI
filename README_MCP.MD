# Como integrar agentes de IA com Supabase usando o Model Context Protocol (MCP)

O Model Context Protocol (MCP) é um padrão aberto desenvolvido pela Anthropic que permite a comunicação padronizada entre modelos de linguagem (LLMs) e fontes de dados externas. Esta pesquisa detalha como criar um servidor MCP em Python para conectar com Supabase, explicando a arquitetura, implementação e melhores práticas.


1 - criar um servidor Python personalizado para ter controle total sobre a integração

## Como funciona a integração MCP-Supabase

A integração segue uma arquitetura cliente-servidor onde o agente de IA se comunica com o Supabase através de um servidor MCP intermediário. O fluxo de comunicação é:

```
Agente IA (Claude, Cursor) → Cliente MCP → Servidor MCP → API/Banco Supabase
```

O servidor MCP atua como uma ponte, expondo as funcionalidades do Supabase através de um protocolo padronizado que os agentes de IA entendem. Isso permite que os agentes executem operações no banco de dados usando linguagem natural.

## Configurando um servidor MCP em Python para Supabase

### Abordagem 1: Servidor MCP oficial do Supabase (Node.js)

O Supabase fornece um servidor MCP oficial, mas ele roda em Node.js, não Python. Para usá-lo:

```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": [
        "-y",
        "@supabase/mcp-server-supabase@latest",
        "--access-token",
        "<seu-personal-access-token>"
      ]
    }
  }
}
```

### Abordagem 2: Criar servidor Python personalizado

Para um servidor MCP em Python, você precisa criar uma aplicação separada que implemente o protocolo MCP. Aqui está a estrutura básica:

```python
# server.py
from mcp.server.fastmcp import FastMCP
import os
from supabase import create_client, Client

# Inicializar servidor MCP
mcp = FastMCP("Servidor Supabase MCP")

# Cliente Supabase
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

@mcp.tool()
async def consultar_usuarios(limite: int = 10):
    """Consulta usuários no banco Supabase"""
    try:
        response = supabase.table("users").select("*").limit(limite).execute()
        return {
            "status": "sucesso",
            "dados": response.data,
            "total": len(response.data)
        }
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@mcp.tool()
async def criar_usuario(nome: str, email: str):
    """Cria novo usuário no Supabase"""
    try:
        response = supabase.table("users").insert({
            "name": nome,
            "email": email
        }).execute()
        return {"status": "sucesso", "dados": response.data}
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

if __name__ == "__main__":
    mcp.run()
```

## Passo a passo de implementação

### 1. Preparação do ambiente

```bash
# Criar projeto Python
mkdir supabase-mcp-server
cd supabase-mcp-server

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install "mcp[cli]" supabase python-dotenv
```

### 2. Configuração das credenciais

Crie um arquivo `.env`:
```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-api
```

### 3. Estrutura do projeto

```
supabase-mcp-server/
├── server.py           # Servidor MCP principal
├── .env               # Credenciais
├── requirements.txt   # Dependências
└── config/
    └── settings.py    # Configurações
```

### 4. Implementação completa do servidor

```python
# server.py - Versão completa
from mcp.server.fastmcp import FastMCP, Context
import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Dict, Any, List

load_dotenv()

# Configurar cliente Supabase
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

# Criar servidor MCP
mcp = FastMCP("Servidor Supabase Python")

@mcp.tool()
async def executar_query(sql: str, ctx: Context = None):
    """Executa query SQL no Supabase"""
    if ctx:
        await ctx.info(f"Executando query: {sql}")
    
    try:
        # Para queries SELECT, use RPC ou views
        result = supabase.rpc("execute_sql", {"query": sql}).execute()
        return {
            "status": "sucesso",
            "dados": result.data,
            "linhas_afetadas": len(result.data)
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"Erro na query: {str(e)}")
        return {"status": "erro", "mensagem": str(e)}

@mcp.tool()
async def listar_tabelas():
    """Lista todas as tabelas do banco"""
    try:
        # Query para listar tabelas do schema public
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        """
        result = supabase.rpc("get_tables").execute()
        return {
            "status": "sucesso",
            "tabelas": result.data
        }
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

@mcp.tool()
async def operacao_crud(
    tabela: str, 
    operacao: str, 
    dados: Dict[str, Any] = None,
    filtros: Dict[str, Any] = None,
    ctx: Context = None
):
    """Executa operações CRUD em qualquer tabela"""
    try:
        if operacao == "SELECT":
            query = supabase.table(tabela).select("*")
            if filtros:
                for campo, valor in filtros.items():
                    query = query.eq(campo, valor)
            result = query.execute()
            
        elif operacao == "INSERT":
            result = supabase.table(tabela).insert(dados).execute()
            
        elif operacao == "UPDATE":
            query = supabase.table(tabela).update(dados)
            if filtros:
                for campo, valor in filtros.items():
                    query = query.eq(campo, valor)
            result = query.execute()
            
        elif operacao == "DELETE":
            query = supabase.table(tabela).delete()
            if filtros:
                for campo, valor in filtros.items():
                    query = query.eq(campo, valor)
            result = query.execute()
        else:
            return {"status": "erro", "mensagem": "Operação inválida"}
        
        if ctx:
            await ctx.info(f"{operacao} executado com sucesso em {tabela}")
            
        return {
            "status": "sucesso",
            "operacao": operacao,
            "dados": result.data,
            "total": len(result.data)
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"Erro em {operacao}: {str(e)}")
        return {"status": "erro", "mensagem": str(e)}

@mcp.resource("supabase://schema")
async def obter_schema():
    """Retorna o schema do banco de dados"""
    try:
        # Implementar lógica para obter schema
        return "Schema do banco de dados Supabase"
    except Exception as e:
        return f"Erro: {str(e)}"

@mcp.prompt()
def gerar_migration(descricao: str):
    """Gera prompt para criar migration SQL"""
    return f"""
Preciso criar uma migration SQL para: {descricao}

Considere:
1. Usar transações para garantir atomicidade
2. Incluir rollback quando possível
3. Adicionar comentários explicativos
4. Seguir convenções de nomenclatura do Supabase
5. Incluir políticas RLS apropriadas

Gere o SQL completo para esta migration.
"""

if __name__ == "__main__":
    mcp.run()
```

### 5. Integração com o agente de IA

Para Windows, adicione ao arquivo de configuração do Claude Desktop:
```json
{
  "mcpServers": {
    "supabase-python": {
      "command": "cmd",
      "args": ["/c", "python", "C:\\caminho\\para\\server.py"],
      "env": {
        "SUPABASE_URL": "${SUPABASE_URL}",
        "SUPABASE_KEY": "${SUPABASE_KEY}"
      }
    }
  }
}
```

## Arquitetura da solução

### Fluxo de comunicação completo

1. **Agente IA** recebe comando do usuário em linguagem natural
2. **Cliente MCP** traduz para chamada de protocolo MCP
3. **Servidor MCP Python** recebe a requisição via JSON-RPC 2.0
4. **SDK Supabase Python** executa a operação no banco
5. **Resposta** retorna pelo mesmo caminho

### Componentes principais

- **Transporte**: stdio (local) ou HTTP+SSE (remoto)
- **Protocolo**: JSON-RPC 2.0 sobre UTF-8
- **Autenticação**: Personal Access Token ou chaves de API
- **Segurança**: RLS (Row Level Security) do Supabase é respeitada

## Você precisa criar um servidor Python separado?

**Sim**, você precisa criar um servidor Python separado que:

1. **Implemente o protocolo MCP** usando a biblioteca `mcp`
2. **Conecte-se ao Supabase** usando o SDK Python do Supabase
3. **Exponha ferramentas (tools)** que o agente IA possa chamar
4. **Gerencie o ciclo de vida** da conexão com o Supabase

O servidor Python atua como uma **ponte** entre o agente de IA e o Supabase, traduzindo comandos em linguagem natural para operações de banco de dados.

## Melhores práticas identificadas

### Segurança
- **Armazene credenciais em variáveis de ambiente**, nunca no código
- **Use modo read-only** quando possível: `--read-only`
- **Implemente validação de SQL** para prevenir injeções
- **Configure RLS adequadamente** no Supabase

### Performance
- **Use connection pooling** para requisições concorrentes
- **Implemente cache** para consultas frequentes
- **Configure timeouts apropriados** (30s padrão)
- **Use operações em lote** quando possível

### Tratamento de erros
```python
@mcp.tool()
async def operacao_segura(tabela: str, ctx: Context):
    max_tentativas = 3
    for tentativa in range(max_tentativas):
        try:
            resultado = supabase.table(tabela).select("*").execute()
            return {"sucesso": True, "dados": resultado.data}
        except Exception as e:
            if tentativa == max_tentativas - 1:
                await ctx.error(f"Falha após {max_tentativas} tentativas: {e}")
                return {"sucesso": False, "erro": str(e)}
            await asyncio.sleep(1)  # Backoff
```

### Monitoramento
- **Configure logs detalhados** para debugging
- **Monitore uso de recursos** do servidor MCP
- **Implemente health checks** para disponibilidade
- **Rastreie métricas de performance** das queries

## Configurações necessárias no Supabase

1. **Criar Personal Access Token**:
   - Acesse Dashboard → Settings → Access Tokens
   - Crie novo token com permissões adequadas

2. **Configurar RLS**:
   - Habilite RLS em todas as tabelas públicas
   - Crie políticas apropriadas para acesso

3. **Preparar funções RPC** (opcional):
   - Para operações complexas, crie funções PostgreSQL
   - Exponha via RPC para uso pelo MCP

4. **Configurar connection pooling**:
   - Use Supavisor para gerenciar conexões
   - Configure limites apropriados

## Conclusão

A integração entre agentes de IA e Supabase via MCP representa um avanço significativo na automação de tarefas de desenvolvimento. O protocolo MCP padroniza a comunicação, enquanto servidores Python personalizados fornecem flexibilidade para implementar lógicas específicas de negócio.

