#!/usr/bin/env python3
"""
Solução reutilizável de análise de testes A/B — Méliuz Growth Team.

Uso:
    python analyze_ab_test.py <arquivo.csv>
    python analyze_ab_test.py <arquivo.csv> --output reports/meu_relatorio.md
    python analyze_ab_test.py <arquivo.csv> --tracking minha_planilha.csv
"""

import argparse
import csv
import os
import sys
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_currency(value: str) -> float:
    """Converte 'R$ 10.273' → 10273.0"""
    return float(value.replace("R$", "").replace(".", "").replace(",", ".").strip())


def load_dataset(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    df.columns = [c.strip() for c in df.columns]
    df["Data"] = pd.to_datetime(df["Data"])
    for col in ["comissão", "cashback", "vendas totais"]:
        df[col] = df[col].apply(parse_currency)
    df["compradores"] = df["compradores"].astype(int)
    df["margem_liquida"] = df["comissão"] - df["cashback"]
    df["taxa_cashback"] = df["cashback"] / df["vendas totais"]
    df["taxa_margem"] = df["margem_liquida"] / df["vendas totais"]
    df["gmv_por_comprador"] = df["vendas totais"] / df["compradores"]
    return df


# ---------------------------------------------------------------------------
# Métricas agregadas por grupo
# ---------------------------------------------------------------------------

def compute_group_metrics(df: pd.DataFrame) -> pd.DataFrame:
    agg = df.groupby("Grupos de usuários").agg(
        compradores_total=("compradores", "sum"),
        gmv_total=("vendas totais", "sum"),
        comissao_total=("comissão", "sum"),
        cashback_total=("cashback", "sum"),
        margem_total=("margem_liquida", "sum"),
        dias=("Data", "count"),
    ).reset_index()
    agg["taxa_cashback_pct"] = agg["cashback_total"] / agg["gmv_total"] * 100
    agg["taxa_margem_pct"] = agg["margem_total"] / agg["gmv_total"] * 100
    agg["gmv_por_comprador"] = agg["gmv_total"] / agg["compradores_total"]
    agg["margem_por_comprador"] = agg["margem_total"] / agg["compradores_total"]
    return agg.set_index("Grupos de usuários")


# ---------------------------------------------------------------------------
# Testes estatísticos
# ---------------------------------------------------------------------------

def stat_test(control_series: pd.Series, variant_series: pd.Series):
    """t-test de Welch na série diária. Retorna (statistic, p_value, ci_lower, ci_upper)."""
    t_stat, p_value = stats.ttest_ind(variant_series, control_series, equal_var=False)
    diff_mean = variant_series.mean() - control_series.mean()
    se = np.sqrt(variant_series.std(ddof=1)**2 / len(variant_series) +
                 control_series.std(ddof=1)**2 / len(control_series))
    df_dof = len(variant_series) + len(control_series) - 2
    t_crit = stats.t.ppf(0.975, df=df_dof)
    ci_lower = diff_mean - t_crit * se
    ci_upper = diff_mean + t_crit * se
    return t_stat, p_value, ci_lower, ci_upper


def run_statistical_tests(df: pd.DataFrame, grupos: list, control: str = "Grupo 1") -> dict:
    results = {}
    control_series = df[df["Grupos de usuários"] == control]["margem_liquida"]
    for grupo in grupos:
        if grupo == control:
            continue
        variant_series = df[df["Grupos de usuários"] == grupo]["margem_liquida"]
        t_stat, p_value, ci_lower, ci_upper = stat_test(control_series, variant_series)
        diff_pct = (variant_series.mean() - control_series.mean()) / control_series.mean() * 100
        results[grupo] = {
            "t_stat": t_stat,
            "p_value": p_value,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "diff_pct": diff_pct,
            "significativo": p_value < 0.05,
        }
    return results


# ---------------------------------------------------------------------------
# Framework de decisão
# ---------------------------------------------------------------------------

def decide_winner(metrics: pd.DataFrame, stat_results: dict, control: str = "Grupo 1") -> tuple:
    """
    Retorna (vencedor, justificativa, detalhes_decisao).
    Critério primário: margem líquida total. Critério de desempate: GMV total.
    """
    variantes_sig = {g: r for g, r in stat_results.items() if r["significativo"]}

    if not variantes_sig:
        return (
            control,
            "Nenhuma variante apresentou diferença estatisticamente significativa (p < 0.05) "
            "em relação ao controle. Recomenda-se manter o Grupo 1 (controle).",
            "sem_significancia",
        )

    # Entre as variantes significativas, escolhe a de maior margem total
    best = max(variantes_sig.keys(), key=lambda g: metrics.loc[g, "margem_total"])
    best_r = stat_results[best]

    margem_melhor = metrics.loc[best, "margem_total"]
    margem_ctrl = metrics.loc[control, "margem_total"]
    gmv_melhor = metrics.loc[best, "gmv_total"]
    gmv_ctrl = metrics.loc[control, "gmv_total"]

    if margem_melhor > margem_ctrl:
        if gmv_melhor >= gmv_ctrl * 0.95:
            justificativa = (
                f"{best} apresenta margem líquida {best_r['diff_pct']:+.1f}% superior ao controle "
                f"(p={best_r['p_value']:.4f}) sem perda relevante de GMV. Escalar com confiança."
            )
            tipo = "escalar_com_confianca"
        else:
            queda_gmv = (gmv_melhor / gmv_ctrl - 1) * 100
            justificativa = (
                f"{best} melhora a margem em {best_r['diff_pct']:+.1f}% (p={best_r['p_value']:.4f}), "
                f"porém o GMV cai {queda_gmv:.1f}%. Avaliar trade-off antes de escalar."
            )
            tipo = "escalar_com_ressalva"
    else:
        justificativa = (
            f"{best} é estatisticamente diferente, mas com margem inferior ao controle. "
            f"Manter {control}."
        )
        best = control
        tipo = "manter_controle"

    return best, justificativa, tipo


# ---------------------------------------------------------------------------
# Geração do relatório Markdown
# ---------------------------------------------------------------------------

def fmt_brl(value: float) -> str:
    return f"R$ {value:,.0f}".replace(",", ".")


def generate_report(
    df: pd.DataFrame,
    metrics: pd.DataFrame,
    stat_results: dict,
    vencedor: str,
    justificativa: str,
    filepath: str,
) -> str:
    parceiro = df["Parceiro"].iloc[0]
    data_inicio = df["Data"].min().strftime("%d/%m/%Y")
    data_fim = df["Data"].max().strftime("%d/%m/%Y")
    grupos = sorted(df["Grupos de usuários"].unique())
    n_dias = (df["Data"].max() - df["Data"].min()).days + 1

    linhas = []
    linhas.append(f"# Análise de Teste A/B — {parceiro}")
    linhas.append(f"\n**Arquivo:** `{Path(filepath).name}`  ")
    linhas.append(f"**Período:** {data_inicio} a {data_fim} ({n_dias} dias)  ")
    linhas.append(f"**Grupos testados:** {', '.join(grupos)}  ")
    linhas.append(f"**Análise gerada em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

    linhas.append("---\n")
    linhas.append("## 1. Métricas Consolidadas por Grupo\n")
    linhas.append(
        "| Grupo | Compradores | GMV Total | Comissão | Cashback | Margem Líquida | "
        "Taxa Cashback | Taxa Margem | GMV/Comprador |"
    )
    linhas.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for grupo in grupos:
        m = metrics.loc[grupo]
        linhas.append(
            f"| {grupo} "
            f"| {int(m['compradores_total']):,} "
            f"| {fmt_brl(m['gmv_total'])} "
            f"| {fmt_brl(m['comissao_total'])} "
            f"| {fmt_brl(m['cashback_total'])} "
            f"| {fmt_brl(m['margem_total'])} "
            f"| {m['taxa_cashback_pct']:.2f}% "
            f"| {m['taxa_margem_pct']:.2f}% "
            f"| {fmt_brl(m['gmv_por_comprador'])} |"
        )

    linhas.append("\n---\n")
    linhas.append("## 2. Significância Estatística\n")
    linhas.append(
        "> Métrica base: **margem líquida diária** por grupo.  \n"
        "> Teste: **t de Welch** (bilateral).  \n"
        "> Nível de significância: **α = 0,05**.\n"
    )
    if stat_results:
        linhas.append("| Comparação | Δ Margem (%) | p-value | Sig.? | IC 95% (margem diária) |")
        linhas.append("|---|---:|---:|:---:|---|")
        for grupo, r in stat_results.items():
            sig_label = "✅ Sim" if r["significativo"] else "❌ Não"
            linhas.append(
                f"| Grupo 1 vs {grupo} "
                f"| {r['diff_pct']:+.1f}% "
                f"| {r['p_value']:.4f} "
                f"| {sig_label} "
                f"| [{fmt_brl(r['ci_lower'])} ; {fmt_brl(r['ci_upper'])}] |"
            )
    else:
        linhas.append("_Apenas um grupo presente — sem comparação estatística._\n")

    linhas.append("\n---\n")
    linhas.append("## 3. Análise de Trade-offs\n")
    ctrl = "Grupo 1"
    ctrl_m = metrics.loc[ctrl] if ctrl in metrics.index else None
    for grupo in grupos:
        if grupo == ctrl or ctrl_m is None:
            continue
        m = metrics.loc[grupo]
        delta_margem = (m["margem_total"] / ctrl_m["margem_total"] - 1) * 100
        delta_gmv = (m["gmv_total"] / ctrl_m["gmv_total"] - 1) * 100
        delta_comp = (m["compradores_total"] / ctrl_m["compradores_total"] - 1) * 100
        linhas.append(f"### {grupo} vs Grupo 1 (controle)")
        linhas.append(f"- Δ Margem líquida: **{delta_margem:+.1f}%**")
        linhas.append(f"- Δ GMV: {delta_gmv:+.1f}%")
        linhas.append(f"- Δ Compradores: {delta_comp:+.1f}%")
        linhas.append(f"- Taxa de cashback: {m['taxa_cashback_pct']:.2f}% (controle: {ctrl_m['taxa_cashback_pct']:.2f}%)\n")

    linhas.append("---\n")
    linhas.append("## 4. Decisão\n")
    linhas.append(f"### ▶ Escalar para 100% do tráfego: **{vencedor}**\n")
    linhas.append(f"{justificativa}\n")

    linhas.append("---\n")
    linhas.append("## 5. Ressalvas e Limitações\n")
    linhas.append("- A análise assume que os grupos foram formados de forma aleatória e que não houve contaminação entre eles.")
    linhas.append("- Os dados não contêm informação sobre a taxa de cashback de cada variante (apenas o valor pago); inferências sobre o percentual de cashback partem do ratio `cashback / GMV`.")
    linhas.append("- Testes com menos de 30 dias ou com poucos compradores por grupo têm poder estatístico reduzido.")
    linhas.append("- Efeitos sazonais não foram controlados — validar se o período do teste é representativo do comportamento médio do parceiro.")

    report = "\n".join(linhas)
    return report


# ---------------------------------------------------------------------------
# Registro no tracking CSV
# ---------------------------------------------------------------------------

TRACKING_COLS = [
    "nome_teste", "parceiro", "periodo_inicio", "periodo_fim",
    "grupos", "vencedor", "decisao", "p_value_melhor_variante",
    "diferenca_margem_pct", "data_analise",
]


def append_tracking(df: pd.DataFrame, metrics: pd.DataFrame, stat_results: dict,
                    vencedor: str, tipo_decisao: str, tracking_path: str):
    parceiro = df["Parceiro"].iloc[0]
    data_inicio = df["Data"].min().strftime("%Y-%m-%d")
    data_fim = df["Data"].max().strftime("%Y-%m-%d")
    grupos = ", ".join(sorted(df["Grupos de usuários"].unique()))
    nome_teste = f"Teste {parceiro} ({data_inicio} a {data_fim})"

    best_p = ""
    best_diff = ""
    if stat_results:
        sig = {g: r for g, r in stat_results.items() if r["significativo"]}
        if sig:
            best_g = max(sig, key=lambda g: stat_results[g]["diff_pct"])
            best_p = f"{stat_results[best_g]['p_value']:.4f}"
            best_diff = f"{stat_results[best_g]['diff_pct']:+.1f}%"

    row = {
        "nome_teste": nome_teste,
        "parceiro": parceiro,
        "periodo_inicio": data_inicio,
        "periodo_fim": data_fim,
        "grupos": grupos,
        "vencedor": vencedor,
        "decisao": tipo_decisao,
        "p_value_melhor_variante": best_p,
        "diferenca_margem_pct": best_diff,
        "data_analise": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    file_exists = Path(tracking_path).exists()
    with open(tracking_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TRACKING_COLS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    print(f"[OK] Registro adicionado em: {tracking_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Análise de teste A/B — Méliuz Growth")
    parser.add_argument("file", help="Caminho para o arquivo CSV do teste")
    parser.add_argument("--output", help="Caminho para salvar o relatório markdown")
    parser.add_argument(
        "--tracking",
        default="tracking_results.csv",
        help="Caminho para a planilha de acompanhamento (CSV)",
    )
    args = parser.parse_args()

    if not Path(args.file).exists():
        print(f"Erro: arquivo '{args.file}' não encontrado.", file=sys.stderr)
        sys.exit(1)

    print(f"\n[ANALISE] Carregando dataset: {args.file}")
    df = load_dataset(args.file)

    parceiro = df["Parceiro"].iloc[0].replace(" ", "")
    grupos = sorted(df["Grupos de usuários"].unique())
    print(f"   Parceiro: {df['Parceiro'].iloc[0]}")
    print(f"   Periodo: {df['Data'].min().date()} a {df['Data'].max().date()}")
    print(f"   Grupos: {grupos}")

    print("\n[METRICAS] Calculando metricas por grupo...")
    metrics = compute_group_metrics(df)

    print("[STATS] Rodando testes estatisticos...")
    stat_results = run_statistical_tests(df, grupos) if len(grupos) > 1 else {}

    print("[DECISAO] Aplicando framework de decisao...")
    vencedor, justificativa, tipo_decisao = decide_winner(metrics, stat_results)

    # Determinar caminho do relatório
    if args.output:
        output_path = args.output
    else:
        Path("reports").mkdir(exist_ok=True)
        output_path = f"reports/report_{parceiro}.md"

    print(f"\n[RELATORIO] Gerando relatorio em: {output_path}")
    report = generate_report(df, metrics, stat_results, vencedor, justificativa, args.file)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"[OK] Relatorio salvo: {output_path}")

    print(f"\n[TRACKING] Registrando em: {args.tracking}")
    append_tracking(df, metrics, stat_results, vencedor, tipo_decisao, args.tracking)

    print("\n" + "=" * 60)
    print(f"DECISAO: Escalar -> {vencedor}")
    print(f"MOTIVO:  {justificativa}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
