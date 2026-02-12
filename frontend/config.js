// Configuração para ler dados do repositório GitHub
// Os arquivos JSON são gerados automaticamente pelos workflows:
// - data/current-analysis.json (a cada hora)
// - data/backtest.json (toda segunda-feira)

// URL base do repositório (raw GitHub content)
const REPO_OWNER = 'avilaedgard';
const REPO_NAME = 'Agente-MF';
const BRANCH = 'main';

const BASE_RAW_URL = `https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/${BRANCH}`;

window.APP_CONFIG = {
    // URLs dos arquivos JSON gerados pelo GitHub Actions
    urls: {
        currentAnalysis: `${BASE_RAW_URL}/data/current-analysis.json`,
        backtest: `${BASE_RAW_URL}/data/backtest.json`
    },
    
    // Cache para não fazer requisições a cada atualização
    cacheTimeMs: 30 * 1000,  // 30 segundos
    
    // Auto-refresh
    autoRefreshMs: 5 * 60 * 1000,  // 5 minutos
    
    debug: window.location.hostname === 'localhost'
};

// Fazer disponível globalmente
window.DATA_URLS = window.APP_CONFIG.urls;

// Debug
if (window.APP_CONFIG.debug) {
    console.log('🔧 MODO DESENVOLVIMENTO');
} else {
    console.log('🚀 MODO PRODUÇÃO - GitHub Actions');
    console.log('Análise atualiza: a cada hora');
    console.log('Backtest atualiza: toda segunda-feira');
}
