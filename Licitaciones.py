import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import re
import warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Filtro de Licitaciones MVP",
    page_icon="📋",
    layout="wide"
)

def normalizar_texto_completo(texto):
    """Normaliza texto de manera simple y efectiva"""
    if pd.isna(texto) or texto is None:
        return ""
    
    # Convertir a string
    texto_str = str(texto)
    
    # Eliminar acentos de manera simple
    acentos = {
        'á': 'a', 'à': 'a', 'ä': 'a', 'â': 'a',
        'é': 'e', 'è': 'e', 'ë': 'e', 'ê': 'e',
        'í': 'i', 'ì': 'i', 'ï': 'i', 'î': 'i',
        'ó': 'o', 'ò': 'o', 'ö': 'o', 'ô': 'o',
        'ú': 'u', 'ù': 'u', 'ü': 'u', 'û': 'u',
        'ñ': 'n'
    }
    
    for acento, sin_acento in acentos.items():
        texto_str = texto_str.replace(acento, sin_acento)
        texto_str = texto_str.replace(acento.upper(), sin_acento.upper())
    
    # Convertir a minúsculas y limpiar
    texto_str = texto_str.lower()
    texto_str = re.sub(r'[^\w\s,]', ' ', texto_str)  # Solo letras, números, espacios y comas
    texto_str = re.sub(r'\s+', ' ', texto_str)  # Normalizar espacios
    
    return texto_str.strip()

def obtener_productos_de_descripcion(texto):
    """Extrae productos de texto usando método simple y probado"""
    if pd.isna(texto) or texto is None:
        return []
    
    # Normalizar texto
    texto_limpio = normalizar_texto_completo(texto)
    
    if not texto_limpio:
        return []
    
    # Dividir por comas para procesar cada producto
    segmentos = [s.strip() for s in texto_limpio.split(',') if s.strip()]
    
    productos = []
    
    for segmento in segmentos:
        # Buscar patrón: número + palabras
        match = re.match(r'^(\d+)\s+(.+)$', segmento)
        
        if match:
            try:
                cantidad = int(match.group(1))
                nombre_crudo = match.group(2).strip()
                
                # Validar cantidad
                if cantidad <= 0 or cantidad > 50000:
                    continue
                
                # Clasificar producto
                categoria = clasificar_producto_simple(nombre_crudo)
                
                if categoria != 'desconocido':
                    productos.append({
                        'nombre': categoria,
                        'cantidad': cantidad,
                        'nombre_original': nombre_crudo,
                        'unidad': 'unidad'
                    })
            except:
                continue
    
    return productos

def clasificar_producto_simple(nombre):
    """Clasifica productos usando mapeo directo simple"""
    if not nombre:
        return 'desconocido'
    
    nombre_lower = nombre.lower()
    
    # Mapeo directo basado en inventario real
    clasificaciones = {
        'computadora': ['computadora', 'pc'],
        'proyector': ['proyector'],
        'papel': ['resma', 'papel', 'hoja'],
        'boligrafo': ['boligrafo', 'lapicero', 'pluma'],
        'carpeta': ['carpeta', 'folder'],
        'pupitre': ['pupitre'],
        'pizarron': ['pizarron', 'pizarra'],
        'escritorio': ['escritorio', 'mesa'],
        'silla': ['silla', 'asiento'],
        'cubrebocas': ['cubrebocas', 'mascarilla'],
        'guantes': ['guantes'],
        'microscopio': ['microscopio'],
        'centrifuga': ['centrifuga'],
        'cloro': ['cloro'],
        'jabon': ['jabon', 'soap'],
        'trapeador': ['trapeador', 'mop'],
        'servidor': ['servidor', 'server'],
        'switch': ['switch'],
        'lapiz': ['lapiz'],
        'marcador': ['marcador'],
        'litros': ['litros']  # Para manejar "200 litros cloro"
    }
    
    # Buscar coincidencia
    for categoria, palabras_clave in clasificaciones.items():
        if any(palabra in nombre_lower for palabra in palabras_clave):
            return categoria
    
    return 'desconocido'

