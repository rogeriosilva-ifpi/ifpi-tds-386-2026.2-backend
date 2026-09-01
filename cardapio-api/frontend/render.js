// =====================================================================
// CONCEITO DIDÁTICO: Camada de Renderização Pura (Render / View)
//
// 1. O que este módulo faz?
//    Recebe o 'estado' da aplicação como parâmetro e projeta esse estado no DOM.
// 2. Por que é "pura"?
//    Não faz chamadas de rede (fetch) nem decide regras de negócio.
//    Dado um mesmo estado X, a interface sempre terá a mesma aparência Y.
// =====================================================================

// Seletores do DOM (cacheados para melhor performance)
const elementos = {
    gridCardapio: document.getElementById("grid-cardapio"),
    vazioMsg: document.getElementById("vazio-msg"),
    statTotal: document.getElementById("stat-total"),
    statDisponiveis: document.getElementById("stat-disponiveis"),
    statEsgotados: document.getElementById("stat-esgotados"),
    botoesCategoria: document.querySelectorAll(".btn-categoria"),
    filtroDisponivel: document.getElementById("filtro-disponivel"),
    campoBusca: document.getElementById("campo-busca"),
    statusConexao: document.getElementById("status-conexao"),
    modalItem: document.getElementById("modal-item"),
    modalTitulo: document.getElementById("modal-titulo"),
    formItem: document.getElementById("form-item"),
    itemId: document.getElementById("item-id"),
    itemNome: document.getElementById("item-nome"),
    itemDescricao: document.getElementById("item-descricao"),
    itemPreco: document.getElementById("item-preco"),
    itemCategoria: document.getElementById("item-categoria"),
    itemDisponivel: document.getElementById("item-disponivel"),
    itemTempo: document.getElementById("item-tempo"),
};


/**
 * CONCEITO: Função Master de Renderização
 * É esta função que é passada para o subscribe(renderizarApp).
 * Sempre que notify() for disparado no state.js, ela é executada.
 */
export function renderizarApp(estado) {
    renderizarStatus(estado);
    renderizarEstatisticas(estado);
    renderizarFiltros(estado);
    renderizarCards(estado);
    renderizarModal(estado);
}


/**
 * CONCEITO: Renderização de Feedback Visual (Loading e Erros)
 */
export function renderizarStatus(estado) {
    const el = elementos.statusConexao;
    if (!el) return;

    if (estado.erro) {
        el.className = "mb-6 p-4 rounded-xl border border-rose-200 bg-rose-50 text-rose-800 text-xs flex items-center justify-between";
        el.innerHTML = `
            <div class="flex items-center gap-2">
                <i class="fa-solid fa-triangle-exclamation text-rose-500 text-base"></i>
                <div>
                    <p class="font-bold">Aviso de Comunicação</p>
                    <p class="text-rose-600 mt-0.5">${escapeHtml(estado.erro)}</p>
                </div>
            </div>
            <button id="btn-tentar-novamente" class="px-3 py-1.5 bg-rose-600 text-white font-bold rounded-lg hover:bg-rose-500 transition">
                Tentar Novamente
            </button>
        `;
        el.classList.remove("hidden");
    } else {
        el.classList.add("hidden");
        el.innerHTML = "";
    }
}


/**
 * CONCEITO: Renderização de Estatísticas Calculadas
 */
export function renderizarEstatisticas(estado) {
    const total = estado.itens.length;
    const disponiveis = estado.itens.filter(i => i.disponivel).length;
    const esgotados = total - disponiveis;

    if (elementos.statTotal) elementos.statTotal.innerText = total;
    if (elementos.statDisponiveis) elementos.statDisponiveis.innerText = disponiveis;
    if (elementos.statEsgotados) elementos.statEsgotados.innerText = esgotados;
}


/**
 * CONCEITO: Renderização dos Filtros Ativos
 */
export function renderizarFiltros(estado) {
    // 1. Destaque do botão de categoria ativa
    elementos.botoesCategoria.forEach(btn => {
        const cat = btn.getAttribute("data-categoria");
        if (cat === estado.categoriaAtiva) {
            btn.className = "btn-categoria px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-600 text-white shadow-sm transition";
        } else {
            btn.className = "btn-categoria px-3 py-1.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition";
        }
    });

    // 2. Checkbox de disponíveis
    if (elementos.filtroDisponivel && elementos.filtroDisponivel.checked !== estado.filtroDisponivel) {
        elementos.filtroDisponivel.checked = estado.filtroDisponivel;
    }
}


/**
 * CONCEITO: Renderização Declarativa da Coleção de Cards
 * Filtra a lista de acordo com os critérios do estado antes de desenhar.
 */
