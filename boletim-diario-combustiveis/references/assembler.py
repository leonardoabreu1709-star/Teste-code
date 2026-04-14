#!/usr/bin/env python3
"""
Assembler do Boletim Diario AR Souza
Monta o HTML final a partir de um JSON de noticias + template.html + Logo.png
Uso: python assembler.py <caminho_json> [--logo <caminho_logo>] [--template <caminho_template>] [--output <caminho_saida>]
"""
import argparse, base64, json, os, re, sys

# ── Metadados das secoes (absorve secoes.md) ──────────────────────────
SECOES = {
    1: {
        "titulo": "1. Contabilidade \u2014 Normas e Atualiza\u00e7\u00f5es",
        "cor": "#1565C0",
        "svg": '<svg viewBox="0 0 15 15" width="20" height="20" xmlns="http://www.w3.org/2000/svg"><rect x="1.5" y="11.5" width="12" height="1.8" fill="#1565C0"/><rect x="1.5" y="8" width="9.5" height="1.8" fill="#1565C0"/><rect x="1.5" y="4.5" width="7" height="1.8" fill="#1565C0"/></svg>',
    },
    2: {
        "titulo": "2. Fiscal e Tribut\u00e1rio \u2014 Setor de Combust\u00edveis",
        "cor": "#2E7D32",
        "svg": '<svg viewBox="0 0 15 15" width="20" height="20" xmlns="http://www.w3.org/2000/svg"><circle cx="7.5" cy="7.5" r="6" fill="none" stroke="#2E7D32" stroke-width="1.4"/><circle cx="4.8" cy="10.2" r="1.1" fill="#2E7D32"/><circle cx="10.2" cy="4.8" r="1.1" fill="#2E7D32"/><line x1="4.5" y1="10.5" x2="10.5" y2="4.5" stroke="#2E7D32" stroke-width="1.2"/></svg>',
    },
    3: {
        "titulo": "3. Mercado de Distribui\u00e7\u00e3o de Combust\u00edveis",
        "cor": "#E65100",
        "svg": '<svg viewBox="0 0 15 15" width="20" height="20" xmlns="http://www.w3.org/2000/svg"><path d="M7.5,1 C7.5,1 13,6 13,8.5 C13,12 10.5,14 7.5,14 C4.5,14 2,12 2,8.5 C2,6 7.5,1 7.5,1 Z" fill="#E65100"/><circle cx="5.5" cy="6.5" r="1.2" fill="white" opacity="0.4"/></svg>',
    },
    4: {
        "titulo": "4. Regulat\u00f3rio e ANP",
        "cor": "#6A1B9A",
        "svg": '<svg viewBox="0 0 15 15" width="20" height="20" xmlns="http://www.w3.org/2000/svg"><rect x="6.8" y="5.5" width="1.4" height="9" fill="#6A1B9A"/><rect x="1.5" y="3.8" width="12" height="1.2" fill="#6A1B9A"/><circle cx="3.5" cy="6.5" r="1.8" fill="none" stroke="#6A1B9A" stroke-width="1.1"/><circle cx="11.5" cy="6.5" r="1.8" fill="none" stroke="#6A1B9A" stroke-width="1.1"/><rect x="4.5" y="13.3" width="6" height="1.2" fill="#6A1B9A"/></svg>',
    },
    5: {
        "titulo": "5. Dados do Setor \u2014 Pre\u00e7os, Petr\u00f3leo e Mercado",
        "cor": "#00695C",
        "svg": '<svg viewBox="0 0 15 15" width="20" height="20" xmlns="http://www.w3.org/2000/svg"><rect x="1.5" y="6.5" width="3.5" height="5" fill="#00695C"/><rect x="5.5" y="3" width="3.5" height="8.5" fill="#00695C"/><rect x="9.5" y="0.5" width="3.5" height="11" fill="#00695C"/><rect x="1" y="12" width="13" height="0.8" fill="#00695C"/></svg>',
    },
}


