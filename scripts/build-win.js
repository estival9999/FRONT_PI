const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Iniciando build para Windows...\n');

// Limpar diretórios anteriores
console.log('📦 Limpando builds anteriores...');
const dirsToClean = ['dist', 'dist-electron'];
dirsToClean.forEach(dir => {
  if (fs.existsSync(dir)) {
    fs.rmSync(dir, { recursive: true, force: true });
    console.log(`   ✓ ${dir} removido`);
  }
});

// Verificar se os ícones existem
console.log('\n🎨 Verificando ícones...');
const iconPath = path.join(__dirname, '..', 'build', 'icon.ico');
if (!fs.existsSync(iconPath)) {
  console.error('❌ Erro: icon.ico não encontrado em build/icon.ico');
  console.log('   Por favor, gere o ícone usando o arquivo build/generate-icon.html');
  process.exit(1);
} else {
  console.log('   ✓ Ícone encontrado');
}

// Build do CSS com Tailwind
console.log('\n🎨 Compilando CSS com Tailwind...');
try {
  execSync('npm run build:css', { stdio: 'inherit' });
  console.log('   ✓ CSS compilado com sucesso');
} catch (error) {
  console.error('❌ Erro ao compilar CSS:', error);
  process.exit(1);
}

// Build do Vite
console.log('\n📦 Compilando aplicação React com Vite...');
try {
  execSync('npm run build', { stdio: 'inherit' });
  console.log('   ✓ Build do Vite concluído');
} catch (error) {
  console.error('❌ Erro no build do Vite:', error);
  process.exit(1);
}

// Verificar se o build foi criado
if (!fs.existsSync('dist/index.html')) {
  console.error('❌ Erro: dist/index.html não foi criado');
  process.exit(1);
}

// Build do Electron
console.log('\n🔨 Criando executável com Electron Builder...');
try {
  execSync('electron-builder --win', { stdio: 'inherit' });
  console.log('   ✓ Executável criado com sucesso');
} catch (error) {
  console.error('❌ Erro no Electron Builder:', error);
  process.exit(1);
}

// Listar arquivos gerados
console.log('\n✅ Build concluído com sucesso!');
console.log('\n📁 Arquivos gerados em dist-electron:');
const distElectronPath = path.join(__dirname, '..', 'dist-electron');
if (fs.existsSync(distElectronPath)) {
  const files = fs.readdirSync(distElectronPath);
  files.forEach(file => {
    const stats = fs.statSync(path.join(distElectronPath, file));
    const size = (stats.size / 1024 / 1024).toFixed(2);
    console.log(`   - ${file} (${size} MB)`);
  });
}

console.log('\n🎉 Instalador Windows criado com sucesso!');
console.log('   Execute o arquivo .exe em dist-electron para instalar o aplicativo.');