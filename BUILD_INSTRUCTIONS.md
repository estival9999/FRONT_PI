# Instruções de Build - Audio Transcription App

## Pré-requisitos

1. **Node.js** (versão 16 ou superior)
2. **npm** ou **yarn**
3. **Windows** para criar executável Windows

## Preparação

### 1. Instalar Dependências
```bash
npm install
```

### 2. Criar Ícone
1. Abra o arquivo `build/generate-icon.html` em um navegador
2. Clique em "Download PNG (256x256)"
3. Use um conversor online (como icoconverter.com) para converter o PNG em ICO
4. Salve o arquivo como `build/icon.ico`

### 3. Configurar Variáveis de Ambiente (Opcional)
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

## Build para Windows

### Opção 1: Script Automatizado
```bash
node scripts/build-win.js
```

### Opção 2: Comandos Manuais
```bash
# 1. Compilar CSS
npm run build:css

# 2. Build do React/Vite
npm run build

# 3. Criar executável Windows
npm run build:win
```

### Build para Arquiteturas Específicas
```bash
# Windows 32-bit
npm run build:win32

# Windows 64-bit
npm run build:win64
```

## Estrutura de Saída

Após o build, você encontrará:

```
dist-electron/
├── Audio Transcription-Setup-1.0.0.exe  # Instalador
├── win-unpacked/                        # Aplicativo não empacotado
└── builder-effective-config.yaml        # Configuração utilizada
```

## Personalização

### Alterar Nome do Aplicativo
Edite `productName` em `package.json`:
```json
"build": {
  "productName": "Seu Nome Aqui"
}
```

### Alterar Versão
Edite `version` em `package.json`:
```json
{
  "version": "1.0.1"
}
```

### Configurações do Instalador
As configurações NSIS em `package.json` controlam:
- Ícones
- Atalhos
- Diretório de instalação
- Permissões

## Assinatura de Código

Para assinar o executável (recomendado para distribuição):

1. Obtenha um certificado de assinatura de código
2. Configure as variáveis de ambiente:
   ```bash
   export CSC_LINK=path/to/certificate.pfx
   export CSC_KEY_PASSWORD=your_password
   ```
3. Execute o build normalmente

## Solução de Problemas

### Erro: "icon.ico não encontrado"
- Certifique-se de criar o ícone seguindo as instruções acima
- O arquivo deve estar em `build/icon.ico`

### Erro: "Cannot find module"
- Execute `npm install` novamente
- Verifique se todas as dependências estão instaladas

### Build falha no Windows Defender
- Adicione a pasta do projeto como exceção no Windows Defender
- Ou desative temporariamente a proteção em tempo real durante o build

### Aplicativo não abre após instalação
- Verifique se o build do Vite foi concluído (`dist/index.html` existe)
- Verifique logs em `%APPDATA%/Audio Transcription/logs`

## Distribuição

### Opções de Distribuição:

1. **Distribuição Manual**
   - Compartilhe o arquivo `.exe` diretamente
   - Ideal para distribuição interna

2. **Auto-atualização**
   - Configure um servidor de atualização
   - Adicione `electron-updater` ao projeto

3. **Windows Store**
   - Converta para APPX usando `electron-builder`
   - Siga as diretrizes da Microsoft Store

## Checklist Final

- [ ] Ícone criado e salvo em `build/icon.ico`
- [ ] Dependências instaladas com `npm install`
- [ ] CSS compilado
- [ ] Build do React/Vite concluído
- [ ] Executável gerado em `dist-electron/`
- [ ] Testado em máquina limpa do Windows
- [ ] Antivírus não bloqueia o executável