def load_logo_b64(logo_path):
    """Le Logo.png e retorna string base64."""
    with open(logo_path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def build_news_html(section_news):
    """Gera o HTML das noticias de uma secao."""
    if not section_news:
        return (
            '<div class="noticia">'
            '<div class="tag">SEM NOTICIAS</div>'
            '<div class="noticia-titulo">Nenhuma publica\u00e7\u00e3o relevante</div>'
            '<div class="noticia-texto">N\u00e3o foram identificadas publica\u00e7\u00f5es relevantes '
            "para esta se\u00e7\u00e3o na data de cobertura.</div>"
            "</div>"
        )
    parts = []
    for n in section_news:
        parts.append(
            f'<div class="noticia">\n'
            f'  <div class="tag">{n["tags"]}</div>\n'
            f'  <div class="noticia-titulo">{n["title"]}</div>\n'
            f'  <div class="noticia-texto">{n["text"]} '
            f'<em>Fonte: {n["source"]} \u2014 {n["date"]}</em></div>\n'
            f"</div>"
        )
    return "\n".join(parts)


def build_sections_html(sections_data):
    """Gera o HTML de todas as 5 secoes."""
    parts = []
    for sec_id in range(1, 6):
        meta = SECOES[sec_id]
        sec_data = next((s for s in sections_data if s["section_id"] == sec_id), None)
        news = sec_data["news"] if sec_data else []
        news_html = build_news_html(news)
        parts.append(
            f'<div class="secao" style="--cor:{meta["cor"]}">\n'
            f'  <div class="secao-header">\n'
            f'    <div class="secao-icon">{meta["svg"]}</div>\n'
            f'    <div class="secao-titulo">{meta["titulo"]}</div>\n'
            f"  </div>\n"
            f"  {news_html}\n"
            f"</div>"
        )
    return "\n\n".join(parts)


def assemble(data, template_html, logo_b64):
    """Substitui placeholders no template com os dados do JSON."""
    highlights_html = "\n".join(
        f"          <li>{h}</li>" for h in data["highlights"]
    )
    sections_html = build_sections_html(data["sections"])

    replacements = {
        "{{HEADER_DATA}}": data["edition_date"],
        "{{COBERTURA_DATA}}": data["coverage_date"],
        "{{FOOTER_DATA}}": data["edition_date"],
        "{{LOGO_B64}}": logo_b64,
        "{{VISAO_EXECUTIVA}}": data["executive_summary"],
        "{{HIGHLIGHTS}}": highlights_html,
        "{{SECOES}}": sections_html,
    }
    html = template_html
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    return html


# ── Validacao (absorve validacao.md) ──────────────────────────────────
def validate(html):
    """Executa todos os checks de validacao. Retorna (ok, resultados)."""
    checks = {
        "Estrutura .page": 'class="page"' in html,
        "CSS Helvetica Neue": "Helvetica Neue" in html,
        "Border-radius 18px": "border-radius:18px" in html,
        "Brand-row presente": 'class="brand-row"' in html,
        "Brand-name AR SOUZA": "AR SOUZA" in html,
        "Slogan Tradicao que evolui": "que evolui" in html,
        "Slogan code tag": 'class="code"' in html,
        "Edition EDICAO e COBERTURA": bool(re.search(r"EDI\u00c7\u00c3O.*COBERTURA", html)),
        "Hero section presente": 'class="hero"' in html,
        "Visao executiva": "executiva" in html.lower(),
        "Destaques do dia": "Destaques do dia" in html,
        "Destaques (5 itens)": (
            len(re.findall(r"<li>", html.split("Destaques do dia")[1].split("</ul>")[0])) == 5
            if "Destaques do dia" in html
            else False
        ),
        "Footer branco (sem #1A3A5C)": "#1A3A5C" not in html,
        "Footer barra gradiente": 'class="footer-bar"' in html,
        "Footer-row presente": 'class="footer-row"' in html,
        "Secao 1 --cor:#1565C0": "--cor:#1565C0" in html,
        "Secao 2 --cor:#2E7D32": "--cor:#2E7D32" in html,
        "Secao 3 --cor:#E65100": "--cor:#E65100" in html,
        "Secao 4 --cor:#6A1B9A": "--cor:#6A1B9A" in html,
        "Secao 5 --cor:#00695C": "--cor:#00695C" in html,
        "Noticias (5-15)": 5 <= len(re.findall(r'class="noticia"', html)) <= 15,
        "Tags = Noticias": len(re.findall(r'class="tag"', html)) == len(re.findall(r'class="noticia"', html)),
        "Logo base64": "base64," in html,
        "Tag pipe format": (
            "|" in re.findall(r'class="tag">(.*?)</div>', html)[0]
            if re.findall(r'class="tag">(.*?)</div>', html)
            else False
        ),
        "Script news-wrap": "news-wrap" in html,
        "div.body wrapper": 'class="body"' in html,
        "Data fonte DD/MM/AAAA": all(
            re.match(r"\d{2}/\d{2}/\d{4}", d)
            for d in re.findall(r"Fonte:.*?(\d{2}/\d{2}/\d{4})", html)
        ),
    }
    all_ok = all(checks.values())
    return all_ok, checks


def main():
    parser = argparse.ArgumentParser(description="Assembler do Boletim Diario AR Souza")
    parser.add_argument("json_path", help="Caminho do JSON com dados das noticias")
    parser.add_argument("--logo", help="Caminho do Logo.png", default=None)
    parser.add_argument("--template", help="Caminho do template.html", default=None)
    parser.add_argument("--output", "-o", help="Caminho de saida do HTML", default=None)
    args = parser.parse_args()

    # Resolver caminhos relativos ao diretorio do script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    template_path = args.template or os.path.join(script_dir, "template.html")
    if not os.path.exists(template_path):
        print(f"ERRO: template nao encontrado: {template_path}", file=sys.stderr)
        sys.exit(1)

    with open(args.json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(template_path, "r", encoding="utf-8") as f:
        template_html = f.read()

    # Logo: argumento > campo no JSON > busca automatica
    logo_path = args.logo or data.get("logo_path")
    if not logo_path:
        # Tentar encontrar Logo.png no mesmo dir do JSON
        json_dir = os.path.dirname(os.path.abspath(args.json_path))
        candidate = os.path.join(json_dir, "Logo.png")
        if os.path.exists(candidate):
            logo_path = candidate

    if logo_path and os.path.exists(logo_path):
        logo_b64 = load_logo_b64(logo_path)
    else:
        print("AVISO: Logo.png nao encontrado. Usando placeholder.", file=sys.stderr)
        logo_b64 = ""

    html = assemble(data, template_html, logo_b64)

    # Determinar caminho de saida
    output_path = args.output or data.get("output_path")
    if not output_path:
        json_dir = os.path.dirname(os.path.abspath(args.json_path))
        edition = data.get("edition_date", "").replace(" ", "_")
        output_path = os.path.join(json_dir, f"ARS_BOLETIM_COMBUSTIVEIS_{edition}.html")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Validacao
    ok, checks = validate(html)
    for name, passed in checks.items():
        status = "OK" if passed else "FAIL"
        print(f"{status} -- {name}")
    print(f"\nRESULTADO: {'APROVADO' if ok else 'REPROVADO'}")
    print(f"Arquivo: {output_path}")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
