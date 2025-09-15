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
    page_title="Sistema de Licitaciones Médicas",
    page_icon="🏥",
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
    texto_str = re.sub(r'[^\w\s,]', ' ', texto_str)
    texto_str = re.sub(r'\s+', ' ', texto_str)
    
    return texto_str.strip()

def detectar_unidad_medica(texto):
    """Detecta unidades médicas específicas en el texto"""
    texto_lower = texto.lower()
    
    unidades_medicas = {
        'ml': ['ml', 'mililitro', 'mililitros'],
        'mg': ['mg', 'miligramo', 'miligramos'],
        'gr': ['gr', 'gramo', 'gramos'],
        'kg': ['kg', 'kilogramo', 'kilogramos'],
        'mcg': ['mcg', 'microgramo', 'microgramos'],
        'ui': ['ui', 'unidad internacional', 'unidades internacionales'],
        'caja': ['caja', 'cajas', 'estuche', 'estuches'],
        'frasco': ['frasco', 'frascos', 'vial', 'viales'],
        'ampolla': ['ampolla', 'ampollas', 'ampolleta', 'ampolletas'],
        'tableta': ['tableta', 'tabletas', 'comprimido', 'comprimidos'],
        'capsula': ['capsula', 'capsulas', 'gelcap'],
        'tubo': ['tubo', 'tubos'],
        'rollo': ['rollo', 'rollos'],
        'pieza': ['pieza', 'piezas', 'unidad', 'unidades']
    }
    
    for unidad, variantes in unidades_medicas.items():
        if any(variante in texto_lower for variante in variantes):
            return unidad
    
    return 'unidad'

def clasificar_producto_medico(nombre):
    """Clasifica productos médicos usando mapeo especializado"""
    if not nombre:
        return 'desconocido'
    
    nombre_lower = nombre.lower()
    
    # Mapeo completo de productos médicos
    clasificaciones_medicas = {
        # MEDICAMENTOS
        'paracetamol': ['paracetamol', 'acetaminofen'],
        'ibuprofeno': ['ibuprofeno', 'advil'],
        'aspirina': ['aspirina', 'acido acetilsalicilico'],
        'amoxicilina': ['amoxicilina', 'amoxil'],
        'diclofenaco': ['diclofenaco', 'voltaren'],
        'omeprazol': ['omeprazol', 'prilosec'],
        'losartan': ['losartan', 'cozaar'],
        'metformina': ['metformina', 'glucophage'],
        'insulina': ['insulina'],
        'morfina': ['morfina'],
        'tramadol': ['tramadol'],
        
        # SUEROS Y SOLUCIONES
        'suero_fisiologico': ['suero fisiologico', 'solucion salina', 'nacl', 'cloruro sodio'],
        'dextrosa': ['dextrosa', 'glucosa'],
        'hartmann': ['hartmann', 'lactato ringer'],
        'agua_inyectable': ['agua inyectable', 'agua destilada'],
        
        # MATERIAL DE CURACIÓN
        'gasas': ['gasas', 'gasa', 'gasas esteriles'],
        'vendas': ['vendas', 'venda', 'vendaje'],
        'alcohol': ['alcohol', 'alcohol etilico'],
        'yodo': ['yodo', 'povidona yodada', 'isodine'],
        'algodon': ['algodon', 'torundas'],
        'suturas': ['suturas', 'sutura', 'hilo quirurgico'],
        'apositos': ['apositos', 'aposito', 'curita'],
        
        # JERINGAS Y AGUJAS
        'jeringas': ['jeringas', 'jeringa'],
        'agujas': ['agujas', 'aguja'],
        'cateter': ['cateter', 'sonda'],
        
        # GUANTES Y EPP
        'guantes_latex': ['guantes latex', 'guantes'],
        'guantes_nitrilo': ['guantes nitrilo'],
        'mascarillas': ['mascarillas', 'cubrebocas', 'mascarilla quirurgica'],
        'batas': ['batas', 'bata quirurgica'],
        
        # EQUIPOS MÉDICOS
        'estetoscopio': ['estetoscopio', 'fonendoscopio'],
        'tensiometro': ['tensiometro', 'baumanometro'],
        'termometro': ['termometro'],
        'glucometro': ['glucometro', 'medidor glucosa'],
        'pulsioximetro': ['pulsioximetro', 'oximetro'],
        'microscopio': ['microscopio'],
        'centrifuga': ['centrifuga'],
        'desfibrilador': ['desfibrilador'],
        
        # INSTRUMENTAL QUIRÚRGICO
        'bisturi': ['bisturi', 'escalpelo'],
        'pinzas': ['pinzas', 'forceps'],
        'tijeras': ['tijeras quirurgicas'],
        
        # PRODUCTOS DE LIMPIEZA
        'desinfectante': ['desinfectante', 'germicida'],
        'cloro': ['cloro', 'hipoclorito'],
        'alcohol_gel': ['alcohol gel', 'gel antibacterial'],
        
        # OXÍGENO Y GASES
        'oxigeno': ['oxigeno', 'o2'],
        'tanque_oxigeno': ['tanque oxigeno', 'cilindro oxigeno']
    }
    
    # Buscar coincidencia directa
    for categoria, palabras_clave in clasificaciones_medicas.items():
        if any(palabra in nombre_lower for palabra in palabras_clave):
            return categoria
    
    return 'desconocido'

