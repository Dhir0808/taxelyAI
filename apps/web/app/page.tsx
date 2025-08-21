"use client";
import { useState } from "react";
import InputForm from "./components/InputForm";
import ResultPanel from "./components/ResultPanel";
import ImportSheetCard from "./components/ImportSheetCard";

export default function Page() {
  const [data, setData] = useState<any>(null);
  const [imported, setImported] = useState<Record<string, any> | null>(null);
  return (
    <>
      <section className="hero" id="top">
        <div>
          <h1>Taxely — UK Corporation Tax Copilot</h1>
          <p>
            Plan credits, estimate tax, and prepare a compliance checklist for
            UK companies. Uses OpenCorporates + an offline UK tax knowledge
            base. Free demo, not tax advice.
          </p>
          <div className="help">
            • Companies: public data lookup. • Tax: simplified marginal relief
            between 19% and 25%. • Credits: SME R&D, AIA, Patent Box.
          </div>
        </div>
        <div className="card">
          <h2>At a glance</h2>
          <ul className="clean">
            <li>Live company lookup with mock fallback</li>
            <li>Transparent step-by-step execution trace</li>
            <li>Downloadable Markdown report</li>
          </ul>
        </div>
      </section>

      <section className="section">
        <ImportSheetCard onImported={(parsed) => setImported(parsed)} />
      </section>

      <section id="what" className="section card">
        <h2>What is Taxely?</h2>
        <p className="help" style={{ marginTop: 8 }}>
          Taxely is a multi-agent planning demo that evaluates a UK company’s
          corporation tax using simplified, illustrative rules and suggests
          credits. It returns a breakdown and a compliance checklist to guide
          filings.
        </p>
      </section>

      <section id="how" className="section card">
        <h2>How it works</h2>
        <ol className="clean" style={{ listStyle: "decimal inside" }}>
          <li>Compute profit and fetch company details.</li>
          <li>Estimate corporation tax (marginal relief approximation).</li>
          <li>Suggest credits (R&D, AIA, Patent Box).</li>
          <li>Confirm credits (human-in-the-loop) and build checklist.</li>
        </ol>
      </section>

      <InputForm onRun={setData} prefill={imported || undefined} />
      <ResultPanel data={data} />
    </>
  );
}
