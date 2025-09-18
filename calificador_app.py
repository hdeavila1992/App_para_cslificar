import streamlit as st
from fpdf import FPDF
import datetime
import pandas as pd
import os

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Calificador de Taller de Vigas",
    page_icon="📏",
    layout="wide"
)

# --- Definiciones ---
componentes_problemas = {
    "C1: Diagrama de cuerpo libre": 25, "C2: Reacciones en los apoyos": 25,
    "C3: Función de singularidad": 25, "C4: Función de carga cortante": 25,
    "C5: Función de momento flector": 25, "C6: Diagrama de momento flector": 25,
    "C7: Diagrama de fuerza cortante": 25,
}
componentes_adicionales = {
    "C8: Deflexión en viga (Punto 2)": 5, "C9: Validación con Software (Punto 3)": 5
}
problemas = ["1.a", "1.b", "1.c", "1.d", "1.e"]
MAX_SCORE = 185
GRADEBOOK_FILE = "calificaciones_finales.csv"

# --- Función de PDF (sin cambios) ---
def generar_pdf(datos_estudiante):
    # (Esta función no necesita cambios, se mantiene igual)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Reporte de Calificación - Taller de Vigas", 0, 1, "C")
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Estudiante(s): {datos_estudiante['nombres']}", 0, 1)
    pdf.cell(0, 8, f"Fecha de calificación: {datetime.date.today().strftime('%Y-%m-%d')}", 0, 1)
    pdf.ln(10)

    pdf.set_font("Arial", "B", 10)
    COLOR_ROJO, COLOR_AMARILLO, COLOR_VERDE, COLOR_NEGRO = (220, 53, 69), (255, 193, 7), (40, 167, 69), (0, 0, 0)

    def get_color_for_score(score):
        if score < 2.5: return COLOR_ROJO
        elif score < 3.5: return COLOR_AMARILLO
        else: return COLOR_VERDE

    col_width_comp, col_width_prob, col_width_total = 75, 16, 20
    pdf.cell(col_width_comp, 8, "Competencia", 1, 0, "C")
    for prob in problemas: pdf.cell(col_width_prob, 8, prob, 1, 0, "C")
    pdf.cell(col_width_total, 8, "Total", 1, 1, "C")

    pdf.set_font("Arial", "", 9)
    for comp, scores in datos_estudiante['scores_grid'].items():
        pdf.cell(col_width_comp, 8, comp.split(':')[1].strip(), 1, 0, "L")
        for prob in problemas:
            score = scores[prob]
            color = get_color_for_score(score)
            pdf.set_text_color(*color)
            pdf.cell(col_width_prob, 8, str(score), 1, 0, "C")
            pdf.set_text_color(*COLOR_NEGRO)
        total_comp, max_comp = scores['Total'], componentes_problemas[comp]
        pdf.set_font("Arial", "B", 9)
        pdf.cell(col_width_total, 8, f"{total_comp}/{max_comp}", 1, 1, "C")
        pdf.set_font("Arial", "", 9)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(col_width_comp, 8, "Componentes Adicionales", 1, 0, "C")
    pdf.cell(col_width_prob * 5 + col_width_total, 8, "Puntaje", 1, 1, "C")
    pdf.set_font("Arial", "", 9)
    for comp, score in datos_estudiante['scores_adicionales'].items():
        pdf.cell(col_width_comp, 8, comp.split(':')[1].strip(), 1, 0, "L")
        color, max_score_add = get_color_for_score(score), componentes_adicionales[comp]
        pdf.set_text_color(*color)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(col_width_prob * 5 + col_width_total, 8, f"{score}/{max_score_add}", 1, 1, "C")
        pdf.set_text_color(*COLOR_NEGRO)
        pdf.set_font("Arial", "", 9)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Comentarios por Componente", 0, 1)
    pdf.set_font("Arial", "", 10)
    comentarios_ingresados = False
    for key, value in datos_estudiante['comentarios'].items():
        if value.strip():
            pdf.multi_cell(0, 6, f"- {key}: {value}")
            comentarios_ingresados = True
    if not comentarios_ingresados: pdf.multi_cell(0, 6, "No se ingresaron comentarios específicos.")
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Comentario Final", 0, 1)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 6, datos_estudiante['comentario_final'])
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 12, f"Puntaje Total: {datos_estudiante['puntaje_total']} / {MAX_SCORE}", 0, 1, "R")
    pdf.cell(0, 12, f"Calificación Final (Calculada): {datos_estudiante['calificacion_final']:.2f} / 5.0", 0, 1, "R")
    return pdf.output(dest='S').encode('latin-1')

