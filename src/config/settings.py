import os

# =============================================================
# Rutas locales
# =============================================================
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CATALOGOS_DIR = os.path.join(BASE_DIR, "data", "input", "catalogos")
OUTPUT_DIR    = os.path.join(BASE_DIR, "data", "output")

# =============================================================
# URLs fuentes de datos - Portal datos abiertos MSPAS
# =============================================================

# cd = Categoría Desnutrición
URLS_CD = {
    "mda": "https://datosabiertos.mspas.gob.gt/dataset/d69f3342-d233-47f1-b2b8-c20066e41921/resource/d016b1e0-27db-4c05-99c0-3744d274fb9b/download/morbilidad-desnutricion-aguda-departamento-municipio-2012-a-2024.csv",
    "mrd": "https://datosabiertos.mspas.gob.gt/dataset/d69f3342-d233-47f1-b2b8-c20066e41921/resource/491698d4-cafb-48d4-a15b-9fd9d702854a/download/morbilidad-retardo-desarrollo-departamento-municipio-2012-2024.csv",
}

# cec = Categoría Enfermedades Crónicas (un CSV por año)
URLS_CEC = {
    2012: "https://datosabiertos.mspas.gob.gt/dataset/353ffabb-2a3d-4ac1-9816-001b7c3cf62c/resource/7385dff6-f718-4a68-bbe7-a2f8822cae7d/download/mec-2012-departamento-municipio.csv",
    2013: "https://datosabiertos.mspas.gob.gt/dataset/353ffabb-2a3d-4ac1-9816-001b7c3cf62c/resource/c55fa06c-3f65-431a-a918-a4bbf6bad8f2/download/mec-2013-departamento-municipio.csv",
    2014: "https://datosabiertos.mspas.gob.gt/dataset/353ffabb-2a3d-4ac1-9816-001b7c3cf62c/resource/29bfd51d-461b-4f2c-a258-2447ceba933e/download/mec-2014-departamento-municipio.csv",
    2015: "https://datosabiertos.mspas.gob.gt/dataset/353ffabb-2a3d-4ac1-9816-001b7c3cf62c/resource/2c395da2-f18a-4839-bcf4-8cd67e3c41c9/download/mec-2015-departamento-municipio.csv",
    2016: "https://datosabiertos.mspas.gob.gt/dataset/353ffabb-2a3d-4ac1-9816-001b7c3cf62c/resource/ec760375-a081-4dd0-9920-2b699b580f84/download/mec-2016-departamento-municipio.csv",
    2017: "https://datosabiertos.mspas.gob.gt/dataset/353ffabb-2a3d-4ac1-9816-001b7c3cf62c/resource/f1d3e4c1-ce5f-4ec6-a660-93736fc24a22/download/mec-2017-departamento-municipio.csv",
    2018: "https://datosabiertos.mspas.gob.gt/dataset/353ffabb-2a3d-4ac1-9816-001b7c3cf62c/resource/96c479a5-18c9-4055-9db4-088b7dd4969a/download/mec-2018-departamento-municipio.csv",
    2019: "https://datosabiertos.mspas.gob.gt/dataset/353ffabb-2a3d-4ac1-9816-001b7c3cf62c/resource/01c3442c-efd9-4eab-a488-eea6c15f6d99/download/mec-2019-departamento-municipio.csv",
    2020: "https://datosabiertos.mspas.gob.gt/dataset/353ffabb-2a3d-4ac1-9816-001b7c3cf62c/resource/7efd56dd-861e-4ab0-956f-13d0508c6713/download/mec-2020-departamento-municipio.csv",
    2021: "https://datosabiertos.mspas.gob.gt/dataset/353ffabb-2a3d-4ac1-9816-001b7c3cf62c/resource/131175da-ab49-4515-b018-b98abbf3b109/download/mec-2021-departamento-municipio.csv",
    2022: "https://datosabiertos.mspas.gob.gt/dataset/353ffabb-2a3d-4ac1-9816-001b7c3cf62c/resource/7a5fd776-e6f6-4658-8c2b-5eb2155ed008/download/mec-2022-departamento-municipio.csv",
    2023: "https://datosabiertos.mspas.gob.gt/dataset/353ffabb-2a3d-4ac1-9816-001b7c3cf62c/resource/f048000b-3c3f-4b75-a0c2-94bc61bf6040/download/mec-2023-departamento-municipio.csv",
    2024: "https://datosabiertos.mspas.gob.gt/dataset/353ffabb-2a3d-4ac1-9816-001b7c3cf62c/resource/ad2416d9-6617-4968-9ed3-5de6efb32b05/download/mec-2024-departamento-municipio.csv",
}