def buscar_en_inventario(producto_buscado, inventario_df):
    """Busca producto en inventario con algoritmo simple y efectivo"""
    if inventario_df.empty:
        return {'encontrado': False, 'stock_disponible': 0, 'stock_suficiente': False, 'producto_match': '', 'score': 0}
    
    nombre_buscar = producto_buscado['nombre'].lower()
    cantidad_necesaria = producto_buscado['cantidad']
    
    # Mapeo de categorías a productos del inventario real
    mapeo_inventario = {
        'computadora': ['Computadora Dell OptiPlex'],
        'proyector': ['Proyector Epson'],
        'papel': ['Papel Bond Carta'],
        'boligrafo': ['Bolígrafos azules Bic'],
        'carpeta': ['Carpeta tamaño carta'],
        'pupitre': ['Pupitre metálico'],
        'pizarron': ['Pizarrón blanco'],
        'escritorio': ['Escritorio ejecutivo'],
        'silla': ['Silla ergonómica ejecutiva'],
        'cubrebocas': ['Cubrebocas tricapa'],
        'guantes': ['Guantes de látex talla M'],
        'microscopio': ['Microscopio óptico'],
        'centrifuga': ['Centrífuga de mesa'],
        'cloro': ['Cloro'],
        'jabon': ['Jabón líquido'],
        'trapeador': ['Trapeador industrial'],
        'servidor': ['Servidor Dell PowerEdge'],
        'switch': ['Switch Cisco 24 puertos'],
        'lapiz': ['Lápiz HB'],
        'marcador': ['Marcador permanente'],
        'litros': ['Cloro']  # Para casos especiales como "200 litros cloro"
    }
    
    # Buscar coincidencia directa
    productos_match = mapeo_inventario.get(nombre_buscar, [])
    
    if not productos_match:
        # Si no encuentra mapeo directo, buscar por similitud en el inventario
        return buscar_por_similitud(nombre_buscar, cantidad_necesaria, inventario_df)
    
    # Buscar en inventario real
    for _, fila in inventario_df.iterrows():
        nombre_inventario = str(fila.get('nombre', '')).strip()
        
        for producto_esperado in productos_match:
            if producto_esperado.lower() in nombre_inventario.lower():
                # Encontrado! Obtener stock
                stock_disponible = 0
                for col_stock in ['stock', 'existencia', 'cantidad', 'disponible']:
                    if col_stock in fila and pd.notna(fila[col_stock]):
                        try:
                            stock_disponible = int(float(fila[col_stock]))
                            break
                        except:
                            continue
                
                return {
                    'encontrado': True,
                    'stock_disponible': stock_disponible,
                    'stock_suficiente': stock_disponible >= cantidad_necesaria,
                    'producto_match': nombre_inventario,
                    'score': 0.9
                }
    
    return {'encontrado': False, 'stock_disponible': 0, 'stock_suficiente': False, 'producto_match': '', 'score': 0}

def buscar_por_similitud(nombre_buscar, cantidad_necesaria, inventario_df):
    """Busca por similitud cuando no hay mapeo directo"""
    mejor_match = None
    mejor_score = 0
    
    for _, fila in inventario_df.iterrows():
        nombre_item = str(fila.get('nombre', '')).lower()
        desc_item = str(fila.get('descripcion', '')).lower()
        texto_completo = f"{nombre_item} {desc_item}"
        
        # Calcular similitud simple
        score = 0
        if nombre_buscar in texto_completo:
            score = 0.8
        elif any(palabra in texto_completo for palabra in nombre_buscar.split()):
            score = 0.6
        
        if score > mejor_score:
            # Obtener stock
            stock_disponible = 0
            for col_stock in ['stock', 'existencia', 'cantidad', 'disponible']:
                if col_stock in fila and pd.notna(fila[col_stock]):
                    try:
                        stock_disponible = int(float(fila[col_stock]))
                        break
                    except:
                        continue
            
            mejor_score = score
            mejor_match = {
                'stock': stock_disponible,
                'nombre': str(fila.get('nombre', ''))
            }
    
    if mejor_match and mejor_score >= 0.6:
        return {
            'encontrado': True,
            'stock_disponible': mejor_match['stock'],
            'stock_suficiente': mejor_match['stock'] >= cantidad_necesaria,
            'producto_match': mejor_match['nombre'],
            'score': mejor_score
        }
    
    return {'encontrado': False, 'stock_disponible': 0, 'stock_suficiente': False, 'producto_match': '', 'score': 0}

def consolidar_productos(productos_lista):
    """Consolida productos duplicados de manera simple"""
    if not productos_lista:
        return []
    
    # Diccionario para consolidar
    productos_consolidados = {}
    
    for producto in productos_lista:
        nombre = producto['nombre']
        if nombre in productos_consolidados:
            # Sumar cantidades
            productos_consolidados[nombre]['cantidad'] += producto['cantidad']
        else:
            # Agregar nuevo producto
            productos_consolidados[nombre] = producto.copy()
    
    return list(productos_consolidados.values())

