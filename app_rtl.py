
import streamlit as st

st.set_page_config(page_title="RTL–MC PRECISO FINAL", layout="wide")

st.title("🧭 Generador RTL–MC PRECISO FINAL")

# INPUTS
puntos = st.text_area("📌 TABLA DE PUNTOS (Punto,Norte,Este)")
linderos = st.text_area("📐 AGRUPACIÓN DE LINDEROS")
colindantes = st.text_area("🏡 TABLA DE COLINDANTES")

# -------- FUNCIONES --------

def formato_col(valor):
    return str(valor).replace(".", ",")

# -------- EJECUCIÓN --------

if st.button("🚀 GENERAR RTL"):

    try:
        salida = "LINDEROS TÉCNICOS\n"

        # ----------- PUNTOS -----------
        puntos_dict = {}
        orden_puntos = []

        for linea in puntos.strip().split("\n"):
            partes = linea.split(",")
            punto = partes[0].zfill(2)
            norte = partes[1]
            este = partes[2]

            puntos_dict[punto] = (norte, este)
            orden_puntos.append(punto)

        # ----------- COLINDANTES -----------
        col = []
        for linea in colindantes.strip().split("\n"):
            partes = linea.split(",")
            col.append(partes)

        indice_col = 0

        # ----------- LINDEROS -----------
        for linea in linderos.strip().split("\n"):

            if not linea.strip():
                continue

            es_continua = "continúa" in linea.lower()

            if "Lindero" in linea:
                salida += "\n"
                prefijo = linea.split(":")[0]
            elif es_continua:
                prefijo = "continúa"
            else:
                continue

            contenido = linea.split(":")[1]
            bloques = contenido.split(",")

            rango = bloques[0]
            sentido = bloques[1].replace("sentido", "").strip()

            p_ini = rango.split("al")[0].split()[-1].zfill(2)
            p_fin = rango.split("al")[1].strip().zfill(2)

            N_ini, E_ini = puntos_dict[p_ini]
            N_fin, E_fin = puntos_dict[p_fin]

            # ----------- INTERMEDIOS -----------
            i1 = orden_puntos.index(p_ini)
            i2 = orden_puntos.index(p_fin)

            if i2 < i1:
                intermedios = orden_puntos[i1+1:] + orden_puntos[:i2]
            else:
                intermedios = orden_puntos[i1+1:i2]

            # ----------- TIPO DE LÍNEA -----------
            tipo_linea = "en línea recta"
            if len(intermedios) > 0:
                tipo_linea = "en línea quebrada"

            # ----------- TEXTO INTERMEDIOS -----------
            texto_intermedios = ""
            if len(intermedios) > 0:
                texto_intermedios = "pasando por los puntos de coordenadas "
                for p in intermedios:
                    N, E = puntos_dict[p]
                    texto_intermedios += f"punto {p} N= {formato_col(N)} m, E= {formato_col(E)} m, "
                texto_intermedios = texto_intermedios.rstrip(", ") + ", "

            # ----------- COLINDANTE -----------
            nombre, condicion, npn, fmi, titular, distancia = col[indice_col]
            indice_col += 1

            if condicion.upper() == "TRASLAPA":
                colindancia = (
                    f"colindando con {nombre}, que traslapa con el Número Predial Nacional {npn}, "
                    f"Folio de Matrícula Inmobiliaria {fmi} y cuyo titular catastral es {titular}"
                )
            elif condicion.upper() == "CORRESPONDE":
                colindancia = (
                    f"colindando con {nombre}, que corresponde con el Número Predial Nacional {npn}, "
                    f"Folio de Matrícula Inmobiliaria {fmi} y cuyo titular catastral es {titular}"
                )
            else:
                colindancia = f"colindando con {nombre}"

            # ----------- REDACCIÓN FINAL RTL -----------

            texto_base = (
                f"Inicia en el punto {p_ini} con coordenadas planas N= {formato_col(N_ini)} m, E= {formato_col(E_ini)} m; "
                f"{tipo_linea} en sentido {sentido}, "
                f"{texto_intermedios}"
                f"en una distancia de {formato_col(distancia)} m, "
                f"hasta encontrar el punto número {p_fin} de coordenadas planas N= {formato_col(N_fin)} m, E= {formato_col(E_fin)} m; "
                f"{colindancia}"
            )

            if es_continua:
                salida += f"; continúa en el punto {p_ini} con coordenadas planas N= {formato_col(N_ini)} m, E= {formato_col(E_ini)} m; {tipo_linea} en sentido {sentido}, {texto_intermedios}en una distancia de {formato_col(distancia)} m, hasta encontrar el punto número {p_fin} de coordenadas planas N= {formato_col(N_fin)} m, E= {formato_col(E_fin)} m; {colindancia}"
            else:
                salida += f"{prefijo}: {texto_base}."

        st.text_area("📄 RESULTADO RTL", salida, height=500)

    except Exception as e:
        st.error(f"Error en el formato de datos: {e}")