def determinar_categoria_medica(producto):
    """Determina la categoría médica general del producto"""
    categorias_mapping = {
        # Medicamentos
        'paracetamol': 'Medicamentos', 'ibuprofeno': 'Medicamentos', 'aspirina': 'Medicamentos',
        'amoxicilina': 'Medicamentos', 'diclofenaco': 'Medicamentos', 'omeprazol': 'Medicamentos',
        'losartan': 'Medicamentos', 'metformina': 'Medicamentos', 'insulina': 'Medicamentos',
        'morfina': 'Medicamentos', 'tramadol': 'Medicamentos',
        
        # Sueros y soluciones
        'suero_fisiologico': 'Sueros y Soluciones', 'dextrosa': 'Sueros y Soluciones',
        'hartmann': 'Sueros y Soluciones', 'agua_inyectable': 'Sueros y Soluciones',
        
        # Material de curación
        'gasas': 'Material de Curación', 'vendas': 'Material de Curación',
        'alcohol': 'Material de Curación', 'yodo': 'Material de Curación',
        'algodon': 'Material de Curación', 'suturas': 'Material de Curación',
        'apositos': 'Material de Curación',
        
        # Dispositivos médicos desechables
        'jeringas': 'Dispositivos Desechables', 'agujas': 'Dispositivos Desechables',
        'cateter': 'Dispositivos Desechables',
        
        # EPP
        'guantes_latex': 'Equipo de Protección', 'guantes_nitrilo': 'Equipo de Protección',
        'mascarillas': 'Equipo de Protección', 'batas': 'Equipo de Protección',
        
        # Equipos médicos
        'estetoscopio': 'Equipos Médicos', 'tensiometro': 'Equipos Médicos',
        'termometro': 'Equipos Médicos', 'glucometro': 'Equipos Médicos',
        'pulsioximetro': 'Equipos Médicos', 'microscopio': 'Equipos Médicos',
        'centrifuga': 'Equipos Médicos', 'desfibrilador': 'Equipos Médicos',
        
        # Instrumental quirúrgico
        'bisturi': 'Instrumental Quirúrgico', 'pinzas': 'Instrumental Quirúrgico',
        'tijeras': 'Instrumental Quirúrgico',
        
        # Limpieza
        'desinfectante': 'Limpieza y Desinfección', 'cloro': 'Limpieza y Desinfección',
        'alcohol_gel': 'Limpieza y Desinfección',
        
        # Gases medicinales
        'oxigeno': 'Gases Medicinales', 'tanque_oxigeno': 'Gases Medicinales'
    }
    
    return categorias_mapping.get(producto, 'General')

