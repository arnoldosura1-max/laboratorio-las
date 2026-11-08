from datetime import datetime


def registrar_respuesta(usuario):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("respuesta.log", "a", encoding="utf-8") as archivo:
        archivo.write(f"{fecha},USUARIO_BLOQUEADO,{usuario}\n")

    return fecha   # ← IMPORTANTE: devolver la fecha


intentos = {}

with open("eventos.log", "r", encoding="utf-8") as archivo:
    for linea in archivo:
        partes = linea.strip().split(",")
        if len(partes) != 3:
            continue  # saltar líneas mal formadas
        fecha, tipo, usuario = partes

        if tipo == "LOGIN_FALLIDO":
            intentos.setdefault(usuario, []).append(fecha)


for usuario, registros in intentos.items():
    if len(registros) >= 3:
        print("ALERTA DE SEGURIDAD")
        print("Usuario:", usuario)
        print("Intentos fallidos:", len(registros))
        print("Primer intento:", registros[0])
        print("Detección:", registros[2])

        # 1) Registrar la respuesta (bloqueo) y obtener su fecha
        fecha_respuesta = registrar_respuesta(usuario)
        print("Acción aplicada: bloqueo de usuario")
        print("Respuesta:", fecha_respuesta)

        # 2) Parsear fechas
        inicio = datetime.strptime(registros[0], "%Y-%m-%d %H:%M:%S")
        deteccion = datetime.strptime(registros[2], "%Y-%m-%d %H:%M:%S")
        respuesta = datetime.strptime(fecha_respuesta, "%Y-%m-%d %H:%M:%S")

        # 3) Calcular métricas
        mttd = (deteccion - inicio).total_seconds()
        mttr = (respuesta - deteccion).total_seconds()

        print("MTTD:", mttd, "segundos")
        print("MTTR:", mttr, "segundos")
        print("-" * 40)