export function renderizarCards(estado) {
    const grid = elementos.gridCardapio;
    const vazio = elementos.vazioMsg;
    if (!grid) return;

    // Filtros reativos aplicados sobre a lista de itens
    let itensVisiveis = estado.itens;

    if (estado.categoriaAtiva) {
        itensVisiveis = itensVisiveis.filter(i => i.categoria === estado.categoriaAtiva);
    }

    if (estado.filtroDisponivel) {
        itensVisiveis = itensVisiveis.filter(i => i.disponivel === true);
    }

    if (estado.busca) {
        const termo = estado.busca;
        itensVisiveis = itensVisiveis.filter(i => 
            i.nome.toLowerCase().includes(termo) || 
            (i.descricao && i.descricao.toLowerCase().includes(termo))
        );
    }

    grid.innerHTML = "";

    if (itensVisiveis.length === 0) {
        if (vazio) vazio.classList.remove("hidden");
        return;
    }

    if (vazio) vazio.classList.add("hidden");

    itensVisiveis.forEach(item => {
        const card = document.createElement("article");
        card.className = `bg-white rounded-2xl p-5 border transition-all duration-200 hover:shadow-md flex flex-col justify-between ${
            item.disponivel ? "border-slate-200" : "border-rose-200 bg-rose-50/20"
        }`;

        let corBadge = "bg-amber-100 text-amber-800";
        if (item.categoria === "Bebidas") corBadge = "bg-sky-100 text-sky-800";
        if (item.categoria === "Sobremesas") corBadge = "bg-purple-100 text-purple-800";

        const precoFormatado = Number(item.preco).toLocaleString("pt-BR", {
            style: "currency",
            currency: "BRL"
        });

        const tempoBadge = item.tempo_preparo_minutos 
            ? `<span class="inline-flex items-center gap-1 text-[11px] text-slate-500 font-medium bg-slate-100 px-2 py-0.5 rounded-full">
                <i class="fa-regular fa-clock text-amber-500"></i> ${item.tempo_preparo_minutos} min
               </span>` 
            : "";

        // O uso de data-action e data-id viabiliza a delegação de eventos desacoplada
        card.innerHTML = `
            <div>
                <div class="flex justify-between items-start gap-2 mb-2">
                    <div class="flex items-center gap-1.5 flex-wrap">
                        <span class="text-[11px] font-bold px-2.5 py-0.5 rounded-full ${corBadge}">
                            ${escapeHtml(item.categoria)}
                        </span>
                        ${tempoBadge}
                    </div>
                    <span class="inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-0.5 rounded-full ${
                        item.disponivel ? "bg-emerald-100 text-emerald-800" : "bg-rose-100 text-rose-800"
                    }">
                        <span class="w-1.5 h-1.5 rounded-full ${item.disponivel ? "bg-emerald-500" : "bg-rose-500"}"></span>
                        ${item.disponivel ? "Disponível" : "Esgotado"}
                    </span>
                </div>
                
                <h4 class="font-bold text-slate-900 text-base mb-1">${escapeHtml(item.nome)}</h4>
                <p class="text-xs text-slate-500 line-clamp-2 mb-4">${escapeHtml(item.descricao || "Sem descrição informada.")}</p>
            </div>

            <div class="pt-3 border-t border-slate-100 flex items-center justify-between mt-auto">
                <span class="text-base font-extrabold text-slate-900">${precoFormatado}</span>

                <div class="flex items-center gap-1">
                    <!-- Alternar Disponibilidade (PATCH) -->
                    <button data-action="alternar" data-id="${item.id}"
                            title="${item.disponivel ? "Marcar como Esgotado" : "Marcar como Disponível"}"
                            class="p-2 text-xs rounded-lg transition ${
                                item.disponivel 
                                    ? "text-slate-400 hover:text-rose-600 hover:bg-rose-50" 
                                    : "text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50"
                            }">
                        <i class="fa-solid fa-power-off pointer-events-none"></i>
                    </button>

                    <!-- Editar Item (PUT) -->
                    <button data-action="editar" data-id="${item.id}"
                            title="Editar Item"
                            class="p-2 text-xs text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition">
                        <i class="fa-solid fa-pen pointer-events-none"></i>
                    </button>

                    <!-- Excluir Item (DELETE) -->
                    <button data-action="excluir" data-id="${item.id}" data-nome="${escapeHtml(item.nome)}"
                            title="Excluir Item"
                            class="p-2 text-xs text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition">
                        <i class="fa-solid fa-trash-can pointer-events-none"></i>
                    </button>
                </div>
            </div>
        `;

        grid.appendChild(card);
    });
}


/**
 * CONCEITO: Renderização do Modal de Cadastro/Edição
 * Controla abertura, fechamento e preenchimento dos campos conforme o estado.
 */
export function renderizarModal(estado) {
    const modal = elementos.modalItem;
    if (!modal) return;

    if (estado.modalAberto) {
        modal.classList.remove("hidden");

        if (estado.itemEmEdicao) {
            elementos.modalTitulo.innerText = `Editar Item #${estado.itemEmEdicao.id}`;
            elementos.itemId.value = estado.itemEmEdicao.id;
            elementos.itemNome.value = estado.itemEmEdicao.nome;
            elementos.itemDescricao.value = estado.itemEmEdicao.descricao || "";
            elementos.itemPreco.value = estado.itemEmEdicao.preco;
            elementos.itemCategoria.value = estado.itemEmEdicao.categoria;
            elementos.itemDisponivel.checked = estado.itemEmEdicao.disponivel;
            if (elementos.itemTempo) {
                elementos.itemTempo.value = estado.itemEmEdicao.tempo_preparo_minutos || "";
            }
        } else {
            elementos.modalTitulo.innerText = "Novo Item no Cardápio";
            elementos.formItem.reset();
            elementos.itemId.value = "";
            elementos.itemDisponivel.checked = true;
            if (elementos.itemTempo) {
                elementos.itemTempo.value = "";
            }
        }

        setTimeout(() => elementos.itemNome.focus(), 50);
    } else {
        modal.classList.add("hidden");
    }
}


/**
 * Função utilitária de sanitização HTML básica (Prevenção de XSS)
 */
function escapeHtml(texto) {
    if (!texto) return "";
    return String(texto)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
