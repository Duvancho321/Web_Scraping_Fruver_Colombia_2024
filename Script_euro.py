"""
Codigo para web scraping de almacenes euro.

__author__: "Duvan Nieves"
__copyright__: "UNAL"
__version__: "0.0.2"
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
from selenium.webdriver.common.action_chains import ActionChains

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
            EC.element_to_be_clickable((By.XPATH, '//button[@class="vtex-modal-layout-0-x-closeButton vtex-modal-layout-0-x-closeButton--delivery-geolocation-modal ma0 bg-transparent pointer bw0 pa3"]'))
        )
        banner_close.click()
        print("Banner cerrado exitosamente.")
        sleep(2)
    except TimeoutException:
        print("No se encontró el banner o no se pudo cerrar.")

def extraer_informacion_producto(driver, producto):
    try:
        nombre = obtener_texto(producto, './/span[contains(@class, "vtex-product-summary-2-x-productBrand")]')
        precio = obtener_texto(producto, './/span[contains(@class, "vtex-product-price-1-x-currencyContainer")]')
        precio_unidad = "No disponible"
        return {
            'producto': nombre,
            'precio': precio,
            'precio_unidad': precio_unidad
        }
    except Exception as e:
        print(f"Error al extraer información del producto: {str(e)}")
        return None

def scroll_hasta_mostrar_mas(driver):
    try:
        mostrar_mas = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[@type="button"]//div[contains(text(), "Mostrar más")]'))
        )
        actions = ActionChains(driver)
        actions.move_to_element(mostrar_mas).perform()
        return mostrar_mas
    except:
        return None

#%% URL y configuración
url = 'https://www.eurosupermercados.com.co/mercado/fruver'
hoy = datetime.now().strftime('%d%m%Y%H%M')
path_save = '/home/dunievesr/Dropbox/UNAL/Web_scraping/'

#%% OPCIONES DE DRIVER
opts = Options()
opts.add_argument("User-Agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
opts.add_argument('--headless')
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=opts
)

#%% SCRAPING
driver.get(url)
sleep(uniform(6, 12))
productos_list = []
iteraciones = 0
#%%
while True:
    cerrar_banner(driver)
    try:

        mostrar_mas = scroll_hasta_mostrar_mas(driver)
        if not mostrar_mas:
            print("No se encontró el botón 'Mostrar más'. Finalizando.")
            break
        
        mostrar_mas.click()
        sleep(uniform(5, 8))
        
        new_products = driver.find_elements(By.XPATH, '//article[contains(@class, "vtex-product-summary-2-x-element")]')
        productos_antes = len(productos_list)
        
        for producto in new_products:
            info_producto = extraer_informacion_producto(driver, producto)
            if info_producto and info_producto not in productos_list:
                productos_list.append(info_producto)
        
        productos_nuevos = len(productos_list) - productos_antes
        iteraciones += 1
        print(f"Iteración {iteraciones}: {productos_nuevos} nuevos productos. Total: {len(productos_list)}")
        
        if productos_nuevos == 0:
            print("No se encontraron nuevos productos. Finalizando.")
            break
    except Exception as e:
        print(f"Error en iteración {iteraciones + 1}: {str(e)}. Finalizando.")
        break

print(f"Total de productos encontrados: {len(productos_list)}")
driver.quit()
#%% POSPROCESAMIENTO
df_productos = DataFrame(productos_list)
df_productos['precio'] = df_productos['precio'].str.replace(r'\$|\.', '', regex=True)
df_productos['precio_x_unidad'] = df_productos['precio_unidad']
df_productos.drop(columns=['precio_unidad'],inplace=True)

#%% GUARDADO DE DATOS
df_productos.to_csv(path_save+'euro_'+hoy+'.csv', index=False)
print('Terminó la ejecución para el euro')