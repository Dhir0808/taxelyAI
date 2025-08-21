"use client";
import { useState } from "react";
import { SHEETS_IMPORT_URL, WAIT_URL, SHEETS_LIST_URL } from "../lib/config";

type Props = {
  onImported?: (parsed: Record<string, any>) => void;
};

async function withOAuthRetry(doCall: () => Promise<any>) {
  let resp = await doCall();
  if (resp?.needsOAuth && resp?.auth?.authUrl && resp?.auth?.clarificationId) {
    window.open(resp.auth.authUrl, "_blank");
    const q = new URLSearchParams({
      clarification_id: resp.auth.clarificationId,
    });
    await fetch(`${WAIT_URL}?${q.toString()}`).then((r) => r.json());
    resp = await doCall();
  }
  return resp;
}

export default function ImportSheetCard({ onImported }: Props) {
  const [spreadsheetId, setSpreadsheetId] = useState("");
  const [rangeA1, setRangeA1] = useState("Sheet1!A1:B10");
  const [loading, setLoading] = useState(false);
  const [rawPreview, setRawPreview] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [sheets, setSheets] = useState<{ id: string; name: string }[] | null>(
    null
  );

  async function importSheet() {
    if (!spreadsheetId) {
      setError("Please enter or select a Google Spreadsheet ID.");
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const resp = await withOAuthRetry(async () => {
        const res = await fetch(SHEETS_IMPORT_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ spreadsheetId, rangeA1 }),
        });
        return res.json();
      });

      if (resp?.sdkAvailable === false) {
        setError(
          "Portia SDK not available in this environment. Sheets import and listing are disabled."
        );
        return;
      }

      if (resp?.parsed) {
        onImported?.(resp.parsed);
        setRawPreview(resp.parsed);
      } else if (resp?.detail) {
        setError(resp.detail);
      } else {
        setError("Unexpected response. Check console/network tab.");
        console.warn("Sheets import response:", resp);
      }
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setLoading(false);
    }
  }

  async function connectAndList() {
    setError(null);
    setLoading(true);
    try {
      const resp = await withOAuthRetry(async () => {
        const res = await fetch(SHEETS_LIST_URL);
        return res.json();
      });

      if (resp?.sdkAvailable === false) {
        setError(
          "Portia SDK not available in this environment. Sheets listing is disabled."
        );
        return;
      }

      if (resp?.files && Array.isArray(resp.files)) {
        setSheets(resp.files);
      } else if (resp?.detail) {
        setError(resp.detail);
      } else {
        setError("Could not list sheets. Check console.");
        console.warn("Sheets list response:", resp);
      }
    } catch (e: any) {
      setError(e?.message || String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card" style={{ display: "grid", gap: 12 }}>
      <div>
        <h2 style={{ margin: 0, fontSize: 18 }}>Import from Google Sheets</h2>
        <p style={{ opacity: 0.75, marginTop: 4 }}>
          Connect via Portia OAuth. We’ll read a simple two-column range and map
          it into Taxely inputs.
        </p>
      </div>

      <div style={{ display: "grid", gap: 8 }}>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <button onClick={connectAndList} disabled={loading}>
            {loading ? "Connecting…" : "Connect and list my Sheets"}
          </button>
          <span className="help">Or paste a Spreadsheet ID below.</span>
        </div>
        {sheets && sheets.length > 0 && (
          <div className="card" style={{ display: "grid", gap: 6 }}>
            <strong>Select a Spreadsheet</strong>
            <div className="grid" style={{ gridTemplateColumns: "1fr" }}>
              {sheets.map((s) => (
                <button
                  key={s.id}
                  style={{ textAlign: "left" }}
                  onClick={() => setSpreadsheetId(s.id)}
                >
                  {s.name}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      <label style={{ display: "grid", gap: 6 }}>
        <span>Spreadsheet ID</span>
        <input
          placeholder="1A2B3C... (Google Sheets ID)"
          value={spreadsheetId}
          onChange={(e) => setSpreadsheetId(e.target.value)}
        />
      </label>

      <label style={{ display: "grid", gap: 6 }}>
        <span>Range (A1 notation)</span>
        <input
          placeholder="Sheet1!A1:B10"
          value={rangeA1}
          onChange={(e) => setRangeA1(e.target.value)}
        />
      </label>

      <button onClick={importSheet} disabled={loading}>
        {loading ? "Importing…" : "Import"}
      </button>

      {error && <div style={{ color: "#ffb3b3", fontSize: 13 }}>{error}</div>}

      <div className="card" style={{ display: "grid", gap: 8 }}>
        <strong>Allowed CSV / Sheet format</strong>
        <p style={{ margin: 0, opacity: 0.8 }}>
          We accept a <b>2-column layout</b> only:
        </p>
        <pre
          style={{
            whiteSpace: "pre-wrap",
            margin: 0,
            background: "#0b0e11",
            padding: 10,
            borderRadius: 8,
          }}
        >
          A) With header: key,value revenueGBP,20000000 expensesGBP,14000000
          rAndDSpendGBP,3000000 capexGBP,1000000 patentRevenueGBP,500000 B)
          Without header (first two columns used): revenueGBP,20000000
          expensesGBP,14000000 rAndDSpendGBP,3000000 capexGBP,1000000
          patentRevenueGBP,500000
        </pre>
        <p style={{ margin: 0, opacity: 0.8 }}>
          <b>Required keys</b> (any subset is fine): <code>revenueGBP</code>,{" "}
          <code>expensesGBP</code>, <code>rAndDSpendGBP</code>,{" "}
          <code>capexGBP</code>, <code>patentRevenueGBP</code>. Non-numeric
          values are kept as text.
        </p>
      </div>

      {rawPreview && (
        <div className="card" style={{ display: "grid", gap: 6 }}>
          <strong>Imported preview</strong>
          <pre
            style={{ whiteSpace: "pre-wrap", maxHeight: 240, overflow: "auto" }}
          >
            {JSON.stringify(rawPreview, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
