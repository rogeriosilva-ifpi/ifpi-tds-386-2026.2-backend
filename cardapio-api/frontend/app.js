// =====================================================================
// CONCEITO DIDÁTICO: Controlador da Aplicação (App / Controller)
//
// 1. O que este módulo faz?
//    - Faz o startup da aplicação (inicialização).
//    - Registra o render.js como ouvinte do state.js via subscribe().
//    - Vincula os eventos do DOM (clicks, submits, inputs) às regras de negócio.
//    - Orquestra o ciclo: Usuário -> Evento -> API -> State -> Notify -> Render.
// =====================================================================

import {
    getState,
    subscribe,
    setItens,
    setCategoria,
    setFiltroDisponivel,
    setBusca,
    setCarregando,
    setErro,
    abrirModalNovo,
    abrirModalEdicao,
    fecharModal
} from "./state.js";

import * as api from "./api.js";
import { renderizarApp } from "./render.js";

// Variável para controle de debounce na busca por texto
let debounceTimeout = null;


// =====================================================================
// CONCEITO: Inscrição Reativa Principal (The Reactive Hook)
// Conecta o motor de renderização às mudanças de estado.
// A partir desta linha, qualquer alteração em state.js dispara renderizarApp!
// =====================================================================
subscribe(renderizarApp);


// =====================================================================
// CONCEITO: Inicialização e Carregamento de Dados (Startup)
// =====================================================================
async function carregarDadosIniciais() {
    setCarregando(true);
    setErro(null);

    try {
        const dados = await api.listarCardapio();
        setItens(dados);
    } catch (erro) {
        console.error("Falha na inicialização da aplicação:", erro);
        setErro(erro.message);
    } finally {
        setCarregando(false);
    }
}


// =====================================================================
// CONCEITO: Vinculação de Eventos (Event Binding Desacoplado)
// Remove a necessidade de atributos onclick/onsubmit no HTML.
// =====================================================================
function configurarEventos() {
    // 1. Botão de Abertura do Modal de Novo Item
    const btnNovo = document.getElementById("btn-novo-item");
    if (btnNovo) {
        btnNovo.addEventListener("click", () => abrirModalNovo());
    }

    // 2. Botões de Fechar Modal
    const btnFechar = document.getElementById("btn-fechar-modal");
    const btnCancelar = document.getElementById("btn-cancelar-modal");
    const modal = document.getElementById("modal-item");

    if (btnFechar) btnFechar.addEventListener("click", () => fecharModal());
    if (btnCancelar) btnCancelar.addEventListener("click", () => fecharModal());

    // Fechar ao clicar no backdrop (fundo escuro)
    if (modal) {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) fecharModal();
        });
    }

    // 3. Submissão do Formulário (POST ou PUT)
    const form = document.getElementById("form-item");
    if (form) {
        form.addEventListener("submit", lidarComSubmissaoFormulario);
    }

    // 4. Filtro por Categoria (clique nos botões de pílula)
    const containerFiltros = document.getElementById("filtros-categoria");
    if (containerFiltros) {
        containerFiltros.addEventListener("click", (e) => {
            const btn = e.target.closest(".btn-categoria");
            if (!btn) return;
            const categoria = btn.getAttribute("data-categoria");
            setCategoria(categoria);
        });
    }

    // 5. Filtro de Disponíveis (Checkbox)
    const chkDisponivel = document.getElementById("filtro-disponivel");
    if (chkDisponivel) {
        chkDisponivel.addEventListener("change", (e) => {
            setFiltroDisponivel(e.target.checked);
        });
    }

    // 6. Campo de Busca com Debounce (evita requisições excessivas enquanto o usuário digita)
    const campoBusca = document.getElementById("campo-busca");
    if (campoBusca) {
        campoBusca.addEventListener("input", (e) => {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => {
                setBusca(e.target.value);
            }, 250);
        });
    }

    // 7. Delegação de Eventos no Grid de Cards (Alternar, Editar, Excluir)
    // Em vez de vincular centenas de listeners a cada card, vinculamos um único ao grid pai.
    const grid = document.getElementById("grid-cardapio");
    if (grid) {
        grid.addEventListener("click", lidarComAcoesDosCards);
    }

    // 8. Botão de Tentar Novamente no banner de erro
    const containerStatus = document.getElementById("status-conexao");
    if (containerStatus) {
        containerStatus.addEventListener("click", (e) => {
            if (e.target.id === "btn-tentar-novamente") {
                carregarDadosIniciais();
            }
        });
    }
}


// =====================================================================
// CONCEITO: Manipulador de Submissão do Formulário (Cadastro / Edição)
// =====================================================================
async function lidarComSubmissaoFormulario(evento) {
    evento.preventDefault();

    const id = document.getElementById("item-id").value;
    const tempoVal = document.getElementById("item-tempo").value;
    const payload = {
        nome: document.getElementById("item-nome").value.trim(),
        descricao: document.getElementById("item-descricao").value.trim() || null,
        preco: parseFloat(document.getElementById("item-preco").value),
        categoria: document.getElementById("item-categoria").value,
        disponivel: document.getElementById("item-disponivel").checked,
        tempo_preparo_minutos: tempoVal ? parseInt(tempoVal, 10) : null,
    };

    try {
        setCarregando(true);

        if (id) {
            // Se possui ID, atualiza via PUT
            await api.atualizarItem(Number(id), payload);
        } else {
            // Se não possui ID, cadastra novo via POST
            await api.cadastrarItem(payload);
        }

        fecharModal();

        // Atualiza a lista no estado com os dados mais recentes do backend
        const pratosAtualizados = await api.listarCardapio();
        setItens(pratosAtualizados);
    } catch (erro) {
        alert(`Erro ao salvar item: ${erro.message}`);
    } finally {
        setCarregando(false);
    }
}


// =====================================================================
// CONCEITO: Delegação de Ações dos Cards
// Identifica qual botão de ação foi clicado com base em data-action
// =====================================================================
async function lidarComAcoesDosCards(evento) {
    const botao = evento.target.closest("button[data-action]");
    if (!botao) return;

    const acao = botao.getAttribute("data-action");
    const id = Number(botao.getAttribute("data-id"));

    if (acao === "alternar") {
        try {
            await api.alternarDisponibilidade(id);
            // Atualiza o estado recarregando os itens
            const pratos = await api.listarCardapio();
            setItens(pratos);
        } catch (erro) {
            alert(`Falha ao alternar disponibilidade: ${erro.message}`);
        }
    } else if (acao === "editar") {
        const estadoAtual = getState();
        const itemParaEditar = estadoAtual.itens.find(i => i.id === id);
        if (itemParaEditar) {
            abrirModalEdicao(itemParaEditar);
        }
    } else if (acao === "excluir") {
        const nome = botao.getAttribute("data-nome") || "este item";
        const confirmou = confirm(`Deseja realmente excluir "${nome}" do cardápio?`);
        if (!confirmou) return;

        try {
            await api.removerItem(id);
            const pratos = await api.listarCardapio();
            setItens(pratos);
        } catch (erro) {
            alert(`Falha ao excluir item: ${erro.message}`);
        }
    }
}


// =====================================================================
// Ponto de Entrada: Inicialização no ciclo de vida do DOM
// =====================================================================
document.addEventListener("DOMContentLoaded", () => {
    configurarEventos();
    carregarDadosIniciais();
});
