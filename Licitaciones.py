import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Licitaciones Médicas",
    page_icon="🏥",
    layout="wide"
)

# =============================================================================
# FUNCIONES PRINCIPALES
# =============================================================================

def normalizar_texto(texto):
    """Normaliza texto para búsqueda"""
    if pd.isna(texto) or texto is None:
        return ""
    
    texto_str = str(texto).lower()
    # Eliminar acentos básicos
    acentos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n'}
    for acento, sin_acento in acentos.items():
        texto_str = texto_str.replace(acento, sin_acento)
    
    # Limpiar caracteres especiales
    texto_str = re.sub(r'[^\w\s]', ' ', texto_str)
    texto_str = re.sub(r'\s+', ' ', texto_str)
    
    return texto_str.strip()

def extraer_productos_medicos(descripcion):
    """Extrae productos médicos de la descripción"""
    if pd.isna(descripcion):
        return []
    
    texto = normalizar_texto(descripcion)
    productos = []
    
    # Patrones para detectar cantidad + producto
    patrones = [
        r'(\d+)\s+(\w+.*?)(?=\d+\s+\w+|$)',  # 100 paracetamol, 50 gasas
        r'(\d+)\s*([a-z\s]+?)(?=,|$)'        # 100 paracetamol, 50 gasas
    ]
    
    for patron in patrones:
        matches = re.findall(patron, texto)
        for match in matches:
            try:
                cantidad = int(match[0])
                nombre = match[1].strip()
                
                if cantidad > 0 and len(nombre) > 2:
                    categoria = clasificar_producto_medico(nombre)
                    if categoria:
                        productos.append({
                            'nombre': categoria,
                            'cantidad': cantidad,
                            'descripcion_original': nombre,
                            'categoria': determinar_categoria(categoria)
                        })
            except:
                continue
    
    return productos

def clasificar_producto_medico(nombre):
    """Clasifica productos médicos"""
    nombre_lower = nombre.lower()
    
    # Mapeo de productos médicos comunes
    productos_medicos = {
        'paracetamol': ['paracetamol', 'acetaminofen'],
        'ibuprofeno': ['ibuprofeno', 'advil'],
        'aspirina': ['aspirina', 'acido acetilsalicilico'],
        'amoxicilina': ['amoxicilina'],
        'alcohol': ['alcohol', 'alcohol etilico'],
        'gasas': ['gasas', 'gasa', 'compresas'],
        'vendas': ['vendas', 'venda', 'vendaje'],
        'jeringas': ['jeringas', 'jeringa', 'jeringuilla'],
        'agujas': ['agujas', 'aguja'],
        'guantes': ['guantes', 'guante'],
        'mascarillas': ['mascarillas', 'mascarilla', 'cubrebocas'],
        'suero_fisiologico': ['suero', 'solucion salina', 'suero fisiologico'],
        'dextrosa': ['dextrosa', 'glucosa'],
        'termometro': ['termometro'],
        'estetoscopio': ['estetoscopio', 'fonendoscopio'],
        'tensiómetro': ['tensiometro', 'baumanometro'],
        'oximetro': ['oximetro', 'pulsioximetro'],
        'microscopio': ['microscopio'],
        'yodo': ['yodo', 'povidona'],
        'batas': ['batas', 'bata'],
        'gorros': ['gorros', 'gorro'],
        'cloro': ['cloro', 'hipoclorito'],
        'desinfectante': ['desinfectante'],
        'insulina': ['insulina'],
        'morfina': ['morfina'],
        'tramadol': ['tramadol'],
        'omeprazol': ['omeprazol'],
        'losartan': ['losartan'],
        'metformina': ['metformina']
    }
    
    for producto, variantes in productos_medicos.items():
        if any(variante in nombre_lower for variante in variantes):
            return producto
    
    return None

