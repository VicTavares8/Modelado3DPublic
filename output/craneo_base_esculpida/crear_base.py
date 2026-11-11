"""Base inicial: una esfera y pinceladas nativas de Sculpt Mode (Blender 4.3)."""
import bpy, math, json, os
from mathutils import Vector,Quaternion
from bpy_extras.view3d_utils import location_3d_to_region_2d
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'regenerado'))
os.makedirs(ROOT,exist_ok=True)
LOG=[]
def run():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=160, ring_count=112, radius=1)
    obj=bpy.context.object; obj.name='Craneo_Base_Esculpida';obj.data.name='Arcilla_base'
    for p in obj.data.polygons:p.use_smooth=True
    bpy.ops.object.mode_set(mode='SCULPT')
    obj.use_mesh_mirror_x=True;obj.use_mesh_mirror_y=False;obj.use_mesh_mirror_z=False
    sculpt=bpy.context.tool_settings.sculpt
    area=next(a for a in bpy.context.screen.areas if a.type=='VIEW_3D'); region=next(r for r in area.regions if r.type=='WINDOW'); space=area.spaces.active;rv=space.region_3d
    rv.view_distance=5;rv.view_location=(0,0,-.1);rv.view_perspective='ORTHO'
    brushes={}
    for kind in ['GRAB','DRAW','SMOOTH','FLATTEN']:
        b=bpy.data.brushes.new('Base / '+kind,mode='SCULPT'); b.sculpt_tool=kind; b.strength=1 if kind=='GRAB' else .18;brushes[kind]=b
    def stroke(kind,view,start,end,radius,strength=1,steps=7):
        # Genuine Blender sculpt stroke, screen projection + object-space contact.
        rv.view_rotation=Quaternion((1,0,0),math.pi/2) if view=='front' else Quaternion((.5,.5,.5,.5))
        rv.update()
        b=brushes[kind];sculpt.brush=b;b.strength=strength
        p=location_3d_to_region_2d(region,rv,Vector(start));q=location_3d_to_region_2d(region,rv,Vector(end))
        px=location_3d_to_region_2d(region,rv,Vector(start)+rv.view_rotation@Vector((radius,0,0)))
        size=round((px-p).length);b.size=size
        # Unified settings otherwise override brush radius.
        bpy.context.tool_settings.unified_paint_settings.use_unified_size=False
        bpy.context.tool_settings.unified_paint_settings.use_unified_strength=False
        before=[v.co.copy() for v in obj.data.vertices]
        path=[]
        for i in range(steps):
            f=i/(steps-1);m=p.lerp(q,f);loc=Vector(start).lerp(Vector(end),f)
            path.append(dict(name='',location=loc,mouse=m,mouse_event=m,pressure=1,size=size,pen_flip=False,x_tilt=0,y_tilt=0,time=i*.08,is_start=i==0))
        with bpy.context.temp_override(area=area,region=region):
            result=bpy.ops.sculpt.brush_stroke(stroke=path)
        delta=max((v.co-v0).length for v,v0 in zip(obj.data.vertices,before))
        LOG.append(dict(brush=kind,view=view,start=start,end=end,radius=radius,max_displacement=delta))
        print('STROKE',len(LOG),kind,round(delta,5),flush=True)
    # Low-resolution artistic intent, broad grabs, bilateral X symmetry.
    stroke('GRAB','front',(0,-.2,-.97),(0,-.2,-1.32),.9)
    stroke('GRAB','front',(.77,-.43,-.48),(.57,-.43,-.48),.63)
    stroke('GRAB','front',(.57,-.42,-.92),(.48,-.42,-.92),.48)
    stroke('GRAB','side',(.42,-.43,-1.0),(.42,-.69,-1.0),.7)
    stroke('GRAB','side',(.3,.42,-.84),(.3,.24,-.69),1.0)
    stroke('GRAB','side',(.58,.64,.35),(.58,.82,.35),.85)
    stroke('GRAB','side',(.45,-.83,.38),(.45,-.92,.38),.68)
    # Suggest cheek width and a modest narrowing below, no anatomical cavities.
    stroke('GRAB','front',(.73,-.58,-.19),(.84,-.58,-.19),.42)
    stroke('GRAB','front',(.58,-.56,-.62),(.53,-.56,-.62),.3)
    # A few broad shallow clay marks left intentionally unresolved.
    stroke('DRAW','front',(.45,-.8,.53),(.53,-.75,.68),.25,.09,4)
    stroke('DRAW','front',(.28,-.81,-.73),(.35,-.77,-.83),.23,.08,4)
    stroke('FLATTEN','front',(0,-.91,.38),(.12,-.9,.44),.58,.12,4)
    # Light cleanup of pinched Grab transitions, keeping broad unevenness.
    for i in range(3):
        stroke('SMOOTH','side',(.65,.35,-.55),(.62,-.15,-.75),.85,.65,12)
    stroke('SMOOTH','front',(.45,-.7,-.5),(.35,-.6,-.95),.55,.4,10)
    # Material and saved sculpt workspace.
    mat=bpy.data.materials.new('Arcilla gris');mat.diffuse_color=(.48,.45,.41,1);obj.data.materials.append(mat)
    obj['proceso']='Esfera inicial + pinceladas nativas Grab, Draw y Flatten. Simetría X.'
    obj['alcance']='Solo silueta inicial. Sin dientes, suturas, órbitas ni detalles finos.'
    bpy.ops.object.mode_set(mode='OBJECT')
    # No modifiers, booleans, extrusions, direct vertex edits or assembled volumes.
    scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO';scene.display.shading.studio_light='paint.sl';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.2;scene.display.shading.curvature_valley_factor=1.0;scene.display.shading.background_type='WORLD';scene.world.color=(.065,.065,.065)
    bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Vista previa';scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=3.4
    for name,pos in [('tres_cuartos',(3,-6,2)),('frente',(0,-6,0)),('perfil',(6,0,0))]:
        cam.location=pos;cam.rotation_euler=(Vector((0,0,-.1))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=ROOT+'/'+name+'.png';bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam,do_unlink=True);scene.camera=None
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    bpy.ops.object.mode_set(mode='SCULPT');sculpt.brush=brushes['GRAB'];brushes['GRAB'].size=100
    rv.view_rotation=Quaternion((.88,.4,.1,.22)).normalized();rv.view_distance=4.7;rv.view_location=(0,0,-.1)
    space.overlay.show_floor=False;space.overlay.show_axis_x=False;space.overlay.show_axis_y=False;space.shading.color_type='MATERIAL'
    text=bpy.data.texts.new('LEEME');text.write('BASE INICIAL DE CRÁNEO\n\nUna sola esfera esculpida con pinceles nativos de Blender, automatizados mediante Python.\nSimetría X activa. No es una escultura manual de una persona.\nSolo volumen y silueta: sin órbitas, dientes, suturas ni detalles.\nPasadas amplias y transiciones poco refinadas, como un ejercicio inicial.\n')
    bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/Craneo_Base.blend',compress=True)
    with open(ROOT+'/pinceladas.json','w') as f:json.dump(LOG,f,indent=2)
    bpy.ops.wm.quit_blender()
bpy.app.timers.register(run,first_interval=2)
