// =====================================================================
// CONCEITO: Consumo de API REST com Fetch API (JavaScript Vanilla)
// Esta aplicação demonstra como o navegador consome uma API backend:
// - GET: Recuperar dados
// - POST: Criar novos recursos
// - PUT: Atualizar recursos existentes
// - PATCH: Atualização parcial rápida
// - DELETE: Remover recursos
// =====================================================================

const API_BASE_URL = "http://127.0.0.1:8000";

let categoriaAtiva = "";
let debounceTimeout = null;

// Elementos da Interface
const gridCardapio = document.getElementById("grid-cardapio");
const vazioMsg = document.getElementById("vazio-msg");
const campoBusca = document.getElementById("campo-busca");
const filtroDisponivel = document.getElementById("filtro-disponivel");
const modalItem = document.getElementById("modal-item");
const formItem = document.getElementById("form-item");
const statusConexao = document.getElementById("status-conexao");

// Contadores de Estatísticas
const statTotal = document.getElementById("stat-total");
const statDisponiveis = document.getElementById("stat-disponiveis");
const statEsgotados = document.getElementById("stat-esgotados");


// =====================================================================
// CONCEITO: Requisição GET com Query Parameters
// Envia filtros na URL (?categoria=...&disponivel=...&busca=...)
// =====================================================================
async function carregarItens() {
    try {
        const params = new URLSearchParams();

        if (categoriaAtiva) {
            params.append("categoria", categoriaAtiva);
        }

        if (filtroDisponivel.checked) {
            params.append("disponivel", "true");
        }

        const termoBusca = campoBusca.value.trim();
        if (termoBusca) {
            params.append("busca", termoBusca);
        }

        const url = `${API_BASE_URL}/cardapio/?${params.toString()}`;
        const resposta = await fetch(url);

        if (!resposta.ok) {
            throw new Error(`Erro HTTP ${resposta.status}: ${resposta.statusText}`);
        }

        const itens = await resposta.json();
        ocultarErroConexao();
        renderizarCards(itens);
        atualizarEstatisticas(itens);
    } catch (erro) {
        console.error("Falha ao comunicar com a API:", erro);
        exibirErroConexao(erro.message);
    }
}


// =====================================================================
// CONCEITO: Renderização Dinâmica do DOM
// Cria elementos HTML para cada item retornado pelo Backend
// =====================================================================
function renderizarCards(itens) {
    gridCardapio.innerHTML = "";

    if (!itens || itens.length === 0) {
        vazioMsg.classList.remove("hidden");
        return;
    }

    vazioMsg.classList.add("hidden");

    itens.forEach(item => {
        const card = document.createElement("article");
        card.className = `bg-white rounded-2xl p-5 border transition-all duration-200 hover:shadow-md flex flex-col justify-between ${
            item.disponivel ? "border-slate-200" : "border-rose-200 bg-rose-50/20"
        }`;

        // Cores semânticas por categoria
        let corBadge = "bg-amber-100 text-amber-800";
        if (item.categoria === "Bebidas") corBadge = "bg-sky-100 text-sky-800";
        if (item.categoria === "Sobremesas") corBadge = "bg-purple-100 text-purple-800";

        // Formatação de moeda BRL (Real)
        const precoFormatado = Number(item.preco).toLocaleString("pt-BR", {
            style: "currency",
            currency: "BRL"
        });

        card.innerHTML = `
            <div>
                <div class="flex justify-between items-start gap-2 mb-2">
                    <span class="text-[11px] font-bold px-2.5 py-0.5 rounded-full ${corBadge}">
                        ${item.categoria}
                    </span>
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
                    <button onclick="alternarDisponibilidade(${item.id})" 
                            title="${item.disponivel ? "Marcar como Esgotado" : "Marcar como Disponível"}"
                            class="p-2 text-xs rounded-lg transition ${
                                item.disponivel 
                                    ? "text-slate-400 hover:text-rose-600 hover:bg-rose-50" 
                                    : "text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50"
                            }">
                        <i class="fa-solid fa-power-off"></i>
                    </button>

                    <!-- Editar Item (PUT) -->
                    <button onclick='abrirModalEdicao(${JSON.stringify(item)})' 
                            title="Editar Item"
                            class="p-2 text-xs text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition">
                        <i class="fa-solid fa-pen"></i>
                    </button>

                    <!-- Excluir Item (DELETE) -->
                    <button onclick="excluirItem(${item.id}, '${escapeHtml(item.nome)}')" 
                            title="Excluir Item"
                            class="p-2 text-xs text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </div>
            </div>
        `;

        gridCardapio.appendChild(card);
    });
}


// =====================================================================
// CONCEITO: Requisição POST (Criação) ou PUT (Edição) com Body JSON
// Envia os dados no corpo com cabeçalho 'Content-Type': 'application/json'
// =====================================================================
async function salvarItem(event) {
    event.preventDefault();

    const id = document.getElementById("item-id").value;
    const nome = document.getElementById("item-nome").value.trim();
    const descricao = document.getElementById("item-descricao").value.trim() || null;
    const preco = parseFloat(document.getElementById("item-preco").value);
    const categoria = document.getElementById("item-categoria").value;
    const disponivel = document.getElementById("item-disponivel").checked;

    const payload = { nome, descricao, preco, categoria, disponivel };

    try {
        let url = `${API_BASE_URL}/cardapio/`;
        let metodo = "POST";

        if (id) {
            // Se possui ID, é uma atualização (PUT)
            url = `${API_BASE_URL}/cardapio/${id}`;
            metodo = "PUT";
        }

        const resposta = await fetch(url, {
            method: metodo,
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        });

        if (!resposta.ok) {
            const erroData = await resposta.json().catch(() => ({}));
            throw new Error(erroData.detail || `Erro HTTP ${resposta.status}`);
        }

        fecharModal();
        await carregarItens();
    } catch (erro) {
        alert(`Erro ao salvar item: ${erro.message}`);
    }
}


