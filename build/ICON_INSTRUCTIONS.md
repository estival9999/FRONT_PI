# Instruções para Gerar Ícones

Para gerar os ícones necessários para o aplicativo, você tem algumas opções:

## Opção 1: Usar um serviço online (Recomendado)

1. Acesse https://www.icoconverter.com/ ou https://cloudconvert.com/
2. Faça upload do arquivo `icon.svg` ou use uma imagem PNG de 256x256 pixels
3. Gere os seguintes formatos:
   - **icon.ico** - Para Windows (incluir tamanhos: 16x16, 32x32, 48x48, 256x256)
   - **icon.png** - Para Linux (256x256 pixels)
   - **icon.icns** - Para macOS (se necessário)

## Opção 2: Usar ferramentas de linha de comando

### Para Windows (icon.ico)
```bash
# Instalar ImageMagick
# Depois executar:
convert icon.svg -define icon:auto-resize=16,32,48,256 icon.ico
```

### Para Linux (icon.png)
```bash
convert icon.svg -resize 256x256 icon.png
```

## Opção 3: Usar electron-icon-builder

```bash
npm install -g electron-icon-builder
electron-icon-builder --input=icon.svg --output=./
```

## Ícone Temporário

Por enquanto, criei um ícone SVG básico representando um microfone com ondas sonoras. 
Você pode substituí-lo por seu próprio design seguindo estas especificações:

- Tamanho recomendado: 256x256 pixels ou maior
- Formato: PNG com fundo transparente ou SVG
- Cores que combinem com o tema do aplicativo

## Localização dos Arquivos

Após gerar os ícones, certifique-se de que estejam na pasta `build/`:
- `/build/icon.ico` - Windows
- `/build/icon.png` - Linux
- `/build/icon.icns` - macOS (opcional)