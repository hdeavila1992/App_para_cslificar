import streamlit as st
import pandas as pd
import datetime
import os
from fpdf import FPDF
import io

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Calificador Flexible por Rúbricas", layout="wide", page_icon="📝")
GRADEBOOK_FILE = "calificaciones_finales.csv"

# --- FUNCIONES AUXILIARES ---

def guardar_nota(lista_estudiantes, calificacion_final):
    if not os.path.exists(GRADEBOOK_FILE):
        pd.DataFrame(columns=["Estudiante", "Calificacion Final", "Fecha"]).to_csv(GRADEBOOK_FILE, index=False)
    df_gradebook = pd.read_csv(GRADEBOOK_FILE)
    nuevas_notas = [{"Estudiante": est, "Calificacion Final": f"{calificacion_final:.2f}", "Fecha": datetime.date.today().strftime('%Y-%m-%d')} for est in lista_estudiantes]
    df_nuevas_notas = pd.DataFrame(nuevas_notas)
    df_gradebook = pd.concat([df_gradebook, df_nuevas_notas], ignore_index=True)
    df_gradebook.to_csv(GRADEBOOK_FILE, index=False)

def parse_rubric_csv(df):
    preguntas_col, sub_item_cols = df.columns[0], df.columns[1:-2]
    rubric = [{'pregunta': row[preguntas_col], 'sub_items': [item for item in sub_item_cols if str(row[item]).strip().lower() == 'si'], 'sobre': row['sobre'], 'peso': row['peso']} for _, row in df.iterrows()]
    return rubric

def generar_reporte_dinamico_pdf(datos_reporte):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Reporte de Calificación", 0, 1, "C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, f"Estudiante(s): {datos_reporte['nombres']}", 0, 1)
    pdf.cell(0, 8, f"Fecha: {datetime.date.today().strftime('%Y-%m-%d')}", 0, 1)
    pdf.ln(10)
    COLOR_ROJO, COLOR_AMARILLO, COLOR_VERDE, COLOR_NEGRO = (220, 53, 69), (255, 193, 7), (40, 167, 69), (0, 0, 0)
    def get_color_for_score_0_5(score): # Modificado para escala 0-5
        if score < 3.0: return COLOR_ROJO
        elif score < 4.0: return COLOR_AMARILLO
        else: return COLOR_VERDE
    pdf.set_font("Arial", "B", 10)
    pdf.cell(90, 8, "Item Evaluado", 1, 0, "C")
    pdf.cell(70, 8, "Sub-item", 1, 0, "C")
    pdf.cell(30, 8, "Puntaje (0-5)", 1, 1, "C")
    pdf.set_font("Arial", "", 9)
    for pregunta in datos_reporte['rubrica']:
        nombre_pregunta = pregunta['pregunta']
        # Usar el promedio guardado para el color
        promedio_pregunta = datos_reporte['promedios_por_pregunta'][nombre_pregunta]
        pdf.set_font("Arial", "B", 9)
        pdf.cell(90, 8, nombre_pregunta, 1, 0, "L")
        pdf.cell(70, 8, f"Promedio: {promedio_pregunta:.2f}", 1, 0, "C")
        color = get_color_for_score_0_5(promedio_pregunta)
        pdf.set_text_color(*color)
        pdf.cell(30, 8, f"{promedio_pregunta:.2f}", 1, 1, "C")
        pdf.set_text_color(*COLOR_NEGRO)
        pdf.set_font("Arial", "", 9)
        for sub_item in pregunta['sub_items']:
            puntaje_sub_item = datos_reporte['calificaciones'][pregunta['pregunta']][sub_item]
            pdf.cell(90, 6, "", 'L', 0)
            pdf.cell(70, 6, f"- {sub_item}", 'LR', 0, "L")
            pdf.cell(30, 6, f"{puntaje_sub_item:.2f}", 'R', 1, "C")
    pdf.ln(10)
    # ... (resto de la función de PDF sin cambios)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Comentarios de Retroalimentación", 0, 1)
    pdf.set_font("Arial", "", 10)
    comentarios_opcionales_ingresados = False
    for pregunta, comentario in datos_reporte.get('optional_comments', {}).items():
        if comentario.strip():
            pdf.set_font("Arial", "B", 10)
            pdf.multi_cell(0, 6, f"- Sobre '{pregunta}':")
            pdf.set_font("Arial", "I", 10)
            pdf.multi_cell(0, 6, f'"{comentario}"')
            comentarios_opcionales_ingresados = True
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Comentario Final", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, datos_reporte.get('final_comment', ''))
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 12, f"Calificación Final: {datos_reporte['calificacion_final']:.2f} / 5.0", 0, 1, "R")
    if datos_reporte.get('firmar', False):
        pdf.set_y(-40)
        pdf.set_font("Arial", "", 10)
        pdf.cell(80, 8, "_" * 35, 0, 1, "C")
        pdf.cell(80, 8, "Firma del Docente", 0, 1, "C")
    return pdf.output(dest='S').encode('latin-1')

