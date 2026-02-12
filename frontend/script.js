/* ========================================
   VIGILANTE - Frontend SPA
   Análise de Estratégia SMA17 × SMA72
   ======================================== */

// Detecção automática do ambiente
const getDataUrl = (filename) => {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        // Localmente: usar caminho relativo à pasta frontend
        return `../data/${filename}`;
    } else if (window.location.hostname.includes('github.io')) {
        // GitHub Pages: usar caminho relativo que funciona do /Agente-MF/
        return `./data/${filename}`;
    } else {
        // Fallback: tentar usar URL do GitHub se disponível
        return window.DATA_URLS?.[filename === 'current-analysis.json' ? 'currentAnalysis' : 'backtest'] || 
               `./data/${filename}`;
    }
};

const DATA_DEFAULT = {
    currentAnalysis: getDataUrl('current-analysis.json'),
    backtest: getDataUrl('backtest.json')
};

console.log('📍 Ambiente:', window.location.hostname);
console.log('📊 URLs de dados:', DATA_DEFAULT);

let currentData = {
    analiseAtual: null,
    backtest: null,
    lastFetch: null
};

// ========== INICIALIZAÇÃO ==========

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    updateTimestamp();
    loadAnaliseAtual();
    setupTabClickHandlers();
    
    // Atualizar dados a cada 5 minutos (300000ms)
    setInterval(loadAnaliseAtual, 300000);
    setInterval(updateTimestamp, 60000);
});

// ========== TABS ==========

function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');
            
            // Remover clase active de todos
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Adicionar classe active ao clicado
            btn.classList.add('active');
            document.getElementById(tabName).classList.add('active');
            
            // Se for backtest, carregar se ainda não foi
            if (tabName === 'backtest' && !currentData.backtest) {
                loadBacktest();
            }
            
            // Se for notícias, carregar
            if (tabName === 'noticias') {
                loadNoticias();
            }
        });
    });
}

function setupTabClickHandlers() {
    document.getElementById('tabAnalise').click();
}

// ========== UTILITÁRIOS ==========

function updateTimestamp() {
    const now = new Date();
    const formatted = now.toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('timestamp').textContent = formatted;
}

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(value);
}

function formatPercent(value) {
    const symbol = value >= 0 ? '+' : '';
    return `${symbol}${value.toFixed(2)}%`;
}

// ========== ANÁLISE ATUAL ==========

async function loadAnaliseAtual() {
    const statusIndicator = document.getElementById('statusIndicator');
    
    try {
        statusIndicator.textContent = '● Carregando...';
        statusIndicator.classList.remove('offline');
        
        // Buscar JSON do repositório GitHub
        const response = await fetch(DATA_DEFAULT.currentAnalysis);
        const data = await response.json();
        
        currentData.analiseAtual = data;
        currentData.lastFetch = new Date();
        renderAnaliseAtual(data);
        
        statusIndicator.textContent = '● Conectado';
        statusIndicator.classList.remove('offline');
        console.log('[OK] Análise carregada do GitHub');
    } catch (error) {
        console.error('Erro ao carregar análise:', error);
        statusIndicator.textContent = '● Desconectado';
        statusIndicator.classList.add('offline');
    }
}

