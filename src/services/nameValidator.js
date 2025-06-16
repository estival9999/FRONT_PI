import FuzzySet from 'fuzzyset.js';
import funcionariosData from '../../data/funcionarios.json';

class NameValidator {
  constructor() {
    // Inicializa o FuzzySet com os nomes dos funcionários
    this.funcionarios = funcionariosData.funcionarios;
    this.fuzzySet = FuzzySet();
    
    // Adiciona cada nome ao FuzzySet
    this.funcionarios.forEach(funcionario => {
      this.fuzzySet.add(funcionario.nome);
    });
  }

  /**
   * Valida um nome transcrito contra o banco de funcionários
   * @param {string} nomeTranscrito - Nome a ser validado
   * @param {number} threshold - Limite mínimo de similaridade (padrão: 0.7)
   * @returns {Object|null} - Retorna objeto com o funcionário encontrado ou null
   */
  validarNome(nomeTranscrito, threshold = 0.7) {
    if (!nomeTranscrito || typeof nomeTranscrito !== 'string') {
      return null;
    }

    // Remove espaços extras e normaliza o nome
    const nomeNormalizado = nomeTranscrito.trim().replace(/\s+/g, ' ');
    
    // Busca matches fuzzy
    const matches = this.fuzzySet.get(nomeNormalizado);
    
    if (!matches || matches.length === 0) {
      return null;
    }

    // Pega o melhor match
    const [score, nomeEncontrado] = matches[0];
    
    // Verifica se o score está acima do threshold
    if (score >= threshold) {
      // Encontra o funcionário correspondente
      const funcionario = this.funcionarios.find(f => f.nome === nomeEncontrado);
      
      return {
        nomeCorreto: nomeEncontrado,
        score: score,
        funcionario: funcionario,
        nomeOriginal: nomeTranscrito
      };
    }

    return null;
  }

  /**
   * Valida múltiplos nomes de uma vez
   * @param {Array<string>} nomes - Array de nomes a serem validados
   * @param {number} threshold - Limite mínimo de similaridade (padrão: 0.7)
   * @returns {Array<Object>} - Array com os resultados da validação
   */
  validarMultiplosNomes(nomes, threshold = 0.7) {
    if (!Array.isArray(nomes)) {
      return [];
    }

    return nomes.map(nome => {
      const resultado = this.validarNome(nome, threshold);
      return resultado || {
        nomeOriginal: nome,
        nomeCorreto: null,
        score: 0,
        funcionario: null,
        erro: 'Nome não encontrado ou similaridade abaixo do threshold'
      };
    });
  }

  /**
   * Busca funcionários com base em parte do nome
   * @param {string} parteNome - Parte do nome a ser buscada
   * @param {number} limite - Número máximo de resultados (padrão: 5)
   * @returns {Array<Object>} - Array com os funcionários encontrados
   */
  buscarPorParteNome(parteNome, limite = 5) {
    if (!parteNome || typeof parteNome !== 'string') {
      return [];
    }

    const parteNormalizada = parteNome.trim().toLowerCase();
    
    // Filtra funcionários que contenham a parte do nome
    const resultados = this.funcionarios
      .filter(f => f.nome.toLowerCase().includes(parteNormalizada))
      .slice(0, limite);

    return resultados;
  }

  /**
   * Retorna todos os funcionários
   * @returns {Array<Object>} - Array com todos os funcionários
   */
  listarTodosFuncionarios() {
    return this.funcionarios;
  }

  /**
   * Adiciona um novo funcionário ao validador
   * @param {Object} funcionario - Objeto do funcionário a ser adicionado
   * @returns {boolean} - True se adicionado com sucesso
   */
  adicionarFuncionario(funcionario) {
    if (!funcionario || !funcionario.nome) {
      return false;
    }

    // Adiciona ao array de funcionários
    this.funcionarios.push(funcionario);
    
    // Adiciona ao FuzzySet
    this.fuzzySet.add(funcionario.nome);
    
    return true;
  }
}

// Exporta uma instância única do validador
const nameValidator = new NameValidator();

export default nameValidator;
export { NameValidator };