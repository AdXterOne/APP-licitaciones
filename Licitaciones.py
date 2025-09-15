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

def obtener_requerimientos_documentales_medicos(nombre_licitacion, requerimientos_df):
    """Obtiene los documentos requeridos para una licitación médica específica"""
    if requerimientos_df is None or requerimientos_df.empty:
        return []
    
    nombre_normalizado = normalizar_texto_completo(nombre_licitacion)
    requerimientos_encontrados = []
    
    for _, fila in requerimientos_df.iterrows():
        nombre_req = ""
        for col in ['nombre', 'licitacion', 'proyecto', 'titulo']:
            if col in fila and pd.notna(fila[col]):
                nombre_req = str(fila[col])
                break
        
        if not nombre_req:
            continue
        
        nombre_req_normalizado = normalizar_texto_completo(nombre_req)
        
        if (nombre_normalizado in nombre_req_normalizado or 
            nombre_req_normalizado in nombre_normalizado or
            calcular_similitud_nombres(nombre_normalizado, nombre_req_normalizado) > 0.6):
            
            documentos = extraer_documentos_requeridos_medicos(fila)
            if documentos:
                requerimientos_encontrados.extend(documentos)
    
    return requerimientos_encontrados

def calcular_similitud_nombres(nombre1, nombre2):
    """Calcula similitud entre nombres considerando términos médicos"""
    if not nombre1 or not nombre2:
        return 0
    
    palabras1 = set(nombre1.split())
    palabras2 = set(nombre2.split())
    
    if not palabras1 or not palabras2:
        return 0
    
    # Dar mayor peso a términos médicos específicos
    terminos_medicos = {
        'medicamentos', 'farmacia', 'hospital', 'clinica', 'salud',
        'medico', 'quirurgico', 'laboratorio', 'reactivos'
    }
    
    interseccion = len(palabras1.intersection(palabras2))
    union = len(palabras1.union(palabras2))
    
    # Bonus por términos médicos comunes
    terminos_medicos_comunes = palabras1.intersection(palabras2).intersection(terminos_medicos)
    if terminos_medicos_comunes:
        interseccion += len(terminos_medicos_comunes) * 0.5
    
    return interseccion / union if union > 0 else 0

def extraer_documentos_requeridos_medicos(fila):
    """Extrae documentos requeridos específicos para licitaciones médicas"""
    documentos = []
    
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
    
    texto_normalizado = normalizar_texto_completo(texto_documentos)
    
    # Documentos específicos para licitaciones médicas y farmacéuticas
    documentos_medicos = [
        # Documentos regulatorios médicos
        'licencia sanitaria', 'permiso sanitario', 'aviso funcionamiento',
        'registro sanitario', 'cofepris', 'invima', 'fda',
        'buenas practicas manufactura', 'certificado gmp', 'iso 13485',
        'farmacovigilancia', 'tecnovigilancia',
        
        # Documentos específicos de medicamentos
        'registro medicamento', 'ficha tecnica', 'monografia',
        'certificado analisis', 'certificado calidad',
        'cadena custodia', 'cadena frio',
        
        # Personal especializado
        'quimico farmacobiologo', 'director tecnico',
        'responsable sanitario', 'profesional salud',
        'cedula profesional',
        
        # Documentos generales básicos
        'acta constitutiva', 'cedula rfc', 'poder notarial',
        'estados financieros', 'declaracion anual',
        'constancia situacion fiscal', 'opinion cumplimiento',
        'propuesta tecnica', 'propuesta economica'
    ]
    
    # Buscar documentos específicos médicos
    for doc in documentos_medicos:
        if doc in texto_normalizado:
            doc_formateado = doc.replace('_', ' ').title()
            if doc_formateado not in [d['nombre'] for d in documentos]:
                documentos.append({
                    'nombre': doc_formateado,
                    'tipo': clasificar_tipo_documento_medico(doc),
                    'obligatorio': determinar_obligatoriedad_medica(texto_normalizado, doc),
                    'sector': 'Salud' if 'sanitaria' in doc or 'medico' in doc or 'farmaco' in doc else 'General'
                })
    
    return documentos

def clasificar_tipo_documento_medico(documento):
    """Clasifica documentos considerando especificidades médicas"""
    doc_lower = documento.lower()
    
    if any(x in doc_lower for x in ['sanitaria', 'sanitario', 'cofepris', 'invima', 'fda', 'registro medicamento']):
        return 'Regulatorio Médico'
    elif any(x in doc_lower for x in ['gmp', 'iso 13485', 'buenas practicas', 'farmacovigilancia']):
        return 'Calidad Médica'
    elif any(x in doc_lower for x in ['farmacobiologo', 'director tecnico', 'responsable sanitario']):
        return 'Personal Especializado'
    elif any(x in doc_lower for x in ['acta', 'cedula', 'rfc', 'poder']):
        return 'Legal'
    elif any(x in doc_lower for x in ['financiero', 'estados', 'declaracion']):
        return 'Financiero'
    elif any(x in doc_lower for x in ['propuesta', 'tecnica', 'economica']):
        return 'Propuesta'
    else:
        return 'General'

def determinar_obligatoriedad_medica(texto, documento):
    """Determina obligatoriedad considerando regulaciones médicas"""
    # Documentos críticos siempre obligatorios en sector salud
    criticos_salud = [
        'licencia sanitaria', 'registro sanitario', 'cofepris',
        'buenas practicas', 'responsable sanitario'
    ]
    
    if any(critico in documento for critico in criticos_salud):
        return True
    
    # Evaluar contexto general
    pos = texto.find(documento)
    if pos == -1:
        return True
    
    contexto = texto[max(0, pos-50):pos+len(documento)+50]
    
    palabras_obligatorio = ['obligatorio', 'requerido', 'indispensable', 'necesario', 'debe']
    palabras_opcional = ['opcional', 'deseable', 'preferible', 'conveniente']
    
    if any(palabra in contexto for palabra in palabras_opcional):
        return False
    
    return True

def evaluar_licitacion_medica_completa(fila, inventario_df, requerimientos_df=None):
    """Evalúa una licitación médica completa incluyendo productos y requerimientos especializados"""
    # Evaluación médica de productos
    resultado = evaluar_licitacion_medica(fila, inventario_df)
    
    # Agregar evaluación de requerimientos documentales médicos
    if requerimientos_df is not None and not requerimientos_df.empty:
        nombre_licitacion = ""
        for col in ['nombre', 'titulo', 'licitacion', 'descripcion']:
            if col in fila and pd.notna(fila[col]):
                nombre_licitacion = str(fila[col])
                break
        
        if nombre_licitacion:
            documentos_requeridos = obtener_requerimientos_documentales_medicos(nombre_licitacion, requerimientos_df)
            resultado['documentos_requeridos'] = documentos_requeridos
            resultado['total_documentos'] = len(documentos_requeridos)
            
            # Clasificar documentos por tipo médico
            tipos_docs = {}
            for doc in documentos_requeridos:
                tipo = doc['tipo']
                if tipo not in tipos_docs:
                    tipos_docs[tipo] = []
                tipos_docs[tipo].append(doc)
            resultado['documentos_por_tipo'] = tipos_docs
            
            # Contar documentos críticos médicos
            docs_criticos = sum(1 for doc in documentos_requeridos 
                              if doc['tipo'] in ['Regulatorio Médico', 'Calidad Médica', 'Personal Especializado'])
            resultado['documentos_criticos_medicos'] = docs_criticos
        else:
            resultado['documentos_requeridos'] = []
            resultado['total_documentos'] = 0
            resultado['documentos_por_tipo'] = {}
            resultado['documentos_criticos_medicos'] = 0
    else:
        resultado['documentos_requeridos'] = []
        resultado['total_documentos'] = 0
        resultado['documentos_por_tipo'] = {}
        resultado['documentos_criticos_medicos'] = 0
    
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
    
    archivo_requerimientos = st.file_uploader(
        "Archivo de Requerimientos Documentales (Opcional)",
        type=['csv', 'xlsx', 'xls'],
        help="Documentos regulatorios y certificaciones requeridas para cada licitación médica"
    )
    
    archivos_cargados = sum([bool(archivo_licitaciones), bool(archivo_inventario)])
    if archivo_requerimientos:
        archivos_cargados += 1
        st.success("✅ Archivos médicos cargados correctamente (incluyendo requerimientos)")
    elif archivo_licitaciones and archivo_inventario:
        st.success("✅ Archivos médicos básicos cargados")
        st.info("💡 Opcionalmente puedes cargar requerimientos documentales")
    
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