# --- Función de Guardado (sin cambios) ---
def guardar_nota(lista_estudiantes, calificacion_calculada, calificacion_subjetiva):
    columnas = ["Estudiante", "Calificacion Calculada", "Calificacion Subjetiva", "Fecha"]
    if not os.path.exists(GRADEBOOK_FILE):
        df_gradebook = pd.DataFrame(columns=columnas)
        df_gradebook.to_csv(GRADEBOOK_FILE, index=False)

    df_gradebook = pd.read_csv(GRADEBOOK_FILE)
    nuevas_notas_lista = []
    for estudiante in lista_estudiantes:
        nuevas_notas_lista.append({
            "Estudiante": estudiante,
            "Calificacion Calculada": f"{calificacion_calculada:.2f}",
            "Calificacion Subjetiva": f"{calificacion_subjetiva:.2f}",
            "Fecha": datetime.date.today().strftime('%Y-%m-%d')
        })
    if nuevas_notas_lista:
        nuevas_notas_df = pd.DataFrame(nuevas_notas_lista)
        df_gradebook = pd.concat([df_gradebook, nuevas_notas_df], ignore_index=True)
        if 'Calificacion Final' in df_gradebook.columns:
            df_gradebook = df_gradebook.rename(columns={'Calificacion Final': 'Calificacion Calculada'})
        df_gradebook.to_csv(GRADEBOOK_FILE, index=False)

# --- Interfaz Principal ---
st.title("📏 Calificador Avanzado: Taller de Vigas")

st.header("1. Cargar la Lista del Curso")
uploaded_file = st.file_uploader(
    "Selecciona el archivo CSV con la lista de estudiantes", type=["csv"]
)

