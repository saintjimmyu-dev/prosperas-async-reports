import { startTransition, useEffect, useEffectEvent, useRef, useState } from "react";

import { ReportComposer } from "../components/ReportComposer";
import { JobsBoard } from "../components/JobsBoard";
import { connectJobsRealtime, createJob, listJobs } from "../services/api";

function mergeJobs(currentJobs, incomingJobs) {
  const byId = new Map(currentJobs.map((job) => [job.job_id, job]));

  for (const job of incomingJobs) {
    byId.set(job.job_id, job);
  }

  return [...byId.values()].sort((left, right) => {
    return new Date(right.created_at).getTime() - new Date(left.created_at).getTime();
  });
}

function summarizeJobs(jobs) {
  return jobs.reduce(
    (summary, job) => {
      summary.total += 1;
      summary[job.status] += 1;
      return summary;
    },
    {
      total: 0,
      PENDING: 0,
      PROCESSING: 0,
      COMPLETED: 0,
      FAILED: 0,
    },
  );
}

export function DashboardPage({ onLogout, onSessionExpired, pushToast, token, username }) {
  const [jobs, setJobs] = useState([]);
  const [nextCursor, setNextCursor] = useState(null);
  const [isBootstrapping, setIsBootstrapping] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [lastSyncAt, setLastSyncAt] = useState(null);
  const [connectionState, setConnectionState] = useState("connecting");
  const [lastRefreshError, setLastRefreshError] = useState("");
  const [isRealtimeActive, setIsRealtimeActive] = useState(false);
  const realtimeConnectedRef = useRef(false);
  const sessionExpiredHandledRef = useRef(false);

  const handleSessionExpired = useEffectEvent((message) => {
    if (sessionExpiredHandledRef.current) {
      return;
    }

    sessionExpiredHandledRef.current = true;
    setConnectionState("degraded");
    setLastRefreshError(message ?? "Token invalido o expirado.");
    pushToast({
      kind: "warning",
      title: "Sesion expirada",
      message: "Tu sesion expiro. Vuelve a iniciar sesion para continuar.",
    });
    onSessionExpired();
  });

  const refreshJobs = useEffectEvent(async ({ showErrorToast = false, silent = false } = {}) => {
    if (silent) {
      setIsRefreshing(true);
    } else {
      setIsBootstrapping(true);
    }

    try {
      const response = await listJobs(token, { pageSize: 20 });
      startTransition(() => {
        setJobs((currentJobs) => mergeJobs(currentJobs, response.items));
        setNextCursor(response.next_cursor);
        setLastSyncAt(new Date().toISOString());
      });
      setConnectionState("online");
      setLastRefreshError("");
    } catch (error) {
      if (error?.status === 401 || error?.code === "UNAUTHORIZED") {
        handleSessionExpired(error.message);
        return;
      }

      if (!realtimeConnectedRef.current) {
        setConnectionState("degraded");
      }
      setLastRefreshError(error.message);

      if (showErrorToast) {
        pushToast({
          kind: "error",
          title: "No fue posible leer los jobs",
          message: jobs.length
            ? "Se mantiene la ultima informacion cargada mientras se recupera la conexion con el backend."
            : error.message,
        });
      }
    } finally {
      setIsBootstrapping(false);
      setIsRefreshing(false);
    }
  });

  useEffect(() => {
    void refreshJobs({ showErrorToast: true });

    const disconnectRealtime = connectJobsRealtime(token, {
      onOpen: () => {
        realtimeConnectedRef.current = true;
        setIsRealtimeActive(true);
        setConnectionState("online");
        setLastRefreshError("");
      },
      onClose: (event) => {
        if (event?.code === 4401) {
          handleSessionExpired("Token invalido o expirado.");
          return;
        }

        realtimeConnectedRef.current = false;
        setIsRealtimeActive(false);
        setConnectionState("degraded");
      },
      onError: (error) => {
        if (!sessionExpiredHandledRef.current) {
          setLastRefreshError(error.message);
        }
      },
      onSnapshot: (items) => {
        startTransition(() => {
          setJobs((currentJobs) => mergeJobs(currentJobs, items));
          setLastSyncAt(new Date().toISOString());
          setNextCursor(null);
        });
        setConnectionState("online");
      },
    });

    const intervalId = window.setInterval(() => {
      if (!realtimeConnectedRef.current) {
        void refreshJobs({ silent: true });
      }
    }, 5000);

    return () => {
      window.clearInterval(intervalId);
      disconnectRealtime();
    };
  }, [token]);

  async function handleCreateJob(payload) {
    setIsCreating(true);

    try {
      const response = await createJob(token, payload);
      pushToast({
        kind: "success",
        title: "Job creado",
        message: `Se creo ${response.job_id} con estado inicial ${response.status}.`,
      });
      await refreshJobs({ silent: true });
    } catch (error) {
      pushToast({
        kind: "error",
        title: "No fue posible crear el job",
        message: error.message,
      });
    } finally {
      setIsCreating(false);
    }
  }

  async function handleLoadMore() {
    if (!nextCursor) {
      return;
    }

    setIsLoadingMore(true);

    try {
      const response = await listJobs(token, { cursor: nextCursor, pageSize: 20 });
      startTransition(() => {
        setJobs((currentJobs) => mergeJobs(currentJobs, response.items));
        setNextCursor(response.next_cursor);
        setLastSyncAt(new Date().toISOString());
      });
    } catch (error) {
      pushToast({
        kind: "error",
        title: "No fue posible cargar mas jobs",
        message: error.message,
      });
    } finally {
      setIsLoadingMore(false);
    }
  }

  const summary = summarizeJobs(jobs);

  return (
    <main className="dashboard-shell">
      <section className="hero-card panel-shell">
        <div>
          <p className="eyebrow">Prosperas · Jimmy Uruchima</p>
          <h1>Visibilidad operacional para reportes asincronos</h1>
          <p className="hero-card__copy">
            La interfaz consulta el backend cada 5 segundos para reflejar el avance del worker sin recargar la pagina.
          </p>
        </div>

        <div className="hero-card__actions">
          <div className="hero-card__user-pill">
            <span>Sesion actual</span>
            <strong>{username}</strong>
          </div>
          <button className="button button--ghost" onClick={onLogout} type="button">
            Cerrar sesion
          </button>
        </div>
      </section>

      <section className="stats-grid">
        <article className="stat-card">
          <span>Total</span>
          <strong>{summary.total}</strong>
        </article>
        <article className="stat-card">
          <span>Pendientes</span>
          <strong>{summary.PENDING}</strong>
        </article>
        <article className="stat-card">
          <span>Procesando</span>
          <strong>{summary.PROCESSING}</strong>
        </article>
        <article className="stat-card">
          <span>Completados</span>
          <strong>{summary.COMPLETED}</strong>
        </article>
        <article className="stat-card">
          <span>Fallidos</span>
          <strong>{summary.FAILED}</strong>
        </article>
      </section>

      <section className="dashboard-grid">
        <ReportComposer isCreating={isCreating} onCreateJob={handleCreateJob} />
        <JobsBoard
          connectionState={connectionState}
          isRealtimeActive={isRealtimeActive}
          isLoadingMore={isLoadingMore}
          isRefreshing={isRefreshing}
          jobs={jobs}
          lastRefreshError={lastRefreshError}
          lastSyncAt={lastSyncAt}
          nextCursor={nextCursor}
          onLoadMore={handleLoadMore}
          onRefresh={() => refreshJobs({ showErrorToast: true })}
        />
      </section>

      {isBootstrapping ? <p className="bootstrapping-copy">Cargando jobs iniciales desde el backend...</p> : null}
    </main>
  );
}
