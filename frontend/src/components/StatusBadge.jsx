const STATUS_LABELS = {
  PENDING: "Pendiente",
  PROCESSING: "Procesando",
  COMPLETED: "Completado",
  FAILED: "Fallido",
};

export function StatusBadge({ status }) {
  return (
    <span className={`status-badge status-badge--${String(status).toLowerCase()}`}>
      {STATUS_LABELS[status] ?? status}
    </span>
  );
}
