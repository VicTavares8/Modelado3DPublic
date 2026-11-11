# Base de cráneo — escultura inicial

Abre **Craneo_Base.blend** en Blender 4.3.2 o posterior. Se guarda en Sculpt Mode con una sola malla y simetría X activa.

Solo volumen y silueta inicial: bóveda redondeada, parte inferior estrecha y transiciones sin refinar. Sin dientes, suturas ni cavidades anatómicas trabajadas. El acabado busca un ejercicio de principiante, con irregularidades moderadas.

Se partió de una esfera y se aplicaron pinceladas nativas de **Grab, Draw, Flatten y Smooth**, automatizadas con Python. No es una escultura manual realizada por una persona. No se utilizaron extrusiones, booleanos, ensamblaje de volúmenes ni edición directa de vértices para formar el cráneo.

![Vista de tres cuartos](tres_cuartos.png)

[Vista frontal](frente.png) · [Vista lateral](perfil.png)

## Comprobación

El archivo se volvió a abrir en Blender: una malla, cero modificadores y cero aristas no manifold. Simetría X comprobada numéricamente. Los recuentos están en `validacion.json`; `pinceladas.json` registra las operaciones aplicadas. La apariencia es una interpretación artística inicial, no una reconstrucción anatómica.

## Reproducir

`crear_base.py` conserva la secuencia de pinceles. Ejecutar con Blender 4.3.2 y una sesión gráfica activa:

```bash
blender --factory-startup --python crear_base.py
```

No usar `--background`: los pinceles requieren una vista 3D activa. El script crea los archivos en la subcarpeta `regenerado`, sustituyendo sus salidas si ya existen, y cierra esa instancia de Blender al terminar. La secuencia fue ejecutada y comprobada en Linux con Blender 4.3.2; otras versiones pueden variar en el comportamiento de los pinceles.
