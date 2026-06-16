# Análise de Teste A/B — Parceiro B

**Arquivo:** `dataset_02_parceiroB.csv`  
**Período:** 01/05/2011 a 30/06/2011 (61 dias)  
**Grupos testados:** Grupo 1, Grupo 2, Grupo 3  
**Análise gerada em:** 16/06/2026 16:53

---

## 1. Métricas Consolidadas por Grupo

| Grupo | Compradores | GMV Total | Comissão | Cashback | Margem Líquida | Taxa Cashback | Taxa Margem | GMV/Comprador |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Grupo 1 | 7,990 | R$ 4.093.818 | R$ 450.321 | R$ 163.751 | R$ 286.570 | 4.00% | 7.00% | R$ 512 |
| Grupo 2 | 5,452 | R$ 2.863.019 | R$ 314.935 | R$ 171.778 | R$ 143.157 | 6.00% | 5.00% | R$ 525 |
| Grupo 3 | 5,029 | R$ 2.629.963 | R$ 289.290 | R$ 236.697 | R$ 52.593 | 9.00% | 2.00% | R$ 523 |

---

## 2. Significância Estatística

> Métrica base: **margem líquida diária** por grupo.  
> Teste: **t de Welch** (bilateral).  
> Nível de significância: **α = 0,05**.

| Comparação | Δ Margem (%) | p-value | Sig.? | IC 95% (margem diária) |
|---|---:|---:|:---:|---|
| Grupo 1 vs Grupo 2 | -50.0% | 0.0000 | ✅ Sim | [R$ -2.906 ; R$ -1.796] |
| Grupo 1 vs Grupo 3 | -81.6% | 0.0000 | ✅ Sim | [R$ -4.328 ; R$ -3.344] |

---

## 3. Análise de Trade-offs

### Grupo 2 vs Grupo 1 (controle)
- Δ Margem líquida: **-50.0%**
- Δ GMV: -30.1%
- Δ Compradores: -31.8%
- Taxa de cashback: 6.00% (controle: 4.00%)

### Grupo 3 vs Grupo 1 (controle)
- Δ Margem líquida: **-81.6%**
- Δ GMV: -35.8%
- Δ Compradores: -37.1%
- Taxa de cashback: 9.00% (controle: 4.00%)

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