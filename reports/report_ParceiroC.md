# Análise de Teste A/B — Parceiro C

**Arquivo:** `dataset_03_parceiroC.csv`  
**Período:** 01/07/2011 a 14/08/2011 (45 dias)  
**Grupos testados:** Grupo 1, Grupo 2  
**Análise gerada em:** 16/06/2026 16:53

---

## 1. Métricas Consolidadas por Grupo

| Grupo | Compradores | GMV Total | Comissão | Cashback | Margem Líquida | Taxa Cashback | Taxa Margem | GMV/Comprador |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Grupo 1 | 4,549 | R$ 1.738.460 | R$ 121.693 | R$ 86.924 | R$ 34.769 | 5.00% | 2.00% | R$ 382 |
| Grupo 2 | 4,522 | R$ 1.685.235 | R$ 117.967 | R$ 117.967 | R$ 0 | 7.00% | 0.00% | R$ 373 |

---

## 2. Significância Estatística

> Métrica base: **margem líquida diária** por grupo.  
> Teste: **t de Welch** (bilateral).  
> Nível de significância: **α = 0,05**.

| Comparação | Δ Margem (%) | p-value | Sig.? | IC 95% (margem diária) |
|---|---:|---:|:---:|---|
| Grupo 1 vs Grupo 2 | -100.0% | 0.0000 | ✅ Sim | [R$ -832 ; R$ -713] |

---

## 3. Análise de Trade-offs

### Grupo 2 vs Grupo 1 (controle)
- Δ Margem líquida: **-100.0%**
- Δ GMV: -3.1%
- Δ Compradores: -0.6%
- Taxa de cashback: 7.00% (controle: 5.00%)

---

## 4. Decisão

### ▶ Escalar para 100% do tráfego: **Grupo 1**

Grupo 2 é estatisticamente diferente, mas com margem inferior ao controle. Manter Grupo 1.

---

## 5. Ressalvas e Limitações

- A análise assume que os grupos foram formados de forma aleatória e que não houve contaminação entre eles.
- Os dados não contêm informação sobre a taxa de cashback de cada variante (apenas o valor pago); inferências sobre o percentual de cashback partem do ratio `cashback / GMV`.
- Testes com menos de 30 dias ou com poucos compradores por grupo têm poder estatístico reduzido.
- Efeitos sazonais não foram controlados — validar se o período do teste é representativo do comportamento médio do parceiro.