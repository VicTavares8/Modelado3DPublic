import bpy
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out = Path(__file__).resolve().parents[1] / 'output' / 'skull_cave_v01'
bpy.ops.wm.open_mainfile(filepath=str(out/'skull_cave_v01.blend'))
obj=bpy.data.objects['Skull_Cave_Rock_Shell']
depsgraph=bpy.context.evaluated_depsgraph_get()
bvh=BVHTree.FromObject(obj,depsgraph)
results={}
for name, origin, direction, limit in [
    ('no_floor', (0,0,2), (0,0,-1), 5),
    ('mouth_passage', (0,-8,1.5), (0,1,0), 8),
    ('left_eye_open', (-2.55,-8,5.4), (0,1,0), 8),
    ('right_eye_open', (2.55,-8,5.4), (0,1,0), 8),
    ('nose_open', (0,-8,4.6), (0,1,0), 8)]:
    hit=bvh.ray_cast(Vector(origin),Vector(direction),limit)
    assert hit[0] is None, (name,hit)
    results[name]='passed'
for name,direction in [('roof',(0,0,1)),('back_wall',(0,1,0)),('side_wall',(1,0,0))]:
    hit=bvh.ray_cast(Vector((0,0,2)),Vector(direction),20)
    assert hit[0] is not None, name
    results[name]='passed'
(out/'cavity_checks.json').write_text(json.dumps(results,indent=2)+'\n')
print('CAVITY_CHECKS',json.dumps(results))
