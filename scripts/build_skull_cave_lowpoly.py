"""Build v02: a coarse quad shell from the reviewed v01 model, using QuadriFlow."""
import bpy
import bmesh
import json
import math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'skull_cave_v02'
OUT.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/skull_cave_v01/skull_cave_v01.blend'))
scene = bpy.context.scene
obj = bpy.data.objects['Skull_Cave_Rock_Shell']
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
original_triangles = sum(len(p.vertices)-2 for p in obj.data.polygons)

# Remeshing follows the exterior, interior and connected rims of the same shell.
# No modifiers with render-time subdivision are added.
print('QUADRIFLOW_START', flush=True)
bpy.ops.object.quadriflow_remesh(
    mode='FACES', target_faces=1200, seed=0,
    use_mesh_symmetry=False, use_preserve_sharp=False,
    use_preserve_boundary=True, preserve_attributes=False,
    smooth_normals=False)
print('QUADRIFLOW_END', len(obj.data.polygons), flush=True)
obj.name = 'Skull_Cave_v02_Quad_Shell'
obj.data.name = 'Skull_Cave_v02_Quad_Mesh'

# Restore the agreed envelope after remeshing slightly rounds the extremes.
mins=Vector(tuple(min(v.co[i] for v in obj.data.vertices) for i in range(3)))
maxs=Vector(tuple(max(v.co[i] for v in obj.data.vertices) for i in range(3)))
size=maxs-mins
for v in obj.data.vertices:
    v.co.x=(v.co.x-(mins.x+maxs.x)/2)*12/size.x
    v.co.y=(v.co.y-(mins.y+maxs.y)/2)*10/size.y
    v.co.z=(v.co.z-mins.z)*8/size.z
obj.data.update()
bpy.context.view_layer.update()

mat=bpy.data.materials.new('v02 — matte stone')
mat.use_nodes=True
mat.diffuse_color=(0.38,0.355,0.29,1)
shader=mat.node_tree.nodes.get('Principled BSDF')
shader.inputs['Base Color'].default_value=mat.diffuse_color
shader.inputs['Roughness'].default_value=0.95
obj.data.materials.clear()
obj.data.materials.append(mat)
for face in obj.data.polygons:
    face.material_index=0
    face.use_smooth=False

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=0.025)
bpy.ops.object.mode_set(mode='OBJECT')

# Topology and passage checks operate on the actual delivery mesh.
bm=bmesh.new()
bm.from_mesh(obj.data)
bad_edges=sum(not e.is_manifold for e in bm.edges)
degenerate=sum(f.calc_area()<1e-9 for f in bm.faces)
components=0
remaining=set(bm.verts)
while remaining:
    components+=1
    stack=[remaining.pop()]
    while stack:
        v=stack.pop()
        for e in v.link_edges:
            other=e.other_vert(v)
            if other in remaining:
                remaining.remove(other)
                stack.append(other)
bm.free()
assert bad_edges==0, bad_edges
assert degenerate==0, degenerate
assert components==1, components
face_counts={str(n):sum(len(p.vertices)==n for p in obj.data.polygons)
             for n in sorted(set(len(p.vertices) for p in obj.data.polygons))}
assert len(obj.data.polygons)<1800
assert face_counts.get('4',0)/len(obj.data.polygons)>0.9
assert not obj.modifiers
bvh=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
passages={}
for name,origin,direction,distance in [
    ('no_floor',(0,0,2),(0,0,-1),5),
    ('mouth_open',(0,-8,1.5),(0,1,0),8),
    ('left_eye_open',(-2.55,-8,5.4),(0,1,0),8),
    ('right_eye_open',(2.55,-8,5.4),(0,1,0),8),
    ('nose_open',(0,-8,4.6),(0,1,0),8)]:
    hit=bvh.ray_cast(Vector(origin),Vector(direction),distance)
    assert hit[0] is None,(name,hit)
    passages[name]='passed'
for name,direction in [('roof',(0,0,1)),('back_wall',(0,1,0)),('side_wall',(1,0,0))]:
    assert bvh.ray_cast(Vector((0,0,2)),Vector(direction),20)[0] is not None,name
    passages[name]='passed'
triangles=sum(len(p.vertices)-2 for p in obj.data.polygons)
stats={'blender':bpy.app.version_string,'vertices':len(obj.data.vertices),
       'faces':len(obj.data.polygons),'face_counts_by_sides':face_counts,
       'triangles_equivalent':triangles,'v01_triangles':original_triangles,
       'triangle_reduction_percent':round(100*(1-triangles/original_triangles),2),
       'nonmanifold_edges':bad_edges,'degenerate_faces':degenerate,
       'connected_components':components,'dimensions_m':list(obj.dimensions),
       'render_modifiers':0,'cavity_checks':passages}
obj['description']='v02 coarse quad shell; hollow, no floor; flat shading and one stone material.'
obj['material_note']='One plain rough material. No detailed textures or displacement.'
obj['topology_note']='Quads in BLEND; standard glTF triangulation in GLB.'
obj['generation']='QuadriFlow target 1200 faces, seed 0, from v01.'

scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.camera=bpy.data.objects['Front three-quarter']
scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'skull_cave_v02.blend'))
bpy.ops.export_scene.gltf(filepath=str(OUT/'skull_cave_v02.glb'),export_format='GLB',
                         use_selection=True,export_yup=True,export_apply=True)
for name,filename in [('Front three-quarter','01_exterior'),('Front','02_front'),
                     ('Interior looking toward entrance','03_interior')]:
    scene.camera=bpy.data.objects[name]
    scene.render.filepath=str(OUT/(filename+'.png'))
    bpy.ops.render.render(write_still=True)

# Render actual polygon edges (not triangulation), solely as a review overlay.
wire=obj.copy()
wire.data=obj.data.copy()
wire.name='Preview only — quad edges'
scene.collection.objects.link(wire)
ink=bpy.data.materials.new('Preview edge ink')
ink.use_nodes=True
ink.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.012,0.02,0.025,1)
ink.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=1
wire.data.materials.clear()
wire.data.materials.append(ink)
mod=wire.modifiers.new('Actual quad edges','WIREFRAME')
mod.thickness=0.015
mod.offset=1
mod.use_replace=True
scene.camera=bpy.data.objects['Front three-quarter']
scene.render.filepath=str(OUT/'04_quad_topology.png')
bpy.ops.render.render(write_still=True)
bpy.data.objects.remove(wire,do_unlink=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(OUT/'skull_cave_v02.glb'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
assert len(meshes)==1
result=meshes[0]
assert all(abs(a-b)<0.01 for a,b in zip(sorted(result.dimensions),[8,10,12]))
assert len(result.data.polygons)==triangles
assert len(result.data.materials)==1
stats['glb_roundtrip']='passed: one mesh, one material, dimensions and triangle count'
stats['glb_bytes']=(OUT/'skull_cave_v02.glb').stat().st_size
(OUT/'validation.json').write_text(json.dumps(stats,indent=2)+'\n')
print('LOWPOLY_COMPLETE',json.dumps(stats),flush=True)
