
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
            col.append(linea.split(","))

        indice_col = 0

        # ----------- LINDEROS (CON BLOQUES) -----------

        lineas = linderos.strip().split("\n")
        i = 0

        while i < len(lineas):

            linea = lineas[i].strip()

            if linea.startswith("Lindero"):

                salida += "\n"
                prefijo = linea.split(":")[0]

                bloque = [linea]
                i += 1

                # 🔥 AGRUPAR TODOS LOS CONTINUA
                while i < len(lineas) and "contin" in lineas[i].lower():
                    bloque.append(lineas[i].strip())
                    i += 1

                texto_bloque = ""

                for j, tramo in enumerate(bloque):

                    contenido = tramo.split(":")[1]
                    partes = contenido.split(",")

                    rango = partes[0]
                    sentido = partes[1].replace("sentido", "").strip()

                    p_ini = rango.split("al")[0].split()[-1].zfill(2)
                    p_fin = rango.split("al")[1].strip().zfill(2)

                    N_ini, E_ini = puntos_dict[p_ini]
                    N_fin, E_fin = puntos_dict[p_fin]

                    # INTERMEDIOS
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
                    if len(intermedios) > 0:
                        texto_intermedios = "pasando por los puntos de coordenadas "
                        for p in intermedios:
                            N, E = puntos_dict[p]
                            texto_intermedios += f"punto {p} N= {formato_col(N)} m, E= {formato_col(E)} m, "
                        texto_intermedios = texto_intermedios.rstrip(", ") + ", "

                    # ✅ COLINDANTE SOLO EN EL ÚLTIMO
                    nombre, condicion, npn, fmi, titular, distancia = col[indice_col]
                    indice_col += 1
                    es_ultimo = (j == len(bloque) - 1)

                    if condicion.upper() == "TRASLAPA":
                        colindancia = f"colindando con {nombre}, que traslapa con el Número Predial Nacional {npn}, Folio de Matrícula Inmobiliaria {fmi} y cuyo titular catastral es {titular}"
                    elif condicion.upper() == "CORRESPONDE":
                        colindancia = f"colindando con {nombre}, que corresponde con el Número Predial Nacional {npn}, Folio de Matrícula Inmobiliaria {fmi} y cuyo titular catastral es {titular}"
                    else:
                        colindancia = f"colindando con {nombre}"

                    texto_tramo = (
                        f"Inicia en el punto {p_ini} con coordenadas planas N= {formato_col(N_ini)} m, E= {formato_col(E_ini)} m; "
                        f"{tipo_linea} en sentido {sentido}, "
                        f"{texto_intermedios}"
                        f"en una distancia de {formato_col(distancia)} m, "
                        f"hasta encontrar el punto número {p_fin} de coordenadas planas N= {formato_col(N_fin)} m, E= {formato_col(E_fin)} m"
                    )

                    # ✅ ARMAR BLOQUE
                    if j == 0:
                        texto_bloque += texto_tramo
                    else:
                        texto_bloque += f"; continúa en el punto {p_ini} con coordenadas planas N= {formato_col(N_ini)} m, E= {formato_col(E_ini)} m; {tipo_linea} en sentido {sentido}, {texto_intermedios}en una distancia de {formato_col(distancia)} m, hasta encontrar el punto número {p_fin} de coordenadas planas N= {formato_col(N_fin)} m, E= {formato_col(E_fin)} m"

                    if es_ultimo:
                        texto_bloque += f"; {colindancia}."

                salida += f"{prefijo}: {texto_bloque}"

            else:
                i += 1

        st.text_area("📄 RESULTADO RTL", salida, height=500)

    except Exception as e:
        st.error(f"Error en el formato de datos: {e}")
