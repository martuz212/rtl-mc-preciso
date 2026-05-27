import streamlit as st

# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(page_title="RTL–MC PRECISO PRO", layout="wide")
st.title("🧭 Generador RTL–MC PRECISO PRO")

# ---------------- INPUTS ----------------
puntos = st.text_area("📌 TABLA DE PUNTOS (Punto,Norte,Este)")
linderos = st.text_area("📐 LINDEROS (con continúa)")
colindantes = st.text_area("🏡 TABLA ORDEN–COLINDANTES")

# ---------------- FORMATO ----------------
def formato_col(v):
    return str(round(v, 2)).replace(".", ",")

# ---------------- EJECUCIÓN ----------------
if st.button("🚀 GENERAR RTL"):

    try:
        salida = "LINDEROS TÉCNICOS\n"

        # ===============================
        # 1. LEER PUNTOS
        # ===============================
        puntos_dict = {}
        orden_puntos = []

        for linea in puntos.strip().split("\n"):
            p, n, e = linea.split(",")
            p = p.zfill(2)
            puntos_dict[p] = (float(n), float(e))
            orden_puntos.append(p)

        # ===============================
        # 2. LEER TABLA DE COLINDANTES
        # ===============================
        tabla = []

        for linea in colindantes.strip().split("\n"):
            partes = linea.split(",")
            tabla.append({
                "col": partes[1],
                "cond": partes[2],
                "npn": partes[3],
                "fmi": partes[4],
                "tit": partes[5],
                "dist": float(partes[6])
            })

        # ===============================
        # 3. LEER LINDEROS (AGRUPAR BLOQUES)
        # ===============================
        lineas = linderos.strip().split("\n")
        i = 0

        while i < len(lineas):

            linea = lineas[i].strip()

            if linea.startswith("Lindero"):

                salida += "\n"
                titulo = linea.split(":")[0]

                # -------- AGRUPAR BLOQUE (LINDERO + CONTINÚA)
                bloque = [linea]
                i += 1

                while i < len(lineas) and "contin" in lineas[i].lower():
                    bloque.append(lineas[i].strip())
                    i += 1

                texto_bloque = ""
                dist_total_bloque = 0
                fila_final = None

                # ===============================
                # 4. PROCESAR TRAMOS DEL BLOQUE
                # ===============================
                for j, tramo in enumerate(bloque):

                    contenido = tramo.split(":")[1]
                    datos = contenido.split(",")

                    # -------- RANGOS
                    rango = datos[0].split("al")
                    sentido = datos[1].replace("sentido", "").strip()

                    p_ini = rango[0].split()[-1].zfill(2)
                    p_fin = rango[1].strip().zfill(2)

                    N_ini, E_ini = puntos_dict[p_ini]
                    N_fin, E_fin = puntos_dict[p_fin]

                    # ===============================
                    # 5. CALCULAR RUTA PUNTO A PUNTO
                    # ===============================
                    i1 = orden_puntos.index(p_ini)
                    i2 = orden_puntos.index(p_fin)

                    if i2 > i1:
                        ruta = orden_puntos[i1:i2]
                    else:
                        ruta = orden_puntos[i1:] + orden_puntos[:i2]

                    # ===============================
                    # 6. SUMAR DISTANCIAS REALES
                    # ===============================
                    dist_tramo = 0

                    for p in ruta:
                        idx_tabla = orden_puntos.index(p)
                        dist_tramo += tabla[idx_tabla]["dist"]

                    dist_total_bloque += dist_tramo

                    # almacenar última fila
                    if ruta:
                        idx_last = orden_puntos.index(ruta[-1])
                        fila_final = tabla[idx_last]

                    # ===============================
                    # 7. INTERMEDIOS
                    # ===============================
                    if i2 < i1:
                        intermedios = orden_puntos[i1+1:] + orden_puntos[:i2]
                    else:
                        intermedios = orden_puntos[i1+1:i2]

                    tipo = "en línea recta"
                    if intermedios:
                        tipo = "en línea quebrada"

                    texto_int = ""
                    if intermedios:
                        texto_int = "pasando por los puntos de coordenadas "
                        for p2 in intermedios:
                            N2, E2 = puntos_dict[p2]
                            texto_int += f"punto {p2} N= {formato_col(N2)} m, E= {formato_col(E2)} m, "
                        texto_int = texto_int.rstrip(", ") + ", "

                    # ===============================
                    # 8. REDACCIÓN TRAMO
                    # ===============================
                    if j == 0:
                        texto_bloque += (
                            f"Inicia en el punto {p_ini} con coordenadas planas N= {formato_col(N_ini)} m, "
                            f"E= {formato_col(E_ini)} m; {tipo} en sentido {sentido}, {texto_int}"
                            f"hasta encontrar el punto número {p_fin} de coordenadas planas "
                            f"N= {formato_col(N_fin)} m, E= {formato_col(E_fin)} m"
                        )
                    else:
                        texto_bloque += (
                            f"; continúa en el punto {p_ini} con coordenadas planas N= {formato_col(N_ini)} m, "
                            f"E= {formato_col(E_ini)} m; {tipo} en sentido {sentido}, {texto_int}"
                            f"hasta encontrar el punto número {p_fin} de coordenadas planas "
                            f"N= {formato_col(N_fin)} m, E= {formato_col(E_fin)} m"
                        )

                # ===============================
                # 9. COLINDANTE FINAL
                # ===============================
                if fila_final:

                    if fila_final["cond"].upper() == "TRASLAPA":
                        txt_col = f"que traslapa con el Número Predial Nacional {fila_final['npn']}, Folio de Matrícula Inmobiliaria {fila_final['fmi']} y cuyo titular catastral es {fila_final['tit']}"
                    elif fila_final["cond"].upper() == "CORRESPONDE":
                        txt_col = f"que corresponde con el Número Predial Nacional {fila_final['npn']}, Folio de Matrícula Inmobiliaria {fila_final['fmi']} y cuyo titular catastral es {fila_final['tit']}"
                    else:
                        txt_col = ""

                    texto_bloque += f"; en una distancia de {formato_col(dist_total_bloque)} m, colindando con {fila_final['col']}"

                    if txt_col:
                        texto_bloque += f", {txt_col}."

                    else:
                        texto_bloque += "."

                salida += f"{titulo}: {texto_bloque}"

            else:
                i += 1

        st.text_area("📄 RESULTADO RTL", salida, height=500)

    except Exception as e:
        st.error(f"Error: {e}")
