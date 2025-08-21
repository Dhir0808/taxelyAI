export function fmtCurrency(value: number | null | undefined, currency: string = "GBP"): string {
  const n = typeof value === "number" ? value : 0;
  return new Intl.NumberFormat("en-GB", { style: "currency", currency, maximumFractionDigits: 0 }).format(n);
}

export function fmtNumber(value: number | null | undefined): string {
  const n = typeof value === "number" ? value : 0;
  return new Intl.NumberFormat("en-GB").format(n);
}

export function fmtPercent(value: number | null | undefined): string {
  const n = typeof value === "number" ? value : 0;
  return `${(n * 100).toFixed(1)}%`;
}
