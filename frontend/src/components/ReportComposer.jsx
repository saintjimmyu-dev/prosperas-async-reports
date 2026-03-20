import { useState } from "react";

const INITIAL_FORM = {
  reportType: "ventas_diarias",
  startDate: "2026-03-01",
  endDate: "2026-03-10",
  format: "pdf",
};

export function ReportComposer({ isCreating, onCreateJob }) {
  const [form, setForm] = useState(INITIAL_FORM);

  function updateField(field, value) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();

    await onCreateJob({
      report_type: form.reportType,
      date_range: {
        start_date: form.startDate,
        end_date: form.endDate,
      },
      format: form.format,
    });
  }

  return (
    <section className="panel-shell composer-card">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Nuevo job</p>
          <h2>Solicitar reporte</h2>
        </div>
        <p className="section-heading__aside">La API responde de inmediato y el worker procesa en segundo plano.</p>
      </div>

      <form className="stack-form" onSubmit={handleSubmit}>
        <label>
          <span>Tipo de reporte</span>
          <input
            name="report_type"
            onChange={(event) => updateField("reportType", event.target.value)}
            placeholder="ventas_diarias"
            value={form.reportType}
          />
        </label>

        <div className="form-grid">
          <label>
            <span>Fecha inicial</span>
            <input
              name="start_date"
              onChange={(event) => updateField("startDate", event.target.value)}
              type="date"
              value={form.startDate}
            />
          </label>

          <label>
            <span>Fecha final</span>
            <input
              name="end_date"
              onChange={(event) => updateField("endDate", event.target.value)}
              type="date"
              value={form.endDate}
            />
          </label>
        </div>

        <label>
          <span>Formato</span>
          <select name="format" onChange={(event) => updateField("format", event.target.value)} value={form.format}>
            <option value="pdf">PDF</option>
            <option value="csv">CSV</option>
            <option value="xlsx">XLSX</option>
          </select>
        </label>

        <div className="composer-card__footer">
          <p>
            Pruebas utiles: <strong>priority_ventas</strong> para cola prioritaria y <strong>fail_demo</strong> para fallo controlado.
          </p>
          <button className="button button--primary" disabled={isCreating} type="submit">
            {isCreating ? "Creando job..." : "Crear job"}
          </button>
        </div>
      </form>
    </section>
  );
}
