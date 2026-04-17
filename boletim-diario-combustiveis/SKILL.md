---
name: boletim-diario-combustiveis
description: >
  Gera Boletim Diario AR Souza (combustiveis). Triggers: "gerar", "boletim", "gerar boletim", "gerar hoje".
  Executa fluxo completo automaticamente sem perguntas. Produz HTML com 5 secoes x 3 noticias = 15 noticias.
---

# Boletim Diario AR Souza — v4.0 (Otimizado)

## Contexto

A AR Souza Servicos Contabeis envia diariamente um boletim de noticias para clientes do setor de distribuicao de combustiveis. A curadoria e veracidade das noticias sao prioridade absoluta — qualquer erro compromete a reputacao da empresa.

## Comportamento

Quando o usuario digitar "gerar", "boletim" ou variacoes, executar o fluxo completo **sem fazer nenhuma pergunta**.

## Pasta de trabalho

```python
import glob, os
logo_path = next(p for p in glob.glob('/sessions/*/mnt/R18*/*') if p.endswith('Logo.png'))
out_dir = os.path.dirname(logo_path)
```

Atencao: glob do Python nao funciona com colchetes no caminho. Usar `os.listdir()` + `os.path.join()`. Escrever em arquivo temporario e copiar com `shutil.copy2()` se a escrita direta falhar.

---

## Fluxo de execucao (5 passos)

### 1. Determinar datas

- Edicao = hoje (`datetime.now()`)
- Cobertura = dia anterior (ou sexta+sab+dom se segunda-feira)
- Formato de busca: `DD/MM/AAAA` ou por extenso. Evitar apenas mes/ano.
- Formato header/footer: `DD MMM YYYY` (ex: `14 ABR 2026`)

### 2. Buscar noticias (5 buscas em paralelo)

Lancar 5 WebSearches simultaneas. Consultar `references/fontes.md` para dominios permitidos.

**IMPORTANTE:** Selecionar 5-6 candidatos por secao (over-fetch). Incluir a data de cobertura nos termos. Filtrar resultados pela data JA nos snippets/URLs do WebSearch antes de qualquer verificacao.

**Secoes e termos de busca:**

#### Secao 1 — Contabilidade: Normas e Atualizacoes
- **Termos:** CFC, NBC, CPC, IFRS, CVM, ISSB, contabilidade Brasil, audiencia publica CPC, oficio-circular CVM
- **Escopo:** Pronunciamentos contabeis (CPC, IFRS, NBC), normas de auditoria e divulgacao financeira para distribuidoras de combustiveis. Novos pronunciamentos, revisoes, audiencias publicas, interpretacoes, oficios-circulares da CVM, normas ISSB sustentabilidade.

#### Secao 2 — Fiscal e Tributario: Setor de Combustiveis
- **Termos:** ICMS combustiveis, PIS COFINS monofasico, CIDE combustiveis, IRPJ CSLL distribuidora, IBS CBS reforma tributaria, CONFAZ, substituicao tributaria, subvencao diesel, LC 192/2022, LC 214/2025, RECOB, EFD NF-e SINIEF, STF STJ combustiveis
- **Escopo:** Legislacao tributaria/fiscal da cadeia de combustiveis — tributos federais/estaduais, reforma tributaria, obrigacoes acessorias, jurisprudencia. ICMS monofasico, CIDE, PIS/COFINS monofasico, IBS/CBS/IS, regimes especiais (RECOB, diferimentos), EFD, NF-e, SINIEF, decisoes STF/STJ.

#### Secao 3 — Mercado de Distribuicao de Combustiveis
- **Termos:** Petrobras distribuidora estrategia, distribuidora combustiveis mercado, biodiesel, GLP, QAV querosene aviacao, Vibra, Ipiranga Ultrapar, Raizen, Atem, market share distribuidoras, fusao aquisicao combustiveis, fraude adulteracao combustiveis
- **Escopo:** Dinamica competitiva, movimentos empresariais das distribuidoras. Fusoes/aquisicoes, market share, resultados financeiros, expansao de redes, combate a informalidade, operacoes policiais, transicao energetica. Players: Vibra, Ipiranga/Ultrapar, Raizen, Atem, bandeira branca.

#### Secao 4 — Regulatorio e ANP
- **Termos:** ANP fiscalizacao postos, regulacao combustiveis, resolucao ANP, qualidade combustiveis, PMQC, consulta publica ANP, biodiesel mistura obrigatoria, CNPE, RenovaBio, Combustivel do Futuro
- **Escopo:** Atos normativos e fiscalizacao — resolucoes, portarias, consultas publicas, autorizacoes, processos sancionadores, PMQC, especificacoes de combustiveis, percentuais de mistura (CNPE), metas RenovaBio, Lei do Combustivel do Futuro, decisoes CNPE/MME.