def obtener_productos_de_descripcion(texto):
    """Extrae productos médicos de texto usando método especializado"""
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
        match = re.match(r'^(\d+)\s*([a-z]*)\s*(.+)$', segmento)
        
        if match:
            try:
                cantidad = int(match.group(1))
                unidad_detectada = match.group(2).strip() if match.group(2) else ""
                nombre_crudo = match.group(3).strip()
                
                # Validar cantidad
                if cantidad <= 0 or cantidad > 100000:
                    continue
                
                # Detectar unidad médica si no está especificada
                if not unidad_detectada:
                    unidad_detectada = detectar_unidad_medica(nombre_crudo)
                
                # Clasificar producto médico
                categoria = clasificar_producto_medico(nombre_crudo)
                
                if categoria != 'desconocido':
                    productos.append({
                        'nombre': categoria,
                        'cantidad': cantidad,
                        'nombre_original': nombre_crudo,
                        'unidad': unidad_detectada or 'unidad',
                        'categoria_medica': determinar_categoria_medica(categoria)
                    })
            except:
                continue
    
    return productos

def obtener_stock(fila):
    """Obtiene el stock de una fila de inventario"""
    stock_disponible = 0
    for col_stock in ['stock', 'existencia', 'cantidad', 'disponible', 'inventory', 'qty']:
        if col_stock in fila and pd.notna(fila[col_stock]):
            try:
                stock_disponible = int(float(fila[col_stock]))
                break
            except:
                continue
    return stock_disponible

def buscar_en_inventario_medico(producto_buscado, inventario_df):
    """Busca producto médico en inventario con algoritmo especializado"""
    if inventario_df.empty:
        return {'encontrado': False, 'stock_disponible': 0, 'stock_suficiente': False, 
                'producto_match': '', 'score': 0, 'categoria': '', 'lote': '', 'caducidad': ''}
    
    nombre_buscar = producto_buscado['nombre'].lower()
    cantidad_necesaria = producto_buscado['cantidad']
    
    # Mapeo especializado para productos médicos
    mapeo_inventario_medico = {
        'paracetamol': ['Paracetamol', 'Acetaminofén'],
        'ibuprofeno': ['Ibuprofeno', 'Advil'],
        'amoxicilina': ['Amoxicilina'],
        'suero_fisiologico': ['Suero Fisiológico', 'Solución Salina', 'NaCl'],
        'dextrosa': ['Dextrosa', 'Glucosa'],
        'gasas': ['Gasas estériles', 'Gasa'],
        'vendas': ['Vendas elásticas', 'Venda'],
        'alcohol': ['Alcohol etílico', 'Alcohol 70%'],
        'jeringas': ['Jeringas desechables', 'Jeringa'],
        'agujas': ['Agujas hipodérmicas', 'Aguja'],
        'guantes_latex': ['Guantes de látex', 'Guantes estériles'],
        'mascarillas': ['Mascarillas quirúrgicas', 'Cubrebocas'],
        'estetoscopio': ['Estetoscopio', 'Fonendoscopio'],
        'tensiometro': ['Tensiómetro', 'Baumanómetro'],
        'termometro': ['Termómetro digital', 'Termómetro'],
        'microscopio': ['Microscopio óptico', 'Microscopio'],
        'centrifuga': ['Centrífuga', 'Centrifugadora']
    }
    
    # Buscar coincidencia directa
    productos_match = mapeo_inventario_medico.get(nombre_buscar, [])
    
    if productos_match:
        # Buscar en inventario real
        for _, fila in inventario_df.iterrows():
            nombre_inventario = str(fila.get('nombre', '')).strip()
            descripcion_inventario = str(fila.get('descripcion', '')).strip()
            texto_completo = f"{nombre_inventario} {descripcion_inventario}".lower()
            
            for producto_esperado in productos_match:
                if producto_esperado.lower() in texto_completo:
                    # Encontrado! Obtener información completa
                    stock_disponible = obtener_stock(fila)
                    lote = str(fila.get('lote', fila.get('batch', ''))).strip()
                    caducidad = str(fila.get('caducidad', fila.get('expiry', fila.get('fecha_vencimiento', '')))).strip()
                    categoria = str(fila.get('categoria', fila.get('tipo', ''))).strip()
                    
                    return {
                        'encontrado': True,
                        'stock_disponible': stock_disponible,
                        'stock_suficiente': stock_disponible >= cantidad_necesaria,
                        'producto_match': nombre_inventario,
                        'score': 0.9,
                        'categoria': categoria,
                        'lote': lote,
                        'caducidad': caducidad
                    }
    
    # Búsqueda por similitud si no hay mapeo directo
    mejor_match = None
    mejor_score = 0
    
    for _, fila in inventario_df.iterrows():
        nombre_item = str(fila.get('nombre', '')).lower()
        desc_item = str(fila.get('descripcion', '')).lower()
        texto_completo = f"{nombre_item} {desc_item}"
        
        # Calcular similitud
        score = 0
        if nombre_buscar in texto_completo:
            score = 0.8
        elif any(palabra in texto_completo for palabra in nombre_buscar.split()):
            score = 0.6
        
        if score > mejor_score:
            stock_disponible = obtener_stock(fila)
            lote = str(fila.get('lote', '')).strip()
            caducidad = str(fila.get('caducidad', '')).strip()
            categoria = str(fila.get('categoria', '')).strip()
            
            mejor_score = score
            mejor_match = {
                'stock': stock_disponible,
                'nombre': str(fila.get('nombre', '')),
                'lote': lote,
                'caducidad': caducidad,
                'categoria': categoria
            }
    
    if mejor_match and mejor_score >= 0.6:
        return {
            'encontrado': True,
            'stock_disponible': mejor_match['stock'],
            'stock_suficiente': mejor_match['stock'] >= cantidad_necesaria,
            'producto_match': mejor_match['nombre'],
            'score': mejor_score,
            'categoria': mejor_match['categoria'],
            'lote': mejor_match['lote'],
            'caducidad': mejor_match['caducidad']
        }
    
    return {'encontrado': False, 'stock_disponible': 0, 'stock_suficiente': False, 
            'producto_match': '', 'score': 0, 'categoria': '', 'lote': '', 'caducidad': ''}