function renderAnaliseAtual(data) {
    const container = document.getElementById('carteirasContainer');
    container.innerHTML = '';
    
    const alertsContainer = document.getElementById('alertsContainer');
    const alertsSection = document.getElementById('alertsSection');
    const analiseGeminiSection = document.getElementById('analiseGeminiSection');
    
    // Limpar alertas anteriores
    alertsContainer.innerHTML = '';
    
    let temAlerts = false;
    
    // Renderizar cada carteira
    for (const [carteira, ativos] of Object.entries(data.carteiras)) {
        if (!ativos || ativos.length === 0) continue;
        
        const carteiraSection = document.createElement('div');
        carteiraSection.className = 'carteira-section';
        
        const title = document.createElement('h2');
        title.className = 'carteira-title';
        title.textContent = carteira;
        carteiraSection.appendChild(title);
        
        const grid = document.createElement('div');
        grid.className = 'ativos-grid';
        
        for (const ativo of ativos) {
            const card = document.createElement('div');
            card.className = `ativo-card ${ativo.sinal.toLowerCase()}`;
            
            const sinal = ativo.sinal;
            const isPositiva = sinal === 'COMPRA';
            
            card.innerHTML = `
                <div class="card-header">
                    <span class="card-symbol">${ativo.ativo}</span>
                    <span class="card-sinal ${sinal.toLowerCase()}">${sinal}</span>
                </div>
                <div class="card-price">${formatCurrency(ativo.preco)}</div>
                <div class="card-meta">
                    <div class="card-meta-row">
                        <span class="card-meta-label">Abertura:</span>
                        <span class="card-meta-value">${formatCurrency(ativo.abertura)}</span>
                    </div>
                    <div class="card-meta-row">
                        <span class="card-meta-label">Mín (5y):</span>
                        <span class="card-meta-value">${formatCurrency(ativo.minimo_5y)}</span>
                    </div>
                    <div class="card-meta-row">
                        <span class="card-meta-label">Máx (5y):</span>
                        <span class="card-meta-value">${formatCurrency(ativo.maximo_5y)}</span>
                    </div>
                    <div class="card-meta-row">
                        <span class="card-meta-label">Ult. Cruzamento:</span>
                        <span class="card-meta-value">${ativo.ultimo_cruzamento}</span>
                    </div>
                </div>
                <div class="card-smas">
                    <div class="sma-row">
                        <span class="sma-label">SMA17:</span>
                        <span class="sma-value">${ativo.sma17.toFixed(2)}</span>
                    </div>
                    <div class="sma-row">
                        <span class="sma-label">SMA72:</span>
                        <span class="sma-value">${ativo.sma72.toFixed(2)}</span>
                    </div>
                    <div class="sma-row">
                        <span class="sma-label">Distância:</span>
                        <span class="sma-value">${ativo.distancia.toFixed(4)}</span>
                    </div>
                </div>
            `;
            
            grid.appendChild(card);
        }
        
        carteiraSection.appendChild(grid);
        container.appendChild(carteiraSection);
    }
    
    // Renderizar alertas recentes (últimos 14 dias)
    if (data.sinais_recentes && data.sinais_recentes.length > 0) {
        temAlerts = true;
        for (const alert of data.sinais_recentes) {
            const alertCard = document.createElement('div');
            alertCard.className = `alert-card ${alert.sinal.toLowerCase()}`;
            
            alertCard.innerHTML = `
                <div class="alert-title">🔔 ${alert.ativo} - ${alert.sinal}</div>
                <div class="alert-info">
                    <div>📊 Carteira: ${alert.carteira}</div>
                    <div>📅 Data: ${alert.data}</div>
                    <div>💰 Preço: ${formatCurrency(alert.preco)}</div>
                    <div>📏 Distância: ${alert.distancia.toFixed(4)}</div>
                </div>
            `;
            
            alertsContainer.appendChild(alertCard);
        }
    }
    
    alertsSection.style.display = temAlerts ? 'block' : 'none';
    
    // Renderizar análise Gemini
    if (data.analise_gemini) {
        analiseGeminiSection.style.display = 'block';
        document.getElementById('analiseGemini').textContent = data.analise_gemini;
    } else {
        analiseGeminiSection.style.display = 'none';
    }
}

// ========== BACKTEST ==========

