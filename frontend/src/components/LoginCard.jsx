import { useState } from "react";

import { login } from "../services/api";

export function LoginCard({ onAuthenticated, pushToast }) {
  const [username, setUsername] = useState("demo");
  const [password, setPassword] = useState("demo123");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await login(username, password);
      onAuthenticated({ token: response.access_token, username });
      pushToast({
        kind: "success",
        title: "Sesion iniciada",
        message: "El panel quedo autenticado con el usuario demo.",
      });
    } catch (error) {
      pushToast({
        kind: "error",
        title: "No fue posible iniciar sesion",
        message: error.message,
      });
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="login-card panel-shell">
      <p className="eyebrow">Prosperas · Jimmy Uruchima</p>
      <h1>Control Desk</h1>
      <p className="login-card__copy">
        Plataforma de generacion de reportes asincronos. Ingresa con el usuario demo para crear
        reportes y seguir el cambio de estado en tiempo real.
      </p>

      <form className="stack-form" onSubmit={handleSubmit}>
        <label>
          <span>Usuario</span>
          <input
            autoComplete="username"
            name="username"
            onChange={(event) => setUsername(event.target.value)}
            value={username}
          />
        </label>

        <label>
          <span>Contrasena</span>
          <input
            autoComplete="current-password"
            name="password"
            onChange={(event) => setPassword(event.target.value)}
            type="password"
            value={password}
          />
        </label>

        <button type="submit" className="button button--primary" disabled={isSubmitting}>
          {isSubmitting ? "Ingresando..." : "Entrar al panel"}
        </button>
      </form>

      <dl className="login-card__hint-grid">
        <div>
          <dt>Usuario demo</dt>
          <dd>demo</dd>
        </div>
        <div>
          <dt>Password demo</dt>
          <dd>demo123</dd>
        </div>
      </dl>

      <p className="login-card__signature">Desarrollado por <strong>Jimmy Uruchima</strong></p>
    </section>
  );
}
