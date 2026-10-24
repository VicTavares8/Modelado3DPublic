"""Procedural hollow skull cave study. Blender 5.2.3; dimensions in metres."""
import bpy
import bmesh
import json
import math
import pathlib
from mathutils import Vector, noise

OUT = pathlib.Path(__file__).resolve().parents[1] / 'output' / 'skull_cave_v01'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

def active(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

def apply(obj, modifier):
    active(obj)
    bpy.ops.object.modifier_apply(modifier=modifier.name)

def ellipsoid(name, center, scale, segments=64, rings=40):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=center)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj

def subtract(obj, cutter):
    mod = obj.modifiers.new('Carve ' + cutter.name, 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = cutter
    apply(obj, mod)
    bpy.data.objects.remove(cutter, do_unlink=True)

def prism(name, polygon, front=-12.0, back=1.5):
    n = len(polygon)
    verts = [(x, y, z) for y in (front, back) for x, z in polygon]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2*n))]
    faces += [(i, (i+1) % n, (i+1) % n+n, i+n) for i in range(n)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(obj)
    return obj

# A broad, squat dome and projecting cheeks rather than an anatomical jaw.
parts = [ellipsoid('Cranial dome', (0, 0.35, 2.65), (6, 4.65, 5.35)),
         ellipsoid('Left cheek', (-3.8, -2.9, 1.35), (1.95, 2.1, 2.6)),
         ellipsoid('Right cheek', (3.8, -2.9, 1.35), (1.95, 2.1, 2.6)),
         ellipsoid('Projecting muzzle arch', (0, -3.45, 2.85), (3.45, 1.95, 1.55))]
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:
    obj.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()
shell = bpy.context.object
shell.name = 'Skull_Cave_Rock_Shell'
active(shell)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
remesh = shell.modifiers.new('Fuse stone masses', 'REMESH')
remesh.mode = 'VOXEL'
remesh.voxel_size = 0.14
remesh.use_smooth_shade = True
apply(shell, remesh)
smooth = shell.modifiers.new('Soften stone transitions', 'SMOOTH')
smooth.factor = 0.9
smooth.iterations = 4
apply(shell, smooth)

# Low-frequency irregularity changes the silhouette; it is exported as geometry.
for v in shell.data.vertices:
    p = v.co.copy()
    broad = noise.noise_vector(p * 0.52, noise_basis='PERLIN_ORIGINAL')
    fine = noise.noise_vector(p * 1.8, noise_basis='PERLIN_ORIGINAL')
    v.co += broad * 0.19 + fine * 0.045
shell.data.update()

# Hollow the dome; the cavity crosses the ground plane. No interior floor.
subtract(shell, ellipsoid('Interior volume', (0, 0.3, 2.5), (5.35, 4.0, 4.8)))

# Ground cut leaves a solid wall rim, not a ground plane across the interior.
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, -10))
ground_cut = bpy.context.object
ground_cut.name = 'Below ground'
ground_cut.scale = (20, 20, 10)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
subtract(shell, ground_cut)

# Mouth: an irregular broad arch, open at the base, connected to the cavity.
mouth = [(-2.35, -2), (2.35, -2), (2.34, 0.65), (2.23, 1.65),
         (2.05, 2.36), (1.6, 2.77), (0.9, 3.02), (0.25, 3.16),
         (-0.4, 3.1), (-1.1, 2.96), (-1.76, 2.68), (-2.18, 2.12),
         (-2.35, 1.2)]
subtract(shell, prism('Mouth entrance', mouth))

# Eye sockets use asymmetric polygonal outlines with rounded overall silhouettes.
for side in (-1, 1):
    cx, cz = side*2.55, 5.42
    points = []
    for i in range(22):
        a = i * math.tau / 22
        r = 1 + 0.035*math.sin(3*a+side) + 0.022*math.cos(5*a)
        x = 1.37*math.cos(a)*r
        z = 1.42*math.sin(a)*r
        points.append((cx+x, cz+z-side*0.10*x))
    subtract(shell, prism('Eye opening', points, back=0.4))

# Narrow triangular nose with a small upward notch at its base.
nose = [(-0.62, 3.95), (-0.5, 4.35), (-0.22, 4.93), (0, 5.25),
        (0.25, 4.94), (0.5, 4.36), (0.61, 3.96), (0.08, 4.12)]
subtract(shell, prism('Nasal opening', nose, back=0.5))

# Rebuild the boolean seams as one watertight wall, softening cut edges slightly.
remesh = shell.modifiers.new('Continuous stone wall topology', 'REMESH')
remesh.mode = 'VOXEL'
remesh.voxel_size = 0.105
remesh.use_smooth_shade = True
apply(shell, remesh)
smooth = shell.modifiers.new('Worn socket rims', 'SMOOTH')
smooth.factor = 0.7
smooth.iterations = 2
apply(shell, smooth)
decimate = shell.modifiers.new('Low polygon stone', 'DECIMATE')
decimate.ratio = 0.15
apply(shell, decimate)
tri = shell.modifiers.new('Consistent export triangles', 'TRIANGULATE')
apply(shell, tri)