#### Secao 5 — Dados do Setor: Precos, Petroleo e Mercado
- **Termos:** Brent petroleo, WTI, dolar cambio, IPCA, Focus Banco Central, precos combustiveis semana, reajuste Petrobras, defasagem ABICOM, OPEP producao, estoques petroleo EIA, LPC ANP
- **Escopo:** Dados quantitativos — cotacoes de petroleo (Brent/WTI), precos de combustiveis, defasagem ABICOM, cambio USD/BRL, dados de producao/vendas ANP, estoques petroleo, decisoes OPEP+, reajustes Petrobras, LPC/ANP.

**Regra de classificacao:** alocar cada noticia na secao mais aderente ao tema principal. Na duvida, priorizar a secao cujas fontes publicaram a materia.

### 3. Verificar datas (OBRIGATORIO — nao pular)

A AR Souza ja teve problemas com noticias defasadas. Este passo e inegociavel.

**Fluxo de verificacao em 2 niveis (economiza tokens):**

**Nivel 1 — Pre-filtro nos resultados do WebSearch (sem custo extra):**
- Extrair data dos metadados/snippet de cada resultado
- Verificar se a URL contem padrao de data (ex: `/2026/04/13/`)
- Descartar imediatamente resultados fora do periodo de cobertura
- Selecionar os 3 melhores candidatos por secao que passarem no pre-filtro

**Nivel 2 — Verificacao via Chrome MCP (apenas para os selecionados):**
- Navegar ate a URL com `mcp__Claude_in_Chrome__navigate`
- Usar `find` com seletores de data: `time`, `.date`, `.published`, `meta[property='article:published_time']`, ou padrao `DD/MM/AAAA`
- **NAO usar `get_page_text`** — retorna a pagina inteira e consome tokens demais
- Se `find` nao localizar a data, usar `get_page_text` limitado aos primeiros 2000 caracteres como fallback
- Se a data NAO for da data exata de cobertura → descartar e usar proximo candidato da lista de over-fetch (sem nova busca)

**Regras inegociaveis:**
- TODAS as noticias devem ser da DATA EXATA de cobertura (excecao: segunda-feira = sexta+sab+dom)
- A data na tag `<em>Fonte: Nome — DD/MM/AAAA</em>` deve ser a data REAL de publicacao
- JAMAIS inventar, alterar ou forcar datas
- JAMAIS fabricar noticias, titulos ou dados numericos
- Se uma secao ficar com 0 noticias: manter no HTML com mensagem "Nao foram identificadas publicacoes relevantes para esta secao na data de cobertura (DD/MM/AAAA)."
- Minimo 5 noticias no total para o boletim ser publicavel

### 4. Gerar JSON e montar HTML

**O modelo NAO gera HTML diretamente.** Em vez disso:

1. **Gerar Visao Executiva**: paragrafo de 3-5 frases (max 400 chars), tom executivo e direto. Nao repetir titulos — sintetizar temas.
2. **Gerar Destaques do Dia**: 5 bullets (um por secao), max 15 palavras cada.
3. **Salvar um arquivo JSON** no `out_dir` com esta estrutura:

```json
{
  "edition_date": "14 ABR 2026",
  "coverage_date": "13 ABR 2026",
  "logo_path": "/caminho/para/Logo.png",
  "output_path": "/caminho/para/ARS_BOLETIM_COMBUSTIVEIS_2026_04_14.html",
  "executive_summary": "Texto da visao executiva...",
  "highlights": ["Destaque 1", "Destaque 2", "Destaque 3", "Destaque 4", "Destaque 5"],
  "sections": [
    {
      "section_id": 1,
      "news": [
        {
          "tags": "CPC | IFRS | NORMA",
          "title": "Titulo da noticia",
          "text": "Texto com 3-5 linhas resumindo a noticia",
          "source": "Nome da Fonte",
          "date": "13/04/2026"
        }
      ]
    }
  ]
}
```

4. **Executar o assembler** para montar o HTML e validar:
```bash
python references/assembler.py /caminho/para/dados.json
```

O assembler le `references/template.html`, codifica o Logo.png em base64, embute SVGs/cores das secoes, monta o HTML completo e roda a validacao automaticamente. Se a validacao falhar, corrigir o JSON e re-executar.

### 5. Entregar

Construir link `computer://` com o caminho real:
```
[Ver Boletim DD/MM/YYYY](computer://{out_dir}/ARS_BOLETIM_COMBUSTIVEIS_YYYY_MM_DD.html)
```
Incluir resumo da validacao.

---

## Referencias

| Arquivo | Quando ler |
|---------|-----------|
| `references/fontes.md` | Passo 2 — dominios permitidos por secao |
| `references/template.html` | Usado automaticamente pelo assembler.py (nao precisa ler) |
| `references/assembler.py` | Passo 4 — executar via `python` (nao precisa ler) |
