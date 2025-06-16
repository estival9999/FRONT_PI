/**
 * Analisa transcrições de reuniões usando GPT-4
 */

const ANALYSIS_PROMPT = `Analise a seguinte transcrição de reunião e extraia as informações solicitadas de forma estruturada e objetiva.

TRANSCRIÇÃO:
{transcription}

Por favor, forneça uma análise detalhada com os seguintes tópicos:

1. PAUTA: Liste os principais tópicos discutidos na reunião
2. PARTICIPANTES: Identifique todos os participantes mencionados
3. PENDÊNCIAS: Liste itens que ficaram pendentes ou precisam de acompanhamento
4. RESOLVIDOS: Liste problemas ou questões que foram resolvidos durante a reunião
5. PROBLEMAS: Identifique problemas ou desafios mencionados
6. TAREFAS: Liste tarefas atribuídas com seus respectivos responsáveis e prazos (se mencionados)
7. RESUMO: Faça um resumo executivo conciso da reunião

Formato esperado:
- Use bullets para listas
- Seja específico e objetivo
- Inclua nomes e datas quando mencionados
- Se não houver informação para algum tópico, indique "Nenhum item identificado"`;

/**
 * Analisa uma transcrição usando a API do GPT-4
 */
export async function analyzeTranscription(transcription, meetingInfo = {}) {
  try {
    // Get GPT API key
    let apiKey = '';
    if (window.electronAPI && window.electronAPI.settings) {
      apiKey = await window.electronAPI.settings.get('gpt_api_key');
    }
    
    if (!apiKey) {
      throw new Error('GPT API Key não configurada');
    }

    // Prepara o prompt com a transcrição
    const prompt = ANALYSIS_PROMPT.replace('{transcription}', transcription);

    // Chama a API do GPT-4 diretamente
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: 'Você é um assistente especializado em analisar transcrições de reuniões.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.3,
        max_tokens: 2000
      })
    });

    if (!response.ok) {
      throw new Error(`GPT API error: ${response.status}`);
    }

    const data = await response.json();
    const gptResponse = data.choices[0].message.content;

    // Processa a resposta do GPT-4
    const analysis = parseGPTResponse(gptResponse);

    // Adiciona informações da reunião se disponíveis
    if (meetingInfo.participants) {
      analysis.participantes = combineParticipants(
        analysis.participantes,
        meetingInfo.participants
      );
    }

    return analysis;
  } catch (error) {
    console.error('Erro ao analisar transcrição:', error);
    
    // Retorna análise padrão em caso de erro
    return {
      pauta: 'Erro ao analisar pauta',
      participantes: meetingInfo.participants || 'Não identificados',
      pendencias: 'Erro ao identificar pendências',
      resolvidos: 'Erro ao identificar itens resolvidos',
      problemas: 'Erro ao identificar problemas',
      tarefas: 'Erro ao identificar tarefas',
      resumo: 'Erro ao gerar resumo. Por favor, verifique a transcrição original.',
      erro: error.message
    };
  }
}

/**
 * Processa a resposta do GPT-4 e extrai as seções
 */
function parseGPTResponse(response) {
  const sections = {
    pauta: '',
    participantes: '',
    pendencias: '',
    resolvidos: '',
    problemas: '',
    tarefas: '',
    resumo: ''
  };

  try {
    // Divide a resposta em linhas
    const lines = response.split('\n');
    let currentSection = null;

    for (const line of lines) {
      const trimmedLine = line.trim();
      
      // Identifica seções principais
      if (trimmedLine.includes('PAUTA:') || trimmedLine.includes('1. PAUTA')) {
        currentSection = 'pauta';
        continue;
      } else if (trimmedLine.includes('PARTICIPANTES:') || trimmedLine.includes('2. PARTICIPANTES')) {
        currentSection = 'participantes';
        continue;
      } else if (trimmedLine.includes('PENDÊNCIAS:') || trimmedLine.includes('3. PENDÊNCIAS')) {
        currentSection = 'pendencias';
        continue;
      } else if (trimmedLine.includes('RESOLVIDOS:') || trimmedLine.includes('4. RESOLVIDOS')) {
        currentSection = 'resolvidos';
        continue;
      } else if (trimmedLine.includes('PROBLEMAS:') || trimmedLine.includes('5. PROBLEMAS')) {
        currentSection = 'problemas';
        continue;
      } else if (trimmedLine.includes('TAREFAS:') || trimmedLine.includes('6. TAREFAS')) {
        currentSection = 'tarefas';
        continue;
      } else if (trimmedLine.includes('RESUMO:') || trimmedLine.includes('7. RESUMO')) {
        currentSection = 'resumo';
        continue;
      }

      // Adiciona conteúdo à seção atual
      if (currentSection && trimmedLine) {
        sections[currentSection] += trimmedLine + '\n';
      }
    }

    // Limpa espaços extras
    Object.keys(sections).forEach(key => {
      sections[key] = sections[key].trim() || 'Nenhum item identificado';
    });

    return sections;
  } catch (error) {
    console.error('Erro ao processar resposta do GPT:', error);
    return sections;
  }
}

