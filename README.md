# Proyecto FastAPI - Estructura Simple

Este proyecto implementa una estructura simple de una aplicación **FastAPI** con Docker y un entorno virtual. La aplicación contiene un solo endpoint y está estructurada para facilitar su expansión en el futuro.

## Estructura del Proyecto

La estructura del proyecto es la siguiente:


### Descripción de las carpetas y archivos:

- **api/**: Carpeta que contiene la lógica principal de la aplicación FastAPI.
  - **main.py**: Archivo principal donde se configura la aplicación FastAPI y se incluyen las rutas.
  - **routes/**: Carpeta que contiene las rutas (endpoints) organizadas por módulos.
    - **endpoints.py**: Módulo con los endpoints de la aplicación.
  - **service/**: Carpeta con los archivos necesarios para implementar la logica de la aplicacion.
    - **app_service.py**: Contiene la logica de la aplicacion
  - **utils/**: Carpeta con archivos secundarios que pueden tener utilidad para la aplicación como son los serializers o dtos.
  
- **venv/**: Carpeta que contiene el entorno virtual de Python.
  
- **Dockerfile**: Archivo de configuración de Docker para construir la imagen de la aplicación.
  
- **.gitignore**: Archivo que indica qué archivos y carpetas deben ser ignorados por Git.
  
- **requirements.txt**: Archivo que lista las dependencias del proyecto para ser instaladas con `pip`.

---

## Configuración del entorno de desarrollo

### 1. Crear y activar el entorno virtual

#### En Linux:
* Desde la carpeta del repositorio dodne se encuentra el .git
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar dependencias
* Dentro del repositorio de pruebas-gems/api
```bash
pip install -r requirements.txt
```

### 3. Ejecutar aplicacion en terminal

* Dentro del repositorio de prueba-gems/api

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8888
```

### 4. Ejecutar desde el propio swagger en http://localhost:8888/docs
* Click en POST /productionplan
* Click en **Try it out**
* Reemplazar el JSON por uno de los paylaods de ejemplo.


##  Docker
### Imagenes 
#### Construir la imagen docker
```bash
sudo docker build -t mi-fastapi-app .
```

#### Listar imagenes del docker
```bash
sudo docker images
```

#### Eliminar imagenes del docker
```bash
sudo docker rmi <IMAGE_ID> // una especifica
sudo docker rmi $(sudo docker images -q) // todas
```
### Contenedores

#### Levantar un contenedor docker
```bash
sudo docker run -d -p 8888:8888 mi-fastapi-app
```

#### Listar los contenedores levantados
```bash
sudo docker ps
```

#### Detener todos los contenedores activos:

```bash
sudo docker stop $(sudo docker ps -q)
```

#### Eliminar todos los contenedores:

```bash
sudo docker rm $(sudo docker ps -aq)
```

#### Mostrar los logs de un contenedor

```bash
sudo docker logs <container_id>
```

## Ejecucion de Tests

No me he centrado demasiado en los test, unicamente he añadido los 5 payloads 3 aportados + 2 inventados para comprobar la ejeución de todos ellos.
Se trataría de realizar test ás exhaustivos sobre la aplicación y funcionalidad.

* Par ejecutar los tests se aconseja situarse dentro del repositorio prueba-gems/api y después ejecutar el siguiente comando:
```bash
PYTHONPATH=. pytest
```


### Explicacion Algoritmo

# Algoritmo de Producción de Energía

Este proyecto contiene un algoritmo sencillo para calcular el **plan de producción de energía** cuando se tiene una demanda específica y varias plantas de energía disponibles, cada una con diferentes capacidades, eficiencias, y tipos de combustible.

## Explicación del Algoritmo

El algoritmo se encarga de distribuir la generación de energía entre las plantas disponibles de acuerdo con la demanda dada, priorizando el uso de fuentes más baratas y eficientes, y respetando las limitaciones de cada planta, como el **mínimo** (pmin) y **máximo** (pmax) de producción.

### Pasos principales:

1. **Priorización por tipo de planta**: 
   - Primero se asigna la energía generada por **plantas eólicas** (viento), dado que no tienen costo de combustible.
   - Después se utilizan plantas de **gas** y, finalmente, plantas de **turbojet**.
   - Las plantas se seleccionan siguiendo esta priorización inicial, pero se ajusta la producción según las restricciones de cada una.

2. **Asignación inicial de energía**:
   - Se distribuye la energía a las plantas de acuerdo con su **capacidad máxima** (`pmax`) y la energía que pueden generar. 
   - Si una planta tiene un mínimo de energía (`pmin`) y no puede cumplir con él, se asegura que genere al menos esa cantidad, aunque esto signifique que produzca más de lo necesario.

3. **Ajuste de producción (`backward adjustment`)**:
   - Si al final una planta no puede generar lo suficiente para cumplir con su **pmin**, el algoritmo ajusta de manera **recursiva o iterativa** la producción de las plantas anteriores para redistribuir la energía y asegurarse de que todas las plantas cumplan con sus valores mínimos.
   - Este ajuste se realiza restando energía de las plantas anteriores y añadiéndola a las plantas que necesitan más producción.

## Casos a tener en cuenta

### 1. **Backward Adjustment: Redistribuir la demanda entre las plantas**
   Si una planta no llega a su potencia mínima (`pmin`), el algoritmo toma energía de la planta anterior para cubrir el déficit. Esto podría generar un efecto en cadena: si la planta previa se queda por debajo de su propio `pmin`, se ajusta nuevamente hacia atrás, restando energía de las plantas anteriores hasta cumplir con las restricciones de cada planta.

### 2. **Caso especial: Demandas pequeñas vs. Mínimos de producción**

Si la demanda es pequeña y una planta no puede generar menos de su **pmin**, el comportamiento del algoritmo depende de si hay alguna **penalización o beneficio** por devolver energía sobrante a la red.

Por ejemplo, si la demanda es de 50 unidades y la planta eólica puede generar 10, pero la siguiente planta de gas tiene un mínimo de 100, el algoritmo actuaría de la siguiente manera:

- **Si existe penalización** por devolver energía a la red, o no está permitido, el algoritmo se asegura de que solo se genere la cantidad exacta requerida. En este caso, se generarán las 10 unidades de la planta eólica y no se activará la planta de gas.
- **Si no hay penalización** o incluso existe algún tipo de beneficio por devolver energía sobrante a la red, el algoritmo podría decidir activar la planta de gas, generando más energía de la solicitada, hasta cubrir el **pmin** de dicha planta.

Sin embargo, según el enunciado del problema, **no se considera la opción de devolver energía sobrante a la red**. Por tanto, en este caso específico, el algoritmo solo activaría la planta eólica, generando solo las 10 unidades y evitando sobreproducción.

### 2.1. **Orden de activación de las plantas**

Además de manejar el caso de los mínimos de producción, el algoritmo sigue un **orden de activación de plantas** basado en la **eficiencia** y **capacidad** de cada planta para maximizar la energía producida y minimizar el coste de producción. Este orden puede variar según las prioridades, pero en la solución propuesta, el algoritmo sigue estos pasos:

1. **Orden por eficiencia**: Las plantas se ordenan de menor a mayor eficiencia, lo que significa que se priorizan las plantas menos eficientes para desactivar o reducir su producción en caso de exceso.
   - **Eólica**: Las plantas eólicas son las más eficientes, ya que no requieren combustible y su costo de operación es bajo.
   - **Gasfired**: Las plantas de gas son menos eficientes que las eólicas, pero siguen siendo preferibles a las turbojets.
   - **Turbojet**: Las turbojets son las menos eficientes, ya que su costo de operación es mucho mayor.

2. **Orden por capacidad**: Dentro de cada tipo de planta, se ordena por **capacidad de producción** (`pmax`), de menor a mayor. De esta manera, las plantas con menor capacidad son desactivadas primero para minimizar la sobreproducción.

Este enfoque asegura que la **energía producida** sea la **mínima requerida** para cubrir la demanda, evitando generar exceso de energía y optimizando el **coste de operación**.

### 3. **Priorización por eficiencia**:
   Aunque el algoritmo prioriza las plantas de energía según el **tipo** (primero eólica, luego gas, luego turbojet), sería recomendable añadir un sistema de priorización adicional por **eficiencia** dentro de cada tipo de planta. Esto significa que, dentro de las plantas de gas, aquellas que sean más eficientes deberían activarse primero. En algunos casos, una planta de **turbojet avanzada** podría ser más eficiente que una planta de gas antigua, y debería priorizarse.

### 4. **Capacidad de producción**

El algoritmo también debe tener en cuenta la **capacidad máxima** de cada planta. No es lo mismo utilizar tres instalaciones de gas pequeñas que una grande. Por ejemplo, si la primera planta tiene capacidad **x**, la segunda también **x**, y la tercera **2x**, es preferible utilizar una planta de capacidad **2x** y otra de capacidad **x**, en lugar de utilizar tres plantas pequeñas. Esto es importante porque:

- **Desgaste y vida útil de las instalaciones**: Cada vez que una planta se utiliza, se reduce su vida útil. Por lo tanto, es más eficiente desde un punto de vista operativo priorizar el uso de plantas con mayor capacidad para reducir el número de instalaciones activas, disminuyendo así el desgaste en múltiples plantas.

Sin embargo, esta estrategia de priorización por capacidad solo debe aplicarse cuando las plantas tienen la **misma eficiencia**. Si no, siempre es preferible priorizar primero la **eficiencia**, ya que las plantas más eficientes generarán la misma cantidad de energía con menos consumo de combustible, lo que reduce los costos operativos. Solo en casos en que dos plantas sean iguales en eficiencia, debería priorizarse la capacidad para minimizar el uso de las instalaciones y extender su vida útil.

En resumen, el algoritmo debería seguir este orden de prioridades:
1. **Primero por eficiencia**: Usar siempre las plantas más eficientes.
2. **Luego por capacidad**: En caso de igual eficiencia, priorizar aquellas con mayor capacidad para reducir el desgaste general de las instalaciones.

### 5. **Evitar la programación lineal**:
   Aunque este problema se podría resolver de forma óptima mediante técnicas de **programación lineal**, se ha solicitado no utilizar este enfoque. El algoritmo implementado sigue un enfoque más manual y ad hoc, ajustando las producciones de las plantas de manera iterativa y cumpliendo con las restricciones mínimas y máximas de cada una.

## Conclusión

El algoritmo propuesto proporciona una forma estructurada de asignar la demanda de energía entre diferentes plantas de generación, teniendo en cuenta restricciones importantes como los valores de producción mínima y máxima, la eficiencia de las plantas y la capacidad de las instalaciones. A pesar de que no utiliza programación lineal, sigue un enfoque eficiente para cumplir con las restricciones y minimizar el exceso de generación.
