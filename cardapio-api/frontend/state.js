// =====================================================================
// CONCEITO DIDÁTICO: Estado Reativo & Padrão Observador (Observer / Pub-Sub)
//
// 1. O que é Estado (State)?
//    É a "única fonte da verdade" (Single Source of Truth) da interface.
//    Contém todas as variáveis que definem o que deve ser desenhado na tela.
//
// 2. O que é Notificação e Inscrição (Pub-Sub)?
//    - subscribe(listener): Permite que a tela se "inscreva" para ser avisada.
//    - notify(): Percorre todos os inscritos passando o estado novo.
//
// 3. Imutabilidade:
//    O estado nunca deve ser alterado diretamente por fora. Somente funções
//    específicas (mutators / setters) têm permissão de alterar e notificar.
// =====================================================================

// Estado interno e privado da aplicação
const state = {
    itens: [],              // Lista de pratos recebida da API
    categoriaAtiva: "",     // Categoria selecionada ("" = Todos, "Lanches", "Bebidas", "Sobremesas")
    filtroDisponivel: false,// Se true, exibe apenas os disponíveis
    busca: "",              // Termo digitado na caixa de pesquisa
    carregando: false,      // Indica se uma requisição HTTP está em andamento
    erro: null,             // Mensagem de erro caso alguma chamada de rede falhe
    modalAberto: false,     // Controla a visibilidade do modal de cadastro/edição
    itemEmEdicao: null      // Item selecionado para edição (null se for novo cadastro)
};

// Lista de funções "observadoras" que serão executadas quando o estado mudar
const listeners = [];


// =====================================================================
// CONCEITO: subscribe(listener)
// Registra uma função para ser chamada automaticamente a cada alteração.
// Retorna uma função para cancelar a inscrição se desejado.
// =====================================================================
export function subscribe(listener) {
    if (typeof listener === "function") {
        listeners.push(listener);
    }
    return () => {
        const index = listeners.indexOf(listener);
        if (index > -1) {
            listeners.splice(index, 1);
        }
    };
}


// =====================================================================
// CONCEITO: notify()
// Propaga a mudança: executa todos os ouvintes registrados passando o
// estado atualizado.
// =====================================================================
export function notify() {
    const estadoAtual = getState();
    listeners.forEach(listener => {
        try {
            listener(estadoAtual);
        } catch (err) {
            console.error("Erro ao executar ouvinte do estado:", err);
        }
    });
}


// =====================================================================
// CONCEITO: getState()
// Retorna uma cópia protegida do estado para evitar mutações acidentais
// fora dos mutators oficiais.
// =====================================================================
export function getState() {
    return {
        ...state,
        itens: [...state.itens],
        itemEmEdicao: state.itemEmEdicao ? { ...state.itemEmEdicao } : null
    };
}


// =====================================================================
// CONCEITO: Funções de Atualização de Estado (Mutators / Setters)
// Cada função altera um atributo específico e dispara notify().
// =====================================================================

export function setItens(novosItens) {
    state.itens = Array.isArray(novosItens) ? novosItens : [];
    state.erro = null;
    notify();
}

export function setCategoria(novaCategoria) {
    state.categoriaAtiva = novaCategoria || "";
    notify();
}

export function setFiltroDisponivel(apenasDisponiveis) {
    state.filtroDisponivel = Boolean(apenasDisponiveis);
    notify();
}

export function setBusca(termo) {
    state.busca = (termo || "").trim().toLowerCase();
    notify();
}

export function setCarregando(estaCarregando) {
    state.carregando = Boolean(estaCarregando);
    notify();
}

export function setErro(mensagemErro) {
    state.erro = mensagemErro;
    notify();
}

export function abrirModalNovo() {
    state.modalAberto = true;
    state.itemEmEdicao = null;
    notify();
}

export function abrirModalEdicao(item) {
    state.modalAberto = true;
    state.itemEmEdicao = { ...item };
    notify();
}

export function fecharModal() {
    state.modalAberto = false;
    state.itemEmEdicao = null;
    notify();
}