def evaluar_licitacion(fila, inventario_df):
    """Evalúa una licitación contra el inventario mostrando TODOS los productos con problemas"""
    resultado = {
        'estado': 'verde',
        'observaciones': [],
        'productos_analizados': 0,
        'productos_encontrados': 0,
        'productos_con_stock': 0,
        'productos_sin_inventario': [],
        'productos_stock_insuficiente': [],
        'productos_disponibles': []
    }
    
    # Buscar texto de productos en múltiples columnas
    texto_productos = ""
    columnas_descripcion = ['descripcion', 'detalle', 'productos', 'items', 'especificaciones']
    
    for col in columnas_descripcion:
        if col in fila and pd.notna(fila[col]):
            texto_productos += str(fila[col]) + " "
    
    if not texto_productos.strip():
        resultado['estado'] = 'amarillo'
        resultado['observaciones'].append("⚠️ Sin descripción de productos")
        return resultado
    
    # Extraer productos usando función mejorada
    productos_requeridos = obtener_productos_de_descripcion(texto_productos)
    
    if not productos_requeridos:
        resultado['estado'] = 'amarillo'
        resultado['observaciones'].append("⚠️ No se identificaron productos específicos")
        return resultado
    
    resultado['productos_analizados'] = len(productos_requeridos)
    
    # Evaluar cada producto específicamente
    for producto in productos_requeridos:
        busqueda = buscar_en_inventario(producto, inventario_df)
        producto_nombre = producto['nombre'].replace('_', ' ').title()
        cantidad_req = producto['cantidad']
        
        if busqueda['encontrado']:
            resultado['productos_encontrados'] += 1
            stock_disp = busqueda['stock_disponible']
            
            if busqueda['stock_suficiente']:
                resultado['productos_con_stock'] += 1
                resultado['productos_disponibles'].append({
                    'nombre': producto_nombre,
                    'requerido': cantidad_req,
                    'disponible': stock_disp,
                    'sobra': stock_disp - cantidad_req
                })
            else:
                faltante = cantidad_req - stock_disp
                resultado['productos_stock_insuficiente'].append({
                    'nombre': producto_nombre,
                    'requerido': cantidad_req,
                    'disponible': stock_disp,
                    'falta': faltante,
                    'producto_inventario': busqueda['producto_match']
                })
        else:
            resultado['productos_sin_inventario'].append({
                'nombre': producto_nombre,
                'cantidad_requerida': cantidad_req
            })
    
    # Generar observaciones COMPLETAS mostrando TODOS los productos con problemas
    observaciones_detalladas = []
    
    # 1. TODOS los productos que NO existen en inventario
    if resultado['productos_sin_inventario']:
        resultado['estado'] = 'rojo'
        productos_sin_inv_texto = []
        for p in resultado['productos_sin_inventario']:
            productos_sin_inv_texto.append(f"{p['nombre']} ({p['cantidad_requerida']})")
        observaciones_detalladas.append(f"❌ NO EN INVENTARIO: {', '.join(productos_sin_inv_texto)}")
    
    # 2. TODOS los productos con stock insuficiente
    if resultado['productos_stock_insuficiente']:
        if resultado['estado'] == 'verde':
            resultado['estado'] = 'amarillo'
        
        productos_stock_insuf_texto = []
        for p in resultado['productos_stock_insuficiente']:
            productos_stock_insuf_texto.append(f"{p['nombre']}: FALTAN {p['falta']} (tiene {p['disponible']})")
        
        # Dividir en múltiples observaciones si hay muchos productos
        if len(productos_stock_insuf_texto) <= 3:
            observaciones_detalladas.append(f"⚠️ {', '.join(productos_stock_insuf_texto)}")
        else:
            # Primera observación con los primeros 3 productos
            observaciones_detalladas.append(f"⚠️ {', '.join(productos_stock_insuf_texto[:3])}")
            # Segunda observación con el resto
            observaciones_detalladas.append(f"⚠️ {', '.join(productos_stock_insuf_texto[3:])}")
    
    # 3. TODOS los productos disponibles (si no hay problemas)
    if resultado['productos_disponibles'] and not resultado['productos_sin_inventario'] and not resultado['productos_stock_insuficiente']:
        productos_ok_texto = []
        for p in resultado['productos_disponibles']:
            productos_ok_texto.append(f"{p['nombre']} ({p['requerido']})")
        observaciones_detalladas.append(f"✅ TODOS OK: {', '.join(productos_ok_texto)}")
    
    # 4. Estadística general (siempre mostrar)
    porcentaje_ok = (resultado['productos_con_stock'] / resultado['productos_analizados']) * 100 if resultado['productos_analizados'] > 0 else 0
    observaciones_detalladas.append(f"📊 {resultado['productos_con_stock']}/{resultado['productos_analizados']} productos OK ({porcentaje_ok:.0f}%)")
    
    resultado['observaciones'] = observaciones_detalladas
    return resultado

# NUEVAS FUNCIONES PARA REQUERIMIENTOS DOCUMENTALES

def obtener_requerimientos_documentales(nombre_licitacion, requerimientos_df):
    """Obtiene los documentos requeridos para una licitación específica"""
    if requerimientos_df is None or requerimientos_df.empty:
        return []
    
    # Normalizar nombre de licitación para búsqueda
    nombre_normalizado = normalizar_texto_completo(nombre_licitacion)
    
    requerimientos_encontrados = []
    
    # Buscar por coincidencia de nombre
    for _, fila in requerimientos_df.iterrows():
        # Obtener nombre de licitación del archivo de requerimientos
        nombre_req = ""
        for col in ['nombre', 'licitacion', 'proyecto', 'titulo']:
            if col in fila and pd.notna(fila[col]):
                nombre_req = str(fila[col])
                break
        
        if not nombre_req:
            continue
        
        nombre_req_normalizado = normalizar_texto_completo(nombre_req)
        
        # Verificar si hay coincidencia (por similitud o contención)
        if (nombre_normalizado in nombre_req_normalizado or 
            nombre_req_normalizado in nombre_normalizado or
            calcular_similitud_nombres(nombre_normalizado, nombre_req_normalizado) > 0.6):
            
            # Extraer documentos requeridos
            documentos = extraer_documentos_requeridos(fila)
            if documentos:
                requerimientos_encontrados.extend(documentos)
    
    return requerimientos_encontrados

def calcular_similitud_nombres(nombre1, nombre2):
    """Calcula similitud entre nombres de licitaciones"""
    if not nombre1 or not nombre2:
        return 0
    
    palabras1 = set(nombre1.split())
    palabras2 = set(nombre2.split())
    
    if not palabras1 or not palabras2:
        return 0
    
    interseccion = len(palabras1.intersection(palabras2))
    union = len(palabras1.union(palabras2))
    
    return interseccion / union if union > 0 else 0

def extraer_documentos_requeridos(fila):
    """Extrae la lista de documentos requeridos de una fila"""
    documentos = []
    
    # Columnas donde buscar documentos
    columnas_documentos = [
        'documentos', 'requerimientos', 'requisitos', 'archivos', 
        'documentacion', 'docs', 'anexos', 'expediente'
    ]
    
    texto_documentos = ""
    for col in columnas_documentos:
        if col in fila and pd.notna(fila[col]):
            texto_documentos += str(fila[col]) + " "
    
    if not texto_documentos.strip():
        return documentos
    
    # Patterns para extraer documentos
    documentos_extraidos = extraer_lista_documentos(texto_documentos)
    
    return documentos_extraidos

def extraer_lista_documentos(texto):
    """Extrae documentos de un texto usando patrones comunes"""
    if not texto:
        return []
    
    texto_normalizado = normalizar_texto_completo(texto)
    documentos = []
    
    # Documentos comunes en licitaciones
    documentos_comunes = [
        # Documentos legales básicos
        'acta constitutiva', 'cedula rfc', 'cedula fiscal', 'rfc',
        'poder notarial', 'representante legal', 'carta poder',
        
        # Documentos financieros
        'estados financieros', 'balance general', 'estado resultados',
        'flujo efectivo', 'declaracion anual', 'opinion cumplimiento',
        'carta ingresos', 'referencias bancarias',
        
        # Documentos técnicos
        'propuesta tecnica', 'especificaciones tecnicas', 'curriculum empresa',
        'experiencia', 'proyectos realizados', 'cartera clientes',
        'catalogo productos', 'fichas tecnicas', 'manuales',
        
        # Documentos de cumplimiento
        'carta cumplimiento', 'declaracion integridad', 'no conflicto interes',
        'cumplimiento obligaciones', 'seguridad social', 'constancia situacion fiscal',
        
        # Garantías y seguros
        'garantia seriedad', 'garantia cumplimiento', 'poliza seguro',
        'fianza', 'carta credito',
        
        # Documentos operativos
        'propuesta economica', 'cotizacion', 'lista precios',
        'forma pago', 'condiciones entrega', 'tiempo entrega',
        
        # Certificaciones
        'iso 9001', 'iso 14001', 'certificaciones calidad',
        'registro proveedores', 'padron contratistas'
    ]
    
    # Buscar documentos mencionados en el texto
    for doc in documentos_comunes:
        if doc in texto_normalizado:
            # Limpiar y formatear nombre del documento
            doc_formateado = doc.replace('_', ' ').title()
            if doc_formateado not in [d['nombre'] for d in documentos]:
                documentos.append({
                    'nombre': doc_formateado,
                    'tipo': clasificar_tipo_documento(doc),
                    'obligatorio': determinar_obligatoriedad(texto_normalizado, doc)
                })
    
    # También buscar patrones como "1. Documento...", "- Archivo...", etc.
    patrones_lista = [
        r'(?:^|\n)\s*[\d\-\*\•]\s*([^.\n]+(?:documento|certificado|constancia|carta|acta|cedula|rfc)[^.\n]*)',
        r'(?:^|\n)\s*[\d\-\*\•]\s*([^.\n]+(?:original|copia|fotocopia)[^.\n]*)'
    ]
    
    for patron in patrones_lista:
        coincidencias = re.findall(patron, texto_normalizado, re.MULTILINE | re.IGNORECASE)
        for coincidencia in coincidencias:
            doc_limpio = coincidencia.strip().title()
            if len(doc_limpio) > 10 and doc_limpio not in [d['nombre'] for d in documentos]:
                documentos.append({
                    'nombre': doc_limpio,
                    'tipo': 'General',
                    'obligatorio': True
                })
    
    return documentos