def determinar_categoria(producto):
    """Determina la categoría médica del producto"""
    categorias = {
        'paracetamol': 'Medicamentos',
        'ibuprofeno': 'Medicamentos', 
        'aspirina': 'Medicamentos',
        'amoxicilina': 'Medicamentos',
        'insulina': 'Medicamentos',
        'morfina': 'Medicamentos',
        'tramadol': 'Medicamentos',
        'omeprazol': 'Medicamentos',
        'losartan': 'Medicamentos',
        'metformina': 'Medicamentos',
        'gasas': 'Material de Curación',
        'vendas': 'Material de Curación',
        'alcohol': 'Material de Curación',
        'yodo': 'Material de Curación',
        'jeringas': 'Dispositivos Médicos',
        'agujas': 'Dispositivos Médicos',
        'guantes': 'Equipo de Protección',
        'mascarillas': 'Equipo de Protección',
        'batas': 'Equipo de Protección',
        'gorros': 'Equipo de Protección',
        'suero_fisiologico': 'Sueros y Soluciones',
        'dextrosa': 'Sueros y Soluciones',
        'termometro': 'Equipos Médicos',
        'estetoscopio': 'Equipos Médicos',
        'tensiómetro': 'Equipos Médicos',
        'oximetro': 'Equipos Médicos',
        'microscopio': 'Equipos Médicos',
        'cloro': 'Productos de Limpieza',
        'desinfectante': 'Productos de Limpieza'
    }
    
    return categorias.get(producto, 'General')

def buscar_en_inventario(producto_buscado, inventario_df):
    """Busca un producto en el inventario"""
    if inventario_df.empty:
        return {
            'encontrado': False,
            'stock_disponible': 0,
            'producto_match': '',
            'lote': '',
            'caducidad': ''
        }
    
    nombre_buscar = producto_buscado['nombre']
    cantidad_necesaria = producto_buscado['cantidad']
    
    # Mapeo para búsqueda en inventario
    mapeo_busqueda = {
        'paracetamol': ['paracetamol', 'acetaminofen'],
        'ibuprofeno': ['ibuprofeno'],
        'gasas': ['gasas', 'gasa', 'compresas'],
        'alcohol': ['alcohol'],
        'jeringas': ['jeringas', 'jeringa'],
        'guantes': ['guantes'],
        'mascarillas': ['mascarillas', 'cubrebocas'],
        'suero_fisiologico': ['suero', 'salina'],
        'termometro': ['termometro']
    }
    
    terminos_busqueda = mapeo_busqueda.get(nombre_buscar, [nombre_buscar])
    
    # Buscar en el inventario
    for _, fila in inventario_df.iterrows():
        # Buscar en todas las columnas de texto
        texto_fila = ""
        for col in fila.index:
            if pd.notna(fila[col]):
                texto_fila += str(fila[col]).lower() + " "
        
        # Verificar si algún término coincide
        for termino in terminos_busqueda:
            if termino in texto_fila:
                # Obtener stock
                stock = 0
                for col_stock in ['stock', 'cantidad', 'existencia', 'disponible', 'inventario']:
                    if col_stock in fila.index and pd.notna(fila[col_stock]):
                        try:
                            stock = int(float(fila[col_stock]))
                            break
                        except:
                            continue
                
                # Obtener información adicional
                nombre_producto = str(fila.get('nombre', fila.get('producto', fila.get('descripcion', 'Producto'))))
                lote = str(fila.get('lote', fila.get('batch', '')))
                caducidad = str(fila.get('caducidad', fila.get('vencimiento', fila.get('expiry', ''))))
                
                return {
                    'encontrado': True,
                    'stock_disponible': stock,
                    'stock_suficiente': stock >= cantidad_necesaria,
                    'producto_match': nombre_producto,
                    'lote': lote,
                    'caducidad': caducidad
                }
    
    return {
        'encontrado': False,
        'stock_disponible': 0,
        'stock_suficiente': False,
        'producto_match': '',
        'lote': '',
        'caducidad': ''
    }

