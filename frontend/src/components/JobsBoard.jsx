import { StatusBadge } from "./StatusBadge";

const dateTimeFormatter = new Intl.DateTimeFormat("es-ES", {
  dateStyle: "medium",
  timeStyle: "short",
});

function formatDateTime(value) {
  if (!value) {
    return "Sin registro";
  }

  return dateTimeFormatter.format(new Date(value));
}

function isHttpResult(resultUrl) {
  return /^https?:\/\//i.test(resultUrl);
}

export function JobsBoard({
  connectionState,
  isRealtimeActive,
  isLoadingMore,
  isRefreshing,
  jobs,
  lastRefreshError,
  lastSyncAt,
  nextCursor,
  onLoadMore,
  onRefresh,
}) {
  return (
    <section className="panel-shell jobs-card">
      <div className="section-heading section-heading--wide">
        <div>
          <p className="eyebrow">Monitoreo</p>
          <h2>Estado de jobs</h2>
        </div>
        <div className="jobs-card__actions">
          <p>
            {isRealtimeActive
              ? "Tiempo real activo"
              : lastSyncAt
                ? `Fallback polling activo · ultima sincronizacion ${formatDateTime(lastSyncAt)}`
                : "Sin sincronizacion previa"}
          </p>
          <button className="button button--ghost" onClick={onRefresh} type="button">
            {isRefreshing ? "Actualizando..." : "Refrescar ahora"}
          </button>
        </div>
      </div>

      {connectionState === "degraded" ? (
        <div className="connection-banner connection-banner--warning">
          <strong>Conexion inestable con el backend</strong>
          <p>
            Se mantiene la ultima informacion cargada. {lastRefreshError ? `Detalle: ${lastRefreshError}` : ""}
          </p>
        </div>
      ) : null}

      {jobs.length === 0 ? (
        <div className="empty-state">
          <h3>Todavia no hay jobs visibles</h3>
          <p>Crea un reporte y el tablero empezara a mostrar las transiciones PENDING, PROCESSING, COMPLETED o FAILED.</p>
        </div>
      ) : (
        <div className="jobs-list">
          {jobs.map((job) => (
            <article key={job.job_id} className="job-row">
              <div className="job-row__title-group">
                <div>
                  <p className="job-row__eyebrow">{job.job_id}</p>
                  <h3>{job.report_type}</h3>
                </div>
                <StatusBadge status={job.status} />
              </div>

              <dl className="job-row__meta-grid">
                <div>
                  <dt>Formato</dt>
                  <dd>{job.format.toUpperCase()}</dd>
                </div>
                <div>
                  <dt>Rango</dt>
                  <dd>
                    {job.date_range.start_date} → {job.date_range.end_date}
                  </dd>
                </div>
                <div>
                  <dt>Creado</dt>
                  <dd>{formatDateTime(job.created_at)}</dd>
                </div>
                <div>
                  <dt>Actualizado</dt>
                  <dd>{formatDateTime(job.updated_at)}</dd>
                </div>
              </dl>

              {job.result_url ? (
                isHttpResult(job.result_url) ? (
                  <a className="job-row__link" href={job.result_url} rel="noreferrer" target="_blank">
                    Ver resultado
                  </a>
                ) : (
                  <div className="job-row__artifact">
                    <p className="job-row__link job-row__link--muted">
                      Resultado simulado: en esta fase no se genera un PDF descargable real.
                    </p>
                    <code className="job-row__artifact-code">{job.result_url}</code>
                  </div>
                )
              ) : (
                <p className="job-row__link job-row__link--muted">Sin resultado publicado todavia</p>
              )}
            </article>
          ))}
        </div>
      )}

      {nextCursor ? (
        <button className="button button--secondary" disabled={isLoadingMore} onClick={onLoadMore} type="button">
          {isLoadingMore ? "Cargando pagina adicional..." : "Cargar mas jobs"}
        </button>
      ) : null}
    </section>
  );
}