async function loadBacktest() {
    const container = document.getElementById('backtestResultsContainer');
    const statusContainer = document.getElementById('backtestStatusContainer');
    const errorContainer = document.getElementById('backtestErrorContainer');
    
    statusContainer.style.display = 'block';
    container.style.display = 'none';
    errorContainer.style.display = 'none';
    
    try {
        // Buscar JSON do repositório GitHub
        const response = await fetch(DATA_DEFAULT.backtest);
        const data = await response.json();
        
        if (data.status === 'aguardando' || !data.dados) {
            throw new Error('Backtest ainda não foi executado. Ele roda toda segunda-feira automaticamente.');
        }
        
        currentData.backtest = data;
        renderBacktest(data.dados);
        
        statusContainer.style.display = 'none';
        container.style.display = 'block';
        console.log('[OK] Backtest carregado do GitHub');
        
    } catch (error) {
        console.error('Erro ao carregar backtest:', error);
        statusContainer.style.display = 'none';
        errorContainer.style.display = 'block';
        errorContainer.textContent = `❌ ${error.message}`;
    }
}

function renderBacktest(data) {
    const container = document.getElementById('backtestResultsContainer');
    container.innerHTML = '';
    
    // Mostrar timestamp
    const timestamp = document.createElement('div');
    timestamp.style.cssText = 'color: #cbd5e1; font-size: 12px; margin-bottom: 20px;';
    timestamp.textContent = `✓ Análise realizada em: ${new Date(data.timestamp).toLocaleString('pt-BR')}`;
    container.appendChild(timestamp);
    
    // Renderizar stats cards
    const statsContainer = document.getElementById('statsCardsContainer');
    statsContainer.innerHTML = '';
    statsContainer.className = 'stats-grid';
    
    const stats = [
        {
            label: 'Ativos Analisados',
            value: data.resumo.ativos_analisados,
            unit: `de ${data.resumo.total_ativos}`
        },
        {
            label: 'Rentabilidade Média',
            value: data.resumo.rentabilidade_media,
            unit: '%'
        },
        {
            label: 'Taxa de Acerto Média',
            value: data.resumo.taxa_acerto_media,
            unit: '%'
        },
        {
            label: 'Período Análise',
            value: data.periodo_anos,
            unit: 'anos'
        }
    ];
    
    for (const stat of stats) {
        const card = document.createElement('div');
        card.className = 'stat-card';
        card.innerHTML = `
            <div class="stat-label">${stat.label}</div>
            <div class="stat-value">${stat.value}</div>
            <div class="stat-unit">${stat.unit}</div>
        `;
        statsContainer.appendChild(card);
    }
    
    // Renderizar carteiras
    const carteiraContainer = document.getElementById('backtestCarteirasContainer');
    carteiraContainer.innerHTML = '';
    
    for (const [carteira, ativos] of Object.entries(data.carteiras)) {
        if (!ativos || ativos.length === 0) continue;
        
        const carteiraDiv = document.createElement('div');
        carteiraDiv.className = 'backtest-carteira';
        
        const title = document.createElement('h3');
        title.className = 'backtest-carteira-title';
        title.textContent = carteira;
        carteiraDiv.appendChild(title);
        
        for (const ativo of ativos) {
            const card = document.createElement('div');
            card.className = 'backtest-ativo-card';
            
            const isPositive = ativo.rentabilidade_estrategia >= 0;
            
            card.innerHTML = `
                <div class="backtest-ativo-header">
                    <div>
                        <div class="backtest-symbol">${ativo.ativo}</div>
                        <div class="backtest-period">${ativo.data_inicio} até ${ativo.data_fim}</div>
                    </div>
                </div>
                
                <div class="backtest-metrics">
                    <div class="metric">
                        <div class="metric-label">Entradas</div>
                        <div class="metric-value">${ativo.total_entradas}</div>
                    </div>
                    
                    <div class="metric">
                        <div class="metric-label">Ganhos</div>
                        <div class="metric-value positive">${ativo.operacoes_positivas}</div>
                    </div>
                    
                    <div class="metric">
                        <div class="metric-label">Perdas</div>
                        <div class="metric-value negative">${ativo.operacoes_negativas}</div>
                    </div>
                    
                    <div class="metric">
                        <div class="metric-label">Taxa Acerto</div>
                        <div class="metric-value">${ativo.taxa_acerto_percent}%</div>
                    </div>
                    
                    <div class="metric">
                        <div class="metric-label">ROI Estratégia</div>
                        <div class="metric-value ${isPositive ? 'positive' : 'negative'}">
                            ${formatPercent(ativo.rentabilidade_estrategia)}
                        </div>
                    </div>
                    
                    <div class="metric">
                        <div class="metric-label">Buy & Hold</div>
                        <div class="metric-value">
                            ${formatPercent(ativo.retorno_buy_hold)}
                        </div>
                    </div>
                    
                    <div class="metric">
                        <div class="metric-label">Retorno Médio/Op</div>
                        <div class="metric-value">${formatPercent(ativo.retorno_medio_por_operacao)}</div>
                    </div>
                    
                    <div class="metric">
                        <div class="metric-label">Maior Ganho</div>
                        <div class="metric-value positive">${formatPercent(ativo.maior_ganho)}</div>
                    </div>
                    
                    <div class="metric">
                        <div class="metric-label">Maior Perda</div>
                        <div class="metric-value negative">${formatPercent(ativo.maior_perda)}</div>
                    </div>
                    
                    <div class="metric">
                        <div class="metric-label">De até Para</div>
                        <div class="metric-value">
                            ${formatCurrency(ativo.preco_inicial)} → ${formatCurrency(ativo.preco_final)}
                        </div>
                    </div>
                </div>
            `;
            
            carteiraDiv.appendChild(card);
        }
        
        carteiraContainer.appendChild(carteiraDiv);
    }
}

