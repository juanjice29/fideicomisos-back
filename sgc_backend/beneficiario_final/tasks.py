from .models import RPBF_PERIODOS,RPBF_HISTORICO
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import update
from rest_framework.renderers import JSONRenderer
from celery import Celery
from celery import shared_task, chain
from django.http import JsonResponse
from django.http import FileResponse
from rest_framework import status
import cx_Oracle
import logging
from .querys import semilla
from rest_framework.response import Response
from .utils import *
import pandas as pd
import xml.etree.ElementTree as ET
import xml.dom.minidom
import datetime
import os
import zipfile
import subprocess
from .variables import *
import pdb 
from querys.conn import *

logger = logging.getLogger(__name__)
celery = Celery()
def progress_callback(current, total):
    logger.info('Task progress: {}%'.format(current / total * 100))
@shared_task
def calculate_bf_candidates():
    fondos = ["14", "12","10"]
    dsn_tns = cx_Oracle.makedsn(
        url, port, service_name=service_name)
    conn = cx_Oracle.connect(
        user=user, password=password, dsn=dsn_tns)
    cur = conn.cursor()
    sql_delete_candidates = "DELETE FROM RPBF_CANDIDATES"
    cur.execute(sql_delete_candidates)
    conn.commit()

    for i in fondos:
        fondo = i
        novedades = [1, 2, 3]

        last_report_regs = RPBF_HISTORICO.objects.filter(FONDO=fondo)
        df_historico = pd.DataFrame.from_records(last_report_regs.values())
        df_historico["PERIODO_REPORTADO_id"] = df_historico["PERIODO_REPORTADO_id"].apply(
            lambda x: int("".join(x.split("-")))).astype(int)

        saldo = cur.execute(semilla.saldo_fondo.format(
            "2023-12-31", fondo)).fetchone()
        saldo = str(saldo[0]).replace(",", ".")

        cur.execute(semilla.query.format(saldo, "2023-12-31", fondo))
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

        df_current = pd.DataFrame(rows, columns=columns, dtype="string")
        result = []

        for index, row in df_current.iterrows():
            nro_identif = row["NRO_IDENTIF"]
            max_feccre = row["MAX_FECCRE"]
            porcentaje = row["PORCENTAJE_SALDO"]
            porcentaje = f"{float(porcentaje):.5f}"
            filtered_df = df_historico[df_historico["NRO_IDENTIF"].astype(
                str) == str(nro_identif)]
            novedad_t = "1"
            # Calculo de 1 y 2
            if (len(filtered_df) > 0):
                max_index = filtered_df["PERIODO_REPORTADO_id"].idxmax()
                last_state = filtered_df.loc[max_index]

                if (last_state["TIPO_NOVEDAD"] == "1"):
                    novedad_t = "2"
                if (last_state["TIPO_NOVEDAD"] == "2"):
                    novedad_t = "2"
                if (last_state["TIPO_NOVEDAD"] == "3"):
                    novedad_t = "1"
                result.append((nro_identif, novedad_t, fondo,
                              max_feccre, '', porcentaje))
            else:
                novedad_t = "1"
                result.append((nro_identif, novedad_t, fondo,
                              max_feccre, '', porcentaje))

        # del historico de las novedades 1 y 2 , determinar cuales ya salieron
        historico_last_state = df_historico.loc[df_historico.groupby(
            ["NRO_IDENTIF"])["PERIODO_REPORTADO_id"].idxmax()]
        historico_last_state = historico_last_state[(historico_last_state["TIPO_NOVEDAD"] == "1") | (
            historico_last_state["TIPO_NOVEDAD"] == "2")]

        if (fondo == "14"):
            cancelaciones_df = cur.execute(
                semilla.cancelaciones_rendir.format("2023-12-31"))

        if (fondo == "12"):
            cancelaciones_df = cur.execute(
                semilla.cancelaciones_rentafacil.format("2023-12-31"))
            
        if (fondo == "10"):
            cancelaciones_df = cur.execute(
                semilla.cancelaciones_universitas.format("2023-12-31"))

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        cancelaciones_df = pd.DataFrame(rows, columns=columns, dtype="string")

        registros_not_inseed = 0
        cancelaciones_df["NRO_IDENTIF"] = cancelaciones_df["NRO_IDENTIF"].astype(
            str)

        for index, row in historico_last_state.iterrows():
            nro_identif = str(row["NRO_IDENTIF"])
            filtered_df = df_current[df_current["NRO_IDENTIF"].astype(
                str) == nro_identif]

            if (len(filtered_df) == 0):

                registros_not_inseed += 1
                candidato_tn3 = cancelaciones_df[cancelaciones_df["NRO_IDENTIF"] == nro_identif]
                novedad_t = "3"

                if (len(candidato_tn3) > 0):
                    last_cancelation = candidato_tn3.iloc[0]
                    temp_result = (nro_identif, novedad_t, fondo,
                                   row["FECHA_CREACION"], last_cancelation["FECCAN"], row["PORCENTAJE_SALDO"])
                    result.append(temp_result)

        sql_insert = "INSERT INTO RPBF_CANDIDATES (NRO_IDENTIF, NOVEDAD,FONDO,FECCRE,FECCAN,PORCENTAJE_SALDO) VALUES (:1, :2, :3, :4, :5, :6)"
        # Ejecutar la sentencia SQL con la lista de registros
        cur.executemany(sql_insert, result)
        conn.commit()
    cur.close()
    conn.close()
    return Response({"status": "200", "longitud": len(result)})


