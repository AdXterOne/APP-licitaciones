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

def clasificar_producto_medico(nombre):
    """Clasifica productos médicos expandido"""
    nombre_lower = nombre.lower()
    
    # Mapeo expandido de productos médicos
    productos_medicos = {
        # ANALGÉSICOS
        'paracetamol': ['paracetamol', 'acetaminofen'],
        'ibuprofeno': ['ibuprofeno', 'advil'],
        'aspirina': ['aspirina', 'acido acetilsalicilico'],
        'diclofenaco': ['diclofenaco', 'voltaren'],
        'naproxeno': ['naproxeno'],
        'ketorolaco': ['ketorolaco'],
        'metamizol': ['metamizol', 'dipirona'],
        'celecoxib': ['celecoxib'],
        'meloxicam': ['meloxicam'],
        
        # ANTIBIÓTICOS
        'amoxicilina': ['amoxicilina', 'amoxil'],
        'ampicilina': ['ampicilina'],
        'penicilina': ['penicilina'],
        'cefalexina': ['cefalexina', 'keflex'],
        'ciprofloxacino': ['ciprofloxacino', 'cipro'],
        'levofloxacino': ['levofloxacino'],
        'azitromicina': ['azitromicina', 'zitromax'],
        'claritromicina': ['claritromicina'],
        'eritromicina': ['eritromicina'],
        'clindamicina': ['clindamicina'],
        'metronidazol': ['metronidazol'],
        'trimetoprima': ['trimetoprima', 'sulfametoxazol', 'bactrim'],
        'doxiciclina': ['doxiciclina'],
        'tetraciclina': ['tetraciclina'],
        'ceftriaxona': ['ceftriaxona'],
        'cefuroxima': ['cefuroxima'],
        'vancomicina': ['vancomicina'],
        'lincomicina': ['lincomicina'],
        
        # ANTIVIRALES
        'aciclovir': ['aciclovir', 'zovirax'],
        'oseltamivir': ['oseltamivir', 'tamiflu'],
        'ribavirina': ['ribavirina'],
        'ganciclovir': ['ganciclovir'],
        'valaciclovir': ['valaciclovir'],
        'zidovudina': ['zidovudina', 'azt'],
        
        # ANTIFÚNGICOS
        'fluconazol': ['fluconazol'],
        'itraconazol': ['itraconazol'],
        'ketoconazol': ['ketoconazol'],
        'nistatina': ['nistatina'],
        'anfotericina': ['anfotericina'],
        'terbinafina': ['terbinafina'],
        
        # VACUNAS
        'vacuna_influenza': ['vacuna influenza', 'vacuna gripe', 'influenza'],
        'vacuna_covid': ['vacuna covid', 'covid', 'coronavirus'],
        'vacuna_hepatitis': ['vacuna hepatitis', 'hepatitis'],
        'vacuna_tetano': ['vacuna tetano', 'tetano'],
        'vacuna_sarampion': ['vacuna sarampion', 'sarampion'],
        'vacuna_bcg': ['bcg', 'tuberculosis'],
        'vacuna_neumococo': ['neumococo', 'pneumococo'],
        
        # CARDIOVASCULARES
        'losartan': ['losartan', 'cozaar'],
        'enalapril': ['enalapril'],
        'captopril': ['captopril'],
        'amlodipino': ['amlodipino'],
        'nifedipino': ['nifedipino'],
        'atenolol': ['atenolol'],
        'metoprolol': ['metoprolol'],
        'propranolol': ['propranolol'],
        'carvedilol': ['carvedilol'],
        'furosemida': ['furosemida', 'lasix'],
        'hidroclorotiazida': ['hidroclorotiazida', 'hctz'],
        'espironolactona': ['espironolactona'],
        'digoxina': ['digoxina'],
        'warfarina': ['warfarina'],
        'clopidogrel': ['clopidogrel', 'plavix'],
        'simvastatina': ['simvastatina'],
        'atorvastatina': ['atorvastatina'],
        'rosuvastatina': ['rosuvastatina'],
        
        # GASTROINTESTINALES
        'omeprazol': ['omeprazol', 'prilosec'],
        'lansoprazol': ['lansoprazol'],
        'pantoprazol': ['pantoprazol'],
        'ranitidina': ['ranitidina'],
        'cimetidina': ['cimetidina'],
        'sucralfato': ['sucralfato'],
        'domperidona': ['domperidona'],
        'metoclopramida': ['metoclopramida'],
        'loperamida': ['loperamida'],
        'lactulosa': ['lactulosa'],
        'simeticona': ['simeticona'],
        
        # DIABETES
        'metformina': ['metformina', 'glucophage'],
        'glibenclamida': ['glibenclamida'],
        'gliclazida': ['gliclazida'],
        'insulina': ['insulina'],
        'insulina_rapida': ['insulina rapida', 'insulina cristalina'],
        'insulina_nph': ['insulina nph', 'insulina intermedia'],
        'insulina_lenta': ['insulina lenta', 'insulina glargina'],
        
        # RESPIRATORIOS
        'salbutamol': ['salbutamol', 'ventolin'],
        'bromuro_ipratropio': ['ipratropio', 'atrovent'],
        'budesonida': ['budesonida'],
        'beclometasona': ['beclometasona'],
        'prednisolona': ['prednisolona'],
        'prednisona': ['prednisona'],
        'dexametasona': ['dexametasona'],
        'hidrocortisona': ['hidrocortisona'],
        'teofilina': ['teofilina'],
        'montelukast': ['montelukast'],
        
        # NEUROLÓGICOS Y PSIQUIÁTRICOS
        'fenitoina': ['fenitoina'],
        'carbamazepina': ['carbamazepina'],
        'acido_valproico': ['acido valproico', 'valproato'],
        'levodopa': ['levodopa'],
        'haloperidol': ['haloperidol'],
        'clorpromazina': ['clorpromazina'],
        'risperidona': ['risperidona'],
        'olanzapina': ['olanzapina'],
        'quetiapina': ['quetiapina'],
        'fluoxetina': ['fluoxetina', 'prozac'],
        'sertralina': ['sertralina'],
        'paroxetina': ['paroxetina'],
        'amitriptilina': ['amitriptilina'],
        'diazepam': ['diazepam', 'valium'],
        'lorazepam': ['lorazepam'],
        'clonazepam': ['clonazepam'],
        'alprazolam': ['alprazolam'],
        
        # ANESTÉSICOS Y OPIOIDES
        'morfina': ['morfina'],
        'tramadol': ['tramadol'],
        'codeina': ['codeina'],
        'fentanilo': ['fentanilo'],
        'lidocaina': ['lidocaina'],
        'bupivacaina': ['bupivacaina'],
        'procaina': ['procaina'],
        
        # HORMONAS
        'levotiroxina': ['levotiroxina', 'eutirox'],
        'metimazol': ['metimazol'],
        'propiltiouracilo': ['propiltiouracilo'],
        'estradiol': ['estradiol'],
        'progesterona': ['progesterona'],
        'testosterona': ['testosterona'],
        
        # SUEROS Y SOLUCIONES
        'suero_fisiologico': ['suero fisiologico', 'solucion salina', 'nacl', 'cloruro sodio', 'suero'],
        'dextrosa': ['dextrosa', 'glucosa'],
        'hartmann': ['hartmann', 'lactato ringer', 'ringer'],
        'agua_inyectable': ['agua inyectable', 'agua destilada'],
        'bicarbonato_sodio': ['bicarbonato sodio', 'bicarbonato'],
        'albumina': ['albumina'],
        'plasma': ['plasma'],
        
        # MATERIAL DE CURACIÓN
        'gasas': ['gasas', 'gasa', 'compresas', 'gasas esteriles'],
        'vendas': ['vendas', 'venda', 'vendaje', 'vendas elasticas'],
        'alcohol': ['alcohol', 'alcohol etilico', 'alcohol 70'],
        'yodo': ['yodo', 'povidona yodada', 'isodine', 'betadine'],
        'agua_oxigenada': ['agua oxigenada', 'peroxido hidrogeno'],
        'algodon': ['algodon', 'torundas', 'hisopos'],
        'suturas': ['suturas', 'sutura', 'hilo quirurgico'],
        'apositos': ['apositos', 'aposito', 'curita', 'parches'],
        'esparadrapo': ['esparadrapo', 'cinta adhesiva', 'tape'],
        
        # DISPOSITIVOS MÉDICOS
        'jeringas': ['jeringas', 'jeringa', 'jeringuilla'],
        'agujas': ['agujas', 'aguja', 'agujas hipodermicas'],
        'cateter': ['cateter', 'sonda', 'canula'],
        'scalp': ['scalp', 'mariposa', 'butterfly'],
        'sondas_foley': ['sonda foley', 'foley'],
        'sondas_nasogastricas': ['sonda nasogastrica', 'levine'],
        'tubos_endotraqueales': ['tubo endotraqueal', 'tubo orotraqueal'],
        
        # EQUIPO DE PROTECCIÓN PERSONAL
        'guantes_latex': ['guantes latex', 'guantes'],
        'guantes_nitrilo': ['guantes nitrilo'],
        'guantes_vinilo': ['guantes vinilo'],
        'mascarillas': ['mascarillas', 'mascarilla', 'cubrebocas'],
        'mascarillas_n95': ['mascarilla n95', 'n95', 'respirador'],
        'batas': ['batas', 'bata', 'bata quirurgica'],
        'gorros': ['gorros', 'gorro', 'gorro quirurgico'],
        'botas': ['botas', 'cubre calzado'],
        'gafas_proteccion': ['gafas proteccion', 'lentes proteccion'],
        
        # EQUIPOS MÉDICOS
        'termometro': ['termometro', 'termometro digital'],
        'estetoscopio': ['estetoscopio', 'fonendoscopio'],
        'tensiometro': ['tensiometro', 'baumanometro', 'esfigmomanometro'],
        'oximetro': ['oximetro', 'pulsioximetro', 'saturometro'],
        'glucometro': ['glucometro', 'medidor glucosa'],
        'otoscopio': ['otoscopio'],
        'oftalmoscopio': ['oftalmoscopio'],
        'laringoscopio': ['laringoscopio'],
        'desfibrilador': ['desfibrilador'],
        'electrocardiografo': ['electrocardiografo', 'ecg', 'ekg'],
        'monitor_signos': ['monitor signos vitales', 'monitor paciente'],
        'ventilador': ['ventilador mecanico', 'respirador'],
        'bomba_infusion': ['bomba infusion', 'bomba volumetrica'],
        'aspiradora': ['aspiradora', 'succionador'],
        'microscopio': ['microscopio', 'microscopio optico'],
        'centrifuga': ['centrifuga', 'centrifugadora'],
        'autoclave': ['autoclave', 'esterilizador'],
        'incubadora': ['incubadora'],
        'refrigerador': ['refrigerador', 'nevera', 'congelador'],
        
        # INSTRUMENTAL QUIRÚRGICO
        'bisturi': ['bisturi', 'escalpelo', 'hoja bisturi'],
        'pinzas': ['pinzas', 'forceps', 'pinzas quirurgicas'],
        'tijeras': ['tijeras', 'tijeras quirurgicas'],
        'hemostatos': ['hemostatos', 'kelly', 'mosquito'],
        'separadores': ['separadores', 'retractores'],
        'portaagujas': ['portaagujas', 'porta agujas'],
        'clamps': ['clamps', 'pinzas vasculares'],
        'especulos': ['especulo', 'especulos'],
        
        # PRODUCTOS DE LIMPIEZA
        'cloro': ['cloro', 'hipoclorito', 'hipoclorito sodio'],
        'desinfectante': ['desinfectante', 'germicida'],
        'alcohol_gel': ['alcohol gel', 'gel antibacterial'],
        'glutaraldehido': ['glutaraldehido'],
        'formaldehido': ['formaldehido', 'formol'],
        'detergente': ['detergente', 'jabon', 'detergente enzimatico'],
        
        # OXÍGENO Y GASES
        'oxigeno': ['oxigeno', 'o2'],
        'tanque_oxigeno': ['tanque oxigeno', 'cilindro oxigeno'],
        'concentrador_oxigeno': ['concentrador oxigeno'],
        'regulador_oxigeno': ['regulador oxigeno', 'manometro'],
        'mascarilla_oxigeno': ['mascarilla oxigeno'],
        'canula_nasal': ['canula nasal', 'puntas nasales']
    }
    
    # Buscar coincidencia exacta o parcial
    for producto, variantes in productos_medicos.items():
        if any(variante in nombre_lower for variante in variantes):
            return producto
    
    # Búsqueda adicional por sufijos farmacéuticos comunes
    sufijos_farmaceuticos = {
        'cilina': 'antibiotico',
        'floxacino': 'antibiotico',
        'micina': 'antibiotico',
        'prazol': 'inhibidor_bomba_protones',
        'sartan': 'antihipertensivo',
        'pril': 'antihipertensivo',
        'olol': 'betabloqueador',
        'statina': 'estatina',
        'pine': 'bloqueador_calcio',
        'zole': 'antifungico',
        'vir': 'antiviral'
    }
    
    for sufijo, categoria in sufijos_farmaceuticos.items():
        if sufijo in nombre_lower:
            return categoria
    
    return None

