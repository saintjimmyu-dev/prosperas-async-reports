# Reglas del Agente del Proyecto

Este repositorio sigue un desarrollo guiado por SSOT.

Reglas operativas obligatorias:
- Leer SSOT.md antes de hacer o proponer cambios significativos en el proyecto.
- Tratar SSOT.md como la fuente constitucional de verdad para arquitectura, alcance, prioridades, limites de costo y fases de entrega.
- Cuando SSOT.md cambie, actualizar su version, crear un snapshot bajo docs/ssot/versions y anexar docs/ssot/CHANGELOG.md.
- Mantener la implementacion alineada con la arquitectura seleccionada: Arquitectura Event-Driven Contenerizada sobre EC2.
- Mantener el gasto total en AWS por debajo de USD 10.
- Respetar el orden de bonus definido en SSOT.md salvo repriorizacion explicita del owner.
- Agregar comentarios explicativos detallados en espanol en el codigo para logica importante, integraciones, efectos secundarios, retries, concurrencia y decisiones no obvias.
- Toda documentacion del proyecto debe generarse en espanol.
- No iniciar la fase opcional de Terraform hasta que la aplicacion core este completamente estable.

Referencias principales:
- SSOT.md
- docs/ssot/CHANGELOG.md
- docs/diagrams/