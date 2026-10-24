# Cueva calavera — primera versión

Estudio inicial basado en las referencias aportadas, creado con Blender 5.2.3 LTS.

## Descargas

- [Paquete completo ZIP](https://github.com/VicTavares8/Modelado3DPublic/raw/refs/heads/main/output/skull_cave_v01_package.zip)
- [Modelo GLB](https://github.com/VicTavares8/Modelado3DPublic/raw/refs/heads/main/output/skull_cave_v01/skull_cave_v01.glb)
- [Archivo editable Blender](https://github.com/VicTavares8/Modelado3DPublic/raw/refs/heads/main/output/skull_cave_v01/skull_cave_v01.blend)

![Vista exterior de la primera versión](output/skull_cave_v01/01_exterior.png)

## Entrega

- `output/skull_cave_v01/skull_cave_v01.blend`: malla editable y cámaras/luces de presentación en una colección separada.
- `output/skull_cave_v01/skull_cave_v01.glb`: únicamente el cascarón y sus materiales, sin luces ni cámaras.
- `01_exterior.png`, `02_front.png`, `03_rear.png`, `04_interior.png`: vistas de revisión.

Medidas: 12 m de ancho, 10 m de fondo, 8 m de alto. Frente hacia -Y en Blender; exportación GLB con conversión estándar Y-up. Origen en el centro de la base. Sin suelo ni mobiliario. Ojos, nariz y boca abiertos, con superficies interiores y espesor real de pared.

Esta versión prioriza silueta y volumen transitable. Tiene materiales básicos de piedra, sin texturas detalladas, grietas, colisiones ni LOD. La parte trasera es una interpretación de las referencias disponibles. La forma está todavía redondeada y pendiente de revisión artística.

## Validación

19.680 triángulos y 9.836 vértices antes de exportar. La malla no presenta aristas no manifold ni caras degeneradas. Se verificaron mediante rayos la ausencia de suelo, las cuatro aberturas, techo, fondo y pared lateral. Se exportó e importó el GLB para comprobar medidas, materiales y presencia de una sola malla. El exportador puede separar vértices por UV y material.

## Reproducir en este entorno

```bash
export XDG_CONFIG_HOME=/workspace/blender-tools/config
export XDG_CACHE_HOME=/workspace/blender-tools/cache
cd /workspace/Modelado3DPublic
/workspace/blender-tools/blender-5.2.3-linux-x64/blender --background --factory-startup --threads 4 --python-exit-code 1 --python scripts/build_skull_cave.py
/workspace/blender-tools/blender-5.2.3-linux-x64/blender --background --threads 1 --python-exit-code 1 --python scripts/check_skull_cave.py
```

El generador reemplaza los archivos de salida de v01. Guarda tus ediciones manuales con otro nombre antes de ejecutarlo.

En macOS abre el `.blend` con Archivo > Abrir o importa el `.glb` con Archivo > Importar > glTF 2.0. La ejecución y las pruebas se hicieron en Linux con 5.2.3; no se ha probado la apertura en tu Mac con 5.2.2.
