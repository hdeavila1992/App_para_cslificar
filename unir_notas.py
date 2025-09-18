import streamlit as st
import pandas as pd
import io

# Configuración de la página de la aplicación
st.set_page_config(layout="wide", page_title="Unificador de Calificaciones", page_icon="🔗")

# Título y descripción
st.title("🔗 Unificador de Archivos de Calificaciones")
st.write(
    "Esta herramienta te permite cargar dos archivos CSV de calificaciones y unirlos en uno solo. "
    "La unión se hace por la columna 'Estudiante'. Si un estudiante falta en uno de los archivos, "
    "su nota aparecerá en blanco en la columna correspondiente."
)

st.markdown("---")

# Columnas para cargar los archivos
col1, col2 = st.columns(2)

with col1:
    st.subheader("Archivo 1: Calificaciones Finales")
    file1 = st.file_uploader("Carga el archivo `calificaciones_finales.csv`", type=["csv"], key="file1")

with col2:
    st.subheader("Archivo 2: Tarea 1")
    file2 = st.file_uploader("Carga el archivo `calificaciones_finales_tarea_1.csv`", type=["csv"], key="file2")

# Lógica para procesar y unir los archivos una vez que ambos han sido cargados
if file1 is not None and file2 is not None:
    try:
        # Cargar los archivos CSV en DataFrames de pandas
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)

        # Renombrar las columnas de calificación para que sean únicas y claras
        df1 = df1.rename(columns={"Calificacion Final": "Nota Final", "Estudiante": "Estudiante"})
        df2 = df2.rename(columns={"Calificacion Final": "Nota Tarea 1", "Estudiante": "Estudiante"})
        
        # Eliminar la columna 'Fecha' si existe
        if 'Fecha' in df1.columns:
            df1 = df1.drop(columns=['Fecha'])
        if 'Fecha' in df2.columns:
            df2 = df2.drop(columns=['Fecha'])
        
        # Unir los dos DataFrames
        merged_df = pd.merge(df1, df2, on="Estudiante", how="outer")

        st.markdown("---")
        st.success("✅ ¡Archivos unidos exitosamente! Aquí está el resultado consolidado:")
        
        # Mostrar la tabla con los resultados
        st.dataframe(merged_df.fillna(''))

        # Preparar el archivo para la descarga
        output = io.StringIO()
        
        # --- LÍNEA MODIFICADA AQUÍ ---
        # Se agrega el parámetro 'decimal=","' para usar comas en los números decimales.
        merged_df.to_csv(output, index=False, decimal=',')
        
        csv_data = output.getvalue()

        # Botón para descargar el archivo CSV consolidado
        st.download_button(
            label="📥 Descargar Archivo Consolidado (.csv)",
            data=csv_data,
            file_name="calificaciones_consolidadas_con_comas.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"Ocurrió un error al procesar los archivos: {e}")
        st.warning("Por favor, asegúrate de que ambos archivos tienen una columna llamada 'Estudiante'.")