@shared_task
def VerifyDataIntegrityView():
    dsn_tns = cx_Oracle.makedsn(
        url, port, service_name=service_name)
    conn = cx_Oracle.connect(
        user=user, password=password, dsn=dsn_tns)
    cur = conn.cursor()
    return Response({"status": "200"})


@shared_task
def TableToXmlView():
    dsn_tns = cx_Oracle.makedsn(
        url, port, service_name=service_name)
    conn = cx_Oracle.connect(
        user=user, password=password, dsn=dsn_tns)
    cur = conn.cursor()

    cur.execute("SELECT * FROM RPBF_REPORTE_FINAL")
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    report = pd.DataFrame(rows, columns=columns, dtype="string").fillna('')

    dataframes_por_fondos = {}

    for valor, grupo in report.groupby('FONDO'):
        dataframes_por_fondos[valor] = grupo

    for clave_fondo, df_per_fondo in dataframes_por_fondos.items():
        dataframes_por_novedades = {}
        cur.execute(
            "SELECT CONSECUTIVO FROM RPBF_CONSECUTIVOS WHERE FONDO='{0}'".format(clave_fondo))
        row = cur.fetchone()
        numero_envio = row[0]

        for valor, grupo in df_per_fondo.groupby('TNOV'):
            dataframes_por_novedades[valor] = grupo

        for clave_novedad, df_per_nov in dataframes_por_novedades.items():
            tamano_bloque = 5000
            valorTotal = len(df_per_nov)
            total_bloques = (valorTotal // tamano_bloque) + 1
            for i in range(total_bloques):
                inicio = i*tamano_bloque
                fin = (i+1)*tamano_bloque
                bloque_actual = df_per_nov.iloc[inicio:fin]

                root = ET.Element("mas")
                root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
                root.set("xsi:noNamespaceSchemaLocation", "../xsd/2688.xsd")
                cab_element = ET.SubElement(root, "Cab")
                ET.SubElement(cab_element, "Ano").text = str(anio_actual)
                ET.SubElement(cab_element, "CodCpt").text = "1"
                ET.SubElement(cab_element, "Formato").text = "2688"
                ET.SubElement(cab_element, "Version").text = "1"
                ET.SubElement(cab_element, "NumEnvio").text = str(numero_envio)
                ET.SubElement(cab_element, "FecEnvio").text = fecEnvio
                ET.SubElement(cab_element, "FecInicial").text = fecInicial
                ET.SubElement(cab_element, "FecFinal").text = str(fecFinal)
                ET.SubElement(cab_element, "ValorTotal").text = str(valorTotal)
                ET.SubElement(cab_element, "CantReg").text = str(valorTotal)
                for index, fila in bloque_actual.iterrows():
                    attributes = {}
                    for columna, valor in fila.items():
                        if not (valor == '' or pd.isnull(valor)) and columna != 'FONDO':
                            attributes[columna.lower()] = valor

                    genElement = ET.SubElement(root, "bene", attrib=attributes)

                tree = ET.ElementTree(root)
                xml_str = ET.tostring(root, encoding="ISO-8859-1")
                dom = xml.dom.minidom.parseString(xml_str)
                formatted_xml_str = dom.toprettyxml(indent="\t")
                directorio = f"D:/BENEFICIARIO_FINAL2024/resultados/fondo_{clave_fondo}/novedad_{clave_novedad}"
                os.makedirs(directorio, exist_ok=True)
                with open(f"{directorio}/"+file_name.format(str(numero_envio)), "wb") as file:
                    file.write(formatted_xml_str.encode("iso-8859-1"))

                with open(f"{directorio}/"+file_name.format(str(numero_envio)), "r", encoding="ISO-8859-1") as file:
                    lines = file.readlines()
                lines[0] = '<?xml version="1.0" encoding="ISO-8859-1"?>\n'

                with open(f"{directorio}/"+file_name.format(str(numero_envio)), "w", encoding="ISO-8859-1") as file:
                    file.writelines(lines)
                numero_envio += 1
    cur.close()
    conn.close()

    return Response({"status": "200", "num_envio": str(len(dataframes_por_fondos))})


@shared_task
def ZipFile():
    carpeta_a_comprimir = 'D:/BENEFICIARIO_FINAL2024/resultados'
    archivo_salida = 'D:/BENEFICIARIO_FINAL2024/resultados.zip'

    comprimir_carpeta(carpeta_a_comprimir, archivo_salida)

    return Response({"status": "200"})

@shared_task
def FillPostalCodeView():
    engine = create_engine(
        f'oracle+cx_oracle://{user}":{password}@{url}:{port}/?service_name={service_name}')
    sql = """
        SELECT DIREC_DIREC ID_CLIENTE,CIUD_DEPTO||CIUD_DANE AS ID_CIUDAD_RESIDENCIA,CIUD_DEPTO AS ID_DPTO_RESIDENCIA,'COL' AS ID_PAIS_RESIDENCIA,
        DIREC_DIRECCION AS DIRECCION_RECIDENCIAL,NVL(DIREC_BARRIO,'-') BARRIO_DIR_RESIDENCIAL
        FROM TEMP_RPBF_CANDIDATES 
        INNER JOIN CL_TDIREC D1 ON D1.DIREC_NROIDENT=NRO_IDENTIF
        INNER JOIN (SELECT DIREC_NROIDENT,MAX(DIREC_DIREC) MAX_DIREC FROM CL_TDIREC 
        WHERE DIREC_POSTAL IS NULL AND DIREC_ESTADO='ACT' AND DIREC_TPDIR='RES'  AND DIREC_DIRECCION IS NOT NULL
        GROUP BY DIREC_NROIDENT) D2 ON D1.DIREC_DIREC=D2.MAX_DIREC
        INNER JOIN GE_TCIUD ON DIREC_CIUD=CIUD_CIUD
        INNER JOIN GE_TDEPTO ON DEPTO_DEPTO=CIUD_DEPTO
        INNER JOIN GE_TPAIS ON PAIS_PAIS=DEPTO_PAIS
        """
    df = pd.read_sql(sql, engine)
    df.columns = df.columns.str.upper()
    df = df.astype(str)
    df.to_excel('cod_postal.xlsx', index=False)
    return Response({"status": "200"})

@shared_task
def RunJarView():
    renderer_classes = [JSONRenderer]
    result = subprocess.run(['java', '-Dhttp.proxyHost=10.1.5.2', '-Dhttp.proxyPort=80', '-Dhttps.proxyHost=10.1.5.2',
                                '-Dhttps.proxyPort=80', '-jar', 'cp.jar', '-separador', ',', '-entrada', 'cod_postal.xlsx', '-salida', 'salida.csv'], check=True)
    df = pd.read_csv('salida.csv')
    engine = create_engine(
             f'oracle+cx_oracle://{user}":{password}@{url}:{port}/?service_name={service_name}')
    metadata = MetaData()
    metadata.bind = engine
    cl_tdirec = Table('cl_tdirec', metadata, autoload_with=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    for index, row in df.iterrows():
        if pd.isnull(row['CP']):
            continue
        stmt = update(cl_tdirec).where(cl_tdirec.c.direc_direc ==
                                       row['ID_CLIENTE']).values(direc_postal=row['CP'])
        session.execute(stmt)
        logger.info(f"Updated cl_tdirec: direc_direc={row['ID_CLIENTE']}, direc_postal={row['CP']}")
    session.commit()
    return Response({"status": "200"})