def add_enunciado_callback():
    new_pregunta = st.session_state.new_enunciado_input
    if new_pregunta and not any(p['pregunta'] == new_pregunta for p in st.session_state.rubric_builder_data['preguntas']):
        st.session_state.rubric_builder_data['preguntas'].append({'pregunta': new_pregunta, 'sub_items': [], 'sobre': 5.0, 'peso': 1.0})
        st.session_state.new_enunciado_input = ""

# --- APLICACIÓN PRINCIPAL ---
st.title("📝 Calificador Flexible por Rúbricas")

if 'rubric' not in st.session_state: st.session_state.rubric = None
if 'app_mode' not in st.session_state: st.session_state.app_mode = 'define_rubric'
if 'rubric_builder_data' not in st.session_state:
    st.session_state.rubric_builder_data = {'all_sub_items': [], 'preguntas': []}

if st.session_state.app_mode == 'define_rubric':
    st.header("Paso 1: Define tu Rúbrica de Evaluación")
    tab1, tab2 = st.tabs(["Crear Rúbrica Nueva", "Cargar Rúbrica Existente (.csv)"])
    with tab1:
        st.subheader("A. Define todos los posibles Sub-Items (Competencias)")
        sub_items_input = st.text_input("Escribe los sub-items separados por comas (,)", placeholder="Ej: Dibuja DCL, Identifica Fuerzas")
        if st.button("Establecer Sub-Items"):
            st.session_state.rubric_builder_data['all_sub_items'] = [s.strip() for s in sub_items_input.split(',') if s.strip()]
        if st.session_state.rubric_builder_data['all_sub_items']:
            st.info(f"Sub-items definidos: {st.session_state.rubric_builder_data['all_sub_items']}")
            st.markdown("---")
            st.subheader("B. Agrega y configura los Enunciados (Puntos)")
            st.text_input("Nombre del nuevo enunciado", key="new_enunciado_input")
            st.button("➕ Agregar Enunciado", on_click=add_enunciado_callback)
            for i, preg_data in enumerate(st.session_state.rubric_builder_data['preguntas']):
                with st.container(border=True):
                    st.markdown(f"**{i+1}. {preg_data['pregunta']}**")
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1: preg_data['sub_items'] = st.multiselect("Sub-items que aplican:", options=st.session_state.rubric_builder_data['all_sub_items'], default=preg_data['sub_items'], key=f"ms_{i}")
                    with col2: preg_data['sobre'] = st.number_input("Puntaje 'sobre' (informativo):", min_value=0.0, value=preg_data['sobre'], key=f"sobre_{i}")
                    with col3: preg_data['peso'] = st.number_input("Peso:", min_value=0.0, value=preg_data['peso'], key=f"peso_{i}")
            st.markdown("---")
            col_final, col_download = st.columns(2)
            with col_final:
                if st.button("✅ Finalizar y Usar esta Rúbrica", type="primary"):
                    if not st.session_state.rubric_builder_data['preguntas']: st.error("Debes agregar al menos un enunciado.")
                    else:
                        st.session_state.rubric = st.session_state.rubric_builder_data['preguntas']
                        st.session_state.app_mode = 'grading'
                        st.rerun()
            with col_download:
                if st.session_state.rubric_builder_data['preguntas']:
                    rows = [{'Enunciado': p['pregunta'], **{si:('si' if si in p['sub_items'] else 'no') for si in st.session_state.rubric_builder_data['all_sub_items']}, 'sobre':p['sobre'], 'peso':p['peso']} for p in st.session_state.rubric_builder_data['preguntas']]
                    df_to_download = pd.DataFrame(rows)
                    st.download_button(label="📥 Descargar Rúbrica como CSV", data=df_to_download.to_csv(index=False, sep=';').encode('utf-8'), file_name="rubrica_generada.csv", mime="text/csv")
    with tab2:
        st.info("Sube un archivo CSV de una rúbrica que hayas generado y descargado previamente.")
        uploaded_rubric_file = st.file_uploader("Cargar archivo de rúbrica (.csv)", type=["csv"], key="rubric_uploader")
        if uploaded_rubric_file is not None:
            try:
                df = pd.read_csv(uploaded_rubric_file, sep=';')
                st.write("**Vista Previa de la Rúbrica Cargada:**"); st.dataframe(df)
                if st.button("Usar Rúbrica Cargada"):
                    st.session_state.rubric = parse_rubric_csv(df)
                    st.session_state.app_mode = 'grading'
                    st.rerun()
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}.")