def verificar_caducidad(fecha_caducidad):
    """Verifica si un producto está próximo a caducar"""
    if not fecha_caducidad or pd.isna(fecha_caducidad):
        return {'estado': 'sin_fecha', 'dias_restantes': None, 'alerta': False}
    
    try:
        # Intentar diferentes formatos de fecha
        formatos_fecha = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']
        fecha_cad = None
        
        for formato in formatos_fecha:
            try:
                fecha_cad = datetime.strptime(str(fecha_caducidad).strip(), formato)
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
            
    except Exception as e:
        return {'estado': 'error', 'dias_restantes': None, 'alerta': False}

def evaluar_licitacion_medica(fila, inventario_df):
    """Evalúa una licitación médica contra el inventario"""
    resultado = {
        'estado': 'verde',
        'observaciones': [],
        'productos_analizados': 0,
        'productos_encontrados': 0,
        'productos_con_stock': 0,
        'productos_sin_inventario': [],
        'productos_stock_insuficiente': [],
        'productos_disponibles': [],
        'alertas_caducidad': [],
        'productos_por_categoria': {}
    }
    
    # Buscar texto de productos en múltiples columnas
    texto_productos = ""
    columnas_descripcion = ['descripcion', 'detalle', 'productos', 'items', 'especificaciones', 'medicamentos', 'insumos']
    
    for col in columnas_descripcion:
        if col in fila and pd.notna(fila[col]):
            texto_productos += str(fila[col]) + " "
    
    if not texto_productos.strip():
        resultado['estado'] = 'amarillo'
        resultado['observaciones'].append("Sin descripción de productos médicos")
        return resultado
    
    # Extraer productos usando función médica especializada
    productos_requeridos = obtener_productos_de_descripcion(texto_productos)
    
    if not productos_requeridos:
        resultado['estado'] = 'amarillo'
        resultado['observaciones'].append("No se identificaron productos médicos específicos")
        return resultado
    
    resultado['productos_analizados'] = len(productos_requeridos)
    
    # Evaluar cada producto médico
    for producto in productos_requeridos:
        busqueda = buscar_en_inventario_medico(producto, inventario_df)
        producto_nombre = producto['nombre'].replace('_', ' ').title()
        cantidad_req = producto['cantidad']
        unidad = producto['unidad']
        categoria_med = producto.get('categoria_medica', 'General')
        
        # Contar productos por categoría médica
        if categoria_med not in resultado['productos_por_categoria']:
            resultado['productos_por_categoria'][categoria_med] = {'total': 0, 'disponibles': 0}
        resultado['productos_por_categoria'][categoria_med]['total'] += 1
        
        if busqueda['encontrado']:
            resultado['productos_encontrados'] += 1
            stock_disp = busqueda['stock_disponible']
            
            # Verificar caducidad si está disponible
            info_caducidad = verificar_caducidad(busqueda.get('caducidad', ''))
            
            if busqueda['stock_suficiente']:
                resultado['productos_con_stock'] += 1
                resultado['productos_por_categoria'][categoria_med]['disponibles'] += 1
                
                producto_info = {
                    'nombre': producto_nombre,
                    'requerido': cantidad_req,
                    'disponible': stock_disp,
                    'sobra': stock_disp - cantidad_req,
                    'unidad': unidad,
                    'categoria': categoria_med,
                    'lote': busqueda.get('lote', ''),
                    'caducidad': busqueda.get('caducidad', ''),
                    'producto_inventario': busqueda['producto_match']
                }
                
                # Agregar alerta de caducidad si es necesario
                if info_caducidad['alerta']:
                    producto_info['alerta_caducidad'] = info_caducidad
                    resultado['alertas_caducidad'].append({
                        'producto': producto_nombre,
                        'estado_caducidad': info_caducidad['estado'],
                        'dias_restantes': info_caducidad['dias_restantes']
                    })
                
                resultado['productos_disponibles'].append(producto_info)
            else:
                faltante = cantidad_req - stock_disp
                producto_insuf = {
                    'nombre': producto_nombre,
                    'requerido': cantidad_req,
                    'disponible': stock_disp,
                    'falta': faltante,
                    'unidad': unidad,
                    'categoria': categoria_med,
                    'producto_inventario': busqueda['producto_match'],
                    'lote': busqueda.get('lote', ''),
                    'caducidad': busqueda.get('caducidad', '')
                }
                
                # Verificar caducidad también para productos con stock insuficiente
                if info_caducidad['alerta']:
                    producto_insuf['alerta_caducidad'] = info_caducidad
                    resultado['alertas_caducidad'].append({
                        'producto': producto_nombre,
                        'estado_caducidad': info_caducidad['estado'],
                        'dias_restantes': info_caducidad['dias_restantes']
                    })
                
                resultado['productos_stock_insuficiente'].append(producto_insuf)
        else:
            resultado['productos_sin_inventario'].append({
                'nombre': producto_nombre,
                'cantidad_requerida': cantidad_req,
                'unidad': unidad,
                'categoria': categoria_med
            })
    
    # Generar observaciones
    observaciones_detalladas = []
    
    # Productos que NO existen en inventario
    if resultado['productos_sin_inventario']:
        resultado['estado'] = 'rojo'
        productos_sin_inv_texto = []
        for p in resultado['productos_sin_inventario']:
            productos_sin_inv_texto.append(f"{p['nombre']} ({p['cantidad_requerida']} {p['unidad']})")
        observaciones_detalladas.append(f"NO EN INVENTARIO: {', '.join(productos_sin_inv_texto)}")
    
    # Productos con stock insuficiente
    if resultado['productos_stock_insuficiente']:
        if resultado['estado'] == 'verde':
            resultado['estado'] = 'amarillo'
        
        productos_stock_insuf_texto = []
        for p in resultado['productos_stock_insuficiente']:
            productos_stock_insuf_texto.append(f"{p['nombre']}: FALTAN {p['falta']} {p['unidad']}")
        
        observaciones_detalladas.append(f"STOCK INSUFICIENTE: {', '.join(productos_stock_insuf_texto)}")
    
    # Alertas de caducidad
    if resultado['alertas_caducidad']:
        if resultado['estado'] == 'verde':
            resultado['estado'] = 'amarillo'
        
        alertas_texto = []
        for alerta in resultado['alertas_caducidad']:
            if alerta['estado_caducidad'] == 'caducado':
                alertas_texto.append(f"{alerta['producto']}: CADUCADO")
            elif alerta['estado_caducidad'] == 'proximo_caducar':
                alertas_texto.append(f"{alerta['producto']}: Caduca en {alerta['dias_restantes']} días")
        
        if alertas_texto:
            observaciones_detalladas.append(f"CADUCIDAD: {', '.join(alertas_texto)}")
    
    # Productos disponibles
    if (resultado['productos_disponibles'] and 
        not resultado['productos_sin_inventario'] and 
        not resultado['productos_stock_insuficiente'] and
        not resultado['alertas_caducidad']):
        productos_ok_texto = []
        for p in resultado['productos_disponibles']:
            productos_ok_texto.append(f"{p['nombre']} ({p['requerido']} {p['unidad']})")
        observaciones_detalladas.append(f"TODOS OK: {', '.join(productos_ok_texto)}")
    
    # Estadística general
    porcentaje_ok = (resultado['productos_con_stock'] / resultado['productos_analizados']) * 100 if resultado['productos_analizados'] > 0 else 0
    observaciones_detalladas.append(f"DISPONIBILIDAD: {resultado['productos_con_stock']}/{resultado['productos_analizados']} ({porcentaje_ok:.0f}%)")
    
    resultado['observaciones'] = observaciones_detalladas
    return resultado