def determinar_categoria(producto):
    """Determina la categoría médica del producto"""
    categorias = {
        # ANALGÉSICOS
        'paracetamol': 'Analgésicos', 'ibuprofeno': 'Analgésicos', 'aspirina': 'Analgésicos',
        'diclofenaco': 'Analgésicos', 'naproxeno': 'Analgésicos', 'ketorolaco': 'Analgésicos',
        'metamizol': 'Analgésicos', 'celecoxib': 'Analgésicos', 'meloxicam': 'Analgésicos',
        
        # ANTIBIÓTICOS
        'amoxicilina': 'Antibióticos', 'ampicilina': 'Antibióticos', 'penicilina': 'Antibióticos',
        'cefalexina': 'Antibióticos', 'ciprofloxacino': 'Antibióticos', 'levofloxacino': 'Antibióticos',
        'azitromicina': 'Antibióticos', 'claritromicina': 'Antibióticos', 'eritromicina': 'Antibióticos',
        'clindamicina': 'Antibióticos', 'metronidazol': 'Antibióticos', 'trimetoprima': 'Antibióticos',
        'doxiciclina': 'Antibióticos', 'tetraciclina': 'Antibióticos', 'ceftriaxona': 'Antibióticos',
        'cefuroxima': 'Antibióticos', 'vancomicina': 'Antibióticos', 'lincomicina': 'Antibióticos',
        'antibiotico': 'Antibióticos',
        
        # ANTIVIRALES
        'aciclovir': 'Antivirales', 'oseltamivir': 'Antivirales', 'ribavirina': 'Antivirales',
        'ganciclovir': 'Antivirales', 'valaciclovir': 'Antivirales', 'zidovudina': 'Antivirales',
        'antiviral': 'Antivirales',
        
        # ANTIFÚNGICOS
        'fluconazol': 'Antifúngicos', 'itraconazol': 'Antifúngicos', 'ketoconazol': 'Antifúngicos',
        'nistatina': 'Antifúngicos', 'anfotericina': 'Antifúngicos', 'terbinafina': 'Antifúngicos',
        'antifungico': 'Antifúngicos',
        
        # VACUNAS
        'vacuna_influenza': 'Vacunas', 'vacuna_covid': 'Vacunas', 'vacuna_hepatitis': 'Vacunas',
        'vacuna_tetano': 'Vacunas', 'vacuna_sarampion': 'Vacunas', 'vacuna_bcg': 'Vacunas',
        'vacuna_neumococo': 'Vacunas',
        
        # CARDIOVASCULARES
        'losartan': 'Cardiovasculares', 'enalapril': 'Cardiovasculares', 'captopril': 'Cardiovasculares',
        'amlodipino': 'Cardiovasculares', 'nifedipino': 'Cardiovasculares', 'atenolol': 'Cardiovasculares',
        'metoprolol': 'Cardiovasculares', 'propranolol': 'Cardiovasculares', 'carvedilol': 'Cardiovasculares',
        'furosemida': 'Cardiovasculares', 'hidroclorotiazida': 'Cardiovasculares', 'espironolactona': 'Cardiovasculares',
        'digoxina': 'Cardiovasculares', 'warfarina': 'Cardiovasculares', 'clopidogrel': 'Cardiovasculares',
        'simvastatina': 'Cardiovasculares', 'atorvastatina': 'Cardiovasculares', 'rosuvastatina': 'Cardiovasculares',
        'antihipertensivo': 'Cardiovasculares', 'betabloqueador': 'Cardiovasculares', 'estatina': 'Cardiovasculares',
        'bloqueador_calcio': 'Cardiovasculares',
        
        # GASTROINTESTINALES
        'omeprazol': 'Gastrointestinales', 'lansoprazol': 'Gastrointestinales', 'pantoprazol': 'Gastrointestinales',
        'ranitidina': 'Gastrointestinales', 'cimetidina': 'Gastrointestinales', 'sucralfato': 'Gastrointestinales',
        'domperidona': 'Gastrointestinales', 'metoclopramida': 'Gastrointestinales', 'loperamida': 'Gastrointestinales',
        'lactulosa': 'Gastrointestinales', 'simeticona': 'Gastrointestinales',
        'inhibidor_bomba_protones': 'Gastrointestinales',
        
        # ENDOCRINOLÓGICOS
        'metformina': 'Endocrinológicos', 'glibenclamida': 'Endocrinológicos', 'gliclazida': 'Endocrinológicos',
        'insulina': 'Endocrinológicos', 'insulina_rapida': 'Endocrinológicos', 'insulina_nph': 'Endocrinológicos',
        'insulina_lenta': 'Endocrinológicos', 'levotiroxina': 'Endocrinológicos', 'metimazol': 'Endocrinológicos',
        'propiltiouracilo': 'Endocrinológicos',
        
        # RESPIRATORIOS
        'salbutamol': 'Respiratorios', 'bromuro_ipratropio': 'Respiratorios', 'budesonida': 'Respiratorios',
        'beclometasona': 'Respiratorios', 'prednisolona': 'Respiratorios', 'prednisona': 'Respiratorios',
        'dexametasona': 'Respiratorios', 'hidrocortisona': 'Respiratorios', 'teofilina': 'Respiratorios',
        'montelukast': 'Respiratorios',
        
        # NEUROLÓGICOS
        'fenitoina': 'Neurológicos', 'carbamazepina': 'Neurológicos', 'acido_valproico': 'Neurológicos',
        'levodopa': 'Neurológicos', 'haloperidol': 'Neurológicos', 'clorpromazina': 'Neurológicos',
        'risperidona': 'Neurológicos', 'olanzapina': 'Neurológicos', 'quetiapina': 'Neurológicos',
        'fluoxetina': 'Neurológicos', 'sertralina': 'Neurológicos', 'paroxetina': 'Neurológicos',
        'amitriptilina': 'Neurológicos', 'diazepam': 'Neurológicos', 'lorazepam': 'Neurológicos',
        'clonazepam': 'Neurológicos', 'alprazolam': 'Neurológicos',
        
        # ANESTÉSICOS Y OPIOIDES
        'morfina': 'Anestésicos y Opioides', 'tramadol': 'Anestésicos y Opioides', 'codeina': 'Anestésicos y Opioides',
        'fentanilo': 'Anestésicos y Opioides', 'lidocaina': 'Anestésicos y Opioides', 'bupivacaina': 'Anestésicos y Opioides',
        'procaina': 'Anestésicos y Opioides',
        
        # HORMONAS
        'estradiol': 'Hormonas', 'progesterona': 'Hormonas', 'testosterona': 'Hormonas',
        
        # SUEROS Y SOLUCIONES
        'suero_fisiologico': 'Sueros y Soluciones', 'dextrosa': 'Sueros y Soluciones',
        'hartmann': 'Sueros y Soluciones', 'agua_inyectable': 'Sueros y Soluciones',
        'bicarbonato_sodio': 'Sueros y Soluciones', 'albumina': 'Sueros y Soluciones', 'plasma': 'Sueros y Soluciones',
        
        # MATERIAL DE CURACIÓN
        'gasas': 'Material de Curación', 'vendas': 'Material de Curación', 'alcohol': 'Material de Curación',
        'yodo': 'Material de Curación', 'agua_oxigenada': 'Material de Curación', 'algodon': 'Material de Curación',
        'suturas': 'Material de Curación', 'apositos': 'Material de Curación', 'esparadrapo': 'Material de Curación',
        
        # DISPOSITIVOS MÉDICOS
        'jeringas': 'Dispositivos Médicos', 'agujas': 'Dispositivos Médicos', 'cateter': 'Dispositivos Médicos',
        'scalp': 'Dispositivos Médicos', 'sondas_foley': 'Dispositivos Médicos', 'sondas_nasogastricas': 'Dispositivos Médicos',
        'tubos_endotraqueales': 'Dispositivos Médicos',
        
        # EQUIPO DE PROTECCIÓN
        'guantes_latex': 'Equipo de Protección', 'guantes_nitrilo': 'Equipo de Protección', 'guantes_vinilo': 'Equipo de Protección',
        'mascarillas': 'Equipo de Protección', 'mascarillas_n95': 'Equipo de Protección', 'batas': 'Equipo de Protección',
        'gorros': 'Equipo de Protección', 'botas': 'Equipo de Protección', 'gafas_proteccion': 'Equipo de Protección',
        
        # EQUIPOS MÉDICOS
        'termometro': 'Equipos Médicos', 'estetoscopio': 'Equipos Médicos', 'tensiometro': 'Equipos Médicos',
        'oximetro': 'Equipos Médicos', 'glucometro': 'Equipos Médicos', 'otoscopio': 'Equipos Médicos',
        'oftalmoscopio': 'Equipos Médicos', 'laringoscopio': 'Equipos Médicos', 'desfibrilador': 'Equipos Médicos',
        'electrocardiografo': 'Equipos Médicos', 'monitor_signos': 'Equipos Médicos', 'ventilador': 'Equipos Médicos',
        'bomba_infusion': 'Equipos Médicos', 'aspiradora': 'Equipos Médicos', 'microscopio': 'Equipos Médicos',
        'centrifuga': 'Equipos Médicos', 'autoclave': 'Equipos Médicos', 'incubadora': 'Equipos Médicos',
        'refrigerador': 'Equipos Médicos',
        
        # INSTRUMENTAL QUIRÚRGICO
        'bisturi': 'Instrumental Quirúrgico', 'pinzas': 'Instrumental Quirúrgico', 'tijeras': 'Instrumental Quirúrgico',
        'hemostatos': 'Instrumental Quirúrgico', 'separadores': 'Instrumental Quirúrgico', 'portaagujas': 'Instrumental Quirúrgico',
        'clamps': 'Instrumental Quirúrgico', 'especulos': 'Instrumental Quirúrgico',
        
        # PRODUCTOS DE LIMPIEZA
        'cloro': 'Productos de Limpieza', 'desinfectante': 'Productos de Limpieza', 'alcohol_gel': 'Productos de Limpieza',
        'glutaraldehido': 'Productos de Limpieza', 'formaldehido': 'Productos de Limpieza', 'detergente': 'Productos de Limpieza',
        
        # GASES MEDICINALES
        'oxigeno': 'Gases Medicinales', 'tanque_oxigeno': 'Gases Medicinales', 'concentrador_oxigeno': 'Gases Medicinales',
        'regulador_oxigeno': 'Gases Medicinales', 'mascarilla_oxigeno': 'Gases Medicinales', 'canula_nasal': 'Gases Medicinales'
    }
    
    return categorias.get(producto, 'Medicamentos Generales')

def extraer_productos_medicos(descripcion):
    """Extrae productos médicos de la descripción con reconocimiento expandido"""
    if pd.isna(descripcion):
        return []
    
    texto = normalizar_texto(descripcion)
    productos = []
    
    # Patrones mejorados para detectar productos médicos
    patrones = [
        r'(\d+)\s+([a-z\s]+?)(?=\d+\s+[a-z]|,|$)',
        r'(\d+)\s*([a-z\s]+?)(?=,|$)',
        r'([a-z\s]+?)\s+(\d+)',
        r'(\d+)\s*(mg|ml|gr|kg|mcg|ui)?\s*([a-z\s]+?)(?=\d+|,|$)',
        r'(licitacion|vacuna|medicamento)\s+([a-z\s]+?)(?=\d+|,|$)'
    ]
    # Primero, intentar extraer con patrones que incluyen cantidad
    for patron in patrones[:3]:
        matches = re.findall(patron, texto)
        for match in matches:
            try:
                if len(match) == 2:
                    cantidad_str, nombre = match
                elif len(match) == 3:
                    cantidad_str, unidad, nombre = match
                else:
                    continue
                
                # Intentar convertir a número
                try:
                    cantidad = int(cantidad_str)
                except:
                    # Si el primer elemento no es número, intercambiar
                    try:
                        cantidad = int(match[1] if len(match) == 2 else match[0])
                        nombre = match[0] if len(match) == 2 else match[2]
                    except:
                        continue
                
                nombre = nombre.strip()
                
                if cantidad > 0 and cantidad <= 100000 and len(nombre) > 2:
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
    
    # Si no se encontraron productos con cantidad, buscar por nombres de medicamentos conocidos
    if not productos:
        medicamentos_conocidos = [
            'paracetamol', 'ibuprofeno', 'aspirina', 'amoxicilina', 'ciprofloxacino',
            'aciclovir', 'oseltamivir', 'insulina', 'morfina', 'tramadol',
            'omeprazol', 'losartan', 'metformina', 'salbutamol', 'dexametasona'
        ]
        
        for medicamento in medicamentos_conocidos:
            if medicamento in texto:
                # Buscar cantidad cerca del medicamento
                patron_cerca = f'(\d+)\s*.*?{medicamento}|{medicamento}\s*.*?(\d+)'
                match = re.search(patron_cerca, texto)
                cantidad = 1  # Cantidad por defecto
                
                if match:
                    try:
                        cantidad = int(match.group(1) or match.group(2))
                    except:
                        cantidad = 1
                
                categoria = clasificar_producto_medico(medicamento)
                if categoria:
                    productos.append({
                        'nombre': categoria,
                        'cantidad': cantidad,
                        'descripcion_original': medicamento,
                        'categoria': determinar_categoria(categoria)
                    })
    
    # Extraer del nombre de la licitación si contiene nombres de medicamentos
    if not productos:
        # Buscar patrones como "Licitación Amoxicilina 3"
        patron_licitacion = r'licitacion\s+([a-z]+)\s*(\d+)?'
        match = re.search(patron_licitacion, texto)
        
        if match:
            nombre_medicamento = match.group(1)
            cantidad = int(match.group(2)) if match.group(2) else 1
            
            categoria = clasificar_producto_medico(nombre_medicamento)
            if categoria:
                productos.append({
                    'nombre': categoria,
                    'cantidad': cantidad,
                    'descripcion_original': nombre_medicamento,
                    'categoria': determinar_categoria(categoria)
                })
    
    # Eliminar duplicados manteniendo la mayor cantidad
    productos_unicos = {}
    for producto in productos:
        nombre = producto['nombre']
        if nombre in productos_unicos:
            if producto['cantidad'] > productos_unicos[nombre]['cantidad']:
                productos_unicos[nombre] = producto
        else:
            productos_unicos[nombre] = producto
    
    return list(productos_unicos.values())

