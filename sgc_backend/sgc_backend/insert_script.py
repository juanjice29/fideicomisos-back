#insercion de datos inicial para funcionamiento basico del aplicativo
from public.models import *
from accounts.models import *
from actores.models import *
from beneficiario_final.models import *
from fidecomisos.models import *
from process.models import *

def delete_scripts():    
# Eliminar todos los datos de cada modelo
    TipoDePersona.objects.all().delete()
    TipoDeDocumento.objects.all().delete()
    TipoNovedadRPBF.objects.all().delete()
    ParametrosRpbf.objects.all().delete()
    TipoParametrizacion.objects.all().delete()
    ParametrosGenericos.objects.all().delete()
    View.objects.all().delete()
    Accion.objects.all().delete()
    TipoActorDeContrato.objects.all().delete()
    ConsecutivosRpbf.objects.all().delete()
    TipoDeProcesoGeneral.objects.all().delete()
    TipoLog.objects.all().delete()
    EstadoEjecucion.objects.all().delete()
    Proceso.objects.all().delete()
    TareaProceso.objects.all().delete()
    
def ejecutar_scripts():
        
    data_list = [
        {'tipoPersona': 'J', 'descripcion': 'Persona Juridica'},
        {'tipoPersona': 'N', 'descripcion': 'Persona Natural'}
    ]
    for data in data_list:
        reg = TipoDePersona(tipoPersona=data['tipoPersona'], descripcion=data['descripcion'])
        reg.save()

    queryJ=TipoDePersona.objects.get(tipoPersona='J').id
    queryN=TipoDePersona.objects.get(tipoPersona='N').id

    # Datos para TipoDeDocumento
    data_list = [
        {'tipoDocumento': 'TI', 'descripcion': 'Tarjeta de Identidad', 'idTipoPersona':queryN},
        {'tipoDocumento': 'CE', 'descripcion': 'Cédula de Extranjería', 'idTipoPersona':queryN},
        {'tipoDocumento': 'NN', 'descripcion': 'NIT Persona Natural', 'idTipoPersona':queryN},
        {'tipoDocumento': 'NE', 'descripcion': 'NIT Persona Extranjera', 'idTipoPersona':queryN},
        {'tipoDocumento': 'NJ', 'descripcion': 'NIT Persona Jurídica', 'idTipoPersona': queryJ},
        {'tipoDocumento': 'PA', 'descripcion': 'Pasaporte', 'idTipoPersona':queryN},
        {'tipoDocumento': 'RC', 'descripcion': 'Registro Civil', 'idTipoPersona':queryN},
        {'tipoDocumento': 'RM', 'descripcion': 'Registro Medico', 'idTipoPersona':queryN},
        {'tipoDocumento': 'RU', 'descripcion': 'Numero unico identificacion', 'idTipoPersona':queryN},
        {'tipoDocumento': 'PEP', 'descripcion': 'Permiso Especial Permanencia', 'idTipoPersona':queryN},
        {'tipoDocumento': 'EE', 'descripcion': 'Empresas Extranjeras', 'idTipoPersona': queryJ},
        {'tipoDocumento': 'CC', 'descripcion': 'Cédula de Ciudadanía', 'idTipoPersona':queryN}
    ]

    # Iterar sobre la lista e insertar los registros
    for data in data_list:
        # Obtener la instancia de TipoDePersona correspondiente
        tipo_persona = TipoDePersona.objects.get(id=data['idTipoPersona'])
        
        # Crear una nueva instancia de TipoDeDocumento
        reg = TipoDeDocumento(
            tipoDocumento=data['tipoDocumento'],
            descripcion=data['descripcion'],
            idTipoPersona=tipo_persona
        )
        reg.save()

    # Datos para TipoNovedadRPBF
    data_list = [
        {'id': 1, 'descripcion': 'Se calculan los registros no reportados.'},
        {'id': 2, 'descripcion': 'Se calculan las actualizaciones de los registros ya reportados que se mantienen en el reporte actual.'},
        {'id': 3, 'descripcion': 'Se reportan los registros que salieron del fondo con los datos de su último reporte.'}
    ]

    # Iterar sobre la lista e insertar los registros
    for data in data_list:
        reg = TipoNovedadRPBF(id=data['id'], descripcion=data['descripcion'])
        reg.save()


    data_list = [
        {'fondo': '12', 'novedad': '1', 'bepjtit': '4', 'bepjben': '8', 'bepjcon': 'N', 'bepjrl': 'N', 'bespjfcp': 'N', 'bespjf': 'N', 'bespjcf': 'N', 'bespjfb': 'N', 'bespjcfe': 'N', 'becespj': 'N', 'pppjepj': '', 'pbpjepj': 'S'},
        {'fondo': '12', 'novedad': '2', 'bepjtit': '4', 'bepjben': '8', 'bepjcon': 'N', 'bepjrl': 'N', 'bespjfcp': 'N', 'bespjf': 'N', 'bespjcf': 'N', 'bespjfb': 'N', 'bespjcfe': 'N', 'becespj': 'N', 'pppjepj': '', 'pbpjepj': 'S'},
        {'fondo': '12', 'novedad': '3', 'bepjtit': '4', 'bepjben': '8', 'bepjcon': 'N', 'bepjrl': 'N', 'bespjfcp': 'N', 'bespjf': 'N', 'bespjcf': 'N', 'bespjfb': 'N', 'bespjcfe': 'N', 'becespj': 'N', 'pppjepj': '', 'pbpjepj': 'S'},
        {'fondo': '14', 'novedad': '1', 'bepjtit': '1', 'bepjben': '8', 'bepjcon': 'N', 'bepjrl': 'N', 'bespjfcp': 'N', 'bespjf': 'N', 'bespjcf': 'N', 'bespjfb': 'S', 'bespjcfe': 'N', 'becespj': 'S', 'pppjepj': '', 'pbpjepj': 'N'},
        {'fondo': '14', 'novedad': '2', 'bepjtit': '1', 'bepjben': '8', 'bepjcon': 'N', 'bepjrl': 'N', 'bespjfcp': 'N', 'bespjf': 'N', 'bespjcf': 'N', 'bespjfb': 'S', 'bespjcfe': 'N', 'becespj': 'S', 'pppjepj': '', 'pbpjepj': 'N'},
        {'fondo': '14', 'novedad': '3', 'bepjtit': '1', 'bepjben': '8', 'bepjcon': 'N', 'bepjrl': 'N', 'bespjfcp': 'N', 'bespjf': 'N', 'bespjcf': 'N', 'bespjfb': 'S', 'bespjcfe': 'N', 'becespj': 'S', 'pppjepj': '', 'pbpjepj': 'N'},
        {'fondo': '10', 'novedad': '1', 'bepjtit': '1', 'bepjben': '8', 'bepjcon': 'N', 'bepjrl': 'N', 'bespjfcp': 'N', 'bespjf': 'N', 'bespjcf': 'N', 'bespjfb': 'S', 'bespjcfe': 'N', 'becespj': 'S', 'pppjepj': '', 'pbpjepj': 'N'},
        {'fondo': '10', 'novedad': '2', 'bepjtit': '1', 'bepjben': '8', 'bepjcon': 'N', 'bepjrl': 'N', 'bespjfcp': 'N', 'bespjf': 'N', 'bespjcf': 'N', 'bespjfb': 'S', 'bespjcfe': 'N', 'becespj': 'S', 'pppjepj': '', 'pbpjepj': 'N'},
        {'fondo': '10', 'novedad': '3', 'bepjtit': '1', 'bepjben': '8', 'bepjcon': 'N', 'bepjrl': 'N', 'bespjfcp': 'N', 'bespjf': 'N', 'bespjcf': 'N', 'bespjfb': 'S', 'bespjcfe': 'N', 'becespj': 'S', 'pppjepj': '', 'pbpjepj': 'N'}
    ]

    # Iterar sobre la lista e insertar los registros
    for data in data_list:
        reg = ParametrosRpbf(
            fondo=data['fondo'], 
            novedad=data['novedad'], 
            bepjtit=data['bepjtit'], 
            bepjben=data['bepjben'], 
            bepjcon=data['bepjcon'], 
            bepjrl=data['bepjrl'], 
            bespjfcp=data['bespjfcp'], 
            bespjf=data['bespjf'], 
            bespjcf=data['bespjcf'], 
            bespjfb=data['bespjfb'], 
            bespjcfe=data['bespjcfe'], 
            becespj=data['becespj'], 
            pppjepj=data['pppjepj'], 
            pbpjepj=data['pbpjepj']
        )
        reg.save()


    # Datos para TipoParametrizacion
    data_list = [
        {'acronimo': 'ROUTE', 'nombre': 'Rutas', 'descripcion': 'Parametrizacion de ruta'},
        {'acronimo': 'CRON', 'nombre': 'Cron', 'descripcion': 'Parametrizacion de crontab para ejecucion de procesos'}
    ]

    # Iterar sobre la lista e insertar los registros
    for data in data_list:
        reg = TipoParametrizacion(
            acronimo=data['acronimo'], 
            nombre=data['nombre'], 
            descripcion=data['descripcion']
        )
        reg.save()

    # Datos para ParametrosGenericos
    data_list = [
        {'tipoParametrizacion': 'ROUTE', 'nombre': 'SALIDA_RPBF', 'valorParametro': 'D:/BENEFICIARIO_FINAL2024/resultados', 'descripcion': 'Ruta de SALIDA donde se ubican los archivos de todos los reportes solicitados de beneficiario final.'},
    ]

    # Iterar sobre la lista e insertar los registros
    for data in data_list:
        tipo_parametrizacion = TipoParametrizacion.objects.get(acronimo=data['tipoParametrizacion'])
        reg = ParametrosGenericos(
            tipoParametrizacion=tipo_parametrizacion, 
            nombre=data['nombre'], 
            valorParametro=data['valorParametro'], 
            descripcion=data['descripcion']
        )
        reg.save()
        
    data_list = [
        'UpdateEncargoFromTemp',
        'UpdateEncargoTemp',
        'UpdateFideicomisoView',
        'ProcessDetailView',
        'ProcessListView',
        'LogEjecucionListView',
        'GenerateRPBF',
        'LogEjecucionTareaDetailView',
        'ActoresFileUploadView',
        'IndexView',
        'FideicomisoList',
        'FideicomisoDetailView',
        'FideicomisoView',
        'LogCreateListView',
        'LogCreateView',
        'LogRelateView',
        'LogUpdateListView',
        'FileUploadView',
        'EncargoListView',
        'ActorView',
        'ActorListView',
        'ActoresByFideicomisoList',
        'ExampleProcessView',
        'KillProcessView',
    ]

    # Iterar sobre la lista e insertar los registros
    for nombre in data_list:
        reg = View(nombre=nombre)
        reg.save()

    data_list = [
        'GET',
        'PUT',
        'DELETE',
        'POST',
    ]

    # Iterar sobre la lista e insertar los registros
    for nombre in data_list:
        reg = Accion(nombre=nombre)
        reg.save()

    # Datos para TipoActorDeContrato
    data_list = [
        {'tipoActor': 'Acreedores Garantizados', 'descripcion': 'Acreedores Garantizados'},
        {'tipoActor': 'Apoderados', 'descripcion': 'Apoderados'},
        {'tipoActor': 'Benefactores', 'descripcion': 'Benefactores'},
        {'tipoActor': 'Beneficiarios Fideicomiso Bienestar Financiero', 'descripcion': 'Beneficiarios Fideicomiso Bienestar Financiero'},
        {'tipoActor': 'Beneficiarios Fideicomiso Gestor de Proyectos', 'descripcion': 'Beneficiarios Fideicomiso Gestor de Proyectos'},
        {'tipoActor': 'Beneficiarios condicionados', 'descripcion': 'Beneficiarios condicionados'},
        {'tipoActor': 'Beneficiarios de contrato de Fiducia', 'descripcion': 'Beneficiarios de contrato de Fiducia'},
        {'tipoActor': 'Cesionarios de derechos económicos', 'descripcion': 'Cesionarios de derechos económicos'},
        {'tipoActor': 'Donantes', 'descripcion': 'Donantes'},
        {'tipoActor': 'Donatarios', 'descripcion': 'Donatarios'},
        {'tipoActor': 'Interventores', 'descripcion': 'Interventores'},
        {'tipoActor': 'Miembros de Comités Fiduciario, Asambleas y/o otros órganos de dirección', 'descripcion': 'Miembros de Comités Fiduciario, Asambleas y/o otros órganos de dirección'},
        {'tipoActor': 'Ordenadores del Gasto', 'descripcion': 'Ordenadores del Gasto'},
        {'tipoActor': 'Otros', 'descripcion': 'Otros'},
        {'tipoActor': 'Pagadores de las Fuente de Pago', 'descripcion': 'Pagadores de las Fuente de Pago'},
        {'tipoActor': 'Pagadores de las Retenciones en Garantía', 'descripcion': 'Pagadores de las Retenciones en Garantía'},
        {'tipoActor': 'Tradentes', 'descripcion': 'Tradentes'},
    ]

    # Iterar sobre la lista e insertar los registros
    for data in data_list:
        reg = TipoActorDeContrato(tipoActor=data['tipoActor'], descripcion=data['descripcion'])
        reg.save()

    # Datos para ConsecutivosRpbf
    data_list = [
        {'fondo': '12', 'consecutivo': 1},
        {'fondo': '14', 'consecutivo': 1},
        {'fondo': '10', 'consecutivo': 1},
    ]

    # Iterar sobre la lista e insertar los registros
    for data in data_list:
        reg = ConsecutivosRpbf(fondo=data['fondo'], consecutivo=data['consecutivo'])
        reg.save()
        
    data_list = [
        {'nombre': 'Integracion', 'acronimo': 'INT', 'descripcion': 'Procesos mediante los que se retroalimenta la base de datos'},
        {'nombre': 'Extraccion', 'acronimo': 'EXT', 'descripcion': 'Procesos mediante los que se extrae informacion interna para exponerla por algun medio.'},
        {'nombre': 'Transformacion', 'acronimo': 'TRS', 'descripcion': 'Procesos mediante los que internamente modificamos nuestros datos sin necesidad de un insumo externo.'},
        {'nombre': 'General', 'acronimo': 'GRAL', 'descripcion': 'Proceso que no se han podido definir o clasificar en las 3 primeras categorias.'},
    ]

    # Iterar sobre la lista e insertar los registros
    for data in data_list:
        reg = TipoDeProcesoGeneral(
            nombre=data['nombre'], 
            acronimo=data['acronimo'], 
            descripcion=data['descripcion']
        )
        reg.save()

    # Datos para TipoLog
    data_list = [
        {'nombre': 'Error', 'acronimo': 'ERR', 'descripcion': 'El log presenta un error'},
        {'nombre': 'Informacion', 'acronimo': 'INFO', 'descripcion': 'El log quiere mostrar informacion'},
        {'nombre': 'Advertencia', 'acronimo': 'WARN', 'descripcion': 'El log muestra una advertencia'},
    ]

    # Iterar sobre la lista e insertar los registros
    for data in data_list:
        reg = TipoLog(
            nombre=data['nombre'], 
            acronimo=data['acronimo'], 
            descripcion=data['descripcion']
        )
        reg.save()

    data_list = [
        {'nombre': 'Iniciado', 'acronimo': 'INI', 'descripcion': 'La ejecucion ha iniciado'},
        {'nombre': 'Procesando', 'acronimo': 'PPP', 'descripcion': 'La ejecucion esta en proceso'},
        {'nombre': 'Finalizada', 'acronimo': 'FIN', 'descripcion': 'La ejecucion termino'},
        {'nombre': 'Pendiente', 'acronimo': 'PND', 'descripcion': 'Pendiente por inicializar'},
        {'nombre': 'Fallida', 'acronimo': 'FAIL', 'descripcion': 'Finalizo pero el proceso general fallo'},
    ]

    # Iterar sobre la lista e insertar los registros
    for data in data_list:
        reg = EstadoEjecucion(
            nombre=data['nombre'], 
            acronimo=data['acronimo'], 
            descripcion=data['descripcion']
        )
        reg.save()

    # Datos para Proceso
    data_list = [
        {
            'nombre': 'Proceso de ejemplo', 
            'acronimo': 'PRCS_GRAL_EJEM', 
            'funcionRelacionada': 'task_process_example',
            'tipoProceso': 'GRAL',
            'descripcion': 'Descripción del proceso de ejemplo',
            'stakeholders': 'Stakeholders relacionados con el proceso de ejemplo',
            'modulosInvolucrados': 'Módulos involucrados en el proceso de ejemplo',
        },
        {
            'nombre': 'Cargar excel actores por fideicomiso', 
            'acronimo': 'INT_ACTORES_BY_FIDEI_EXCEL', 
            'funcionRelacionada': 'tkpCargarActoresPorFideiExcel',
            'tipoProceso': 'INT',
            'descripcion': 'Descripción del proceso de cargar excel actores por fideicomiso',
            'stakeholders': 'Stakeholders relacionados con el proceso de cargar excel actores por fideicomiso',
            'modulosInvolucrados': 'Módulos involucrados en el proceso de cargar excel actores por fideicomiso',
        },
        {
            'nombre': 'Cargar excel actores general', 
            'acronimo': 'INT_ACTORES_MASIVO_EXCEL', 
            'funcionRelacionada': 'tkpCargarActoresExcel',
            'tipoProceso': 'INT',
            'descripcion': 'Descripción del proceso de cargar excel actores general',
            'stakeholders': 'Stakeholders relacionados con el proceso de cargar excel actores general',
            'modulosInvolucrados': 'Módulos involucrados en el proceso de cargar excel actores general',
        },
        {
            'nombre': 'Proceso calculo de beneficiarios finales', 
            'acronimo': 'PRCS_RPBF', 
            'funcionRelacionada': 'tkpCalcularBeneficiariosFinales',
            'tipoProceso': 'TRS',
            'descripcion': 'Descripción del proceso de cálculo de beneficiarios finales',
            'stakeholders': 'Stakeholders relacionados con el proceso de cálculo de beneficiarios finales',
            'modulosInvolucrados': 'Módulos involucrados en el proceso de cálculo de beneficiarios finales',
        },
    ]

    # Iterar sobre la lista e insertar los registros
    for data in data_list:
        tipo_proceso = TipoDeProcesoGeneral.objects.get(acronimo=data['tipoProceso'])
        reg = Proceso(
            tipoProceso=tipo_proceso,
            nombre=data['nombre'],
            acronimo=data['acronimo'],
            funcionRelacionada=data['funcionRelacionada'],
            descripcion=data['descripcion'],
            stakeholders=data['stakeholders'],
            modulosInvolucrados=data['modulosInvolucrados'],
        )
        reg.save()
        
    # Datos para TareaProceso
    data_list = [
        {
            'nombre': 'Guardar Archivo TXT',
            'acronimo': 'CREAR_ARCHV_TXT',
            'funcionRelacionada': 'guardarArchivoTxt',
            'descripcion': 'Funcion que guarda un archivo txt'
        },
        {
            'nombre': 'Transformar excel actores a pandas de un fideicomiso unico',
            'acronimo': 'EXCEL_TO_PD_BY_FIDEI_ACTORES',
            'funcionRelacionada': 'tkExcelActoresPorFideiToPandas',
            'descripcion': 'Esta tarea se encarga de transformar el archivo de excel de actores de contrato a pandas.'
        },
        {
            'nombre': 'Guardar actores de fiducia',
            'acronimo': 'CARGAR_ACTORES',
            'funcionRelacionada': 'tkProcesarPandasActores',
            'descripcion': 'Esta tarea recorre las filas de un pandas para guardar multiples actores para un solo fideicomiso.'
        },
        {
            'nombre': 'Transformar excel actores a pandas masivo',
            'acronimo': 'EXCEL_TO_PD_ACTORES',
            'funcionRelacionada': 'tkExcelActoresToPandas',
            'descripcion': 'Esta tarea recorre un excel que contiene la informacion suficiente para cargar de forma masiva actores de contrato de fiducia.'
        },
        {
            'nombre': 'Obtener codigos postales',
            'acronimo': 'GET_COD_POSTALES',
            'funcionRelacionada': 'tkFillPostalCodeView',
            'descripcion': 'Hace un barrido sobre todos los clientes que no tienen codigo postal.'
        },
        {
            'nombre': 'Calcular posibles beneficiarios finales',
            'acronimo': 'GET_RPBF_CANDIDATOS',
            'funcionRelacionada': 'tkCalculateCandidates',
            'descripcion': 'En base a consultar y tablas temporales, calcula los posibles registros que se van a reportar por cada fondo.'
        },
        {
            'nombre': 'Transformar reporte beneficiario final a xml',
            'acronimo': 'RPBF_TO_XML',
            'funcionRelacionada': 'tkGenerateXML',
            'descripcion': 'Esta funcion pregunta la data que se tiene en base a los calculos previos y genera unas estructuras xml separadas en diferentes carpetas.'
        },
        {
            'nombre': 'Comprimir archivos rporte beneficiario final',
            'acronimo': 'RPBF_ZIP',
            'funcionRelacionada': 'tkZipFileRPBF',
            'descripcion': 'Esta tarea comprime todas las capretas relacionadas con el reporte de beneficiario final y las deja en una ruta especifica'
        },
    ]

    # Iterar sobre la lista e insertar los registros
    for data in data_list:
        reg = TareaProceso(
            nombre=data['nombre'],
            acronimo=data['acronimo'],
            funcionRelacionada=data['funcionRelacionada'],
            descripcion=data['descripcion']
        )
        reg.save()