import streamlit as st
from fpdf import FPDF
import datetime

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Calificador de Taller de Vigas",
    page_icon="📏",
    layout="wide"
)

# --- Definición de Componentes y Problemas ---
componentes_problemas = {
    "C1: Diagrama de cuerpo libre": 25,
    "C2: Reacciones en los apoyos": 25,
    "C3: Función de singularidad": 25,
    "C4: Función de carga cortante": 25,
    "C5: Función de momento flector": 25,
    "C6: Diagrama de momento flector": 25,
    "C7: Diagrama de fuerza cortante": 25,
}

componentes_adicionales = {
    "C8: Deflexión en viga (Punto 2)": 5,
    "C9: Validación con Software (Punto 3)": 5
}

problemas = ["1.a", "1.b", "1.c", "1.d", "1.e"]
MAX_SCORE = 185

# --- NUEVA FUNCIÓN MEJORADA PARA GENERAR EL PDF ---
def generar_pdf(datos_estudiante):
    """Crea un reporte de calificación DETALLADO y con COLORES en formato PDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    # Título
    pdf.cell(0, 10, "Reporte de Calificación - Taller de Vigas", 0, 1, "C")
    pdf.ln(10)

    # Información del estudiante y fecha
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Estudiante(s): {datos_estudiante['nombres']}", 0, 1)
    pdf.cell(0, 8, f"Fecha de calificación: {datetime.date.today().strftime('%Y-%m-%d')}", 0, 1)
    pdf.ln(10)

    # --- INICIO DE LA TABLA DETALLADA Y CON COLORES ---
    pdf.set_font("Arial", "B", 10)

    # Definir colores (R, G, B)
    COLOR_ROJO = (220, 53, 69)
    COLOR_AMARILLO = (255, 193, 7)
    COLOR_VERDE = (40, 167, 69)
    COLOR_NEGRO = (0, 0, 0)

    def get_color_for_score(score):
        if score < 2.5:
            return COLOR_ROJO
        elif score < 3.5:
            return COLOR_AMARILLO
        else:
            return COLOR_VERDE

    # Encabezados de la tabla
    col_width_comp = 75 # Ancho para la columna de competencia
    col_width_prob = 16 # Ancho para las columnas de problemas
    col_width_total = 20 # Ancho para la columna total

    pdf.cell(col_width_comp, 8, "Competencia", 1, 0, "C")
    for prob in problemas:
        pdf.cell(col_width_prob, 8, prob, 1, 0, "C")
    pdf.cell(col_width_total, 8, "Total", 1, 1, "C")

    # Contenido de la tabla (Problemas 1.a - 1.e)
    pdf.set_font("Arial", "", 9)
    for comp, scores in datos_estudiante['scores_grid'].items():
        pdf.cell(col_width_comp, 8, comp.split(':')[1].strip(), 1, 0, "L") # Muestra solo el nombre
        for prob in problemas:
            score = scores[prob]
            color = get_color_for_score(score)
            pdf.set_text_color(*color)
            pdf.cell(col_width_prob, 8, str(score), 1, 0, "C")
            pdf.set_text_color(*COLOR_NEGRO) # Resetear color
        
        # Total por competencia
        total_comp = scores['Total']
        max_comp = componentes_problemas[comp]
        pdf.set_font("Arial", "B", 9)
        pdf.cell(col_width_total, 8, f"{total_comp}/{max_comp}", 1, 1, "C")
        pdf.set_font("Arial", "", 9)

    # Contenido para puntos adicionales (C8 y C9)
    pdf.ln(5) # Espacio antes de la siguiente sección
    pdf.set_font("Arial", "B", 10)
    pdf.cell(col_width_comp, 8, "Componentes Adicionales", 1, 0, "C")
    pdf.cell(col_width_prob * 5 + col_width_total, 8, "Puntaje", 1, 1, "C")

    pdf.set_font("Arial", "", 9)
    for comp, score in datos_estudiante['scores_adicionales'].items():
        pdf.cell(col_width_comp, 8, comp.split(':')[1].strip(), 1, 0, "L")
        color = get_color_for_score(score)
        max_score_add = componentes_adicionales[comp]
        
        pdf.set_text_color(*color)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(col_width_prob * 5 + col_width_total, 8, f"{score}/{max_score_add}", 1, 1, "C")
        pdf.set_text_color(*COLOR_NEGRO)
        pdf.set_font("Arial", "", 9)

    # --- FIN DE LA TABLA ---
    pdf.ln(10)

    # Comentarios (sin cambios)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Comentarios por Componente", 0, 1)
    pdf.set_font("Arial", "", 10)
    comentarios_ingresados = False
    for key, value in datos_estudiante['comentarios'].items():
        if value.strip():
            pdf.multi_cell(0, 6, f"- {key}: {value}")
            comentarios_ingresados = True
    if not comentarios_ingresados:
        pdf.multi_cell(0, 6, "No se ingresaron comentarios específicos.")
    pdf.ln(5)

    # Comentario Final (sin cambios)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Comentario Final", 0, 1)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 6, datos_estudiante['comentario_final'])
    pdf.ln(10)

    # Calificación Final (sin cambios)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 12, f"Puntaje Total: {datos_estudiante['puntaje_total']} / {MAX_SCORE}", 0, 1, "R")
    pdf.cell(0, 12, f"Calificación Final: {datos_estudiante['calificacion_final']:.2f} / 5.0", 0, 1, "R")

    return pdf.output(dest='S').encode('latin-1')


# --- Interfaz de la Aplicación (SIN CAMBIOS) ---
st.title("📏 Herramienta de Calificación: Taller de Vigas")
st.write("Esta aplicación facilita la calificación del taller según la rúbrica, calcula la nota final y genera un reporte en PDF.")

with st.container(border=True):
    st.header("1. Información del Grupo")
    student_names = st.text_input("Nombres de los estudiantes del grupo", placeholder="Ej: Ana Sofia, Carlos Perez")

if 'calificaciones' not in st.session_state:
    st.session_state.calificaciones = {}

st.header("2. Calificación por Componentes")
st.info("Ingrese una puntuación de 0 a 5 para cada ítem. Los comentarios son opcionales.")

col1, col2 = st.columns([0.7, 0.3])

with col1:
    with st.expander("**Problemas 1.a al 1.e (Componentes C1 a C7)**", expanded=True):
        for prob in problemas:
            st.markdown(f"#### Problema {prob}")
            for comp_key in componentes_problemas.keys():
                unique_key = f"{prob}_{comp_key}"
                sub_col1, sub_col2 = st.columns([1, 2])
                with sub_col1:
                     st.session_state.calificaciones[f"{unique_key}_score"] = st.number_input(
                        label=comp_key, min_value=0, max_value=5, step=1,
                        key=f"{unique_key}_score_input", label_visibility="collapsed"
                    )
                with sub_col2:
                    st.session_state.calificaciones[f"{unique_key}_comment"] = st.text_input(
                        "Comentario (opcional)", key=f"{unique_key}_comment_input",
                        label_visibility="collapsed", placeholder=f"Comentario para {comp_key}"
                    )

    with st.expander("**Puntos Adicionales (C8 y C9)**", expanded=True):
        for comp_key in componentes_adicionales.keys():
            unique_key = comp_key
            st.markdown(f"#### {comp_key}")
            sub_col1, sub_col2 = st.columns([1, 2])
            with sub_col1:
                st.session_state.calificaciones[f"{unique_key}_score"] = st.number_input(
                    label=comp_key, min_value=0, max_value=5, step=1,
                    key=f"{unique_key}_score_input", label_visibility="collapsed"
                )
            with sub_col2:
                st.session_state.calificaciones[f"{unique_key}_comment"] = st.text_input(
                    "Comentario (opcional)", key=f"{unique_key}_comment_input",
                    label_visibility="collapsed", placeholder=f"Comentario para {comp_key}"
                )

    st.header("3. Comentario Final")
    final_comment = st.text_area("Escriba aquí un comentario general sobre el trabajo del grupo (Obligatorio).", height=150)

# --- Barra lateral para el resumen (CON AJUSTES EN LA RECOPILACIÓN DE DATOS) ---
with col2:
    with st.sidebar:
        st.header("Resumen de Calificación")

        total_score = 0
        # Recalcular total cada vez para reflejar cambios en la UI
        for key, value in st.session_state.calificaciones.items():
            if "score" in key:
                total_score += value

        final_grade = (5 * total_score / MAX_SCORE) if MAX_SCORE > 0 else 0

        st.metric(label="Puntaje Total Obtenido", value=f"{total_score} / {MAX_SCORE}")
        st.metric(label="Calificación Final", value=f"{final_grade:.2f} / 5.0")

        st.markdown("---")
        st.header("4. Generar Reporte")
        st.warning("Asegúrate de haber llenado todos los campos y el comentario final antes de generar el PDF.")

        if st.button("Generar Reporte PDF", use_container_width=True):
            if not student_names.strip():
                st.error("Por favor, ingrese los nombres de los estudiantes.")
            elif not final_comment.strip():
                st.error("El comentario final es obligatorio.")
            else:
                # --- NUEVA ESTRUCTURA DE DATOS PARA EL REPORTE DETALLADO ---
                scores_grid = {comp: {} for comp in componentes_problemas.keys()}
                scores_adicionales = {}
                comentarios = {}

                # Llenar la grilla de puntajes de los problemas
                for comp_key in componentes_problemas.keys():
                    comp_total = 0
                    for prob in problemas:
                        score = st.session_state.calificaciones.get(f"{prob}_{comp_key}_score", 0)
                        scores_grid[comp_key][prob] = score
                        comp_total += score
                    scores_grid[comp_key]['Total'] = comp_total

                # Llenar los puntajes adicionales
                for comp_key in componentes_adicionales.keys():
                    scores_adicionales[comp_key] = st.session_state.calificaciones.get(f"{comp_key}_score", 0)

                # Llenar los comentarios
                for key, value in st.session_state.calificaciones.items():
                    if "comment" in key and value.strip():
                        clean_key = key.replace("_comment_input", "").replace("_", " -> ")
                        comentarios[clean_key] = value

                datos_estudiante = {
                    "nombres": student_names,
                    "scores_grid": scores_grid,
                    "scores_adicionales": scores_adicionales,
                    "comentarios": comentarios,
                    "comentario_final": final_comment,
                    "puntaje_total": total_score,
                    "calificacion_final": final_grade
                }

                pdf_data = generar_pdf(datos_estudiante)
                st.download_button(
                    label="📥 Descargar Reporte en PDF",
                    data=pdf_data,
                    file_name=f"calificacion_{student_names.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )