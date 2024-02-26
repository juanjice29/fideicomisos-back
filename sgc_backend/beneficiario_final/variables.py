import datetime
import pandas as pd
# Obtener la fecha actual
fecha_actual = datetime.datetime.now()
# Obtener el año
anio_actual = fecha_actual.year
concepto=1
numeroBeneficiacios=2
version=1
numeroEnvio=17
# Formatear la fecha en el formato deseado
fecEnvio = fecha_actual.strftime("%Y-%m-%dT%H:%M:%S")
fecInicial="2023-01-01"
fecFinal="2023-12-31"
f_cc="01"
f_m_5="02688"
f_v="01"
f_a_4="2024"
f_consecutivo="000000"
f_consecutivo2="0000000"
file_name="Dmuisca_"+f_cc+f_m_5+f_v+f_a_4+f_consecutivo+"{0}"+".xml"
temp_file_name="14567_salida.xml"
file_name_e="Dmuisca_"+f_cc+f_m_5+f_v+f_a_4+f_consecutivo2+"{0}"+".xml"

attribute_names = [
        "bepjtit", "bepjben", "bepjcon", "bepjrl", "bespjfcp", "bespjf", "bespjcf",
        "bespjfb", "bespjcfe", "becespj", "tdocben", "niben", "paexben", "nitben",
        "paexnitben", "pape", "sape", "pnom", "onom", "fecnac", "panacb", "pnacion",
        "paresb", "dptoben", "munben", "dirben", "codpoben", "emailben", "pppjepj",
        "pbpjepj", "feiniben", "fecfinben", "tnov"
        ]