// =====================================================================
// CONCEITO: Requisição PATCH (Atualização Parcial)
// Usado aqui para alternar o status disponível/esgotado
// =====================================================================
async function alternarDisponibilidade(id) {
    try {
        const resposta = await fetch(`${API_BASE_URL}/cardapio/${id}/disponibilidade`, {
            method: "PATCH",
        });

        if (!resposta.ok) {
            throw new Error(`Erro ao atualizar disponibilidade (${resposta.status})`);
        }

        await carregarItens();
    } catch (erro) {
        alert(`Não foi possível alterar a disponibilidade: ${erro.message}`);
    }
}


// =====================================================================
// CONCEITO: Requisição DELETE (Remoção com Status 204)
// =====================================================================
async function excluirItem(id, nome) {
    const confirmou = confirm(`Deseja realmente remover o item "${nome}" do cardápio?`);
    if (!confirmou) return;

    try {
        const resposta = await fetch(`${API_BASE_URL}/cardapio/${id}`, {
            method: "DELETE",
        });

        if (!resposta.ok && resposta.status !== 204) {
            throw new Error(`Erro ao excluir item (${resposta.status})`);
        }

        await carregarItens();
    } catch (erro) {
        alert(`Não foi possível excluir o item: ${erro.message}`);
    }
}


// =====================================================================
// Funções Utilitárias e Modais
// =====================================================================
function abrirModalCadastro() {
    formItem.reset();
    document.getElementById("item-id").value = "";
    document.getElementById("item-disponivel").checked = true;
    document.getElementById("modal-titulo").innerText = "Novo Item no Cardápio";
    modalItem.classList.remove("hidden");
    document.getElementById("item-nome").focus();
}

function abrirModalEdicao(item) {
    document.getElementById("item-id").value = item.id;
    document.getElementById("item-nome").value = item.nome;
    document.getElementById("item-descricao").value = item.descricao || "";
    document.getElementById("item-preco").value = item.preco;
    document.getElementById("item-categoria").value = item.categoria;
    document.getElementById("item-disponivel").checked = item.disponivel;
    document.getElementById("modal-titulo").innerText = `Editar Item #${item.id}`;
    modalItem.classList.remove("hidden");
    document.getElementById("item-nome").focus();
}

function fecharModal() {
    modalItem.classList.add("hidden");
    formItem.reset();
}

function filtrarCategoria(categoria) {
    categoriaAtiva = categoria;

    // Atualizar estilo visual dos botões
    document.querySelectorAll(".btn-categoria").forEach(btn => {
        if (btn.getAttribute("data-categoria") === categoria) {
            btn.className = "btn-categoria px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-600 text-white shadow-sm transition";
        } else {
            btn.className = "btn-categoria px-3 py-1.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 transition";
        }
    });

    carregarItens();
}

function atualizarEstatisticas(itens) {
    const total = itens.length;
    const disponiveis = itens.filter(i => i.disponivel).length;
    const esgotados = total - disponiveis;

    statTotal.innerText = total;
    statDisponiveis.innerText = disponiveis;
    statEsgotados.innerText = esgotados;
}

function exibirErroConexao(msg) {
    statusConexao.className = "mb-6 p-4 rounded-xl border border-rose-200 bg-rose-50 text-rose-800 text-xs flex items-center justify-between";
    statusConexao.innerHTML = `
        <div class="flex items-center gap-2">
            <i class="fa-solid fa-triangle-exclamation text-rose-500 text-base"></i>
            <div>
                <p class="font-bold">Não foi possível conectar ao Backend (${API_BASE_URL})</p>
                <p class="text-rose-600 mt-0.5">Certifique-se de que a API está rodando com: <code>uvicorn app.main:app --reload</code></p>
            </div>
        </div>
        <button onclick="carregarItens()" class="px-3 py-1.5 bg-rose-600 text-white font-bold rounded-lg hover:bg-rose-500 transition">
            Tentar Novamente
        </button>
    `;
    statusConexao.classList.remove("hidden");
}

function ocultarErroConexao() {
    statusConexao.classList.add("hidden");
}

function escapeHtml(texto) {
    if (!texto) return "";
    return texto
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Fechar modal ao clicar fora do conteúdo
modalItem.addEventListener("click", (e) => {
    if (e.target === modalItem) {
        fecharModal();
    }
});

// Listener de busca com debounce (300ms)
campoBusca.addEventListener("input", () => {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
        carregarItens();
    }, 300);
});

filtroDisponivel.addEventListener("change", () => {
    carregarItens();
});

// Inicialização automática ao carregar a página
document.addEventListener("DOMContentLoaded", () => {
    carregarItens();
});
