# Análise de Teste A/B — Parceiro A

**Arquivo:** `dataset_01_parceiroA.csv`  
**Período:** 01/01/2011 a 02/04/2011 (92 dias)  
**Grupos testados:** Grupo 1, Grupo 2, Grupo 3  
**Análise gerada em:** 16/06/2026 16:53

---

## 1. Métricas Consolidadas por Grupo

| Grupo | Compradores | GMV Total | Comissão | Cashback | Margem Líquida | Taxa Cashback | Taxa Margem | GMV/Comprador |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Grupo 1 | 9,633 | R$ 5.605.173 | R$ 638.135 | R$ 233.424 | R$ 404.711 | 4.16% | 7.22% | R$ 582 |
| Grupo 2 | 10,814 | R$ 6.423.096 | R$ 728.178 | R$ 370.659 | R$ 357.519 | 5.77% | 5.57% | R$ 594 |
| Grupo 3 | 11,410 | R$ 6.785.856 | R$ 767.887 | R$ 503.600 | R$ 264.287 | 7.42% | 3.89% | R$ 595 |

---

## 2. Significância Estatística

> Métrica base: **margem líquida diária** por grupo.  
> Teste: **t de Welch** (bilateral).  
> Nível de significância: **α = 0,05**.

| Comparação | Δ Margem (%) | p-value | Sig.? | IC 95% (margem diária) |
|---|---:|---:|:---:|---|
| Grupo 1 vs Grupo 2 | -11.7% | 0.1315 | ❌ Não | [R$ -1.181 ; R$ 155] |
| Grupo 1 vs Grupo 3 | -34.7% | 0.0000 | ✅ Sim | [R$ -2.113 ; R$ -939] |

---

## 3. Análise de Trade-offs

### Grupo 2 vs Grupo 1 (controle)
- Δ Margem líquida: **-11.7%**
- Δ GMV: +14.6%
- Δ Compradores: +12.3%
- Taxa de cashback: 5.77% (controle: 4.16%)

### Grupo 3 vs Grupo 1 (controle)
- Δ Margem líquida: **-34.7%**
- Δ GMV: +21.1%
- Δ Compradores: +18.4%
- Taxa de cashback: 7.42% (controle: 4.16%)

---

## 4. Decisão

### ▶ Escalar para 100% do tráfego: **Grupo 1**

Grupo 3 é estatisticamente diferente, mas com margem inferior ao controle. Manter Grupo 1.

---

## 5. Ressalvas e Limitações

- A análise assume que os grupos foram formados de forma aleatória e que não houve contaminação entre eles.
- Os dados não contêm informação sobre a taxa de cashback de cada variante (apenas o valor pago); inferências sobre o percentual de cashback partem do ratio `cashback / GMV`.
- Testes com menos de 30 dias ou com poucos compradores por grupo têm poder estatístico reduzido.
- Efeitos sazonais não foram controlados — validar se o período do teste é representativo do comportamento médio do parceiro.