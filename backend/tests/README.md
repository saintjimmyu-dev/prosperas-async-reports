# Pruebas Backend

Fase 6 introduce la suite base de backend para sostener B6.

Cobertura objetivo:
- pruebas unitarias de worker, servicios y seguridad
- pruebas de integracion de endpoints con TestClient
- pruebas de escenarios de fallo y circuit breaker

Ejecucion sugerida:
- `python -m pytest --cov=app --cov-report=term-missing tests`