# Scale the final visible bounds to the agreed initial envelope.
mins = Vector(tuple(min(v.co[i] for v in shell.data.vertices) for i in range(3)))
maxs = Vector(tuple(max(v.co[i] for v in shell.data.vertices) for i in range(3)))
size = maxs-mins
for v in shell.data.vertices:
    v.co.x = (v.co.x-(mins.x+maxs.x)/2)*12/size.x
    v.co.y = (v.co.y-(mins.y+maxs.y)/2)*10/size.y
    v.co.z = (v.co.z-mins.z)*8/size.z

# Simple glTF-compatible rough stone palette. No non-exportable procedural shader.
for i in range(7):
    mat = bpy.data.materials.new('Warm weathered stone %02d' % i)
    mat.use_nodes = True
    shade = 0.86 + i*0.045
    color = (0.38*shade, 0.355*shade, 0.29*shade, 1)
    mat.diffuse_color = color
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.95
    shell.data.materials.append(mat)
for face in shell.data.polygons:
    p = face.center
    n = noise.noise_vector(p*0.65, noise_basis='PERLIN_ORIGINAL').x
    face.material_index = min(6, max(0, round(3+n*3)))
    face.use_smooth = True
active(shell)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.025)
bpy.ops.object.mode_set(mode='OBJECT')

shell['description'] = 'Hollow rocky skull cave; no floor or props. Initial reference study v01.'
shell['dimensions_m'] = '12 wide x 10 deep x 8 high'
shell['front_direction'] = '-Y'
shell['material_note'] = 'Simple stone palette; detailed texture pass is not included in v01.'

# Validate the shell before adding presentation objects.
bm = bmesh.new()
bm.from_mesh(shell.data)
bad_edges = sum(not e.is_manifold for e in bm.edges)
degenerate = sum(f.calc_area() < 1e-9 for f in bm.faces)
bm.free()
assert bad_edges == 0, f'Nonmanifold edges: {bad_edges}'
assert degenerate == 0, f'Degenerate faces: {degenerate}'
assert abs(shell.dimensions.x-12) < 0.01
stats = {'blender': bpy.app.version_string, 'vertices': len(shell.data.vertices),
         'triangles': len(shell.data.polygons), 'nonmanifold_edges': bad_edges,
         'degenerate_faces': degenerate, 'dimensions_m': list(shell.dimensions),
         'material_stage': 'basic stone colors; no detailed texture pass'}

# GLB contains only the cave mesh, without presentation cameras or lights.
active(shell)
bpy.ops.export_scene.gltf(filepath=str(OUT/'skull_cave_v01.glb'), export_format='GLB',
                         use_selection=True, export_yup=True, export_apply=True)

presentation = bpy.data.collections.new('Presentation — cameras and lights only')
scene.collection.children.link(presentation)
def move_to_presentation(obj):
    for coll in list(obj.users_collection):
        coll.objects.unlink(obj)
    presentation.objects.link(obj)

def aim(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z', 'Y').to_euler()

def camera(name, pos, target, lens):
    bpy.ops.object.camera_add(location=pos)
    obj = bpy.context.object
    obj.name = name
    obj.data.lens = lens
    obj.data.clip_end = 200
    aim(obj, target)
    move_to_presentation(obj)
    return obj

cameras = [camera('Front three-quarter', (15, -22, 12), (0, -0.4, 3.5), 46),
           camera('Front', (0, -25, 6.5), (0, -0.7, 3.8), 48),
           camera('Rear three-quarter', (-15, 20, 12), (0, 0, 3.6), 46),
           camera('Interior looking toward entrance', (0, 2.9, 2.5), (0, -5, 3), 18)]
for name, pos, power, size, color in [
    ('Key', (-7,-12,16), 2400, 9, (1,0.89,0.74)),
    ('Fill', (10,-6,9), 1600, 8, (0.75,0.86,1)),
    ('Rim', (0,9,13), 2200, 7, (1,0.96,0.85)),
    ('Interior soft fill', (0,1,4), 110, 3, (1,0.9,0.76))]:
    bpy.ops.object.light_add(type='AREA', location=pos)
    light=bpy.context.object
    light.name=name
    light.data.energy=power
    light.data.shape='DISK'
    light.data.size=size
    light.data.color=color
    aim(light,(0,-1,2))
    move_to_presentation(light)

scene.world = bpy.data.worlds.new('Studio background')
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (0.11,0.14,0.18,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = 0.45
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = 1200
scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.view_transform = 'AgX'
scene.camera=cameras[0]
active(shell)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'skull_cave_v01.blend'))
for cam, filename in zip(cameras, ['01_exterior','02_front','03_rear','04_interior']):
    scene.camera=cam
    scene.render.filepath=str(OUT/(filename+'.png'))
    bpy.ops.render.render(write_still=True)

# Round trip the actual delivery file and verify mesh dimensions and material presence.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(OUT/'skull_cave_v01.glb'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(meshes)==1
obj=meshes[0]
assert len(obj.data.materials)>0
assert all(abs(a-b)<0.01 for a,b in zip(sorted(obj.dimensions), [8,10,12]))
stats['glb_roundtrip']='passed: one cave mesh, dimensions and materials preserved'
(OUT/'validation.json').write_text(json.dumps(stats,indent=2)+'\n')
print('MODEL_COMPLETE',json.dumps(stats))