def clasificar_tipo_documento(documento):
    """Clasifica el tipo de documento"""
    doc_lower = documento.lower()
    
    if any(x in doc_lower for x in ['acta', 'cedula', 'rfc', 'poder', 'representante']):
        return 'Legal'
    elif any(x in doc_lower for x in ['financiero', 'balance', 'estado', 'ingresos', 'bancaria']):
        return 'Financiero'
    elif any(x in doc_lower for x in ['tecnica', 'especificacion', 'catalogo', 'manual', 'ficha']):
        return 'Técnico'
    elif any(x in doc_lower for x in ['garantia', 'seguro', 'poliza', 'fianza']):
        return 'Garantía'
    elif any(x in doc_lower for x in ['iso', 'certificacion', 'calidad']):
        return 'Certificación'
    else:
        return 'General'

def determinar_obligatoriedad(texto, documento):
    """Determina si un documento es obligatorio basado en el contexto"""
    # Buscar palabras clave que indiquen obligatoriedad cerca del documento
    pos = texto.find(documento)
    if pos == -1:
        return True  # Por defecto, considerar obligatorio
    
    # Buscar en contexto cercano (50 caracteres antes y después)
    contexto = texto[max(0, pos-50):pos+len(documento)+50]
    
    palabras_obligatorio = ['obligatorio', 'requerido', 'indispensable', 'necesario']
    palabras_opcional = ['opcional', 'deseable', 'preferible', 'conveniente']
    
    if any(palabra in contexto for palabra in palabras_opcional):
        return False
    
    return True  # Por defecto obligatorio

def evaluar_licitacion_completa(fila, inventario_df, requerimientos_df=None):
    """Evalúa una licitación completa incluyendo productos y requerimientos documentales"""
    # Primero hacer la evaluación normal de productos
    resultado = evaluar_licitacion(fila, inventario_df)
    
    # Agregar evaluación de requerimientos documentales si está disponible
    if requerimientos_df is not None and not requerimientos_df.empty:
        nombre_licitacion = ""
        for col in ['nombre', 'titulo', 'licitacion', 'descripcion']:
            if col in fila and pd.notna(fila[col]):
                nombre_licitacion = str(fila[col])
                break
        
        if nombre_licitacion:
            documentos_requeridos = obtener_requerimientos_documentales(nombre_licitacion, requerimientos_df)
            resultado['documentos_requeridos'] = documentos_requeridos
            resultado['total_documentos'] = len(documentos_requeridos)
            
            # Clasificar documentos por tipo
            tipos_docs = {}
            for doc in documentos_requeridos:
                tipo = doc['tipo']
                if tipo not in tipos_docs:
                    tipos_docs[tipo] = []
                tipos_docs[tipo].append(doc)
            resultado['documentos_por_tipo'] = tipos_docs
        else:
            resultado['documentos_requeridos'] = []
            resultado['total_documentos'] = 0
            resultado['documentos_por_tipo'] = {}
    else:
        resultado['documentos_requeridos'] = []
        resultado['total_documentos'] = 0
        resultado['documentos_por_tipo'] = {}
    
    return resultado

# INTERFAZ PRINCIPAL

st.title("🎯 Filtro de Licitaciones MVP - Versión Completa")
st.markdown("**Análisis específico y detallado de licitaciones vs inventario + documentos requeridos**")

# Sidebar para carga de archivos
with st.sidebar:
    st.header("📁 Carga de Archivos")
    
    archivo_licitaciones = st.file_uploader(
        "Archivo de Licitaciones",
        type=['csv', 'xlsx', 'xls'],
        help="Archivo con las licitaciones a analizar"
    )
    
    archivo_inventario = st.file_uploader(
        "Archivo de Inventario", 
        type=['csv', 'xlsx', 'xls'],
        help="Archivo con el inventario disponible"
    )
    
    archivo_requerimientos = st.file_uploader(
        "Archivo de Requerimientos Documentales",
        type=['csv', 'xlsx', 'xls'],
        help="Archivo con los documentos requeridos por cada licitación"
    )
    
    archivos_cargados = sum([bool(archivo_licitaciones), bool(archivo_inventario)])
    if archivo_requerimientos:
        archivos_cargados += 1
        st.success("✅ Archivos cargados correctamente (incluyendo requerimientos)")
    elif archivo_licitaciones and archivo_inventario:
        st.success("✅ Archivos básicos cargados")
        st.info("💡 Opcionalmente puedes cargar requerimientos documentales")
    
    st.markdown("---")
    st.markdown("### 🔧 Configuración")
    
    mostrar_debug = st.checkbox("Mostrar información de debug", False)
    mostrar_detalles = st.checkbox("Mostrar detalles por licitación", True)