# INTERFAZ PRINCIPAL
st.title("🏥 Sistema de Licitaciones Médicas")
st.markdown("**Análisis especializado de licitaciones médicas vs inventario hospitalario**")

# Sidebar para carga de archivos
with st.sidebar:
    st.header("📁 Carga de Archivos Médicos")
    
    archivo_licitaciones = st.file_uploader(
        "Archivo de Licitaciones Médicas",
        type=['csv', 'xlsx', 'xls'],
        help="Licitaciones de medicamentos, insumos médicos o equipos hospitalarios"
    )
    
    archivo_inventario = st.file_uploader(
        "Archivo de Inventario Médico", 
        type=['csv', 'xlsx', 'xls'],
        help="Inventario de medicamentos, dispositivos médicos y equipos hospitalarios"
    )
    
    archivos_cargados = sum([bool(archivo_licitaciones), bool(archivo_inventario)])
    if archivo_licitaciones and archivo_inventario:
        st.success("✅ Archivos médicos básicos cargados")
    
    st.markdown("---")
    st.markdown("### 🔧 Configuración")
    
    mostrar_debug = st.checkbox("Mostrar información de debug", False)
    mostrar_detalles = st.checkbox("Mostrar detalles por licitación", True)
    mostrar_caducidades = st.checkbox("Alertas de caducidad", True)

# Verificar archivos
if not archivo_licitaciones or not archivo_inventario:
    st.info("👆 Por favor, carga ambos archivos para comenzar el análisis médico.")
    st.stop()

# Cargar archivos médicos
try:
    # Licitaciones médicas
    if archivo_licitaciones.name.endswith('.csv'):
        licitaciones_df = pd.read_csv(archivo_licitaciones, encoding='utf-8')
    else:
        licitaciones_df = pd.read_excel(archivo_licitaciones)
    
    # Inventario médico
    if archivo_inventario.name.endswith('.csv'):
        inventario_df = pd.read_csv(archivo_inventario, encoding='utf-8')
    else:
        inventario_df = pd.read_excel(archivo_inventario)
    
    # Limpiar datos
    licitaciones_df = licitaciones_df.dropna(how='all')
    inventario_df = inventario_df.dropna(how='all')
    
    st.success(f"Datos médicos cargados: {len(licitaciones_df)} licitaciones médicas, {len(inventario_df)} productos en inventario hospitalario")

except Exception as e:
    st.error(f"Error al cargar archivos médicos: {str(e)}")
    st.info("Verifica que los archivos tengan formato correcto y contengan datos médicos válidos.")
    st.stop()