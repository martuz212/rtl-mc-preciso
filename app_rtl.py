import streamlit as st

st.set_page_config(page_title="RTL–MC PRECISO PRO", layout="wide")
st.title("🧭 Generador RTL–MC PRECISO PRO")

puntos = st.text_area("📌 TABLA DE PUNTOS (Punto,Norte,Este)")
linderos = st.text_area("📐 LINDEROS (con continúa)")
col = st.text_area("🏡 TABLA ORDEN–COLINDANTES")

def f(v):
    return f"{v:.2f}".replace(".", ",")

if st.button("🚀 GENERAR RTL"):

    try:
        salida = "LINDEROS TÉCNICOS \n\n"

        # -------- PUNTOS --------
        puntos_dict = {}
        orden = []

        for line in puntos.strip().split("\n"):
            p,n,e = line.split(",")
            p = p.zfill(2)
            puntos_dict[p] = (float(n), float(e))
            orden.append(p)

        # -------- TABLA --------
        tabla = []
        for line in col.strip().split("\n"):
            partes = line.split(",")
            tabla.append({
                "col": partes[1],
                "cond": partes[2],
                "npn": partes[3],
                "fmi": partes[4],
                "tit": partes[5],
                "dist": float(partes[6])
            })

        lineas = linderos.strip().split("\n")

        i = 0
        cardinal_actual = None

        while i < len(lineas):

            linea = lineas[i].strip()

            if linea.startswith("Lindero"):

                titulo = linea.split(":")[0]

                # -------- CARDINALIDAD (SOLO UNA VEZ) --------
                if "(NORTE)" in titulo and cardinal_actual != "NORTE":
                    salida += "POR EL NORTE:\n\n"
                    cardinal_actual = "NORTE"
                elif "(ESTE)" in titulo and cardinal_actual != "ESTE":
                    salida += "POR EL ESTE:\n\n"
                    cardinal_actual = "ESTE"
                elif "(SUR)" in titulo and cardinal_actual != "SUR":
                    salida += "POR EL SUR:\n\n"
                    cardinal_actual = "SUR"
                elif "(OESTE)" in titulo and cardinal_actual != "OESTE":
                    salida += "POR EL OESTE:\n\n"
                    cardinal_actual = "OESTE"

                salida += f"{titulo.split()[0]} {titulo.split()[1]}:\n"

                # -------- BLOQUE CONTINÚA --------
                bloque = [linea]
                i += 1

                while i < len(lineas) and "contin" in lineas[i].lower():
                    bloque.append(lineas[i].strip())
                    i += 1

                fila_final = None
                texto_lindero = ""

                for j, tramo in enumerate(bloque):

                    contenido = tramo.split(":")[1]
                    datos = contenido.split(",")

                    rango = datos[0].split("al")
                    sentido = datos[1].replace("sentido","").strip()

                    p_ini = rango[0].split()[-1].zfill(2)
                    p_fin = rango[1].strip().zfill(2)

                    N_ini,E_ini = puntos_dict[p_ini]
                    N_fin,E_fin = puntos_dict[p_fin]

                    i1 = orden.index(p_ini)
                    i2 = orden.index(p_fin)

                    # -------- RUTA --------
                    if i2 > i1:
                        ruta = orden[i1:i2]
                    else:
                        ruta = orden[i1:] + orden[:i2]

                    # -------- INTERMEDIOS --------
                    if i2 < i1:
                        intermedios = orden[i1+1:] + orden[:i2]
                    else:
                        intermedios = orden[i1+1:i2]

                    tipo = "recta"
                    if intermedios:
                        tipo = "quebrada"

                    texto_int = ""

                    if len(intermedios) == 1:
                        p2 = intermedios[0]
                        N2,E2 = puntos_dict[p2]
                        texto_int = f"pasando por el punto de coordenadas punto {p2} N= {f(N2)} m, E= {f(E2)} m, "
                    elif len(intermedios) > 1:
                        texto_int = "pasando por los puntos de coordenadas "
                        for p2 in intermedios:
                            N2,E2 = puntos_dict[p2]
                            texto_int += f"punto {p2} N= {f(N2)} m, E= {f(E2)} m, "
                        texto_int = texto_int.rstrip(", ") + ", "

                    # -------- DISTANCIA TRAMO --------
                    dist = 0
                    for p in ruta:
                        idx = orden.index(p)
                        dist += tabla[idx]["dist"]

                    if ruta:
                        idx_last = orden.index(ruta[-1])
                        fila_final = tabla[idx_last]

                    # -------- REDACCIÓN --------
                    if j == 0:
                        texto_lindero += (
                            f"Inicia en el punto {p_ini} con coordenadas planas N= {f(N_ini)} m, E= {f(E_ini)} m; "
                            f"en línea {tipo} en sentido {sentido}, {texto_int}"
                            f"en una distancia de {f(dist)} m, hasta encontrar el punto número {p_fin} de coordenadas planas "
                            f"N= {f(N_fin)} m, E= {f(E_fin)} m.\n\n"
                        )
                    else:
                        texto_lindero += (
                            f"continúa en el punto {p_ini} con coordenadas planas N= {f(N_ini)} m, E= {f(E_ini)} m, "
                            f"en línea {tipo} en sentido {sentido}, {texto_int}"
                            f"en una distancia de {f(dist)} m, hasta encontrar el punto número {p_fin} de coordenadas planas "
                            f"N= {f(N_fin)} m, E= {f(E_fin)} m.\n\n"
                        )

                # -------- COLINDANTE FINAL --------
                if fila_final:

                    if fila_final["cond"].upper() == "TRASLAPA":
                        txt = f"que traslapa con el Número Predial Nacional {fila_final['npn']}, Folio de Matrícula Inmobiliaria {fila_final['fmi']}, y cuyo titular catastral es {fila_final['tit']}"
                    elif fila_final["cond"].upper() == "CORRESPONDE":
                        txt = f"que corresponde con el Número Predial Nacional {fila_final['npn']}, Folio de Matrícula Inmobiliaria {fila_final['fmi']}, y cuyo titular catastral es {fila_final['tit']}"
                    else:
                        txt = ""

                    # ✅ punto y coma correcto antes de colindante
                    texto_lindero = texto_lindero.rstrip()
                    texto_lindero = texto_lindero.rstrip(".") + f"; colindando con {fila_final['col']}"

                    if txt:
                        texto_lindero += f", {txt}."

                    else:
                        texto_lindero += "."

                salida += texto_lindero + "\n"

            else:
                i += 1

        st.text_area("📄 RESULTADO RTL", salida, height=500)

    except Exception as e:
        st.error(f"Error: {e}")
