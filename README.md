# Solução de Análise A/B — Méliuz Growth

Solução reutilizável para analisar testes A/B de cashback e retornar uma decisão acionável sobre qual variante escalar para 100% do tráfego.

---

## Estrutura do repositório

```
.
├── analyze_ab_test.py      # Script principal de análise
├── prompt_system.md        # System prompt para uso via IA (Claude Code, Cursor, GPT)
├── requirements.txt        # Dependências Python
├── README.md               # Este arquivo
├── tracking_results.csv    # Planilha de acompanhamento (gerada automaticamente)
├── reports/
│   ├── report_ParceiroA.md
│   ├── report_ParceiroB.md
│   └── report_ParceiroC.md
├── dataset_01_parceiroA.csv
├── dataset_02_parceiroB.csv
└── dataset_03_parceiroC.csv
```

---

## Pré-requisitos

- Python 3.8+
- pip

---

## Instalação

```bash
pip install -r requirements.txt
```

---

## Uso via linha de comando

```bash
# Análise básica (relatório salvo em reports/ automaticamente)
python analyze_ab_test.py dataset_01_parceiroA.csv

# Com caminhos customizados
python analyze_ab_test.py dataset_02_parceiroB.csv \
    --output reports/relatorio_B.md \
    --tracking tracking_results.csv
```

A **mesma solução** funciona para qualquer dataset novo — basta indicar o arquivo:

```bash
python analyze_ab_test.py dataset_04_parceiroD.csv
```

---

## Uso via IA (Claude Code, Cursor, ChatGPT)

1. Abra sua ferramenta de IA preferida com este repositório como contexto
2. Carregue o arquivo `prompt_system.md` como system prompt (ou cole o conteúdo no início da conversa)
3. Peça em linguagem natural:

> "Analise o arquivo `dataset_01_parceiroA.csv` e me diga qual variante devo escalar."

A IA vai executar o script, ler o relatório gerado e apresentar a análise completa com a decisão acionável.

---

## O que o script entrega

Para cada teste analisado:

| Output | Descrição |
|---|---|
| Relatório markdown | Métricas por grupo, testes estatísticos, trade-offs e decisão |
| Linha no tracking CSV | Registro persistente do teste na planilha de acompanhamento |
| Decisão impressa no terminal | Resposta direta: qual grupo escalar e por quê |

### Métricas calculadas

- GMV total e por comprador
- Comissão e cashback totais
- **Margem líquida** (comissão − cashback)
- Taxa de cashback e taxa de margem sobre GMV
- Teste t de Welch (significância estatística, α = 0,05)
- Intervalo de confiança 95% para a diferença de margem

---

## Planilha de acompanhamento

O arquivo `tracking_results.csv` é criado automaticamente e acumulado a cada análise.

| Campo | Descrição |
|---|---|
| nome_teste | Identificação automática do teste |
| parceiro | Parceiro analisado |
| periodo_inicio / fim | Datas do teste |
| grupos | Variantes testadas |
| vencedor | Grupo recomendado para escalar |
| decisao | Tipo da decisão (ver abaixo) |
| p_value_melhor_variante | Significância da melhor variante |
| diferenca_margem_pct | Δ% de margem vs controle |
| data_analise | Timestamp da análise |

**Tipos de decisão:**
- `escalar_com_confianca` — variante significativamente melhor, sem perda de volume
- `escalar_com_ressalva` — variante melhor em margem, mas com queda de GMV
- `manter_controle` — nenhuma variante supera o controle
- `sem_significancia` — diferenças não são estatisticamente significativas

---

## Lógica de decisão

```
1. Calcular margem líquida diária por grupo (comissão − cashback)
2. Rodar teste t de Welch entre cada variante e o Grupo 1 (controle)
3. Se nenhuma variante é significativa (p ≥ 0,05) → manter controle
4. Entre as variantes significativas, selecionar a de maior margem total
5. Se margem melhor E GMV estável (queda < 5%) → escalar com confiança
6. Se margem melhor MAS GMV cai > 5% → escalar com ressalva (avaliar trade-off)
```

---

## Link da planilha de acompanhamento

> [Meliuz - Acompanhamento de Testes A/B](https://docs.google.com/spreadsheets/d/1b3QabqrZB1wYtq-87CvVsOCPedl8WLy-Q2qj1oS5YGI) — acesso público de leitura
