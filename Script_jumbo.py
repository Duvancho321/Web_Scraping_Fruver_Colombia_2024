"""
Codigo para web scraping de almacenes jumbo.

__author__: "Duvan Nieves"
__copyright__: "UNAL"
__version__: "0.0.1"
__maintaner__:"Duvan Nieves"
__email__:"dnieves@unal.edu.co"
__status__:"Developer"
__changues__:
    - [2024-06-20][Duvan]: Primera version del codigo.
    - [2024-06-21][Duvan]: Se realiza exploración con BeautifulSoup4.
    - [2024-06-24][Duvan]: Se hace llamado a todo el html y se identifican falencias con el paginado.
    - [2024-06-25][Duvan]: Se opta por cambiar a selenium.
    - [2024-06-28][Duvan]: Se ajusta el drive para no tener que decaragar el ejecutable de google chrome.
    - [2024-07-02][Duvan]: Se implementa el movimiento entre las distintas paginas de verduras y frutas dentro de unsitio web de prueba.
    - [2024-07-04][Duvan]: Se implementa manejo de errores para mejorar la eficiencia del codigo.
    - [2024-07-08][Duvan]: Se analizan los xpath de los productor para extraer información relevante.
    - [2024-07-11][Duvan]: Se logra extraccion de variables de interes. 
    - [2024-08-15][Duvan]: Se aumentan los tiempos y se procesa en tiempo real para excluir rutas obsoletas.
    - [2024-08-19][Duvan]: Se incluye scroll para evitar rastreo y lograra cargar efectivamente todos los productos.
    - [2024-08-23][Duvan]: Se inclutye busqueda efectiva de paginación y se añade bottom scroll.
    - [2024-08-26][Duvan]: Se ajusta el procesamiento para guardado de los datos limpios. 
"""
#%% MODULOS
from time import sleep
from random import uniform
from datetime import datetime
from pandas import DataFrame
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

def scroll_page_slowly(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Scroll down slowly
        for i in range(10):
            driver.execute_script(f"window.scrollTo(0, {last_height * (i+1) / 10});")
            sleep(0.5)
        
        # Wait for the page to load
        sleep(2)
        
        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If heights are the same, it might be the end of the page
            break
        last_height = new_height

    # Scroll back to top slowly
    for i in range(10, 0, -1):
        driver.execute_script(f"window.scrollTo(0, {last_height * i / 10});")
        sleep(0.3)

    print("Scroll completo realizado.")

def scroll_to_bottom(driver):
    print("Iniciando scroll hasta el final de la página...")
    # Scroll hasta el final de la página
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(5)  # Espera para que se carguen los elementos

    # Scroll adicional para asegurar que estamos al final
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(2)

    print("Scroll al final de la página completado.")


def obtener_texto(elemento, xpath, tiempo_espera=20, valor_predeterminado="No disponible"):
    try:
        subelemento = WebDriverWait(elemento, tiempo_espera).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return subelemento.text.strip()
    except (TimeoutException, StaleElementReferenceException, NoSuchElementException):
        print(f"Elemento no encontrado o obsoleto para xpath: {xpath}")
        return valor_predeterminado
    except Exception as e:
        print(f"Error al obtener texto para xpath {xpath}: {str(e)}")
        return valor_predeterminado

def extraer_informacion_producto(driver, producto):
    try:
        nombre = obtener_texto(producto, './/span[@class="vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body"]')
        precio = obtener_texto(producto, './/div[contains(@class, "tiendasjumboqaio-jumbo-minicart-2-x-price")]')
        precio_unidad = obtener_texto(producto, './/div[contains(@class, "w-100 tiendasjumboqaio-calculate-pum-2-x-PUMInfo tiendasjumboqaio-calculate-pum-2-x-PUMInfo--shelf")]')
        return {
            'nombre': nombre,
            'precio': precio,
            'precio_unidad': precio_unidad
        }
    except Exception as e:
        print(f"Error al extraer información del producto: {str(e)}")
        return None


def obtener_paginas_disponibles(driver):
    try:
        # Realizar scroll hasta el final de la página
        scroll_to_bottom(driver)
        
        # Intentar encontrar el elemento del desplegable
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//select[contains(@class, "o-0")]'))
        )
        select = Select(select_element)
        paginas = [option.get_attribute('value') for option in select.options if option.get_attribute('value').isdigit()]
        
        print(f"Se encontraron {len(paginas)} páginas disponibles.")
        return paginas
    except Exception as e:
        print(f"Error al obtener las páginas disponibles: {str(e)}")
        return []