def buscar_en_inventario(producto_buscado, inventario_df):
    """Busca un producto en el inventario con mapeo expandido"""
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
    
    # Mapeo expandido para búsqueda en inventario
    mapeo_busqueda = {
        # ANALGÉSICOS
        'paracetamol': ['paracetamol', 'acetaminofen', 'tylenol'],
        'ibuprofeno': ['ibuprofeno', 'advil', 'motrin'],
        'aspirina': ['aspirina', 'acido acetilsalicilico', 'asa'],
        'diclofenaco': ['diclofenaco', 'voltaren'],
        'naproxeno': ['naproxeno'],
        'ketorolaco': ['ketorolaco'],
        'metamizol': ['metamizol', 'dipirona', 'novalgin'],
        
        # ANTIBIÓTICOS
        'amoxicilina': ['amoxicilina', 'amoxil'],
        'ampicilina': ['ampicilina'],
        'penicilina': ['penicilina'],
        'cefalexina': ['cefalexina', 'keflex'],
        'ciprofloxacino': ['ciprofloxacino', 'cipro', 'ciprofloxacina'],
        'levofloxacino': ['levofloxacino', 'levofloxacina'],
        'azitromicina': ['azitromicina', 'zitromax'],
        'claritromicina': ['claritromicina'],
        'eritromicina': ['eritromicina'],
        'clindamicina': ['clindamicina'],
        'metronidazol': ['metronidazol'],
        'trimetoprima': ['trimetoprima', 'sulfametoxazol', 'bactrim'],
        'ceftriaxona': ['ceftriaxona'],
        'antibiotico': ['antibiotico', 'antimicrobiano'],
        
        # ANTIVIRALES
        'aciclovir': ['aciclovir', 'zovirax'],
        'oseltamivir': ['oseltamivir', 'tamiflu'],
        'ribavirina': ['ribavirina'],
        'antiviral': ['antiviral'],
        
        # ANTIFÚNGICOS
        'fluconazol': ['fluconazol'],
        'ketoconazol': ['ketoconazol'],
        'antifungico': ['antifungico', 'antimicotico'],
        
        # VACUNAS
        'vacuna_influenza': ['vacuna influenza', 'vacuna gripe', 'influenza'],
        'vacuna_covid': ['vacuna covid', 'covid', 'coronavirus', 'sars-cov'],
        'vacuna_hepatitis': ['vacuna hepatitis', 'hepatitis'],
        'vacuna_tetano': ['vacuna tetano', 'tetano'],
        
        # CARDIOVASCULARES
        'losartan': ['losartan', 'cozaar'],
        'enalapril': ['enalapril'],
        'captopril': ['captopril'],
        'amlodipino': ['amlodipino', 'norvasc'],
        'atenolol': ['atenolol'],
        'metoprolol': ['metoprolol'],
        'furosemida': ['furosemida', 'lasix'],
        'simvastatina': ['simvastatina'],
        'atorvastatina': ['atorvastatina', 'lipitor'],
        'antihipertensivo': ['antihipertensivo', 'hipertension'],
        'betabloqueador': ['betabloqueador', 'beta bloqueador'],
        
        # GASTROINTESTINALES
        'omeprazol': ['omeprazol', 'prilosec'],
        'lansoprazol': ['lansoprazol'],
        'pantoprazol': ['pantoprazol'],
        'ranitidina': ['ranitidina'],
        'inhibidor_bomba_protones': ['inhibidor bomba protones', 'prazol'],
        
        # DIABETES
        'metformina': ['metformina', 'glucophage'],
        'glibenclamida': ['glibenclamida'],
        'insulina': ['insulina'],
        'insulina_rapida': ['insulina rapida', 'insulina cristalina'],
        'insulina_nph': ['insulina nph', 'insulina intermedia'],
        'antidiabetico': ['antidiabetico', 'diabetes'],
        
        # RESPIRATORIOS
        'salbutamol': ['salbutamol', 'ventolin', 'albuterol'],
        'prednisolona': ['prednisolona'],
        'prednisona': ['prednisona'],
        'dexametasona': ['dexametasona'],
        'corticoide': ['corticoide', 'esteroide'],
        
        # ANESTÉSICOS Y OPIOIDES
        'morfina': ['morfina'],
        'tramadol': ['tramadol'],
        'lidocaina': ['lidocaina'],
        'fentanilo': ['fentanilo'],
        
        # SUEROS Y SOLUCIONES
        'suero_fisiologico': ['suero fisiologico', 'solucion salina', 'nacl', 'suero', 'salina'],
        'dextrosa': ['dextrosa', 'glucosa'],
        'hartmann': ['hartmann', 'lactato ringer', 'ringer'],
        'agua_inyectable': ['agua inyectable', 'agua destilada'],
        
        # MATERIAL DE CURACIÓN
        'gasas': ['gasas', 'gasa', 'compresas', 'gasas esteriles'],
        'vendas': ['vendas', 'venda', 'vendaje', 'vendas elasticas'],
        'alcohol': ['alcohol', 'alcohol etilico', 'alcohol 70'],
        'yodo': ['yodo', 'povidona', 'betadine', 'isodine'],
        'algodon': ['algodon', 'torundas', 'hisopos'],
        'suturas': ['suturas', 'sutura', 'hilo quirurgico'],
        'apositos': ['apositos', 'aposito', 'parches', 'curitas'],
        
        # DISPOSITIVOS MÉDICOS
        'jeringas': ['jeringas', 'jeringa', 'jeringuilla'],
        'agujas': ['agujas', 'aguja', 'agujas hipodermicas'],
        'cateter': ['cateter', 'sonda', 'canula'],
        'scalp': ['scalp', 'mariposa', 'butterfly'],
        'sondas': ['sondas', 'sonda'],
        
        # EQUIPO DE PROTECCIÓN
        'guantes_latex': ['guantes latex', 'guantes'],
        'guantes_nitrilo': ['guantes nitrilo'],
        'mascarillas': ['mascarillas', 'mascarilla', 'cubrebocas'],
        'mascarillas_n95': ['n95', 'respirador n95'],
        'batas': ['batas', 'bata', 'bata quirurgica'],
        'gorros': ['gorros', 'gorro', 'gorro quirurgico'],
        
        # EQUIPOS MÉDICOS
        'termometro': ['termometro', 'termometro digital'],
        'estetoscopio': ['estetoscopio', 'fonendoscopio'],
        'tensiometro': ['tensiometro', 'baumanometro', 'esfigmomanometro'],
        'oximetro': ['oximetro', 'pulsioximetro', 'saturometro'],
        'glucometro': ['glucometro', 'medidor glucosa'],
        'microscopio': ['microscopio', 'microscopio optico'],
        'centrifuga': ['centrifuga', 'centrifugadora'],
        'desfibrilador': ['desfibrilador'],
        
        # INSTRUMENTAL QUIRÚRGICO
        'bisturi': ['bisturi', 'escalpelo', 'hoja bisturi'],
        'pinzas': ['pinzas', 'forceps', 'pinzas quirurgicas'],
        'tijeras': ['tijeras', 'tijeras quirurgicas'],
        
        # PRODUCTOS DE LIMPIEZA
        'cloro': ['cloro', 'hipoclorito', 'hipoclorito sodio'],
        'desinfectante': ['desinfectante', 'germicida'],
        'alcohol_gel': ['alcohol gel', 'gel antibacterial'],
        'detergente': ['detergente', 'jabon'],
        
        # OXÍGENO
        'oxigeno': ['oxigeno', 'o2'],
        'tanque_oxigeno': ['tanque oxigeno', 'cilindro oxigeno']
    }
    
    # Obtener términos de búsqueda para el producto
    terminos_busqueda = mapeo_busqueda.get(nombre_buscar, [nombre_buscar])
    
    # Buscar en el inventario
    for _, fila in inventario_df.iterrows():
        # Crear texto completo de la fila para búsqueda
        texto_fila = ""
        for col in fila.index:
            if pd.notna(fila[col]):
                texto_fila += str(fila[col]).lower() + " "
        
        # Verificar si algún término coincide
        for termino in terminos_busqueda:
            if termino in texto_fila:
                # Obtener stock de diferentes columnas posibles
                stock = 0
                for col_stock in ['stock', 'cantidad', 'existencia', 'disponible', 'inventario', 'qty', 'unidades']:
                    if col_stock in fila.index and pd.notna(fila[col_stock]):
                        try:
                            stock = int(float(fila[col_stock]))
                            break
                        except:
                            continue
                
                # Obtener información adicional del producto
                nombre_producto = str(fila.get('nombre', fila.get('producto', fila.get('descripcion', fila.get('item', 'Producto')))))
                lote = str(fila.get('lote', fila.get('batch', fila.get('numero_lote', ''))))
                
                # Buscar fecha de caducidad en diferentes columnas
                caducidad = ''
                for col_cad in ['caducidad', 'vencimiento', 'expiry', 'fecha_vencimiento', 'fecha_caducidad', 'expiracion']:
                    if col_cad in fila.index and pd.notna(fila[col_cad]):
                        caducidad = str(fila[col_cad])
                        break
                
                return {
                    'encontrado': True,
                    'stock_disponible': stock,
                    'stock_suficiente': stock >= cantidad_necesaria,
                    'producto_match': nombre_producto,
                    'lote': lote if lote != 'nan' else '',
                    'caducidad': caducidad if caducidad != 'nan' else ''
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

def obtener_documentos_requeridos(licitacion_id, documentos_df):
    """Obtiene la lista de documentos requeridos para una licitación específica."""
    if documentos_df is None or documentos_df.empty:
        return []

    documentos = []

    # Verificar si la columna 'documentos' existe en el DataFrame
    if 'documentos' not in documentos_df.columns:
        st.error("❌ El archivo de documentos requeridos debe tener una columna llamada 'documentos'.")
        return []

    # Buscar por un ID único si la columna existe (asumiendo que es 'nombre' en tu caso)
    # y que la columna de la licitación en el archivo de documentos es 'nombre'
    if 'nombre' in documentos_df.columns:
        # Normalizar el texto de búsqueda para una coincidencia flexible
        nombre_licitacion_normalizado = normalizar_texto(licitacion_id)
        
        # Filtrar el DataFrame donde el nombre de la licitación coincide
        docs_encontrados = documentos_df[documentos_df['nombre'].apply(lambda x: nombre_licitacion_normalizado in normalizar_texto(x))]
        
        if not docs_encontrados.empty:
            # Iterar sobre las filas encontradas
            for _, row in docs_encontrados.iterrows():
                # Dividir la cadena de documentos por comas y limpiar espacios
                doc_list = [doc.strip() for doc in str(row['documentos']).split(',')]
                documentos.extend(doc_list)
    
    return documentos

def evaluar_licitacion(fila, inventario_df, documentos_df=None):
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
        'categorias_productos': {},
        'documentos_necesarios': []
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
    
    # Extraer productos usando función médica especializada
    productos = extraer_productos_medicos(descripcion)
    
    # Obtener documentos requeridos (nueva funcionalidad)
    licitacion_id = fila.get('id', fila.get('nombre', ''))
    resultado['documentos_necesarios'] = obtener_documentos_requeridos(licitacion_id, documentos_df)

    if not productos:
        resultado['estado'] = 'amarillo'
        resultado['observaciones'].append("No se identificaron productos médicos específicos")
        return resultado
    
    resultado['productos_analizados'] = len(productos)
    
    # Evaluar cada producto médico
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

# INTERFAZ DE USUARIO
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
    
    archivo_documentos = st.file_uploader(
        "Archivo de Documentos Requeridos (Opcional)",
        type=['csv', 'xlsx', 'xls'],
        help="Archivo con la lista de documentos para cada licitación. Debe tener columnas 'id_licitacion' y 'documento'."
    )
    
    if archivo_licitaciones and archivo_inventario:
        st.success("✅ Archivos cargados correctamente")
    
    st.markdown("---")
    st.markdown("### ⚙️ Configuración")
    
    mostrar_detalles = st.checkbox("Mostrar análisis detallado", True)
    mostrar_debug = st.checkbox("Mostrar información de debug", False)

# Verificar archivos
if not archivo_licitaciones or not archivo_inventario:
    st.info("👆 Por favor, carga los archivos de licitaciones e inventario para comenzar el análisis.")
    
    with st.expander("📖 Guía de uso"):
        st.markdown("""
        ### Estructura esperada de archivos:
        
        **Licitaciones:**
        - Debe contener columnas como: nombre, descripcion, detalle, productos
        - Ejemplo: "100 paracetamol, 50 gasas esteriles, 20 jeringas"
        
        **Inventario:**
        - Debe contener: nombre/producto, stock/cantidad, lote, caducidad
        - Ejemplo: nombre="Paracetamol 500mg", stock=200, lote="L001", caducidad="2025-12-31"
        
        **Documentos Requeridos (Opcional):**
        - Debe contener: id_licitacion/nombre, documento
        - Ejemplo: id_licitacion=1, documento="Certificado de Buenas Prácticas de Manufactura"
        
        ### Productos médicos reconocidos:
        - **Medicamentos**: 200+ incluidos (antibióticos, analgésicos, antivirales, etc.)
        - **Material médico**: gasas, vendas, jeringas, agujas, etc.
        - **Equipos**: termómetros, estetoscopios, tensiómetros, etc.
        - **EPP**: guantes, mascarillas, batas, etc.
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
    
    # Cargar documentos (opcional)
    documentos_df = None
    if archivo_documentos:
        if archivo_documentos.name.endswith('.csv'):
            documentos_df = pd.read_csv(archivo_documentos)
        else:
            documentos_df = pd.read_excel(archivo_documentos)
    
    # Limpiar datos
    licitaciones_df = licitaciones_df.dropna(how='all')
    inventario_df = inventario_df.dropna(how='all')
    if documentos_df is not None:
        documentos_df = documentos_df.dropna(how='all')
    
    st.success(f"📊 Datos cargados: {len(licitaciones_df)} licitaciones, {len(inventario_df)} productos en inventario")
    
except Exception as e:
    st.error(f"❌ Error al cargar archivos: {str(e)}")
    st.info("Verifica que los archivos no estén corruptos y tengan el formato correcto.")
    st.stop()

# Mostrar información de debug si está habilitada
if mostrar_debug:
    with st.expander("🔍 Información de Debug"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Columnas en Licitaciones:**")
            st.write(list(licitaciones_df.columns))
            st.write("**Muestra de datos:**")
            st.dataframe(licitaciones_df.head(3))
            
            # Debug de extracción
            st.write("**🔍 Prueba de extracción:**")
            for idx, fila in licitaciones_df.head(2).iterrows():
                nombre_lic = fila.get('nombre', f'Licitación {idx+1}')
                descripcion = fila.get('descripcion', 'Sin descripción')
                
                st.write(f"**{nombre_lic}:**")
                st.write(f"*Descripción:* {descripcion[:50]}...")
                
                productos = extraer_productos_medicos(descripcion)
                if productos:
                    for prod in productos:
                        st.write(f"  ✅ {prod['nombre']}: {prod['cantidad']} - {prod['categoria']}")
                else:
                    st.write("  ❌ No se extrajeron productos")
        
        with col2:
            st.write("**Columnas en Inventario:**")
            st.write(list(inventario_df.columns))
            st.write("**Muestra de datos:**")
            st.dataframe(inventario_df.head(3))
            
            # Debug de búsqueda
            st.write("**🔍 Prueba de búsqueda:**")
            productos_test = ['paracetamol', 'ciprofloxacino', 'aciclovir', 'gasas', 'jeringas']
            for prod_name in productos_test:
                producto_test = {'nombre': prod_name, 'cantidad': 10}
                resultado = buscar_en_inventario(producto_test, inventario_df)
                
                if resultado['encontrado']:
                    st.write(f"✅ {prod_name}: {resultado['producto_match'][:30]}...")
                else:
                    st.write(f"❌ {prod_name}: No encontrado")

# Botón de análisis
if st.button("🔍 Analizar Licitaciones Médicas", type="primary"):
    with st.spinner("Procesando análisis médico especializado..."):
        resultados = []
        evaluaciones_detalladas = []
        
        for idx, fila in licitaciones_df.iterrows():
            evaluacion = evaluar_licitacion(fila, inventario_df, documentos_df)
            evaluaciones_detalladas.append(evaluacion)
            
            # Obtener nombre de licitación
            nombre_licitacion = "Sin nombre"
            for col in ['nombre', 'titulo', 'licitacion', 'descripcion']:
                if col in fila.index and pd.notna(fila[col]):
                    nombre_licitacion = str(fila[col])[:60] + ("..." if len(str(fila[col])) > 60 else "")
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
            
            # Métricas generales
            total = len(resultados_df)
            verdes = len(resultados_df[resultados_df['Estado'] == 'VERDE'])
            amarillos = len(resultados_df[resultados_df['Estado'] == 'AMARILLO'])
            rojos = len(resultados_df[resultados_df['Estado'] == 'ROJO'])
            
            st.markdown("### 📈 Resumen Ejecutivo")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Licitaciones", total)
            col2.metric("✅ Aptas", verdes, f"{verdes/total*100:.1f}%" if total > 0 else "0%")
            col3.metric("⚠️ Revisar", amarillos, f"{amarillos/total*100:.1f}%" if total > 0 else "0%")
            col4.metric("❌ No Aptas", rojos, f"{rojos/total*100:.1f}%" if total > 0 else "0%")
            
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
                        
                        # Documentos Requeridos (Nuevo)
                        if evaluacion['documentos_necesarios']:
                            st.markdown("#### 📝 Documentos Requeridos:")
                            st.markdown("<ul>" + "".join([f"<li>{doc}</li>" for doc in evaluacion['documentos_necesarios']]) + "</ul>", unsafe_allow_html=True)
                            st.markdown("---")
                        
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
    - **Analgésicos**: paracetamol, ibuprofeno, aspirina, diclofenaco, naproxeno
    - **Antibióticos**: amoxicilina, ciprofloxacino, azitromicina, cefalexina, ceftriaxona
    - **Antivirales**: aciclovir, oseltamivir, ribavirina, ganciclovir
    - **Cardiovasculares**: losartán, enalapril, atenolol, furosemida, simvastatina
    - **Gastrointestinales**: omeprazol, lansoprazol, ranitidina
    - **Antidiabéticos**: metformina, insulina, glibenclamida
    - **Respiratorios**: salbutamol, dexametasona, prednisolona
    - **Anestésicos**: morfina, tramadol, lidocaína
    
    **🩹 Material de Curación:**
    - Gasas estériles, vendas elásticas, alcohol, yodo, algodón
    - Suturas, apósitos, esparadrapo
    
    **💉 Dispositivos Médicos:**
    - Jeringas, agujas hipodérmicas, catéteres, sondas
    
    **🛡️ Equipo de Protección:**
    - Guantes (látex, nitrilo), mascarillas, batas, gorros
    
    **🧪 Sueros y Soluciones:**
    - Suero fisiológico, dextrosa, Hartmann, agua inyectable
    
    **⚕️ Equipos Médicos:**
    - Termómetros, estetoscopios, tensiómetros, oxímetros, microscopios
    
    **🧽 Productos de Limpieza:**
    - Cloro, desinfectantes, alcohol gel
    
    **🫁 Gases Medicinales:**
    - Oxígeno, tanques de oxígeno, reguladores
    """)

with st.expander("🔧 Cómo Funciona el Sistema"):
    st.markdown("""
    **Proceso de análisis:**
    
    1. **Extracción**: El sistema busca patrones como "100 paracetamol" en las descripciones
    2. **Clasificación**: Identifica y categoriza cada producto médico automáticamente
    3. **Búsqueda**: Localiza productos similares en el inventario usando sinónimos
    4. **Evaluación**: Compara cantidades requeridas vs stock disponible
    5. **Alertas**: Verifica fechas de caducidad y genera alertas tempranas
    6. **Resultados**: Clasifica cada licitación como Apta, Para Revisar, o No Apta
    
    **Estados de las licitaciones:**
    - 🟢 **Apta**: Todos los productos disponibles con stock suficiente
    - 🟡 **Para Revisar**: Stock insuficiente o productos próximos a caducar
    - 🔴 **No Apta**: Productos no disponibles en inventario
    
    **Características especiales:**
    - **Reconocimiento por sufijos**: Detecta automáticamente medicamentos por terminaciones (-cilina, -floxacino, -prazol)
    - **Sinónimos comerciales**: Reconoce nombres comerciales y genéricos
    - **Control de caducidades**: Alertas automáticas para productos próximos a vencer
    - **Categorización inteligente**: 15+ categorías médicas especializadas
    """)

st.markdown("""
**🏥 Sistema de Licitaciones Médicas v3.0** *Desarrollado para análisis especializado del sector salud con reconocimiento expandido de productos farmacéuticos*

---

### Instrucciones de Uso:

1. **Preparar archivos**:
   - Licitaciones: CSV/Excel con columnas 'nombre', 'descripcion'
   - Inventario: CSV/Excel con columnas 'nombre', 'stock', 'caducidad', 'lote'
   - **Documentos Requeridos (Opcional)**: CSV/Excel con columnas 'id_licitacion' y 'documento'

2. **Cargar archivos** usando los selectores en la barra lateral

3. **Ejecutar análisis** presionando el botón "Analizar Licitaciones Médicas"

4. **Revisar resultados**:
   - Métricas ejecutivas
   - Tabla de resultados por licitación
   - Análisis detallado expandible
   - Descarga de reporte CSV

### Soporte Técnico:
- El sistema reconoce automáticamente productos médicos en español
- Busca en múltiples columnas del inventario
- Genera alertas de caducidad automáticas
- Clasifica por 15+ categorías médicas especializadas

**Nota**: Si un producto no es reconocido, revisa la ortografía o contacta soporte para agregar nuevos términos al vocabulario médico.
""")