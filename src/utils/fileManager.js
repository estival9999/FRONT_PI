import { analyzeWithFallback } from './gptAnalyzer.js';

class FileManager {
  constructor() {
    this.meetingsFolder = 'reunioes';
  }

  /**
   * Garante que a pasta de reuniões existe
   */
  async ensureMeetingsFolder() {
    try {
      const result = await window.electronAPI.createDirectory(this.meetingsFolder);
      if (!result.success) {
        throw new Error(result.error);
      }
    } catch (error) {
      console.error('Erro ao criar pasta de reuniões:', error);
      throw error;
    }
  }

  /**
   * Gera o próximo ID sequencial baseado nos arquivos existentes
   */
  async getNextSequentialId() {
    try {
      const result = await window.electronAPI.listFiles(this.meetingsFolder);
      const files = result.files || [];
      
      // Extrai números dos nomes de arquivo que começam com dígitos
      const ids = files
        .map(file => {
          const match = file.match(/^(\d+)_/);
          return match ? parseInt(match[1]) : 0;
        })
        .filter(id => !isNaN(id));

      // Retorna o próximo ID disponível
      const maxId = ids.length > 0 ? Math.max(...ids) : 0;
      return String(maxId + 1).padStart(2, '0');
    } catch (error) {
      console.error('Erro ao obter próximo ID:', error);
      return '01';
    }
  }

  /**
   * Formata data e hora para o nome do arquivo
   */
  formatDateTime(date = new Date()) {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return {
      date: `${day}_${month}_${year}`,
      time: `${hours}:${minutes}`,
      fullDateTime: `${day}/${month}/${year} às ${hours}:${minutes}`
    };
  }

  /**
   * Gera o nome do arquivo baseado no ID e informações da reunião
   */
  generateFileName(id, meetingName, date = new Date()) {
    const { date: dateStr, time } = this.formatDateTime(date);
    const sanitizedName = meetingName
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '') // Remove acentos
      .replace(/[^a-z0-9]/g, '_') // Substitui caracteres especiais por _
      .replace(/_+/g, '_') // Remove underscores duplicados
      .replace(/^_|_$/g, ''); // Remove underscores do início e fim