def navegar_a_pagina(driver, numero_pagina):
    try:
        scroll_to_bottom(driver)  # Scroll al final antes de seleccionar la página
        current_url = driver.current_url
        
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//select[contains(@class, "o-0")]'))
        )
        select = Select(select_element)
        select.select_by_value(str(numero_pagina))
                       
        sleep(uniform(3, 5))  # Espera adicional para asegurar que la página se cargue completamente
    except TimeoutException:
        print(f"Timeout al navegar a la página {numero_pagina}. La página pudo haber cambiado, pero no se detectaron nuevos productos.")
    except Exception as e:
        print(f"Error al navegar a la página {numero_pagina}: {str(e)}")
    finally:
        # Scroll to top to ensure we're at the beginning of the new page
        driver.execute_script("window.scrollTo(0, 0);")


#%% URL y configuración
url = 'https://www.tiendasjumbo.co/supermercado/frutas-y-verduras'
hoy = datetime.now().strftime('%d%m%Y%H%M')
path_save = '/home/dunievesr/Dropbox/UNAL/Web_scraping/'  # Actualizar según sea necesario

#%% OPCIONES DE DRIVER
opts = Options()
opts.add_argument("User-Agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
opts.add_argument('--headless')
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=opts
)

#%% SCRAPING CON NAVEGACIÓN POR DESPLEGABLE
driver.get(url)
sleep(uniform(6, 12))
productos_list = []

paginas_disponibles = obtener_paginas_disponibles(driver)
print(f"Páginas disponibles: {paginas_disponibles}")

#%%
for pagina in paginas_disponibles[0:2]:
    print(f"Procesando página {pagina} --> ", end=':')
    
    navegar_a_pagina(driver, pagina)
    scroll_page_slowly(driver)
    sleep(3)  # Espera adicional después del scroll
    
    # Obtener elementos
    nombres = driver.find_elements(By.XPATH, './/span[@class="vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body"]')
    precios = driver.find_elements(By.XPATH, './/div[contains(@class, "tiendasjumboqaio-jumbo-minicart-2-x-price")]')
    precios_x_unidad = driver.find_elements(By.XPATH, './/div[contains(@class, "w-100 tiendasjumboqaio-calculate-pum-2-x-PUMInfo tiendasjumboqaio-calculate-pum-2-x-PUMInfo--shelf")]')
    
    min_elementos = min(len(nombres), len(precios), len(precios_x_unidad))
    
    for i in range(min_elementos):
        producto = {
            'nombre': nombres[i].text if i < len(nombres) else "No disponible",
            'precio': precios[i].text if i < len(precios) else "No disponible",
            'precio_unidad': precios_x_unidad[i].text if i < len(precios_x_unidad) else "No disponible"
        }
        productos_list.append(producto)
    
    print(f"Procesada. Se encontraron {min_elementos} productos.")

print(f"Se han procesado un total de {len(paginas_disponibles)} páginas y se encontraron {len(productos_list)} productos.")
driver.quit()
# %% POSPORCESAMIENTO
df_productos = DataFrame(productos_list)
df_productos['precio'] = df_productos['precio'].str.replace(r'\$|\.', '', regex=True)
df_productos['precio_x_unidad'] = (df_productos['precio_unidad'].str.replace(r'[()]', '', regex=True)
                                   .str.split(' a ')
                                   .str[-1].str.replace(r'\$|\.', '', regex=True)
                                   .str.replace(r'\,','.',regex=True))
df_productos['unidad'] = df_productos['precio_unidad'].str.replace(r'[()]', '', regex=True).str.split(' a ').str[0]
df_productos.drop(columns=['precio_unidad'],inplace=True)
# %% GUARDADO DE DATOS
df_productos.to_csv(path_save+'jumbo_'+hoy+'.csv')
print('Termine la ejecuion para el jumbo')