def verificar_caducidad(fecha_str):
    """Verifica si un producto está próximo a caducar"""
    if not fecha_str or pd.isna(fecha_str) or fecha_str == 'nan':
        return {'estado': 'sin_fecha', 'dias_restantes': None, 'alerta': False}
    
    try:
        # Intentar diferentes formatos de fecha
        formatos = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%Y/%m/%d']
        fecha_cad = None
        
        for formato in formatos:
            try:
                fecha_cad = datetime.strptime(str(fecha_str).strip(), formato)
                break
            except:
                continue
        
        if not fecha_cad:
            return {'estado': 'formato_invalido', 'dias_restantes': None, 'alerta': False}
        
        dias_restantes = (fecha_cad - datetime.now()).days
        
        if dias_restantes < 0:
            return {'estado': 'caducado', 'dias_restantes': dias_restantes, 'alerta': True}
        elif dias_restantes <= 30:
            return {'estado': 'proximo_caducar', 'dias_restantes': dias_restantes, 'alerta': True}
        elif dias_restantes <= 90:
            return {'estado': 'vigilar', 'dias_restantes': dias_restantes, 'alerta': False}
        else:
            return {'estado': 'vigente', 'dias_restantes': dias_restantes, 'alerta': False}
    except:
        return {'estado': 'error', 'dias_restantes': None, 'alerta': False}

def evaluar_licitacion(fila, inventario_df):
    """Evalúa una licitación completa"""
    resultado = {
        'estado': 'verde',
        'observaciones': [],
        'productos_analizados': 0,
        'productos_con_stock': 0,
        'productos_sin_stock': [],
        'productos_con_stock_insuficiente': [],
        'productos_disponibles': [],
        'alertas_caducidad': [],
        'categorias_productos': {}
    }
    
    # Obtener descripción de la licitación
    descripcion = ""
    for col in ['descripcion', 'detalle', 'productos', 'items', 'especificaciones']:
        if col in fila.index and pd.notna(fila[col]):
            descripcion += str(fila[col]) + " "
    
    if not descripcion.strip():
        resultado['estado'] = 'amarillo'
        resultado['observaciones'].append("Sin descripción de productos")
        return resultado
    
    # Extraer productos
    productos = extraer_productos_medicos(descripcion)
    
    if not productos:
        resultado['estado'] = 'amarillo'
        resultado['observaciones'].append("No se identificaron productos médicos")
        return resultado
    
    resultado['productos_analizados'] = len(productos)
    
    # Evaluar cada producto
    for producto in productos:
        categoria = producto['categoria']
        if categoria not in resultado['categorias_productos']:
            resultado['categorias_productos'][categoria] = {'total': 0, 'disponibles': 0}
        resultado['categorias_productos'][categoria]['total'] += 1
        
        busqueda = buscar_en_inventario(producto, inventario_df)
        
        if busqueda['encontrado']:
            # Verificar caducidad
            info_caducidad = verificar_caducidad(busqueda['caducidad'])
            
            if busqueda['stock_suficiente']:
                resultado['productos_con_stock'] += 1
                resultado['categorias_productos'][categoria]['disponibles'] += 1
                
                producto_info = {
                    'nombre': producto['nombre'].replace('_', ' ').title(),
                    'cantidad_requerida': producto['cantidad'],
                    'stock_disponible': busqueda['stock_disponible'],
                    'producto_inventario': busqueda['producto_match'],
                    'categoria': categoria,
                    'lote': busqueda['lote'],
                    'caducidad': busqueda['caducidad']
                }
                
                if info_caducidad['alerta']:
                    resultado['alertas_caducidad'].append({
                        'producto': producto['nombre'],
                        'estado': info_caducidad['estado'],
                        'dias': info_caducidad['dias_restantes']
                    })
                    producto_info['alerta_caducidad'] = info_caducidad
                
                resultado['productos_disponibles'].append(producto_info)
            else:
                # Stock insuficiente
                resultado['productos_con_stock_insuficiente'].append({
                    'nombre': producto['nombre'].replace('_', ' ').title(),
                    'cantidad_requerida': producto['cantidad'],
                    'stock_disponible': busqueda['stock_disponible'],
                    'faltante': producto['cantidad'] - busqueda['stock_disponible'],
                    'categoria': categoria
                })
        else:
            # No encontrado en inventario
            resultado['productos_sin_stock'].append({
                'nombre': producto['nombre'].replace('_', ' ').title(),
                'cantidad_requerida': producto['cantidad'],
                'categoria': categoria
            })
    
    # Determinar estado final
    if resultado['productos_sin_stock']:
        resultado['estado'] = 'rojo'
    elif resultado['productos_con_stock_insuficiente'] or resultado['alertas_caducidad']:
        resultado['estado'] = 'amarillo'
    
    # Generar observaciones
    observaciones = []
    
    if resultado['productos_sin_stock']:
        nombres = [p['nombre'] for p in resultado['productos_sin_stock'][:3]]
        observaciones.append(f"Sin inventario: {', '.join(nombres)}")
    
    if resultado['productos_con_stock_insuficiente']:
        nombres = [f"{p['nombre']} (faltan {p['faltante']})" for p in resultado['productos_con_stock_insuficiente'][:2]]
        observaciones.append(f"Stock insuficiente: {', '.join(nombres)}")
    
    if resultado['alertas_caducidad']:
        caducados = [a for a in resultado['alertas_caducidad'] if a['estado'] == 'caducado']
        if caducados:
            observaciones.append(f"Productos caducados: {len(caducados)}")
        else:
            observaciones.append(f"Próximos a caducar: {len(resultado['alertas_caducidad'])}")
    
    if not observaciones and resultado['productos_disponibles']:
        observaciones.append(f"Todos los productos disponibles ({len(resultado['productos_disponibles'])})")
    
    # Estadística general
    porcentaje = (resultado['productos_con_stock'] / resultado['productos_analizados']) * 100 if resultado['productos_analizados'] > 0 else 0
    observaciones.append(f"Disponibilidad: {porcentaje:.0f}%")
    
    resultado['observaciones'] = observaciones
    
    return resultado

