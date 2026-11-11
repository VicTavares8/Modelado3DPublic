import bpy,bmesh,json,math,sys
from mathutils import Vector,kdtree
from pathlib import Path
ROOT=Path(sys.argv[sys.argv.index('--')+1]).resolve() if '--' in sys.argv else Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Craneo_Base.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1
obj=meshes[0];saved_mode=obj.mode
if obj.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
bm=bmesh.new();bm.from_mesh(obj.data)
remaining=set(bm.verts);components=0
while remaining:
 components+=1;stack=[remaining.pop()]
 while stack:
  v=stack.pop()
  for e in v.link_edges:
   other=e.other_vert(v)
   if other in remaining:remaining.remove(other);stack.append(other)
nonmanifold=sum(not e.is_manifold for e in bm.edges);degenerate=sum(f.calc_area()<1e-14 for f in bm.faces)
original=[obj.matrix_world@v.co for v in obj.data.vertices]
k=kdtree.KDTree(len(original))
for i,v in enumerate(original):k.insert(v,i)
k.balance();sym=max(k.find(Vector((-v.x,v.y,v.z)))[2] for v in original)
dims=list(obj.dimensions);triangles=sum(len(p.vertices)-2 for p in obj.data.polygons)
report={'blender':bpy.app.version_string,'meshes':len(meshes),'vertices':len(original),'faces':len(obj.data.polygons),'triangles':triangles,'connected_components':components,'non_manifold_edges':nonmanifold,'degenerate_faces':degenerate,'volume_m3':bm.calc_volume(signed=True),'dimensions_m':dims,'saved_mode':saved_mode,'symmetry_x':obj.use_mesh_mirror_x,'max_symmetry_error_m':sym,'modifiers':len(obj.modifiers)}
bm.free()
print(json.dumps(report,indent=2),flush=True)
assert nonmanifold==0 and degenerate==0 and components==1
assert abs(dims[2]-.22)<1e-5 and sym<.001
assert all(math.isfinite(c) for v in original for c in v)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'Craneo_Base.glb'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1
obj=meshes[0];bpy.context.view_layer.update()
actual=[obj.matrix_world@v.co for v in obj.data.vertices]
err=max(k.find(v)[2] for v in actual)
roundtrip_triangles=sum(len(p.vertices)-2 for p in obj.data.polygons)
assert err<1e-6 and roundtrip_triangles==triangles
assert all(abs(a-b)<1e-6 for a,b in zip(dims,obj.dimensions))
assert len(obj.data.materials)==1
report['glb_roundtrip']={'status':'passed','meshes':1,'triangles':roundtrip_triangles,'dimensions_m':list(obj.dimensions),'max_position_error_m':err,'materials':len(obj.data.materials),'bytes':(ROOT/'Craneo_Base.glb').stat().st_size}
(ROOT/'validacion.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
