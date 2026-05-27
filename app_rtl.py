import streamlit as st

st.set_page_config(page_title="RTL–MC AUTOMÁTICO PRO", layout="wide")
st.title("🧭 Generador RTL–MC AUTOMÁTICO PRO")

# INPUTS
puntos = st.text_area("📌 TABLA DE PUNTOS (Punto,Norte,Este)")
tabla = st.text_area("📊 TABLA ORDEN–COLINDANTES")

def formato_col(valor):
    return str(valor).replace(".", ",")

if st.button("🚀 GENERAR RTL"):

    try:
        salida = "LINDEROS TÉCNICOS\n"

        # -------- PUNTOS --------
        puntos_dict = {}
        orden_puntos = []

        for linea in puntos.strip().split("\n"):
            partes = linea.split(",")
            p = partes[0].zfill(2)
            N = partes[1]
            E = partes[2]

            puntos_dict[p] = (N, E)
            orden_puntos.append(p)

        # -------- TABLA ORDEN --------
        data = []

        for linea in tabla.strip().split("\n"):
            partes = linea.split(",")
            orden = int(partes[0])
            nombre = partes[1]
            condicion = partes[2]
            npn = partes[3]
            fmi = partes[4]
            titular = partes[5]
            distancia = partes[6]

            data.append({
                "orden": orden,
                "nombre": nombre,
                "condicion": condicion,
                "npn": npn,
                "fmi": fmi,
                "titular": titular,
                "dist": distancia
            })

        # -------- AGRUPAR POR COLINDANTE --------
        bloques = []
        bloque_actual = [data[0]]

        for i in range(1, len(data)):
            if data[i]["nombre"] == data[i-1]["nombre"]:
                bloque_actual.append(data[i])
            else:
                bloques.append(bloque_actual)
                bloque_actual = [data[i]]

        bloques.append(bloque_actual)

        # -------- GENERAR RTL --------
        lindero_num = 1

        for bloque in bloques:

            salida += f"\nLindero {lindero_num}: "

            texto = ""

            for i, tramo in enumerate(bloque):

                p_ini = orden_puntos[tramo["orden"] - 1]
                p_fin = orden_puntos[tramo["orden"]]

                N_ini, E_ini = puntos_dict[p_ini]
                N_fin, E_fin = puntos_dict[p_fin]

                # DETECTAR INTERMEDIOS
                i1 = orden_puntos.index(p_ini)
                i2 = orden_puntos.index(p_fin)

                if i2 < i1:
                    intermedios = orden_puntos[i1+1:] + orden_puntos[:i2]
                else:
                    intermedios = orden_puntos[i1+1:i2]

                tipo_linea = "en línea recta"
                if len(intermedios) > 0:
                    tipo_linea = "en línea quebrada"

                texto_intermedios = ""
                if intermedios:
                    texto_intermedios = "pasando por los puntos de coordenadas "
                    for p in intermedios:
                        N, E = puntos_dict[p]
                        texto_intermedios += f"punto {p} N= {formato_col(N)} m, E= {formato_col(E)} m, "
                    texto_intermedios = texto_intermedios.rstrip(", ") + ", "

                if i == 0:
                    texto += (
                        f"Inicia en el punto {p_ini} con coordenadas planas N= {formato_col(N_ini)} m, "
                        f"E= {formato_col(E_ini)} m; {tipo_linea}, {texto_intermedios}"
                        f"hasta encontrar el punto número {p_fin} de coordenadas planas "
                        f"N= {formato_col(N_fin)} m, E= {formato_col(E_fin)} m"
                    )
                else:
                    texto += (
                        f"; continúa en el punto {p_ini} con coordenadas planas N= {formato_col(N_ini)} m, "
                        f"E= {formato_col(E_ini)} m; {tipo_linea}, {texto_intermedios}"
                        f"hasta encontrar el punto número {p_fin} de coordenadas planas "
                        f"N= {formato_col(N_fin)} m, E= {formato_col(E_fin)} m"
                    )

            # -------- COLINDANTE FINAL --------
            ultimo = bloque[-1]

            if ultimo["condicion"].upper() == "TRASLAPA":
                colindancia = (
                    f"colindando con {ultimo['nombre']}, que traslapa con el Número Predial Nacional {ultimo['npn']}, "
                    f"Folio de Matrícula Inmobiliaria {ultimo['fmi']} y cuyo titular catastral es {ultimo['titular']}"
                )
            elif ultimo["condicion"].upper() == "CORRESPONDE":
                colindancia = (
                    f"colindando con {ultimo['nombre']}, que corresponde con el Número Predial Nacional {ultimo['npn']}, "
                    f"Folio de Matrícula Inmobiliaria {ultimo['fmi']} y cuyo titular catastral es {ultimo['titular']}"
                )
            else:
                colindancia = f"colindando con {ultimo['nombre']}"

            # -------- DISTANCIA TOTAL --------
            total_dist = sum(float(t["dist"]) for t in bloque)

            texto += f", en una distancia de {formato_col(total_dist)} m, {colindancia}."

            salida += texto
            lindero_num += 1

        st.text_area("📄 RESULTADO RTL", salida, height=500)

    except Exception as e:
        st.error(f"Error: {e}")
