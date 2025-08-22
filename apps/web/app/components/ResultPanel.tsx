"use client";
import { fmtCurrency, fmtPercent } from "../lib/format";
import { BACKEND } from "../lib/config";

export default function ResultPanel({ data }: { data: any }) {
  if (!data) return null;

  const tb = data.result?.taxBreakdown || {};
  const credits: any[] = data.result?.credits || [];
  const compliance = data.result?.compliance || { checklist: [] };

  const dl = () => {
    const md = [
      `# Taxely Report`,
      `**Disclaimer:** Hackathon demo. Not tax advice.`,
      ``,
      `## Plan`,
      "```json",
      JSON.stringify(data.plan, null, 2),
      "```",
      `## Company`,
      "```json",
      JSON.stringify(data.company, null, 2),
      "```",
      `## Tax Breakdown`,
      "```json",
      JSON.stringify(data.result?.taxBreakdown, null, 2),
      "```",
      `## Credits`,
      "```json",
      JSON.stringify(data.result?.credits, null, 2),
      "```",
      `## Compliance Checklist`,
      "```json",
      JSON.stringify(data.result?.compliance, null, 2),
      "```",
    ].join("\n");
    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "taxely_report.md";
    a.click();
    URL.revokeObjectURL(url);
  };

  async function postPdf(endpoint: string, payload: any, filename: string) {
    const res = await fetch(`${BACKEND}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const txt = await res.text();
      throw new Error(txt || `PDF request failed (${res.status})`);
    }
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  const openCt600 = async () => {
    const pdfData = {
      company_name: data.input?.companyName || "N/A",
      period_start: `${data.input?.accountingYear}-01-01`,
      period_end: `${data.input?.accountingYear}-12-31`,
      taxable_income: Number(
        tb.profit_after_rd ??
          tb.profit_after_capex ??
          tb.profit_before_capex ??
          0
      ),
      corporation_tax_rate: Math.round((tb.rate_normal ?? 0) * 100 * 100) / 100,
      corp_tax_due: Number(tb.total_tax ?? 0),
    };
    await postPdf("/api/pdf/ct600", { pdfData }, "CT600.pdf");
  };

  const openRd = async () => {
    const pdfData = {
      company_name: data.input?.companyName || "N/A",
      period_start: `${data.input?.accountingYear}-01-01`,
      period_end: `${data.input?.accountingYear}-12-31`,
      rd_expenditure: Number(data.input?.rAndDSpendGBP ?? 0),
      rd_relief: Number(tb.rd_extra_deduction ?? 0),
      rd_credit: 0,
    };
    await postPdf("/api/pdf/rd", { pdfData }, "CT600L_R&D.pdf");
  };

  return (
    <div className="card">
      <div className="grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
        <div>
          <h2>Tax breakdown</h2>
          <div className="kv">
            <div>Profit before CapEx</div>
            <div>{fmtCurrency(tb.profit_before_capex)}</div>
            <div>CapEx Adjusted Profit</div>
            <div>{fmtCurrency(tb.profit_after_capex)}</div>
            <div>Normal Rate</div>
            <div>{fmtPercent(tb.rate_normal)}</div>
            <div>Patent Slice</div>
            <div>{fmtCurrency(tb.patent_slice)}</div>
            <div>Normal Slice</div>
            <div>{fmtCurrency(tb.normal_slice)}</div>
            <div>Tax on Patent Slice</div>
            <div>{fmtCurrency(tb.tax_patent)}</div>
            <div>Tax on Normal Slice</div>
            <div>{fmtCurrency(tb.tax_normal)}</div>
            <div style={{ fontWeight: 700 }}>Total Tax</div>
            <div style={{ fontWeight: 700 }}>{fmtCurrency(tb.total_tax)}</div>
          </div>
        </div>
        <div>
          <h2>Eligible credits</h2>
          {credits.length === 0 ? (
            <div className="help">No credits suggested for this input.</div>
          ) : (
            <ul className="clean">
              {credits.map((c, i) => (
                <li
                  key={i}
                  style={{
                    padding: "8px 0",
                    borderBottom: "1px dashed #203043",
                  }}
                >
                  <div style={{ fontWeight: 600 }}>{c.title}</div>
                  <div className="help">{c.note}</div>
                  <div className="help">Est. treatment: {c.estBenefit}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      <div className="section">
        <h2>Compliance checklist</h2>
        <ul className="clean">
          {compliance.checklist?.map((it: any, i: number) => (
            <li key={i} style={{ padding: "6px 0" }}>
              {it.required ? "✅" : "⬜"} {it.label}
            </li>
          ))}
        </ul>
        <div className="help" style={{ marginTop: 8 }}>
          {compliance.disclaimer}
        </div>
      </div>

      <div className="section">
        <h2>Execution trace</h2>
        <pre style={{ whiteSpace: "pre-wrap" }}>
          {JSON.stringify(data.plan, null, 2)}
        </pre>
      </div>

      <div style={{ display: "flex", gap: 12, marginTop: 8, flexWrap: "wrap" }}>
        <button onClick={dl}>Download Markdown</button>
        <button onClick={openCt600}>Download CT600</button>
        <button onClick={openRd}>Download R&D Schedule</button>
      </div>
    </div>
  );
}
