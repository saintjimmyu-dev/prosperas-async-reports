# Reglas del Agente del Proyecto

Este repositorio sigue un desarrollo guiado por SSOT.

Reglas operativas obligatorias:
- Leer SSOT.md antes de hacer o proponer cambios significativos en el proyecto.
- Tratar SSOT.md como la fuente constitucional de verdad para arquitectura, alcance, prioridades, limites de costo y fases de entrega.
- Cuando SSOT.md cambie, actualizar su version, crear un snapshot bajo docs/ssot/versions y anexar docs/ssot/CHANGELOG.md.
- Todo cambio hacia master debe pasar por Pull Request; no hacer push directo a master salvo aprobacion explicita del owner para una excepcion puntual.
- El agente debe encargarse del flujo Git completo (crear rama, commit, push, abrir PR y ejecutar merge), pero el merge solo puede ejecutarse despues de aprobacion explicita del owner en chat.
- Antes de ejecutar cualquier merge, confirmar en chat la aprobacion del owner para ese PR especifico.
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