# etpv = Enfermedades transmitidas por vectores
URLS_ETPV = {
    "chagas":       "https://datosabiertos.mspas.gob.gt/dataset/edda2ef9-afb9-4d29-a26f-2de87d6d95bb/resource/90ffdeef-4e86-46b4-b854-cb1c8e1e4533/download/enfermedades-transmitidas-por-vectores-2012-al-2024-chagas.csv",
    "chikungunya":  "https://datosabiertos.mspas.gob.gt/dataset/edda2ef9-afb9-4d29-a26f-2de87d6d95bb/resource/e9477b8e-8757-4fa3-933f-412d7dba891b/download/enfermedades-transmitidas-por-vectores-2012-al-2024-chikungunya.csv",
    "dengue_grave": "https://datosabiertos.mspas.gob.gt/dataset/edda2ef9-afb9-4d29-a26f-2de87d6d95bb/resource/a631679d-d9b1-469a-8f30-f58f27846777/download/enfermedades-transmitidas-por-vectores-2012-al-2024-dengue-grave.csv",
    "dengue":       "https://datosabiertos.mspas.gob.gt/dataset/edda2ef9-afb9-4d29-a26f-2de87d6d95bb/resource/bd821403-d902-4a08-bc0a-0667781de4a4/download/enfermedades-transmitidas-por-vectores-2012-al-2024-dengue.csv",
    "malaria":      "https://datosabiertos.mspas.gob.gt/dataset/edda2ef9-afb9-4d29-a26f-2de87d6d95bb/resource/016ce5e5-8f51-4597-8af9-70200bcd8ceb/download/enfermedades-transmitidas-por-vectores-2012-al-2024-malaria.csv",
    "zika":         "https://datosabiertos.mspas.gob.gt/dataset/edda2ef9-afb9-4d29-a26f-2de87d6d95bb/resource/2afcbe52-81dd-4deb-b590-7a4ba623907d/download/enfermedades-transmitidas-por-vectores-2012-al-2024-zika.csv",
}

# mgm = Morbilidad Grupo Materno Infantil
URLS_MGM = {
    "neonatal":       "https://datosabiertos.mspas.gob.gt/dataset/89a0f5d9-5219-4e7d-822a-85aaa01b40a4/resource/98746e82-10a8-431d-8023-20e679296602/download/morbilidad-neonatal-2012-al-2024.csv",
    "materna":        "https://datosabiertos.mspas.gob.gt/dataset/89a0f5d9-5219-4e7d-822a-85aaa01b40a4/resource/51a53177-fd15-4653-a859-048f47951183/download/morbilidad-materna-2012-al-2024.csv",
    "infantil_12_15": "https://datosabiertos.mspas.gob.gt/dataset/89a0f5d9-5219-4e7d-822a-85aaa01b40a4/resource/70fac429-4bbf-449e-ade0-994babc65372/download/morbilidad-infantil-2012-al-2015.csv",
    "infantil_16_19": "https://datosabiertos.mspas.gob.gt/dataset/89a0f5d9-5219-4e7d-822a-85aaa01b40a4/resource/1bf1726d-4c6b-4935-9957-1790854f62cd/download/morbilidad-infantil-2016-al-2019.csv",
    "infantil_20_23": "https://datosabiertos.mspas.gob.gt/dataset/89a0f5d9-5219-4e7d-822a-85aaa01b40a4/resource/c3e65b7e-971c-4ae2-8cbb-fdd6638ed60a/download/morbilidad-infantil-2020-2023.csv",
    "infantil_24":    "https://datosabiertos.mspas.gob.gt/dataset/89a0f5d9-5219-4e7d-822a-85aaa01b40a4/resource/93ac708f-e473-4ec4-9dcf-da1f0e05990f/download/morbilidad-infantil-2024.csv",
}

# mie = Morbilidad IRAS y ETAS
URLS_MIE = {
    "etas": "https://datosabiertos.mspas.gob.gt/dataset/36106feb-ed4e-46a8-a665-596bdf1f52a2/resource/5211b6c4-bc37-48da-97df-c138c4ac8553/download/morbilidad-etas-departamento-y-municipio-2012-al-2024.csv",
    "iras": "https://datosabiertos.mspas.gob.gt/dataset/36106feb-ed4e-46a8-a665-596bdf1f52a2/resource/1d7ad66e-4a0d-43b1-88df-4cdd6e177778/download/morbilidad-iras-departamento-y-municipio-2012-al-2024.csv",
}

