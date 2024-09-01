# Web Scraping de Precios de Productos en Supermercados

## Descripción

Este proyecto realiza web scraping de precios de productos en cinco supermercados principales de Colombia: Éxito, Carulla, Jumbo, Euro y Merkaorgánico. Utiliza Selenium WebDriver para navegar y extraer información de productos de las páginas web de los supermercados, manejando las particularidades de cada tienda, como paginación, carga dinámica y manejo de banners.

## Requisitos

- Python 3.8 o superior
- Google Chrome
- Conexión a internet estable

### Dependencias
- selenium==4.15.2
- webdriver-manager==4.0.1
- pandas==2.1.3

## Instalación
1. Clonar el repositorio:

```
git clone https://github.com/tu-usuario/Web_Scraping_Fruver_Colombia_2024.git
cd Web_Scraping_Fruver_Colombia_2024
```

2. Instalar las dependencias:

```
pip install -r requirements.txt
```

## Uso

Para ejecutar el scraping para un supermercado específico, use el siguiente comando:

```
python script_[nombre_supermercado].py
```

Por ejemplo:

```
python script_exito.py
```

## Estructura del Proyecto

- `script_exito.py`: Script para el supermercado Éxito
- `script_carulla.py`: Script para Carulla
- `script_jumbo.py`: Script para Jumbo
- `script_euro.py`: Script para Euro
- `script_merka.py`: Script para Merkaorgánico
- `requirements.txt`: Lista de dependencias del proyecto

## Notas Importantes

- No ejecute los scripts más de una vez por hora para evitar sobrecargar los servidores de los supermercados.
- El script de Carulla suele ser el que más tiempo toma en ejecutarse. Sea paciente durante su ejecución.
- Los resultados se guardan en archivos CSV con el formato: `[nombre_almacen]_[ddmmYYYYHHMM].csv`


## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Vea el archivo `LICENSE` para más detalles.

La Licencia MIT es una licencia de software permisiva de código abierto. Permite a los usuarios usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar y/o vender copias del software sin restricciones, siempre que se incluya el aviso de copyright y la licencia en todas las copias o partes sustanciales del software.

## Contacto

Duvan Nieves - dnieves@unal.edu.co

Enlace del proyecto: [https://github.com/Duvancho321/Web_Scraping_Fruver_Colombia_2024](https://github.com/Duvancho321/Web_Scraping_Fruver_Colombia_2024)