# Verificar archivos
if not archivo_licitaciones or not archivo_inventario:
    st.info("👆 Por favor, carga ambos archivos básicos para comenzar el análisis.")
    
    with st.expander("📖 Guía de archivos y resultados esperados"):
        st.markdown("""
        ### 📁 **Estructura de archivos:**
        
        **📋 Licitaciones.xlsx:**
        ```
        nombre                     | descripcion                           | fecha_cierre
        Licitación Equipos Oficina | 50 computadoras Dell, 20 impresoras | 2025-09-15
        Papelería Trimestre 4      | 100 resmas papel, 500 bolígrafos    | 2025-09-22
        ```
        
        **📦 Inventario.xlsx:**
        ```
        nombre                    | descripcion                     | stock
        Computadora Dell OptiPlex | Dell OptiPlex 7090 Core i5     | 45
        Papel Bond Carta          | Papel bond carta 75 gramos     | 200
        ```
        
        **📋 Requerimientos.xlsx (OPCIONAL):**
        ```
        nombre                     | documentos
        Licitación Equipos Oficina | RFC, Acta constitutiva, Estados financieros, Propuesta técnica
        Papelería Trimestre 4      | RFC, Constancia situación fiscal, Propuesta económica
        ```
        
        ### 🎯 **Resultados esperados:**
        
        **🔴 Licitación Equipos Oficina:**
        - Computadoras: FALTAN 5 (tiene 45, necesita 50)
        - Impresoras: Sin stock
        - 📋 4 documentos requeridos
        
        **🟡 Papelería Trimestre 4:**
        - Papel: ✅ OK (tiene 200, necesita 100) 
        - Bolígrafos: ❌ NO EN INVENTARIO
        - 📋 3 documentos requeridos
        """)
    st.stop()

# Cargar archivos
try:
    # Licitaciones
    if archivo_licitaciones.name.endswith('.csv'):
        licitaciones_df = pd.read_csv(archivo_licitaciones)
    else:
        licitaciones_df = pd.read_excel(archivo_licitaciones)
    
    # Inventario
    if archivo_inventario.name.endswith('.csv'):
        inventario_df = pd.read_csv(archivo_inventario)
    else:
        inventario_df = pd.read_excel(archivo_inventario)
    
    # Requerimientos (opcional)
    requerimientos_df = None
    if archivo_requerimientos:
        try:
            if archivo_requerimientos.name.endswith('.csv'):
                requerimientos_df = pd.read_csv(archivo_requerimientos)
            else:
                requerimientos_df = pd.read_excel(archivo_requerimientos)
            
            requerimientos_df = requerimientos_df.dropna(how='all')
            st.success(f"📊 Datos cargados: {len(licitaciones_df)} licitaciones, {len(inventario_df)} productos, {len(requerimientos_df)} requerimientos documentales")
        except Exception as e:
            st.warning(f"⚠️ Error al cargar requerimientos: {str(e)}. Continuando sin análisis documental.")
            requerimientos_df = None
    else:
        st.success(f"📊 Datos cargados: {len(licitaciones_df)} licitaciones, {len(inventario_df)} productos en inventario")
    
    # Limpiar datos
    licitaciones_df = licitaciones_df.dropna(how='all')
    inventario_df = inventario_df.dropna(how='all')
        
except Exception as e:
    st.error(f"❌ Error al cargar archivos: {str(e)}")
    st.info("Verifica que los archivos no estén corruptos y tengan el formato correcto.")
    st.stop()

# Mostrar información de debug si está habilitada
if mostrar_debug:
    with st.expander("🔍 Información de Debug"):
        if requerimientos_df is not None:
            col1, col2, col3 = st.columns(3)
        else:
            col1, col2 = st.columns(2)
            col3 = None
        
        with col1:
            st.write("**Columnas en Licitaciones:**")
            st.write(list(licitaciones_df.columns))
            st.write("**Muestra de datos:**")
            st.dataframe(licitaciones_df.head(2))
            
            # Debug SIMPLE de extracción
            st.write("**🔍 Prueba de extracción:**")
            for idx, fila in licitaciones_df.head(2).iterrows():
                nombre_lic = fila.get('nombre', f'Licitación {idx+1}')
                descripcion = fila.get('descripcion', 'Sin descripción')
                
                st.write(f"**{nombre_lic}:**")
                st.write(f"*Descripción:* {descripcion[:50]}...")
                
                productos = obtener_productos_de_descripcion(descripcion)
                if productos:
                    for prod in productos:
                        st.write(f"  ✅ {prod['nombre']}: {prod['cantidad']}")
                else:
                    st.write("  ❌ No se extrajeron productos")
        
        with col2:
            st.write("**Columnas en Inventario:**")
            st.write(list(inventario_df.columns))
            st.write("**Muestra de datos:**")
            st.dataframe(inventario_df.head(2))
            
            # Debug SIMPLE de búsqueda
            st.write("**🔍 Prueba de búsqueda:**")
            productos_test = ['computadora', 'proyector', 'papel', 'silla']
            for prod_name in productos_test:
                producto_test = {'nombre': prod_name, 'cantidad': 10}
                resultado = buscar_en_inventario(producto_test, inventario_df)
                
                if resultado['encontrado']:
                    st.write(f"✅ {prod_name}: {resultado['producto_match'][:30]}...")
                else:
                    st.write(f"❌ {prod_name}: No encontrado")
        
        if col3 and requerimientos_df is not None:
            with col3:
                st.write("**Columnas en Requerimientos:**")
                st.write(list(requerimientos_df.columns))
                st.write("**Muestra de datos:**")
                st.dataframe(requerimientos_df.head(2))
                
                # Debug de requerimientos
                st.write("**🔍 Prueba de requerimientos:**")
                for idx, fila in licitaciones_df.head(2).iterrows():
                    nombre_lic = fila.get('nombre', f'Licitación {idx+1}')
                    documentos = obtener_requerimientos_documentales(nombre_lic, requerimientos_df)
                    
                    st.write(f"**{nombre_lic}:**")
                    if documentos:
                        st.write(f"  📋 {len(documentos)} documentos encontrados")
                    else:
                        st.write("  ❌ No se encontraron documentos")