# =============================================================================
# INTERFAZ DE USUARIO
# =============================================================================

st.title("🏥 Sistema de Licitaciones Médicas")
st.markdown("**Análisis especializado de licitaciones médicas vs inventario hospitalario**")

# Sidebar
with st.sidebar:
    st.header("📁 Carga de Archivos")
    
    archivo_licitaciones = st.file_uploader(
        "Archivo de Licitaciones Médicas",
        type=['csv', 'xlsx', 'xls'],
        help="Archivo con las licitaciones médicas a analizar"
    )
    
    archivo_inventario = st.file_uploader(
        "Archivo de Inventario Médico", 
        type=['csv', 'xlsx', 'xls'],
        help="Archivo con el inventario médico disponible"
    )
    
    if archivo_licitaciones and archivo_inventario:
        st.success("✅ Archivos cargados correctamente")
    
    st.markdown("---")
    st.markdown("### ⚙️ Configuración")
    
    mostrar_detalles = st.checkbox("Mostrar análisis detallado", True)
    mostrar_debug = st.checkbox("Mostrar información de debug", False)

# Verificar archivos
if not archivo_licitaciones or not archivo_inventario:
    st.info("👆 Por favor, carga ambos archivos para comenzar el análisis.")
    
    with st.expander("📖 Guía de uso"):
        st.markdown("""
        ### Estructura esperada de archivos:
        
        **Licitaciones:**
        - Debe contener columnas como: nombre, descripcion, detalle, productos
        - Ejemplo: "100 paracetamol, 50 gasas esteriles, 20 jeringas"
        
        **Inventario:**
        - Debe contener: nombre/producto, stock/cantidad, lote, caducidad
        - Ejemplo: nombre="Paracetamol 500mg", stock=200, lote="L001", caducidad="2025-12-31"
        """)
    
    st.stop()

