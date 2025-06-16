# Aplicativo de Gravação de Reuniões

## Como Executar no Windows

### Pré-requisitos
- Node.js instalado (versão 16 ou superior)
- NPM instalado

### Passos para Executar:

1. **Abra o terminal/CMD no diretório do projeto**
   ```
   cd C:\Users\estiv\Desktop\FRONT
   ```

2. **Instale as dependências** (apenas na primeira vez)
   ```
   npm install
   ```

3. **Execute o aplicativo**
   ```
   npm start
   ```

### Método Alternativo (Windows):
- Dê duplo clique no arquivo `run-app.bat`

## Interface do Aplicativo

O aplicativo abrirá em uma janela de 320x240 pixels com as seguintes telas:

1. **Tela Inicial**: Botão redondo "Iniciar"
2. **Nome do Responsável**: Digite o nome do responsável pela reunião
3. **Objetivo da Reunião**: Descreva o objetivo
4. **Gravação**: 
   - Timer mostrando duração
   - Botão Play/Pause
   - Botão Stop
5. **Participantes**: Grave os nomes dos participantes
6. **Validação**: Lista dos participantes com validação automática
7. **Finalização**: Salvamento dos arquivos

## Configuração de API Keys

Antes de usar, configure as chaves de API:
1. Clique no ícone de configurações
2. Insira sua API Key do OpenAI (para transcrição)
3. Insira sua API Key do GPT-4 (para análise)

## Arquivos Gerados

Os arquivos serão salvos na pasta `reunioes/`:
- Transcrição: `01_nome_dd_mm_aaaa_hhmm.txt`
- Análise: `X_01_nome_dd_mm_aaaa_hhmm.txt`

## Solução de Problemas

Se o aplicativo não abrir:
1. Verifique se o Node.js está instalado: `node --version`
2. Reinstale as dependências: `npm install`
3. Verifique erros no terminal

Se houver erro de porta em uso:
1. Feche outras aplicações usando a porta 5173
2. Ou mude a porta no arquivo `vite.config.js`

## Criar Executável (.exe)

Para criar um executável Windows:
```
npm run build:win
```

O instalador será criado na pasta `dist-electron/`