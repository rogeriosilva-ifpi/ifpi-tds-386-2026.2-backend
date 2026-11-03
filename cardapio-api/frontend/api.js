// =====================================================================
// CONCEITO DIDÁTICO: Camada de Rede Pura (API Client)
//
// Este módulo é 100% focado no protocolo HTTP:
// - Não manipula elementos da tela (DOM).
// - Não altera o estado diretamente.
// - Retorna Promises (usando async/await) para quem o chamou (app.js).
// =====================================================================

// =====================================================================
// CONCEITO: Resolução Dinâmica da URL da API (Local vs Nuvem / Render)
// - Em desenvolvimento com servidores separados (Live Server 5500, Vite 5173, Python 3000):
//   redireciona para http://127.0.0.1:8000.
// - Em produção no Render (https://...onrender.com) ou servido diretamente pelo FastAPI:
//   utiliza a própria origem (window.location.origin), garantindo HTTPS e zero CORS.
// =====================================================================
const portasDevSeparadas = ["3000", "5500", "5173"];
const API_BASE_URL = portasDevSeparadas.includes(window.location.port) 
    ? "http://127.0.0.1:8000" 
    : window.location.origin;



/**
 * CONCEITO: Requisição GET com Query Parameters
 * Busca a lista de pratos com suporte a filtros opcionais.
 */
export async function listarCardapio(filtros = {}) {
    const params = new URLSearchParams();

    if (filtros.categoria) {
        params.append("categoria", filtros.categoria);
    }
    if (filtros.disponivel !== undefined && filtros.disponivel !== null) {
        params.append("disponivel", String(filtros.disponivel));
    }
    if (filtros.busca) {
        params.append("busca", filtros.busca);
    }

    const qs = params.toString();
    const url = `${API_BASE_URL}/cardapio/${qs ? `?${qs}` : ""}`;

    const resposta = await fetch(url);
    if (!resposta.ok) {
        throw new Error(`Erro ${resposta.status}: Não foi possível carregar o cardápio.`);
    }

    return await resposta.json();
}


/**
 * CONCEITO: Requisição GET com Path Parameter
 * Consulta um prato específico pelo seu ID.
 */
export async function obterItemPorId(id) {
    const resposta = await fetch(`${API_BASE_URL}/cardapio/${id}`);
    if (!resposta.ok) {
        throw new Error(`Erro ${resposta.status}: Item não encontrado.`);
    }
    return await resposta.json();
}


/**
 * CONCEITO: Requisição POST (Criação) com Status 201
 * Envia o corpo JSON validado pelo backend.
 */
export async function cadastrarItem(dadosItem) {
    const resposta = await fetch(`${API_BASE_URL}/cardapio/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(dadosItem),
    });

    if (!resposta.ok) {
        const erroJson = await resposta.json().catch(() => ({}));
        throw new Error(erroJson.detail || `Erro ${resposta.status} ao cadastrar prato.`);
    }

    return await resposta.json();
}


/**
 * CONCEITO: Requisição PUT (Atualização Completa)
 */
export async function atualizarItem(id, dadosItem) {
    const resposta = await fetch(`${API_BASE_URL}/cardapio/${id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(dadosItem),
    });

    if (!resposta.ok) {
        const erroJson = await resposta.json().catch(() => ({}));
        throw new Error(erroJson.detail || `Erro ${resposta.status} ao atualizar prato.`);
    }

    return await resposta.json();
}


/**
 * CONCEITO: Requisição PATCH (Atualização Parcial Rápida)
 * Alterna rapidamente a disponibilidade (disponível / esgotado).
 */
export async function alternarDisponibilidade(id) {
    const resposta = await fetch(`${API_BASE_URL}/cardapio/${id}/disponibilidade`, {
        method: "PATCH",
    });

    if (!resposta.ok) {
        throw new Error(`Erro ${resposta.status} ao alternar disponibilidade.`);
    }

    return await resposta.json();
}


/**
 * CONCEITO: Requisição DELETE (Exclusão com Status 204)
 */
export async function removerItem(id) {
    const resposta = await fetch(`${API_BASE_URL}/cardapio/${id}`, {
        method: "DELETE",
    });

    if (!resposta.ok && resposta.status !== 204) {
        throw new Error(`Erro ${resposta.status} ao excluir item.`);
    }

    return true;
}
