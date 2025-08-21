"use client";
import { useEffect, useState } from "react";
import type { CompanyInput } from "../lib/schema";

export default function InputForm({
  onRun,
  prefill,
}: {
  onRun: (data: any) => void;
  prefill?: Partial<CompanyInput>;
}) {
  const [form, setForm] = useState<CompanyInput>({
    accountingYear: 2024,
    revenueGBP: 20000000,
    expensesGBP: 14000000,
    rAndDSpendGBP: 3000000,
    patentRevenueGBP: 5000000,
    capexGBP: 1000000,
    companyNumber: "01234567",
    applyCredits: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [applied, setApplied] = useState(false);

  useEffect(() => {
    if (!prefill) return;
    setForm((f) => ({
      ...f,
      // Only merge known keys; attempt numeric conversion when appropriate
      revenueGBP:
        prefill.revenueGBP !== undefined
          ? Number(prefill.revenueGBP)
          : f.revenueGBP,
      expensesGBP:
        prefill.expensesGBP !== undefined
          ? Number(prefill.expensesGBP)
          : f.expensesGBP,
      rAndDSpendGBP:
        prefill.rAndDSpendGBP !== undefined
          ? Number(prefill.rAndDSpendGBP)
          : f.rAndDSpendGBP,
      capexGBP:
        prefill.capexGBP !== undefined ? Number(prefill.capexGBP) : f.capexGBP,
      patentRevenueGBP:
        prefill.patentRevenueGBP !== undefined
          ? Number(prefill.patentRevenueGBP)
          : f.patentRevenueGBP,
      companyNumber: prefill.companyNumber ?? f.companyNumber,
      companyName: prefill.companyName ?? f.companyName,
    }));
    setApplied(true);
    const t = setTimeout(() => setApplied(false), 2500);
    return () => clearTimeout(t);
  }, [prefill]);

  const submit = async () => {
    setError(null);
    if (!form.companyNumber && !form.companyName) {
      setError("Enter a UK company number or a name to search.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(
        process.env.NEXT_PUBLIC_AGENT_URL ?? "http://localhost:8000/api/run",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(form),
        }
      );
      const data = await res.json();
      onRun(data);
    } catch (e: any) {
      setError("Request failed. Please retry.");
    } finally {
      setLoading(false);
    }
  };

  const onChange = (k: keyof CompanyInput, v: any) =>
    setForm((f) => ({ ...f, [k]: v }));

  return (
    <div id="run" className="card">
      <h2>Run Taxely</h2>
      <div className="help" style={{ marginBottom: 8 }}>
        Enter high-level financials for the year. We’ll fetch public company
        info and compute a simplified UK corporation tax estimate with credits
        and compliance checklist.
      </div>
      {applied && (
        <div className="help" style={{ color: "#ffb14d" }}>
          Imported values applied.
        </div>
      )}
      {error && (
        <div
          className="card"
          style={{ background: "#1a0f12", borderColor: "#5a2633" }}
        >
          {error}
        </div>
      )}
      <div className="grid" style={{ gridTemplateColumns: "1fr 1fr" }}>
        <div className="grid">
          <label>
            Company Number
            <input
              value={form.companyNumber || ""}
              onChange={(e) => onChange("companyNumber", e.target.value)}
              placeholder="01234567"
            />
            <div className="help">Or provide a name instead.</div>
          </label>
          <label>
            Company Name
            <input
              value={form.companyName || ""}
              onChange={(e) => onChange("companyName", e.target.value)}
              placeholder="ACME TECH LTD"
            />
          </label>
          <label>
            Accounting Year
            <input
              type="number"
              value={form.accountingYear}
              onChange={(e) =>
                onChange("accountingYear", Number(e.target.value))
              }
            />
          </label>
          <label>
            Revenue (GBP)
            <input
              type="number"
              value={form.revenueGBP}
              onChange={(e) => onChange("revenueGBP", Number(e.target.value))}
            />
          </label>
          <label>
            Expenses (GBP)
            <input
              type="number"
              value={form.expensesGBP}
              onChange={(e) => onChange("expensesGBP", Number(e.target.value))}
            />
          </label>
        </div>
        <div className="grid">
          <label>
            R&D Spend (GBP)
            <input
              type="number"
              value={form.rAndDSpendGBP || 0}
              onChange={(e) =>
                onChange("rAndDSpendGBP", Number(e.target.value))
              }
            />
            <div className="help">Potential SME R&D relief if eligible.</div>
          </label>
          <label>
            Patent Revenue (GBP)
            <input
              type="number"
              value={form.patentRevenueGBP || 0}
              onChange={(e) =>
                onChange("patentRevenueGBP", Number(e.target.value))
              }
            />
            <div className="help">Patent Box applies 10% on this slice.</div>
          </label>
          <label>
            CapEx (GBP)
            <input
              type="number"
              value={form.capexGBP || 0}
              onChange={(e) => onChange("capexGBP", Number(e.target.value))}
            />
            <div className="help">AIA first-year deduction in demo.</div>
          </label>
          <label>
            Apply Credits?
            <select
              value={form.applyCredits ? "yes" : "no"}
              onChange={(e) =>
                onChange("applyCredits", e.target.value === "yes")
              }
            >
              <option value="yes">Yes (HITL confirm)</option>
              <option value="no">No</option>
            </select>
          </label>
        </div>
      </div>
      <div style={{ display: "flex", gap: 12, marginTop: 10 }}>
        <button onClick={submit} disabled={loading}>
          {loading ? "Running…" : "Run Taxely"}
        </button>
      </div>
    </div>
  );
}
