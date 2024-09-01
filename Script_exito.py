
"""
Codigo para web scraping de almacenes exito.

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
    - [2024-08-07][Duvan]: Se añaden lineas de codigo para evitar banners y promociones. 
    - [2024-08-15][Duvan]: Se aumentan los tiempos y se procesa en tiempo real para excluir rutas obsoletas.
    - [2024-08-22][Duvan]: Se ajusta el procesamiento para guardado de los datos limpios. 
"""
#%% MODULOS
from time import sleep
from random import uniform
from pandas import DataFrame
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#%% FUNCIONES
def obtener_texto(driver, xpath, tiempo_espera=10, valor_predeterminado="No disponible"):
    try:
        elemento = WebDriverWait(driver, tiempo_espera).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return elemento.text
    except (TimeoutException, StaleElementReferenceException):
        print(f"Elemento no encontrado o obsoleto para xpath: {xpath}")
        return valor_predeterminado
    except Exception as e:
        print(f"Error al obtener texto para xpath {xpath}: {str(e)}")
        return valor_predeterminado

def cerrar_banner(driver):
    try:
        banner_close = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "wps-overlay-close-button"))
        )
        banner_close.click()
        print("Banner cerrado exitosamente.")
        sleep(2)  # Esperar un poco después de cerrar el banner
    except TimeoutException:
        print("No se encontró el banner o no se pudo cerrar.")

def extraer_informacion_producto(driver, producto):
    try:
        nombre = obtener_texto(producto, './/p[@class="styles_name__qQJiK"]')
        precio = obtener_texto(producto, './/p[contains(@class, "ProductPrice_container__price")]')
        precio_unidad = obtener_texto(producto, './/span[contains(@class, "product-unit_price-unit__text")]')
        return {
            'producto': nombre,
            'precio': precio,
            'precio_unidad': precio_unidad
        }
    except Exception as e:
        print(f"Error al extraer información del producto: {str(e)}")
        return None

#%% URL
url_exito = 'https://www.exito.com/mercado/frutas-y-verduras' #enlace del sitio a explorar
#%% Fecha
hoy = datetime.now().strftime('%d%m%Y%H%M')
path_save = '/home/dunievesr/Dropbox/UNAL/Web_scraping/' #Actualizar

#%% OPCIONES DE DRIVER
opts = Options()
opts.add_argument("User-Agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
opts.add_argument('--headless')
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=opts
)

#%% SCRAPING INICIAL CON NEXT BUTTON 
driver.get(url_exito)
sleep(uniform(6, 12))
productos_list = []
pagina = 1
url_anterior = ""

while True:
    print(f"Procesando página {pagina} --> ",end='')
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="productCard_productInfo__yn2lK"]')))
    except TimeoutException:
        print("No se pudieron cargar los productos. Finalizando.")
        break
    
    new_products = driver.find_elements(By.XPATH, '//div[@class="productCard_productInfo__yn2lK"]')
    
    for producto in new_products:
        info_producto = extraer_informacion_producto(driver, producto)
        if info_producto:
            productos_list.append(info_producto)
    
    print(f"Procesada. Se encontraron {len(new_products)} productos.")
    
    try:
        next_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@class="Pagination_nextPreviousLink__f7_2J" and @aria-label="Próxima Pagina" and not(@disabled)]'))
        )
        
        try:
            next_button.click()
        except ElementClickInterceptedException:
            print("Click interceptado. Intentando cerrar el banner...")
            cerrar_banner(driver)
            # Intentar hacer clic nuevamente después de cerrar el banner
            next_button.click()
        
        sleep(uniform(8, 12))
        WebDriverWait(driver, 30).until(lambda d: d.current_url != url_anterior)
        url_anterior = driver.current_url
        pagina += 1
    except (TimeoutException, NoSuchElementException):
        print("No se pudo encontrar o hacer clic en el botón 'Próxima Página'. Finalizando.")
        break

print(f"Se han procesado un total de {pagina} páginas y se encontraron {len(productos_list)} productos.")
driver.quit()
# %% POSPORCESAMIENTO
df_productos = DataFrame(productos_list)
df_productos['precio'] = df_productos['precio'].str.replace(r'\$|\.', '', regex=True)
df_productos['precio_x_unidad'] = df_productos['precio_unidad'].str.split(' a ').str[-1].str.replace(r'\$|\.', '', regex=True)
df_productos['unidad'] = df_productos['precio_unidad'].str.split(' a ').str[0]
df_productos.drop(columns=['precio_unidad'],inplace=True)
# %% GUARDADO DE DATOS
df_productos.to_csv(path_save+'exito_'+hoy+'.csv')
print('Termine la ejecuion para el exito')

# %%