# Procesar análisis
if st.button("🔍 Analizar Licitaciones", type="primary"):
    with st.spinner("Procesando análisis detallado..."):
        resultados = []
        evaluaciones_detalladas = []
        
        for idx, fila in licitaciones_df.iterrows():
            evaluacion = evaluar_licitacion_completa(fila, inventario_df, requerimientos_df)
            evaluaciones_detalladas.append(evaluacion)
            
            # Obtener nombre de licitación
            nombre_licitacion = "Sin nombre"
            for col in ['nombre', 'titulo', 'licitacion', 'descripcion']:
                if col in fila and pd.notna(fila[col]):
                    nombre_licitacion = str(fila[col])[:50] + ("..." if len(str(fila[col])) > 50 else "")
                    break
            
            resultado = {
                'ID': idx + 1,
                'Licitación': nombre_licitacion,
                'Estado': evaluacion['estado'],
                'Productos_Analizados': evaluacion['productos_analizados'],
                'Productos_OK': evaluacion['productos_con_stock'],
                'Sin_Inventario': len(evaluacion.get('productos_sin_inventario', [])),
                'Stock_Insuficiente': len(evaluacion.get('productos_stock_insuficiente', [])),
                'Documentos_Requeridos': evaluacion.get('total_documentos', 0),
                'Observaciones': ' | '.join(evaluacion['observaciones'])  # MOSTRAR TODAS las observaciones
            }
            resultados.append(resultado)
        
        # Crear DataFrame de resultados
        if resultados:
            resultados_df = pd.DataFrame(resultados)
            
            # Métricas generales
            total = len(resultados_df)
            verdes = len(resultados_df[resultados_df['Estado'] == 'verde'])
            amarillos = len(resultados_df[resultados_df['Estado'] == 'amarillo'])
            rojos = len(resultados_df[resultados_df['Estado'] == 'rojo'])
            
            # Mostrar métricas principales
            st.markdown("### 🎯 Resumen Ejecutivo")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📋 Total", total)
            col2.metric("✅ Aptas", verdes, f"{verdes/total*100:.1f}%" if total > 0 else "0%")
            col3.metric("⚠️ Revisar", amarillos, f"{amarillos/total*100:.1f}%" if total > 0 else "0%")
            col4.metric("❌ No aptas", rojos, f"{rojos/total*100:.1f}%" if total > 0 else "0%")
            
            # Tabla de resultados con colores
            st.subheader("📋 Resultados por Licitación")
            
            # Crear columna con emojis para estado visual
            resultados_display = resultados_df.copy()
            resultados_display['Estado_Visual'] = resultados_display['Estado'].map({
                'verde': '🟢 APTA',
                'amarillo': '🟡 REVISAR',
                'rojo': '🔴 NO APTA'
            })
            
            # Reordenar columnas para mejor visualización
            if requerimientos_df is not None:
                columnas_orden = ['ID', 'Licitación', 'Estado_Visual', 'Productos_Analizados', 
                                'Productos_OK', 'Sin_Inventario', 'Stock_Insuficiente', 
                                'Documentos_Requeridos', 'Observaciones']
            else:
                columnas_orden = ['ID', 'Licitación', 'Estado_Visual', 'Productos_Analizados', 
                                'Productos_OK', 'Sin_Inventario', 'Stock_Insuficiente', 'Observaciones']
            
            st.dataframe(resultados_display[columnas_orden], use_container_width=True)
            
            # Detalles específicos por licitación
            if mostrar_detalles:
                st.subheader("🔍 Análisis Detallado por Licitación")
                
                for idx, evaluacion in enumerate(evaluaciones_detalladas):
                    nombre_licitacion = resultados[idx]['Licitación']
                    estado = evaluacion['estado'].upper()
                    
                    # Determinar emoji del estado
                    emoji_estado = "🔴" if estado == "ROJO" else ("🟡" if estado == "AMARILLO" else "🟢")
                    
                    with st.expander(f"{emoji_estado} Licitación {idx + 1}: {nombre_licitacion} - Estado: {estado}"):
                        
                        # Productos que NO existen en inventario
                        if evaluacion['productos_sin_inventario']:
                            st.markdown("#### ❌ **PRODUCTOS QUE NO EXISTEN EN INVENTARIO:**")
                            for producto in evaluacion['productos_sin_inventario']:
                                st.error(f"**{producto['nombre']}** - Cantidad requerida: **{producto['cantidad_requerida']} unidades**")
                                st.write("  💡 *Acción: Buscar proveedor externo o declinar licitación*")
                            st.markdown("---")
                        
                        # Productos con stock insuficiente  
                        if evaluacion['productos_stock_insuficiente']:
                            st.markdown("#### ⚠️ **PRODUCTOS CON STOCK INSUFICIENTE:**")
                            for producto in evaluacion['productos_stock_insuficiente']:
                                porcentaje_cobertura = (producto['disponible'] / producto['requerido']) * 100
                                st.warning(
                                    f"**{producto['nombre']}** *(Inventario: {producto['producto_inventario']})*\n\n"
                                    f"• **Requiere:** {producto['requerido']} unidades\n\n"
                                    f"• **Disponible:** {producto['disponible']} unidades\n\n"
                                    f"• **FALTAN:** {producto['falta']} unidades\n\n"
                                    f"• **Cobertura:** {porcentaje_cobertura:.1f}%"
                                )
                                st.write("  💡 *Acción: Conseguir stock adicional o revisar especificaciones*")
                            st.markdown("---")
                        
                        # Productos completamente disponibles
                        if evaluacion['productos_disponibles']:
                            st.markdown("#### ✅ **PRODUCTOS COMPLETAMENTE DISPONIBLES:**")
                            for producto in evaluacion['productos_disponibles']:
                                st.success(
                                    f"**{producto['nombre']}** - Requiere: {producto['requerido']}, "
                                    f"Disponible: {producto['disponible']} (+{producto['sobra']} extra)"
                                )
                        
                        # NUEVA SECCIÓN: Documentos requeridos
                        if evaluacion.get('documentos_requeridos'):
                            st.markdown("---")
                            st.markdown("#### 📋 **DOCUMENTOS REQUERIDOS:**")
                            
                            total_docs = evaluacion.get('total_documentos', 0)
                            st.info(f"📊 **Total de documentos requeridos: {total_docs}**")
                            
                            # Mostrar documentos agrupados por tipo
                            docs_por_tipo = evaluacion.get('documentos_por_tipo', {})
                            
                            if docs_por_tipo:
                                for tipo, documentos in docs_por_tipo.items():
                                    # Emoji por tipo de documento
                                    emoji_tipo = {
                                        'Legal': '⚖️',
                                        'Financiero': '💰',
                                        'Técnico': '🔧',
                                        'Garantía': '🛡️',
                                        'Certificación': '🏆',
                                        'General': '📄'
                                    }.get(tipo, '📄')
                                    
                                    st.markdown(f"**{emoji_tipo} {tipo}:**")
                                    
                                    for doc in documentos:
                                        obligatorio_texto = "🔴 **OBLIGATORIO**" if doc['obligatorio'] else "🟡 *Opcional*"
                                        st.write(f"  • {doc['nombre']} - {obligatorio_texto}")
                                    
                                    st.write("")  # Espacio entre tipos
                            else:
                                # Si no hay agrupación por tipo, mostrar lista simple
                                for doc in evaluacion['documentos_requeridos']:
                                    obligatorio_texto = "🔴 **OBLIGATORIO**" if doc['obligatorio'] else "🟡 *Opcional*"
                                    tipo_emoji = {
                                        'Legal': '⚖️',
                                        'Financiero': '💰',
                                        'Técnico': '🔧',
                                        'Garantía': '🛡️',
                                        'Certificación': '🏆',
                                        'General': '📄'
                                    }.get(doc['tipo'], '📄')
                                    
                                    st.write(f"  {tipo_emoji} {doc['nombre']} - {obligatorio_texto}")
                        
                        elif requerimientos_df is not None:
                            st.markdown("---")
                            st.markdown("#### 📋 **DOCUMENTOS REQUERIDOS:**")
                            st.info("ℹ️ No se encontraron requerimientos documentales específicos para esta licitación.")
                            st.write("*Verifica que el nombre de la licitación coincida con el archivo de requerimientos.*")
            
            # Alertas urgentes por fechas
            alertas_urgentes = [r for r in resultados if 'días' in r['Observaciones']]
            if alertas_urgentes:
                st.warning(f"🚨 **{len(alertas_urgentes)} licitaciones próximas a cerrar**")
                for alerta in alertas_urgentes[:5]:
                    st.write(f"• **{alerta['Licitación']}**")
            
            # Descargar resultados
            csv_resultado = resultados_df.to_csv(index=False)
            st.download_button(
                label="📥 Descargar Análisis Completo (CSV)",
                data=csv_resultado,
                file_name=f"analisis_licitaciones_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            
        else:
            st.error("No se pudieron procesar las licitaciones. Verifica el formato de los archivos.")