# Debug especializado para productos médicos
if mostrar_debug:
    with st.expander("Debug - Análisis de Vocabulario Médico"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Columnas en Licitaciones Médicas:**")
            st.write(list(licitaciones_df.columns))
            st.write("**Muestra de licitaciones:**")
            st.dataframe(licitaciones_df.head(2))
            
            # Debug de extracción de productos médicos
            st.write("**Extracción de productos médicos:**")
            for idx, fila in licitaciones_df.head(2).iterrows():
                nombre_lic = fila.get('nombre', f'Licitación {idx+1}')
                descripcion = fila.get('descripcion', 'Sin descripción')
                
                st.write(f"**{nombre_lic}:**")
                st.write(f"*Descripción:* {descripcion[:100]}...")
                
                productos = obtener_productos_de_descripcion(descripcion)
                if productos:
                    for prod in productos:
                        categoria_med = prod.get('categoria_medica', 'N/A')
                        st.write(f"  ✅ {prod['nombre']}: {prod['cantidad']} {prod['unidad']} - Categoría: {categoria_med}")
                else:
                    st.write("  ❌ No se extrajeron productos médicos")
        
        with col2:
            st.write("**Columnas en Inventario Médico:**")
            st.write(list(inventario_df.columns))
            st.write("**Muestra de inventario:**")
            st.dataframe(inventario_df.head(2))
            
            # Debug de búsqueda médica
            st.write("**Búsqueda en inventario médico:**")
            productos_test_medicos = ['paracetamol', 'gasas', 'jeringas', 'alcohol', 'microscopio', 'suero_fisiologico']
            
            for prod_name in productos_test_medicos:
                producto_test = {'nombre': prod_name, 'cantidad': 10, 'unidad': 'unidad'}
                resultado = buscar_en_inventario_medico(producto_test, inventario_df)
                
                if resultado['encontrado']:
                    caducidad_info = f" - Caduca: {resultado.get('caducidad', 'N/A')}" if resultado.get('caducidad') else ""
                    lote_info = f" - Lote: {resultado.get('lote', 'N/A')}" if resultado.get('lote') else ""
                    st.write(f"✅ {prod_name}: {resultado['producto_match'][:30]}...{caducidad_info}{lote_info}")
                else:
                    st.write(f"❌ {prod_name}: No encontrado en inventario")

# Procesamiento principal
if st.button("Analizar Licitaciones Médicas", type="primary"):
    with st.spinner("Procesando análisis médico especializado..."):
        resultados = []
        evaluaciones_detalladas = []
        alertas_criticas = []
        
        for idx, fila in licitaciones_df.iterrows():
            evaluacion = evaluar_licitacion_medica_completa(fila, inventario_df, requerimientos_df)
            evaluaciones_detalladas.append(evaluacion)
            
            # Obtener nombre de licitación
            nombre_licitacion = "Sin nombre"
            for col in ['nombre', 'titulo', 'licitacion', 'descripcion']:
                if col in fila and pd.notna(fila[col]):
                    nombre_licitacion = str(fila[col])[:50] + ("..." if len(str(fila[col])) > 50 else "")
                    break
            
            # Determinar criticidad específica para sector médico
            estado_critico = evaluacion['estado']
            if evaluacion.get('alertas_caducidad'):
                caducados = [a for a in evaluacion['alertas_caducidad'] if a['estado_caducidad'] == 'caducado']
                if caducados:
                    estado_critico = 'crítico'
                    alertas_criticas.append({
                        'licitacion': nombre_licitacion,
                        'tipo': 'medicamento_caducado',
                        'detalle': caducados
                    })
            
            # Contar productos por categoría médica
            categorias_productos = evaluacion.get('productos_por_categoria', {})
            
            resultado = {
                'ID': idx + 1,
                'Licitación': nombre_licitacion,
                'Estado': estado_critico,
                'Productos_Analizados': evaluacion['productos_analizados'],
                'Productos_OK': evaluacion['productos_con_stock'],
                'Sin_Inventario': len(evaluacion.get('productos_sin_inventario', [])),
                'Stock_Insuficiente': len(evaluacion.get('productos_stock_insuficiente', [])),
                'Alertas_Caducidad': len(evaluacion.get('alertas_caducidad', [])),
                'Documentos_Regulatorios': evaluacion.get('documentos_criticos_medicos', 0),
                'Total_Documentos': evaluacion.get('total_documentos', 0),
                'Categorías_Médicas': len(categorias_productos),
                'Observaciones': ' | '.join(evaluacion['observaciones'])
            }
            
            resultados.append(resultado)
        
        # Crear DataFrame de resultados médicos
        if resultados:
            resultados_df = pd.DataFrame(resultados)
            
            # Métricas generales para sector médico
            total = len(resultados_df)
            verdes = len(resultados_df[resultados_df['Estado'] == 'verde'])
            amarillos = len(resultados_df[resultados_df['Estado'] == 'amarillo'])
            rojos = len(resultados_df[resultados_df['Estado'] == 'rojo'])
            criticos = len(resultados_df[resultados_df['Estado'] == 'crítico'])
            
            # Alertas críticas para medicamentos
            total_alertas_caducidad = resultados_df['Alertas_Caducidad'].sum()
            
            # Mostrar métricas médicas principales
            st.markdown("### Resumen Ejecutivo - Sector Médico")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total", total)
            col2.metric("Aptas", verdes, f"{verdes/total*100:.1f}%" if total > 0 else "0%")
            col3.metric("Revisar", amarillos, f"{amarillos/total*100:.1f}%" if total > 0 else "0%")
            col4.metric("No aptas", rojos, f"{rojos/total*100:.1f}%" if total > 0 else "0%")
            col5.metric("Críticas", criticos + total_alertas_caducidad, "Caducidad/Stock")
            
            # Alertas críticas especiales para medicamentos
            if alertas_criticas:
                st.error(f"ALERTA CRÍTICA: {len(alertas_criticas)} licitaciones con medicamentos caducados")
                for alerta in alertas_criticas[:3]:
                    st.error(f"• **{alerta['licitacion']}**: Medicamentos caducados detectados")
            
            # Mostrar alertas de caducidad si están habilitadas
            if mostrar_caducidades and total_alertas_caducidad > 0:
                st.warning(f"ALERTAS DE CADUCIDAD: {total_alertas_caducidad} productos próximos a caducar o caducados")
            
            # Tabla de resultados médicos con colores
            st.subheader("Resultados por Licitación Médica")
            
            resultados_display = resultados_df.copy()
            resultados_display['Estado_Visual'] = resultados_display['Estado'].map({
                'verde': 'APTA',
                'amarillo': 'REVISAR',
                'rojo': 'NO APTA',
                'crítico': 'CRÍTICA'
            })
            
            # Reordenar columnas para vista médica
            if requerimientos_df is not None:
                columnas_orden = ['ID', 'Licitación', 'Estado_Visual', 'Productos_Analizados', 
                                'Productos_OK', 'Sin_Inventario', 'Stock_Insuficiente', 
                                'Alertas_Caducidad', 'Documentos_Regulatorios', 'Total_Documentos',
                                'Categorías_Médicas', 'Observaciones']
            else:
                columnas_orden = ['ID', 'Licitación', 'Estado_Visual', 'Productos_Analizados', 
                                'Productos_OK', 'Sin_Inventario', 'Stock_Insuficiente', 
                                'Alertas_Caducidad', 'Categorías_Médicas', 'Observaciones']
            
            st.dataframe(resultados_display[columnas_orden], use_container_width=True)
            
            # Análisis detallado por licitación médica
            if mostrar_detalles:
                st.subheader("Análisis Detallado por Licitación Médica")
                
                for idx, evaluacion in enumerate(evaluaciones_detalladas):
                    nombre_licitacion = resultados[idx]['Licitación']
                    estado = evaluacion['estado'].upper()
                    
                    # Determinar emoji del estado
                    emoji_estado = "🚨" if estado == "CRÍTICO" else ("🔴" if estado == "ROJO" else ("🟡" if estado == "AMARILLO" else "🟢"))
                    
                    with st.expander(f"{emoji_estado} Licitación {idx + 1}: {nombre_licitacion} - Estado: {estado}"):
                        
                        # ALERTAS CRÍTICAS DE CADUCIDAD (prioritario para medicamentos)
                        if evaluacion.get('alertas_caducidad'):
                            st.markdown("#### ALERTAS CRÍTICAS DE CADUCIDAD:")
                            for alerta in evaluacion['alertas_caducidad']:
                                if alerta['estado_caducidad'] == 'caducado':
                                    st.error(f"**{alerta['producto']}** - MEDICAMENTO CADUCADO - Venció hace {abs(alerta['dias_restantes'])} días")
                                    st.write("  ACCIÓN INMEDIATA: Retirar del inventario y gestionar disposición")
                                elif alerta['estado_caducidad'] == 'proximo_caducar':
                                    st.warning(f"**{alerta['producto']}** - CADUCA EN {alerta['dias_restantes']} DÍAS")
                                    st.write("  ACCIÓN: Priorizar uso o evaluar reposición")
                            st.markdown("---")
                        
                        # Productos que NO existen en inventario médico
                        if evaluacion['productos_sin_inventario']:
                            st.markdown("#### PRODUCTOS MÉDICOS NO DISPONIBLES:")
                            for producto in evaluacion['productos_sin_inventario']:
                                st.error(f"**{producto['nombre']}** - Cantidad: **{producto['cantidad_requerida']} {producto['unidad']}** - Categoría: *{producto['categoria']}*")
                                st.write("  Acción: Buscar proveedor especializado en productos médicos")
                            st.markdown("---")
                        
                        # Productos con stock insuficiente  
                        if evaluacion['productos_stock_insuficiente']:
                            st.markdown("#### PRODUCTOS CON STOCK INSUFICIENTE:")
                            for producto in evaluacion['productos_stock_insuficiente']:
                                porcentaje_cobertura = (producto['disponible'] / producto['requerido']) * 100
                                caducidad_texto = f" - Caduca: {producto['caducidad']}" if producto.get('caducidad') else ""
                                lote_texto = f" - Lote: {producto['lote']}" if producto.get('lote') else ""
                                
                                st.warning(
                                    f"**{producto['nombre']}** *(Inventario: {producto['producto_inventario']})*\n\n"
                                    f"• **Requiere:** {producto['requerido']} {producto['unidad']}\n\n"
                                    f"• **Disponible:** {producto['disponible']} {producto['unidad']}\n\n"
                                    f"• **FALTAN:** {producto['falta']} {producto['unidad']}\n\n"
                                    f"• **Cobertura:** {porcentaje_cobertura:.1f}%\n\n"
                                    f"• **Categoría:** {producto['categoria']}{caducidad_texto}{lote_texto}"
                                )
                                st.write("  Acción: Conseguir stock adicional o revisar especificaciones médicas")
                            st.markdown("---")
                        
                        # Productos completamente disponibles
                        if evaluacion['productos_disponibles']:
                            st.markdown("#### PRODUCTOS MÉDICOS DISPONIBLES:")
                            for producto in evaluacion['productos_disponibles']:
                                caducidad_texto = f" - Caduca: {producto['caducidad']}" if producto.get('caducidad') else ""
                                lote_texto = f" - Lote: {producto['lote']}" if producto.get('lote') else ""
                                
                                st.success(
                                    f"**{producto['nombre']}** - Requiere: {producto['requerido']} {producto['unidad']}, "
                                    f"Disponible: {producto['disponible']} (+{producto['sobra']} extra) - "
                                    f"Categoría: {producto['categoria']}{caducidad_texto}{lote_texto}"
                                )
                        
                        # Resumen por categorías médicas
                        if evaluacion.get('productos_por_categoria'):
                            st.markdown("---")
                            st.markdown("#### ANÁLISIS POR CATEGORÍA MÉDICA:")
                            
                            for categoria, stats in evaluacion['productos_por_categoria'].items():
                                porcentaje = (stats['disponibles'] / stats['total']) * 100 if stats['total'] > 0 else 0
                                
                                if porcentaje == 100:
                                    st.success(f"**{categoria}**: {stats['disponibles']}/{stats['total']} productos ({porcentaje:.0f}%)")
                                elif porcentaje >= 50:
                                    st.warning(f"**{categoria}**: {stats['disponibles']}/{stats['total']} productos ({porcentaje:.0f}%)")
                                else:
                                    st.error(f"**{categoria}**: {stats['disponibles']}/{stats['total']} productos ({porcentaje:.0f}%)")
                        
                        # SECCIÓN: Documentos regulatorios médicos
                        if evaluacion.get('documentos_requeridos'):
                            st.markdown("---")
                            st.markdown("#### DOCUMENTOS REGULATORIOS MÉDICOS:")
                            
                            total_docs = evaluacion.get('total_documentos', 0)
                            docs_criticos = evaluacion.get('documentos_criticos_medicos', 0)
                            
                            if docs_criticos > 0:
                                st.error(f"**{docs_criticos} documentos regulatorios CRÍTICOS** de {total_docs} totales")
                            else:
                                st.info(f"**Total de documentos requeridos: {total_docs}**")
                            
                            # Mostrar documentos agrupados por tipo médico
                            docs_por_tipo = evaluacion.get('documentos_por_tipo', {})
                            
                            if docs_por_tipo:
                                for tipo, documentos in docs_por_tipo.items():
                                    # Emoji especializado por tipo médico
                                    emoji_tipo = {
                                        'Regulatorio Médico': '🏥',
                                        'Calidad Médica': '🔬',
                                        'Personal Especializado': '👨‍⚕️',
                                        'Legal': '⚖️',
                                        'Financiero': '💰',
                                        'Propuesta': '📄',
                                        'General': '📋'
                                    }.get(tipo, '📄')
                                    
                                    # Determinar criticidad del tipo
                                    es_critico = tipo in ['Regulatorio Médico', 'Calidad Médica', 'Personal Especializado']
                                    
                                    if es_critico:
                                        st.markdown(f"**🚨 {emoji_tipo} {tipo} (CRÍTICO):**")
                                    else:
                                        st.markdown(f"**{emoji_tipo} {tipo}:**")
                                    
                                    for doc in documentos:
                                        obligatorio_texto = "🔴 **OBLIGATORIO**" if doc['obligatorio'] else "🟡 *Opcional*"
                                        sector_texto = f" - Sector: {doc.get('sector', 'N/A')}"
                                        st.write(f"  • {doc['nombre']} - {obligatorio_texto}{sector_texto}")
                                    
                                    st.write("")
                        
                        elif requerimientos_df is not None:
                            st.markdown("---")
                            st.markdown("#### DOCUMENTOS REGULATORIOS:")
                            st.info("ℹ️ No se encontraron requerimientos regulatorios específicos para esta licitación médica.")
                            st.write("*Verifica que el nombre de la licitación coincida con el archivo de requerimientos.*")
            
            # Estadísticas globales médicas
            st.subheader("Estadísticas Globales del Sector Médico")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Distribución por Estado:**")
                chart_data = pd.DataFrame({
                    'Estado': ['Aptas', 'Revisar', 'No Aptas', 'Críticas'],
                    'Cantidad': [verdes, amarillos, rojos, criticos]
                })
                
                for _, row in chart_data.iterrows():
                    porcentaje = (row['Cantidad'] / total * 100) if total > 0 else 0
                    st.write(f"{row['Estado']}: {row['Cantidad']} ({porcentaje:.1f}%)")
            
            with col2:
                st.markdown("**Alertas de Caducidad:**")
                if total_alertas_caducidad > 0:
                    st.error(f"{total_alertas_caducidad} productos con alertas de caducidad")
                    st.write("Revisar medicamentos próximos a caducar")
                    st.write("Implementar rotación FEFO (First Expired, First Out)")
                else:
                    st.success("Sin alertas críticas de caducidad")
            
            # Descargar resultados médicos
            csv_resultado = resultados_df.to_csv(index=False)
            st.download_button(
                label="Descargar Análisis Médico Completo (CSV)",
                data=csv_resultado,
                file_name=f"analisis_licitaciones_medicas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
            
        else:
            st.error("No se pudieron procesar las licitaciones médicas. Verifica el formato de los archivos.")

# Footer con información adicional para sector médico
st.markdown("---")
st.markdown("### Información Adicional para Licitaciones Médicas")

with st.expander("Guía de Categorías Médicas Soportadas"):
    st.markdown("""
    **Categorías principales del sistema:**
    
    **Medicamentos:**
    - Analgésicos (paracetamol, ibuprofeno, aspirina)
    - Antibióticos (amoxicilina, cefalexina)
    - Antihipertensivos (losartán, atenolol)
    - Antidiabéticos (metformina, insulina)
    - Y muchos más...
    
    **Material de Curación:**
    - Gasas estériles y no estériles
    - Vendas elásticas y de diferentes tamaños
    - Antisépticos (alcohol, yodo, povidona)
    - Suturas y material quirúrgico
    
    **Equipos Médicos:**
    - Equipos de diagnóstico (estetoscopios, tensiómetros)
    - Equipos de laboratorio (microscopios, centrífugas)
    - Equipos de emergencia (desfibriladores, monitores)
    
    **Dispositivos Desechables:**
    - Jeringas de diferentes tamaños
    - Agujas hipodérmicas
    - Catéteres y sondas
    
    **Equipo de Protección:**
    - Guantes (látex, nitrilo)
    - Mascarillas y cubrebocas
    - Batas y equipos quirúrgicos
    """)

st.markdown("""
**Sistema especializado para el análisis de licitaciones médicas y farmacéuticas**  
*Versión optimizada para vocabulario médico, control de caducidades y gestión hospitalaria*
""")