if uploaded_file is not None:
    try:
        st.session_state.df_students = pd.read_csv(uploaded_file, encoding='latin1')
        st.success(f"Archivo '{uploaded_file.name}' cargado. Se encontraron {len(st.session_state.df_students)} estudiantes.")
    except Exception as e:
        st.error(f"Ocurrió un error al leer el archivo CSV: {e}")
        st.stop()

    if 'calificaciones' not in st.session_state:
        st.session_state.calificaciones = {}
    if 'current_group' not in st.session_state:
        st.session_state.current_group = []

    st.header("2. Seleccionar Estudiantes del Grupo")
    try:
        student_list = st.session_state.df_students['NOMBRE COMPLETO'].tolist()
    except KeyError:
        st.error("Error: No se encontró la columna 'NOMBRE COMPLETO' en el archivo CSV.")
        st.stop()
    
    col_select, col_group = st.columns(2)
    with col_select:
        selected_student = st.selectbox("Elige un estudiante para agregar:", student_list)
        if st.button("➕ Agregar Estudiante"):
            if selected_student not in st.session_state.current_group:
                st.session_state.current_group.append(selected_student)
    
    with col_group:
        st.write("**Grupo Actual:**")
        if st.session_state.current_group:
            for student in st.session_state.current_group:
                st.markdown(f"- {student}")
            if st.button("🗑️ Limpiar Grupo"):
                st.session_state.current_group = []
                st.rerun()
        else:
            st.write("Aún no se han agregado estudiantes.")
    
    student_names_str = ", ".join(st.session_state.current_group)
    st.markdown("---")

    st.header("3. Calificación por Componentes")
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        with st.expander("**Problemas 1.a al 1.e**", expanded=True):
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
                            "Comentario", key=f"{unique_key}_comment_input",
                            label_visibility="collapsed", placeholder=f"Comentario para {comp_key}"
                        )
        with st.expander("**Puntos Adicionales**", expanded=True):
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
                        "Comentario", key=f"{unique_key}_comment_input",
                        label_visibility="collapsed", placeholder=f"Comentario para {comp_key}"
                    )
        st.header("4. Comentario Final")
        final_comment = st.text_area("Escriba aquí un comentario general (Obligatorio).", height=150)
        
        st.header("5. Calificación Subjetiva (Opcional)")
        subjective_grade = st.number_input(
            "Ingrese una calificación basada en la apreciación del docente (de 0.0 a 5.0).",
            min_value=0.0, max_value=5.0, value=3.0, step=0.1
        )

    # --- BARRA LATERAL ---
    with col2:
        with st.sidebar:
            st.header("Resumen y Acciones")
            total_score = sum(v for k, v in st.session_state.calificaciones.items() if "score" in k)
            calculated_grade = (5 * total_score / MAX_SCORE) if MAX_SCORE > 0 else 0
            st.metric(label="Puntaje Total", value=f"{total_score} / {MAX_SCORE}")
            st.metric(label="Calificación Calculada", value=f"{calculated_grade:.2f} / 5.0")
            st.markdown("---")

            if st.button("💾 Guardar y Generar Reporte", use_container_width=True, type="primary"):
                if not st.session_state.current_group:
                    st.error("Agregue al menos un estudiante al grupo.")
                elif not final_comment.strip():
                    st.error("El comentario final es obligatorio.")
                else:
                    scores_grid = {comp: {} for comp in componentes_problemas.keys()}
                    for comp_key in componentes_problemas.keys():
                        comp_total = 0
                        for prob in problemas:
                            score = st.session_state.calificaciones.get(f"{prob}_{comp_key}_score", 0)
                            scores_grid[comp_key][prob] = score
                            comp_total += score
                        scores_grid[comp_key]['Total'] = comp_total
                    scores_adicionales = {comp_key: st.session_state.calificaciones.get(f"{comp_key}_score", 0) for comp_key in componentes_adicionales.keys()}
                    comentarios = {k.replace("_comment_input", "").replace("_", " -> "): v for k, v in st.session_state.calificaciones.items() if "comment" in k and v.strip()}
                    
                    datos_estudiante = {
                        "nombres": student_names_str, "scores_grid": scores_grid,
                        "scores_adicionales": scores_adicionales, "comentarios": comentarios,
                        "comentario_final": final_comment, "puntaje_total": total_score,
                        "calificacion_final": calculated_grade
                    }
                    
                    guardar_nota(st.session_state.current_group, calculated_grade, subjective_grade)
                    st.success(f"¡Calificaciones guardadas en '{GRADEBOOK_FILE}'!")

                    pdf_data = generar_pdf(datos_estudiante)
                    st.download_button(
                        label="📥 Descargar Reporte PDF Individual",
                        data=pdf_data,
                        file_name=f"calificacion_{student_names_str.replace(' ', '_').replace(',', '')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            
            st.markdown("---")
            
            # --- NUEVA SECCIÓN DE RESET ---
            st.header("Nueva Calificación")
            
            # Usamos el estado de sesión para manejar la confirmación
            if 'confirm_reset' not in st.session_state:
                st.session_state.confirm_reset = False

            if st.session_state.confirm_reset:
                st.warning("**¿Estás seguro de que quieres resetear?** Se perderán todos los datos no guardados.")
                col_reset_1, col_reset_2 = st.columns(2)
                with col_reset_1:
                    if st.button("✅ Sí, resetear", use_container_width=True, type="primary"):
                        # Lógica de reseteo
                        st.session_state.calificaciones = {}
                        st.session_state.current_group = []
                        st.session_state.confirm_reset = False
                        st.success("Formulario reseteado.")
                        st.rerun() # Recargar la app para ver los cambios
                with col_reset_2:
                    if st.button("❌ Cancelar", use_container_width=True):
                        st.session_state.confirm_reset = False
                        st.rerun()
            else:
                if st.button("🔄 Reset Calificación", use_container_width=True):
                    st.session_state.confirm_reset = True
                    st.rerun()

else:
    st.info("Por favor, carga el archivo CSV con la lista del curso para comenzar a calificar.")