    return `${id}_${sanitizedName}_${dateStr}_${time.replace(':', '')}.txt`;
  }

  /**
   * Cria o cabeçalho completo para o arquivo
   */
  createFileHeader(meetingInfo, fileName) {
    const { fullDateTime } = this.formatDateTime(meetingInfo.date);
    const separator = '='.repeat(50);

    return `${separator}
TRANSCRIÇÃO DE REUNIÃO
${separator}

Nome da Reunião: ${meetingInfo.name}
Data e Hora: ${fullDateTime}
Duração: ${meetingInfo.duration || 'Não especificada'}
Participantes: ${meetingInfo.participants || 'Não especificados'}
Local/Plataforma: ${meetingInfo.location || 'Não especificado'}

Arquivo: ${fileName}
Gerado por: Sistema de Transcrição de Reuniões

${separator}
TRANSCRIÇÃO
${separator}

`;
  }

  /**
   * Salva a transcrição bruta da reunião
   */
  async saveTranscription(transcription, meetingInfo) {
    try {
      // Garante que a pasta existe
      await this.ensureMeetingsFolder();

      // Gera ID e nome do arquivo
      const id = await this.getNextSequentialId();
      const fileName = this.generateFileName(id, meetingInfo.name, meetingInfo.date);
      const filePath = `${this.meetingsFolder}/${fileName}`;

      // Cria o conteúdo completo do arquivo
      const header = this.createFileHeader(meetingInfo, fileName);
      const fullContent = header + transcription;

      // Salva o arquivo
      const saveResult = await window.electronAPI.saveFile(filePath, fullContent);
      
      if (!saveResult.success) {
        throw new Error(saveResult.error);
      }

      return {
        id,
        fileName,
        filePath,
        success: true
      };
    } catch (error) {
      console.error('Erro ao salvar transcrição:', error);
      throw error;
    }
  }

  /**
   * Gera e salva o arquivo de análise usando GPT-4
   */
  async generateAnalysis(transcription, originalFileInfo, meetingInfo) {
    try {
      // Analisa a transcrição usando GPT-4 com fallback para análise local
      const analysis = await analyzeWithFallback(transcription, meetingInfo);

      // Gera o nome do arquivo de análise
      const analysisFileName = `X_${originalFileInfo.fileName}`;
      const analysisFilePath = `${this.meetingsFolder}/${analysisFileName}`;

      // Cria o conteúdo do arquivo de análise
      const { fullDateTime } = this.formatDateTime(meetingInfo.date);
      const separator = '='.repeat(50);
      const subSeparator = '-'.repeat(40);

      const analysisContent = `${separator}
ANÁLISE DE REUNIÃO - GERADA POR IA
${separator}

Nome da Reunião: ${meetingInfo.name}
Data e Hora: ${fullDateTime}
Arquivo Original: ${originalFileInfo.fileName}
Data da Análise: ${this.formatDateTime().fullDateTime}

${separator}
PAUTA DA REUNIÃO
${separator}
${analysis.pauta || 'Não identificada'}

${separator}
PARTICIPANTES
${separator}
${analysis.participantes || 'Não identificados'}

${separator}
PENDÊNCIAS
${separator}
${analysis.pendencias || 'Nenhuma pendência identificada'}

${separator}
ITENS RESOLVIDOS
${separator}
${analysis.resolvidos || 'Nenhum item resolvido identificado'}

${separator}
PROBLEMAS IDENTIFICADOS
${separator}
${analysis.problemas || 'Nenhum problema identificado'}

${separator}
TAREFAS E RESPONSÁVEIS
${separator}
${analysis.tarefas || 'Nenhuma tarefa atribuída'}

${separator}
RESUMO EXECUTIVO
${separator}
${analysis.resumo || 'Resumo não disponível'}

${separator}
OBSERVAÇÕES
${separator}
Esta análise foi gerada automaticamente por GPT-4.
Para melhor precisão, revise o conteúdo com a transcrição original.

${separator}`;

      // Salva o arquivo de análise
      const saveResult = await window.electronAPI.saveFile(analysisFilePath, analysisContent);
      
      if (!saveResult.success) {
        throw new Error(saveResult.error);
      }

      return {
        fileName: analysisFileName,
        filePath: analysisFilePath,
        success: true,
        analysis
      };
    } catch (error) {
      console.error('Erro ao gerar análise:', error);
      throw error;
    }
  }

  /**
   * Processa e salva uma reunião completa (transcrição + análise)
   */
  async processMeeting(transcription, meetingInfo) {
    try {
      // Salva a transcrição bruta
      const transcriptionResult = await this.saveTranscription(transcription, meetingInfo);

      // Gera e salva a análise
      const analysisResult = await this.generateAnalysis(
        transcription,
        transcriptionResult,
        meetingInfo
      );

      return {
        transcription: transcriptionResult,
        analysis: analysisResult,
        success: true
      };
    } catch (error) {
      console.error('Erro ao processar reunião:', error);
      throw error;
    }
  }

  /**
   * Lista todas as reuniões salvas
   */
  async listMeetings() {
    try {
      const result = await window.electronAPI.listFiles(this.meetingsFolder);
      const files = result.files || [];
      
      // Separa transcrições e análises
      const transcriptions = files.filter(f => !f.startsWith('X_'));
      const analyses = files.filter(f => f.startsWith('X_'));

      // Mapeia as transcrições com suas análises
      const meetings = transcriptions.map(transcriptionFile => {
        const analysisFile = analyses.find(a => a === `X_${transcriptionFile}`);
        
        // Extrai informações do nome do arquivo
        const match = transcriptionFile.match(/^(\d+)_(.+)_(\d+)_(\d+)_(\d+)_(\d+)(\d+)\.txt$/);
        
        return {
          id: match ? match[1] : null,
          transcriptionFile,
          analysisFile,
          hasAnalysis: !!analysisFile,
          name: match ? match[2].replace(/_/g, ' ') : transcriptionFile,
          date: match ? `${match[3]}/${match[4]}/${match[5]}` : null,
          time: match ? `${match[6]}:${match[7]}` : null
        };
      });

      return meetings.sort((a, b) => b.id.localeCompare(a.id));
    } catch (error) {
      console.error('Erro ao listar reuniões:', error);
      return [];
    }
  }

  /**
   * Lê o conteúdo de um arquivo
   */
  async readFile(fileName) {
    try {
      const filePath = `${this.meetingsFolder}/${fileName}`;
      const result = await window.electronAPI.readFile(filePath);
      
      if (!result.success) {
        throw new Error(result.error);
      }
      
      return result.content;
    } catch (error) {
      console.error('Erro ao ler arquivo:', error);
      throw error;
    }
  }

  /**
   * Deleta um arquivo
   */
  async deleteFile(fileName) {
    try {
      const filePath = `${this.meetingsFolder}/${fileName}`;
      const result = await window.electronAPI.deleteFile(filePath);
      
      if (!result.success) {
        throw new Error(result.error);
      }
      
      return true;
    } catch (error) {
      console.error('Erro ao deletar arquivo:', error);
      throw error;
    }
  }

  /**
   * Deleta uma reunião completa (transcrição + análise)
   */
  async deleteMeeting(transcriptionFileName) {
    try {
      // Deleta a transcrição
      await this.deleteFile(transcriptionFileName);

      // Tenta deletar a análise correspondente
      const analysisFileName = `X_${transcriptionFileName}`;
      try {
        await this.deleteFile(analysisFileName);
      } catch (error) {
        // Ignora se a análise não existir
        console.log('Arquivo de análise não encontrado:', analysisFileName);
      }

      return true;
    } catch (error) {
      console.error('Erro ao deletar reunião:', error);
      throw error;
    }
  }
}

// Exporta uma instância única
export const fileManager = new FileManager();

// Exporta a classe para testes ou extensões
export default FileManager;