# Cargar y procesar archivos
try:
    # Cargar licitaciones
    if archivo_licitaciones.name.endswith('.csv'):
        licitaciones_df = pd.read_csv(archivo_licitaciones)
    else:
        licitaciones_df = pd.read_excel(archivo_licitaciones)
    
    # Cargar inventario
    if archivo_inventario.name.endswith('.csv'):
        inventario_df = pd.read_csv(archivo_inventario)
    else:
        inventario_df = pd.read_excel(archivo_inventario)
    
    # Limpiar datos
    licitaciones_df = licitaciones_df.dropna(how='all')
    inventario_df = inventario_df.dropna(how='all')
    
    st.success(f"📊 Datos cargados: {len(licitaciones_df)} licitaciones, {len(inventario_df)} productos en inventario")
    
except Exception as e:
    st.error(f"❌ Error al cargar archivos: {str(e)}")
    st.stop()

# Debug información
if mostrar_debug:
    with st.expander("🔍 Información de Debug"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Columnas en Licitaciones:**")
            st.write(list(licitaciones_df.columns))
            st.write("**Muestra de datos:**")
            st.dataframe(licitaciones_df.head(3))
        
        with col2:
            st.write("**Columnas en Inventario:**")
            st.write(list(inventario_df.columns))
            st.write("**Muestra de datos:**")
            st.dataframe(inventario_df.head(3))

# Botón de análisis
if st.button("🔍 Analizar Licitaciones Médicas", type="primary"):
    with st.spinner("Analizando licitaciones médicas..."):
        resultados = []
        evaluaciones_detalladas = []
        
        # Procesar cada licitación
        for idx, fila in licitaciones_df.iterrows():
            evaluacion = evaluar_licitacion(fila, inventario_df)
            evaluaciones_detalladas.append(evaluacion)
            
            # Obtener nombre de licitación
            nombre_licitacion = "Sin nombre"
            for col in ['nombre', 'titulo', 'licitacion', 'descripcion']:
                if col in fila.index and pd.notna(fila[col]):
                    nombre_licitacion = str(fila[col])[:60]
                    break
            
            # Preparar resultado para tabla
            resultado = {
                'ID': idx + 1,
                'Licitación': nombre_licitacion,
                'Estado': evaluacion['estado'].upper(),
                'Productos': evaluacion['productos_analizados'],
                'Disponibles': evaluacion['productos_con_stock'],
                'Sin_Stock': len(evaluacion['productos_sin_stock']),
                'Stock_Insuficiente': len(evaluacion['productos_con_stock_insuficiente']),
                'Alertas_Caducidad': len(evaluacion['alertas_caducidad']),
                'Observaciones': ' | '.join(evaluacion['observaciones'])
            }
            resultados.append(resultado)
        
        # Crear DataFrame de resultados
        if resultados:
            resultados_df = pd.DataFrame(resultados)
            
            # Métricas principales
            total = len(resultados_df)
            verdes = len(resultados_df[resultados_df['Estado'] == 'VERDE'])
            amarillos = len(resultados_df[resultados_df['Estado'] == 'AMARILLO'])
            rojos = len(resultados_df[resultados_df['Estado'] == 'ROJO'])
            
            st.markdown("### 📈 Resumen Ejecutivo")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Licitaciones", total)
            col2.metric("✅ Aptas", verdes, f"{verdes/total*100:.1f}%")
            col3.metric("⚠️ Revisar", amarillos, f"{amarillos/total*100:.1f}%")
            col4.metric("❌ No Aptas", rojos, f"{rojos/total*100:.1f}%")
            
            # Alertas importantes
            total_alertas = resultados_df['Alertas_Caducidad'].sum()
            if total_alertas > 0:
                st.warning(f"⚠️ {total_alertas} productos con alertas de caducidad detectados")
            
            # Tabla de resultados
            st.subheader("📋 Resultados por Licitación")
            
            # Mapear estados a emojis
            resultados_display = resultados_df.copy()
            resultados_display['Estado'] = resultados_display['Estado'].map({
                'VERDE': '🟢 APTA',
                'AMARILLO': '🟡 REVISAR', 
                'ROJO': '🔴 NO APTA'
            })
            
            st.dataframe(resultados_display, use_container_width=True)
            
            # Análisis detallado
            if mostrar_detalles:
                st.subheader("🔍 Análisis Detallado por Licitación")
                
                for idx, evaluacion in enumerate(evaluaciones_detalladas):
                    nombre_lic = resultados[idx]['Licitación']
                    estado = evaluacion['estado']
                    
                    emoji = "🟢" if estado == "verde" else ("🟡" if estado == "amarillo" else "🔴")
                    
                    with st.expander(f"{emoji} Licitación {idx+1}: {nombre_lic}"):
                        
                        # Alertas de caducidad (prioritario)
                        if evaluacion['alertas_caducidad']:
                            st.markdown("#### ⚠️ Alertas de Caducidad:")
                            for alerta in evaluacion['alertas_caducidad']:
                                if alerta['estado'] == 'caducado':
                                    st.error(f"🚨 **{alerta['producto']}** - CADUCADO (venció hace {abs(alerta['dias'])} días)")
                                else:
                                    st.warning(f"⏰ **{alerta['producto']}** - Caduca en {alerta['dias']} días")
                            st.markdown("---")
                        
                        # Productos sin stock
                        if evaluacion['productos_sin_stock']:
                            st.markdown("#### ❌ Productos NO Disponibles:")
                            for producto in evaluacion['productos_sin_stock']:
                                st.error(f"**{producto['nombre']}** - Cantidad: {producto['cantidad_requerida']} - Categoría: {producto['categoria']}")
                            st.markdown("---")
                        
                        # Productos con stock insuficiente
                        if evaluacion['productos_con_stock_insuficiente']:
                            st.markdown("#### ⚠️ Productos con Stock Insuficiente:")
                            for producto in evaluacion['productos_con_stock_insuficiente']:
                                st.warning(f"**{producto['nombre']}** - Requiere: {producto['cantidad_requerida']}, Disponible: {producto['stock_disponible']}, Faltan: {producto['faltante']}")
                            st.markdown("---")
                        
                        # Productos disponibles
                        if evaluacion['productos_disponibles']:
                            st.markdown("#### ✅ Productos Disponibles:")
                            for producto in evaluacion['productos_disponibles']:
                                lote_info = f" - Lote: {producto['lote']}" if producto['lote'] and producto['lote'] != 'nan' else ""
                                caducidad_info = f" - Caduca: {producto['caducidad']}" if producto['caducidad'] and producto['caducidad'] != 'nan' else ""
                                
                                st.success(f"**{producto['nombre']}** - Requiere: {producto['cantidad_requerida']}, Disponible: {producto['stock_disponible']}{lote_info}{caducidad_info}")
                        
                        # Resumen por categorías
                        if evaluacion['categorias_productos']:
                            st.markdown("---")
                            st.markdown("#### 📊 Resumen por Categoría:")
                            
                            for categoria, stats in evaluacion['categorias_productos'].items():
                                total_cat = stats['total']
                                disp_cat = stats['disponibles']
                                porcentaje = (disp_cat / total_cat) * 100 if total_cat > 0 else 0
                                
                                if porcentaje == 100:
                                    st.success(f"✅ **{categoria}**: {disp_cat}/{total_cat} productos ({porcentaje:.0f}%)")
                                elif porcentaje >= 50:
                                    st.warning(f"⚠️ **{categoria}**: {disp_cat}/{total_cat} productos ({porcentaje:.0f}%)")
                                else:
                                    st.error(f"❌ **{categoria}**: {disp_cat}/{total_cat} productos ({porcentaje:.0f}%)")
            
            # Descarga de resultados
            csv_resultado = resultados_df.to_csv(index=False)
            st.download_button(
                label="📥 Descargar Análisis Completo (CSV)",
                data=csv_resultado,
                file_name=f"analisis_licitaciones_medicas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            
            # Estadísticas adicionales
            st.markdown("### 📊 Estadísticas Generales")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Distribución por Estado:**")
                st.write(f"🟢 Aptas: {verdes} ({verdes/total*100:.1f}%)")
                st.write(f"🟡 Para revisar: {amarillos} ({amarillos/total*100:.1f}%)")
                st.write(f"🔴 No aptas: {rojos} ({rojos/total*100:.1f}%)")
            
            with col2:
                st.markdown("**Productos Analizados:**")
                total_productos = resultados_df['Productos'].sum()
                productos_disponibles = resultados_df['Disponibles'].sum()
                
                if total_productos > 0:
                    porcentaje_general = (productos_disponibles / total_productos) * 100
                    st.write(f"Total de productos: {total_productos}")
                    st.write(f"Productos disponibles: {productos_disponibles}")
                    st.write(f"Disponibilidad general: {porcentaje_general:.1f}%")
                
                if total_alertas > 0:
                    st.write(f"⚠️ Productos con alertas: {total_alertas}")
        
        else:
            st.error("No se pudieron procesar las licitaciones. Verifica el formato de los archivos.")

# Footer informativo
st.markdown("---")
st.markdown("### 💡 Información del Sistema")

with st.expander("📚 Productos Médicos Reconocidos"):
    st.markdown("""
    **El sistema reconoce automáticamente estos productos médicos:**
    
    **💊 Medicamentos:**
    - Analgésicos: paracetamol, ibuprofeno, aspirina
    - Antibióticos: amoxicilina
    - Otros: insulina, morfina, tramadol, omeprazol, losartán, metformina
    
    **🩹 Material de Curación:**
    - Gasas, vendas, alcohol, yodo
    
    **💉 Dispositivos Médicos:**
    - Jeringas, agujas
    
    **🛡️ Equipo de Protección:**
    - Guantes, mascarillas, batas, gorros
    
    **🧪 Sueros y Soluciones:**
    - Suero fisiológico, dextrosa
    
    **⚕️ Equipos Médicos:**
    - Termómetros, estetoscopios, tensiómetros, oxímetros, microscopios
    
    **🧽 Productos de Limpieza:**
    - Cloro, desinfectantes
    """)

with st.expander("🔧 Cómo Funciona el Sistema"):
    st.markdown("""
    **Proceso de análisis:**
    
    1. **Extracción:** El sistema busca patrones como "100 paracetamol" en las descripciones
    2. **Clasificación:** Identifica y categoriza cada producto médico automáticamente
    3. **Búsqueda:** Localiza productos similares en el inventario usando sinónimos
    4. **Evaluación:** Compara cantidades requeridas vs stock disponible
    5. **Alertas:** Verifica fechas de caducidad y genera alertas tempranas
    6. **Resultados:** Clasifica cada licitación como Apta, Para Revisar, o No Apta
    
    **Estados de las licitaciones:**
    - 🟢 **Apta:** Todos los productos disponibles con stock suficiente
    - 🟡 **Para Revisar:** Stock insuficiente o productos próximos a caducar
    - 🔴 **No Apta:** Productos no disponibles en inventario
    """)

st.markdown("""
**🏥 Sistema de Licitaciones Médicas v2.0**  
*Desarrollado para análisis especializado del sector salud*
""")