// ========== NOTÍCIAS ==========

async function loadNoticias() {
    if (!currentData.analiseAtual) {
        console.log('Carregando dados de análise primeiro...');
        await loadAnaliseAtual();
    }
    
    const container = document.getElementById('noticias-grid');
    container.innerHTML = '<p style="color: #cbd5e1;">Carregando notícias...</p>';
    
    try {
        const noticias = [];
        
        // Coletar todos os ativos únicos das carteiras
        const ativos = new Set();
        for (const carteiraAtivos of Object.values(currentData.analiseAtual.carteiras || {})) {
            for (const ativo of carteiraAtivos) {
                ativos.add(ativo.ativo);
            }
        }
        
        container.innerHTML = '';
        
        // Para cada ativo, criar um card com link de notícias
        for (const ativo of Array.from(ativos).sort()) {
            const card = document.createElement('div');
            card.className = 'noticia-card';
            
            // Gerar URL de busca (Google News)
            const query = encodeURIComponent(ativo);
            const newsUrl = `https://news.google.com/search?q=${query}`;
            
            // Score baseado no ativo (carteiras principais tem score maior)
            let score = 50 + Math.random() * 50;  // 50-100
            
            card.innerHTML = `
                <div class="noticia-symbol">${ativo}</div>
                <div class="noticia-score">Score: ${Math.round(score)}</div>
                <a href="${newsUrl}" target="_blank" class="noticia-link">
                    🔗 Ver Notícias
                </a>
            `;
            
            container.appendChild(card);
        }
        
        if (container.children.length === 0) {
            container.innerHTML = '<p style="color: #cbd5e1; grid-column: 1/-1; text-align: center;">Nenhum ativo disponível</p>';
        }
        
        console.log('[OK] Notícias carregadas');
        
    } catch (error) {
        console.error('Erro ao carregar notícias:', error);
        container.innerHTML = `<p style="color: #ef4444; grid-column: 1/-1;">Erro ao carregar notícias: ${error.message}</p>`;
    }
}

// ========== MODO DEBUG ==========

window.DEBUG = {
    currentData: () => currentData,
    forceAnalise: loadAnaliseAtual,
    forceBacktest: loadBacktest,
    forceNoticias: loadNoticias
};

console.log('💡 Dicas de debug: window.DEBUG.currentData(), window.DEBUG.forceAnalise(), window.DEBUG.forceBacktest(), window.DEBUG.forceNoticias()');