# pcm = 20 primeras causas de morbilidad (un CSV por año)
URLS_PCM = {
    2012: "https://datosabiertos.mspas.gob.gt/dataset/99da410c-e256-4595-b35d-bf1491f50914/resource/c968472d-3aeb-4709-be8f-cc623f26469e/download/20-primeras-causas-de-morbilidad-2012-departamento-y-municipio.csv",
    2013: "https://datosabiertos.mspas.gob.gt/dataset/99da410c-e256-4595-b35d-bf1491f50914/resource/6adbcfed-8a4f-463b-9d2b-555a721a5296/download/20-primeras-causas-de-morbilidad-2013-departamento-y-municipio.csv",
    2014: "https://datosabiertos.mspas.gob.gt/dataset/99da410c-e256-4595-b35d-bf1491f50914/resource/7937b87a-d79f-41a1-91d2-a403c7a2a4c5/download/20-primeras-causas-de-morbilidad-2014-departamento-y-municipio.csv",
    2015: "https://datosabiertos.mspas.gob.gt/dataset/99da410c-e256-4595-b35d-bf1491f50914/resource/444f82f7-d0d9-4887-b53d-349c87121596/download/20-primeras-causas-de-morbilidad-2015-departamento-y-municipio.csv",
    2016: "https://datosabiertos.mspas.gob.gt/dataset/99da410c-e256-4595-b35d-bf1491f50914/resource/45ea817d-f8b0-40ed-9714-99d62795eccc/download/20-primeras-causas-de-morbilidad-2016-departamento-y-municipio.csv",
    2017: "https://datosabiertos.mspas.gob.gt/dataset/99da410c-e256-4595-b35d-bf1491f50914/resource/50bfb26d-0aa1-4686-946b-869de99056c5/download/20-primeras-causas-de-morbilidad-2017-departamento-y-municipio.csv",
    2018: "https://datosabiertos.mspas.gob.gt/dataset/99da410c-e256-4595-b35d-bf1491f50914/resource/abc11019-8cbc-4f19-a1c3-276a0cf2ab86/download/20-primeras-causas-de-morbilidad-2018-departamento-y-municipio.csv",
    2019: "https://datosabiertos.mspas.gob.gt/dataset/99da410c-e256-4595-b35d-bf1491f50914/resource/59fb87da-60c6-410c-9922-b238454007ae/download/20-primeras-causas-de-morbilidad-2019-departamento-y-municipio.csv",
    2020: "https://datosabiertos.mspas.gob.gt/dataset/99da410c-e256-4595-b35d-bf1491f50914/resource/e78ca4cb-33fe-4750-807b-83b3203dbe41/download/20-primeras-causas-de-morbilidad-2020-departamento-y-municipio.csv",
    2021: "https://datosabiertos.mspas.gob.gt/dataset/99da410c-e256-4595-b35d-bf1491f50914/resource/98048888-bb58-4990-8d64-7679561ecc9c/download/20-primeras-causas-de-morbilidad-2021-departamento-y-municipio.csv",
    2022: "https://datosabiertos.mspas.gob.gt/dataset/99da410c-e256-4595-b35d-bf1491f50914/resource/aa81356b-dd4e-42d8-b443-aa8a4460a9bd/download/20-primeras-causas-de-morbilidad-2022-departamento-y-municipio.csv",
    2023: "https://datosabiertos.mspas.gob.gt/dataset/99da410c-e256-4595-b35d-bf1491f50914/resource/40ae9bd0-583c-42b9-9586-2a130abb25cb/download/20-primeras-causas-de-morbilidad-2023-departamento-y-municipio.csv",
    2024: "https://datosabiertos.mspas.gob.gt/dataset/99da410c-e256-4595-b35d-bf1491f50914/resource/a9d252fe-0c11-4c5f-b564-19203a91589e/download/20-primeras-causas-de-morbilidad-2024-departamento-y-municipio.csv",
}

# pcp = Producción de consultas y pacientes nuevos
URLS_PCP = {
    "consultas": "https://datosabiertos.mspas.gob.gt/dataset/5361feea-66b6-4f4e-9cc5-521906699650/resource/13ac7f97-5f6f-4c6c-9cf0-141144328509/download/cantidad-de-pacientes-nuevos-y-consultas-atendidas-2012-al-2024.csv",
}

# snm = Suplementación niños menores 5 años
URLS_SNM = {
    "suplementacion": "https://datosabiertos.mspas.gob.gt/dataset/14427db8-e5f4-4e59-8ded-9bb3f6614e3b/resource/66dd65f7-a75b-457b-bab2-15ac4125a069/download/suplementacion-en-ninos-menores-5-2013-a-2024.csv",
}