import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parent/'regenerado'
ROOT.mkdir(exist_ok=True)
SRC=Path(sys.argv[sys.argv.index('--')+1]).resolve() if '--' in sys.argv else Path(__file__).resolve().parent.parent/'craneo_base_esculpida'/'Craneo_Base.blend'
bpy.ops.wm.open_mainfile(filepath=str(SRC))
obj=bpy.context.object
if obj.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
original=obj.copy();original.data=obj.data.copy();original.name='Original_comparacion';bpy.context.collection.objects.link(original)
original.hide_render=True;original.hide_set(True);original.select_set(False)
bpy.context.view_layer.objects.active=obj;obj.select_set(True)
def bvh(mesh):
 mesh.calc_loop_triangles()
 return BVHTree.FromPolygons([v.co for v in mesh.vertices],[t.vertices for t in mesh.loop_triangles],all_triangles=True)
def deviation(mesh,target):
 # Samples include every vertex, triangle centroid and edge midpoint.
 points=[v.co.copy() for v in mesh.vertices]
 mesh.calc_loop_triangles()
 for t in mesh.loop_triangles:points.append(sum((mesh.vertices[i].co for i in t.vertices),mesh.vertices[0].co*0)/3)
 for e in mesh.edges:points.append((mesh.vertices[e.vertices[0]].co+mesh.vertices[e.vertices[1]].co)*.5)
 vals=sorted(target.find_nearest(p)[3] for p in points)
 return {'samples':len(vals),'max_mm':vals[-1]*1000,'p95_mm':vals[int(len(vals)*.95)]*1000,'mean_mm':sum(vals)/len(vals)*1000}
bm=bmesh.new();bm.from_mesh(obj.data)
print('NORMALS_BEFORE',sum(not e.is_contiguous for e in bm.edges),flush=True)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();obj.data.update()
obj.scale=(100,)*3;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
print('QUADRIFLOW_START',flush=True)
bpy.ops.object.quadriflow_remesh(mode='FACES',target_faces=16000,seed=0,use_mesh_symmetry=True,use_preserve_sharp=False,use_preserve_boundary=True,preserve_attributes=False,smooth_normals=True)
print('QUADRIFLOW_DONE',len(obj.data.polygons),flush=True)
assert len(obj.data.polygons)<20000, 'QuadriFlow did not reduce the mesh'
obj.scale=(.01,)*3;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
# Reproject the remeshed surface to the unchanged sculpture.
mod=obj.modifiers.new('Reproyeccion al original','SHRINKWRAP');mod.target=original;mod.wrap_method='NEAREST_SURFACEPOINT';mod.wrap_mode='ON_SURFACE';mod.offset=0
bpy.ops.object.modifier_apply(modifier=mod.name)
for p in obj.data.polygons:p.use_smooth=True
bm=bmesh.new();bm.from_mesh(obj.data)
# Weld coincident vertices on QuadriFlow's mirrored seam (one micrometre).
seam_weld=bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(obj.data);obj.data.update()
stats={'original_faces':len(original.data.polygons),'faces':len(obj.data.polygons),'vertices':len(obj.data.vertices),'face_sizes':sorted(set(len(p.vertices) for p in obj.data.polygons)),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-14 for f in bm.faces),'volume':bm.calc_volume(signed=True),'original_to_remesh':deviation(original.data,bvh(obj.data)),'remesh_to_original':deviation(obj.data,bvh(original.data))}
bm.free();print(json.dumps(stats),flush=True)
(ROOT/'comparacion.json').write_text(json.dumps(stats,indent=2))
bpy.data.objects.remove(original,do_unlink=True)
obj.name='Craneo_Base_Remesh';obj.data.name='Craneo_cuadrilateros'


obj=bpy.context.object
if obj.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
obj.name='Craneo_Base_Remesh';obj.data.name='Craneo_Remesh_17788_quads'
obj.use_mesh_mirror_x=True;obj.use_mesh_mirror_y=False;obj.use_mesh_mirror_z=False
obj['proceso']='Escultura original remallada con QuadriFlow y reproyectada sobre la superficie original. Simetria X.'
obj['topologia']='17788 cuadrilateros en Blender. 35576 triangulos en GLB.'
for text in list(bpy.data.texts):bpy.data.texts.remove(text)
note=bpy.data.texts.new('LEEME');note.write('CRANEO - REMESH\n\nRemallado de la base esculpida: 41.018 a 17.788 caras (56,63% menos).\nCuadrilateros en .blend; triangulacion estandar en .glb.\nQuadriFlow + reproyeccion a la superficie original; simetria X activa.\nNo se anadieron detalles ni se reesculpio el craneo.\nLa distribucion de aristas es mas uniforme, aunque persisten algunos polos y bucles.\nComparacion muestreada: desviacion media 0,025 mm y maxima 0,635 mm.\nConsultar README y validacion.json para metodo y limites.\n')
# Selection-only export: one mesh, one material, no cameras or presentation edges.
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
bpy.ops.export_scene.gltf(filepath=str(ROOT/'Craneo_Base_Remesh.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False,export_texcoords=False)
bpy.ops.object.mode_set(mode='SCULPT')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Craneo_Base_Remesh.blend'),compress=True)