/**
 * Combina participantes identificados pelo GPT com os fornecidos pelo usuário
 */
function combineParticipants(gptParticipants, userParticipants) {
  if (!gptParticipants || gptParticipants === 'Nenhum item identificado') {
    return userParticipants;
  }

  // Cria um conjunto único de participantes
  const allParticipants = new Set();
  
  // Adiciona participantes do usuário
  if (userParticipants) {
    userParticipants.split(',').forEach(p => allParticipants.add(p.trim()));
  }

  // Adiciona participantes identificados pelo GPT
  const gptList = gptParticipants.split('\n');
  gptList.forEach(line => {
    const cleaned = line.replace(/^[-•*]\s*/, '').trim();
    if (cleaned) allParticipants.add(cleaned);
  });

  return Array.from(allParticipants).join('\n- ');
}

/**
 * Análise simplificada sem GPT-4 (fallback)
 */
export async function analyzeTranscriptionLocal(transcription, meetingInfo = {}) {
  try {
    // Análise básica local
    const lines = transcription.split('\n');
    const speakers = new Set();
    const questions = [];
    const actions = [];

    lines.forEach(line => {
      // Identifica falantes
      const speakerMatch = line.match(/^([^:]+):/);
      if (speakerMatch) {
        speakers.add(speakerMatch[1].trim());
      }

      // Identifica perguntas
      if (line.includes('?')) {
        questions.push(line.trim());
      }

      // Identifica possíveis ações (palavras-chave)
      const actionKeywords = ['fazer', 'realizar', 'criar', 'desenvolver', 'enviar', 'preparar'];
      if (actionKeywords.some(keyword => line.toLowerCase().includes(keyword))) {
        actions.push(line.trim());
      }
    });

    return {
      pauta: 'Análise local - tópicos não identificados automaticamente',
      participantes: Array.from(speakers).join('\n- ') || meetingInfo.participants || 'Não identificados',
      pendencias: questions.length > 0 ? questions.slice(0, 5).join('\n- ') : 'Nenhum item identificado',
      resolvidos: 'Análise local - itens resolvidos não identificados',
      problemas: 'Análise local - problemas não identificados',
      tarefas: actions.length > 0 ? actions.slice(0, 5).join('\n- ') : 'Nenhuma tarefa identificada',
      resumo: `Reunião com ${speakers.size} participantes. ${questions.length} perguntas levantadas e ${actions.length} possíveis ações identificadas.`
    };
  } catch (error) {
    console.error('Erro na análise local:', error);
    return {
      pauta: 'Erro na análise',
      participantes: meetingInfo.participants || 'Não identificados',
      pendencias: 'Erro na análise',
      resolvidos: 'Erro na análise',
      problemas: 'Erro na análise',
      tarefas: 'Erro na análise',
      resumo: 'Erro ao processar transcrição'
    };
  }
}

/**
 * Função principal que tenta usar GPT-4 e cai para análise local se necessário
 */
export async function analyzeWithFallback(transcription, meetingInfo = {}) {
  try {
    // Tenta usar GPT-4 primeiro
    return await analyzeTranscription(transcription, meetingInfo);
  } catch (error) {
    console.warn('GPT-4 não disponível, usando análise local:', error);
    // Usa análise local como fallback
    return await analyzeTranscriptionLocal(transcription, meetingInfo);
  }
}

export default {
  analyzeTranscription,
  analyzeTranscriptionLocal,
  analyzeWithFallback
};