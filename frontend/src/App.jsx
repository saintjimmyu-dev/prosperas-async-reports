import { useEffect, useState } from "react";

import { LoginCard } from "./components/LoginCard";
import { ToastStack } from "./components/ToastStack";
import { DashboardPage } from "./pages/DashboardPage";
import "./styles/global.css";

const TOKEN_STORAGE_KEY = "prosperas.token";
const USERNAME_STORAGE_KEY = "prosperas.username";

function buildToastId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export default function App() {
  const [token, setToken] = useState(() => window.localStorage.getItem(TOKEN_STORAGE_KEY) ?? "");
  const [username, setUsername] = useState(() => window.localStorage.getItem(USERNAME_STORAGE_KEY) ?? "demo");
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    if (token) {
      window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
      window.localStorage.setItem(USERNAME_STORAGE_KEY, username);
      return;
    }

    window.localStorage.removeItem(TOKEN_STORAGE_KEY);
    window.localStorage.removeItem(USERNAME_STORAGE_KEY);
  }, [token, username]);

  function pushToast({ kind, title, message }) {
    const id = buildToastId();
    const nextToast = { id, kind, title, message };

    setToasts((currentToasts) => {
      const alreadyExists = currentToasts.some(
        (toast) => toast.kind === kind && toast.title === title && toast.message === message,
      );

      if (alreadyExists) {
        return currentToasts;
      }

      return [...currentToasts, nextToast].slice(-3);
    });

    window.setTimeout(() => {
      setToasts((currentToasts) => currentToasts.filter((toast) => toast.id !== id));
    }, 4500);
  }

  function dismissToast(toastId) {
    setToasts((currentToasts) => currentToasts.filter((toast) => toast.id !== toastId));
  }

  function handleAuthenticated({ token: accessToken, username: nextUsername }) {
    setToken(accessToken);
    setUsername(nextUsername);
  }

  function handleLogout() {
    setToken("");
    setUsername("demo");
    pushToast({
      kind: "info",
      title: "Sesion cerrada",
      message: "El token local se elimino del navegador.",
    });
  }

  return (
    <div className="app-shell">
      <div className="background-orb background-orb--amber" />
      <div className="background-orb background-orb--teal" />
      {token ? (
        <DashboardPage onLogout={handleLogout} pushToast={pushToast} token={token} username={username} />
      ) : (
        <LoginCard onAuthenticated={handleAuthenticated} pushToast={pushToast} />
      )}
      <ToastStack onDismiss={dismissToast} toasts={toasts} />
      <footer className="app-footer">
        <span className="app-footer__author">Jimmy Uruchima</span>
        <span className="app-footer__sep">&middot;</span>
        <span>Prosperas &copy; 2026</span>
      </footer>
    </div>
  );
}
