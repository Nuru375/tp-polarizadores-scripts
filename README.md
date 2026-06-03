# tp-polarizadores-scripts
En este repositorio se puede hallar los scripts para configurar la placa Arduino y para controlar los motores.

## Set-Up experimental: conexión de los motores (Arduino)
Los detalles de los pines utilizados, los drivers y demás cuestiones referentes a la conexión física de los motores puede hallarse en el informe de laboratorio colocado en `/documentacion/informe.pdf`. Allí también podrá encontrar, en el Apéndice B, el desglose del código `.ino` utilizado para configurar la placa Arduino.

## Guía de uso del repositorio
En este repositorio se encuentran distintos directorios donde fue distribuido el material utilizado para este trabajo. Para utilizar los códigos correctamente, se debe instalar las librerías descritas en el archivo `requirements.txt` (es recomendable hacerlo dentro de un entorno virtual); para hacerlo, basta utilizar el comando:
```
python -m pip install -r requirements.txt
```

Instaladas las dependencias, asumiendo que ya tiene el Set-Up armado, conecte la placa Arduino a la computadora y configúrela con el archivo `control_motores.ino`, que se encuentra en el directorio `/firmware/control_motores`. Luego, cierre el IDE de Arduino y abra el script de Python con el cuál controlará los motores: `ScriptMotor.py`, el mismo se encuentra en el directorio `/adquisicion`. Los detalles sobre cómo utilizar este script pueden hallarse en el Apéndice A del informe de laboratorio.

En el directorio `/analisis` podrá hallar los scripts utilizados para procesar la información recolectada; dicha información se encuentra en el directorio `/datos`.

Utilizamos como referencia scripts armados en MatLab por Claudio Bonin, dichos scripts se encuentran en el directorio `/referencias_matlab`.

Por último, en el directorio `/documentacion` encontrará el informe de laboratorio y la bibliografía utilizada como referencia.