elif st.session_state.app_mode == 'grading':
    st.header("Paso 2: Cargar Lista del Curso")
    uploaded_students = st.file_uploader("Sube el archivo .csv con la lista de estudiantes", type=["csv"])
    if uploaded_students:
        df_students = pd.read_csv(uploaded_students, encoding='latin1')
        student_list = df_students['NOMBRE COMPLETO'].tolist()
        st.header("Paso 3: Seleccionar Grupo y Calificar")
        if 'current_group' not in st.session_state: st.session_state.current_group = []
        col_select, col_group = st.columns(2)
        with col_select:
            selected_student = st.selectbox("Elige un estudiante:", student_list)
            if st.button("➕ Agregar Estudiante"):
                if selected_student not in st.session_state.current_group: st.session_state.current_group.append(selected_student)
        with col_group:
            st.write("**Grupo Actual:**", ", ".join(st.session_state.current_group) or "Ninguno")
            if st.button("🗑️ Limpiar Grupo"):
                st.session_state.current_group, st.session_state.final_grade, st.session_state.calificaciones_data = [], None, None
                st.rerun()
        student_names_str = ", ".join(st.session_state.current_group)
        st.markdown("---")
        calificaciones, optional_comments, total_peso = {}, {}, sum(p['peso'] for p in st.session_state.rubric)
        with st.form("grading_form"):
            for pregunta_data in st.session_state.rubric:
                pregunta = pregunta_data['pregunta']
                st.markdown(f"#### {pregunta}")
                calificaciones[pregunta] = {}
                # --- CAMBIO IMPORTANTE: max_value AHORA ES 5.0 ---
                # Cada sub-item se califica de 0 a 5
                cols = st.columns(len(pregunta_data['sub_items'])) if pregunta_data['sub_items'] else [st]
                for i, sub_item in enumerate(pregunta_data['sub_items']):
                    with cols[i]:
                        calificaciones[pregunta][sub_item] = st.number_input(label=sub_item, min_value=0.0, max_value=5.0, step=0.5, key=f"{pregunta}_{sub_item}")
                optional_comments[pregunta] = st.text_input("Comentario opcional para este enunciado:", key=f"comment_{pregunta}")
            st.markdown("---")
            final_comment = st.text_area("Comentario Final (Obligatorio):", height=150)
            firmar_documento = st.checkbox("Incluir firma del docente en el reporte")
            submitted = st.form_submit_button("Calcular Nota Final y Guardar")
        if submitted:
            if not final_comment.strip():
                st.error("¡Error! El comentario final es obligatorio.")
                st.stop()

            # --- LÓGICA DE CÁLCULO COMPLETAMENTE CORREGIDA ---
            final_score_ponderado = 0
            promedios_por_pregunta = {} # Para el reporte PDF
            
            for pregunta_data in st.session_state.rubric:
                pregunta, peso = pregunta_data['pregunta'], pregunta_data['peso']
                
                # 1. Calcular el promedio de las competencias (sub-items) para esta pregunta
                scores_sub_items = calificaciones[pregunta].values()
                num_sub_items = len(scores_sub_items)
                
                if num_sub_items > 0:
                    promedio_pregunta = sum(scores_sub_items) / num_sub_items
                else:
                    promedio_pregunta = 0
                
                promedios_por_pregunta[pregunta] = promedio_pregunta
                
                # 2. Sumar al puntaje final ponderado
                final_score_ponderado += promedio_pregunta * peso

            # 3. Normalizar el resultado final
            if total_peso > 0:
                nota_final = final_score_ponderado / total_peso
            else:
                nota_final = 0.0

            st.session_state.final_grade, st.session_state.calificaciones_data = nota_final, calificaciones
            st.metric("Calificación Final Calculada", f"{st.session_state.final_grade:.2f} / 5.0")
            
            if st.session_state.current_group:
                guardar_nota(st.session_state.current_group, st.session_state.final_grade)
                st.success(f"¡Calificación guardada individualmente en '{GRADEBOOK_FILE}'!")
                datos_reporte = {"nombres": student_names_str, "calificacion_final": st.session_state.final_grade, "rubrica": st.session_state.rubric, "calificaciones": st.session_state.calificaciones_data, "firmar": firmar_documento, "optional_comments": optional_comments, "final_comment": final_comment, "promedios_por_pregunta": promedios_por_pregunta}
                pdf_data = generar_reporte_dinamico_pdf(datos_reporte)
                st.download_button(label="📥 Descargar Reporte en PDF", data=pdf_data, file_name=f"calificacion_{student_names_str.replace(' ', '_')}.pdf", mime="application/pdf")
            else:
                st.warning("Por favor, selecciona al menos un estudiante para guardar la nota.")