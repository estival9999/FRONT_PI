/**
 * Script de teste para verificar a integração completa
 */

// Este script pode ser executado no console do navegador após abrir a aplicação

async function testIntegration() {
  console.log('=== Teste de Integração ===');
  
  // 1. Verificar se as APIs do Electron estão disponíveis
  console.log('1. Verificando APIs do Electron...');
  if (window.electronAPI) {
    console.log('✓ APIs do Electron disponíveis');
    console.log('  - settings:', !!window.electronAPI.settings);
    console.log('  - fileSystem:', !!window.electronAPI.fileSystem);
    console.log('  - createDirectory:', !!window.electronAPI.createDirectory);
    console.log('  - saveFile:', !!window.electronAPI.saveFile);
  } else {
    console.error('✗ APIs do Electron não encontradas');
    return;
  }
  
  // 2. Verificar configuração de API Keys
  console.log('\n2. Verificando API Keys...');
  try {
    const whisperKey = await window.electronAPI.settings.get('openai_api_key');
    const gptKey = await window.electronAPI.settings.get('gpt_api_key');
    
    console.log('  - Whisper API Key:', whisperKey ? '✓ Configurada' : '✗ Não configurada');
    console.log('  - GPT API Key:', gptKey ? '✓ Configurada' : '✗ Não configurada');
  } catch (error) {
    console.error('✗ Erro ao verificar API Keys:', error);
  }
  
  // 3. Testar criação de diretório
  console.log('\n3. Testando criação de diretório...');
  try {
    const result = await window.electronAPI.createDirectory('test_reunioes');
    console.log(result.success ? '✓ Diretório criado' : '✗ Falha ao criar diretório');
  } catch (error) {
    console.error('✗ Erro ao criar diretório:', error);
  }
  
  // 4. Testar salvamento de arquivo
  console.log('\n4. Testando salvamento de arquivo...');
  try {
    const testContent = 'Teste de integração - ' + new Date().toISOString();
    const result = await window.electronAPI.saveFile('test_reunioes/teste.txt', testContent);
    console.log(result.success ? '✓ Arquivo salvo' : '✗ Falha ao salvar arquivo');
  } catch (error) {
    console.error('✗ Erro ao salvar arquivo:', error);
  }
  
  // 5. Testar leitura de arquivo
  console.log('\n5. Testando leitura de arquivo...');
  try {
    const result = await window.electronAPI.readFile('test_reunioes/teste.txt');
    console.log(result.success ? '✓ Arquivo lido com sucesso' : '✗ Falha ao ler arquivo');
    if (result.success) {
      console.log('  Conteúdo:', result.content.substring(0, 50) + '...');
    }
  } catch (error) {
    console.error('✗ Erro ao ler arquivo:', error);
  }
  
  // 6. Testar listagem de arquivos
  console.log('\n6. Testando listagem de arquivos...');
  try {
    const result = await window.electronAPI.listFiles('test_reunioes');
    console.log(result.success ? '✓ Arquivos listados' : '✗ Falha ao listar arquivos');
    if (result.success) {
      console.log('  Arquivos encontrados:', result.files);
    }
  } catch (error) {
    console.error('✗ Erro ao listar arquivos:', error);
  }
  
  // 7. Limpar teste
  console.log('\n7. Limpando arquivos de teste...');
  try {
    await window.electronAPI.deleteFile('test_reunioes/teste.txt');
    console.log('✓ Arquivo de teste removido');
  } catch (error) {
    console.error('✗ Erro ao remover arquivo de teste:', error);
  }
  
  console.log('\n=== Teste Concluído ===');
}

// Exportar para uso global
window.testIntegration = testIntegration;

console.log('Script de teste carregado. Execute testIntegration() no console para testar.');