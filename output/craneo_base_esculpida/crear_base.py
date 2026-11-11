"""Base inicial: una esfera y pinceladas nativas de Sculpt Mode (Blender 4.3)."""
import bpy, math, json, os
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
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
    rv.view_distance=5;rv.view_location=(0,0,-.18);rv.view_perspective='ORTHO'
    brushes={}
    for kind in ['GRAB','DRAW','SMOOTH','FLATTEN','CLAY_STRIPS','CREASE']:
        b=bpy.data.brushes.new('Base / '+kind,mode='SCULPT'); b.sculpt_tool=kind; b.strength=1 if kind=='GRAB' else .18;brushes[kind]=b
    def stroke(kind,view,start,end,radius,strength=1,steps=7,invert=False):
        # Genuine Blender sculpt stroke, screen projection + object-space contact.
        rv.view_rotation=Quaternion((1,0,0),math.pi/2) if view=='front' else Quaternion((.5,.5,.5,.5))
        rv.update()
        b=brushes[kind];sculpt.brush=b;b.strength=strength
        if kind!='GRAB': b.stroke_method='DOTS'
        b.use_frontface=kind not in {'GRAB','SMOOTH'}
        p=location_3d_to_region_2d(region,rv,Vector(start));q=location_3d_to_region_2d(region,rv,Vector(end))
        px=location_3d_to_region_2d(region,rv,Vector(start)+rv.view_rotation@Vector((radius,0,0)))
        size=round((px-p).length);b.size=size
        # Unified settings otherwise override brush radius.
        bpy.context.tool_settings.unified_paint_settings.use_unified_size=False
        bpy.context.tool_settings.unified_paint_settings.use_unified_strength=False
        before=[v.co.copy() for v in obj.data.vertices]
        bvh=BVHTree.FromPolygons([v.co for v in obj.data.vertices],[p.vertices for p in obj.data.polygons])
        def hit_at(loc):
            origin=Vector((loc.x,-5,loc.z)) if view=='front' else Vector((5,loc.y,loc.z))
            direction=Vector((0,1,0)) if view=='front' else Vector((-1,0,0))
            hit=bvh.ray_cast(origin,direction)[0]
            return hit if hit is not None else loc
        anchor=hit_at(Vector(start)); offset=anchor-Vector(start)
        path=[]
        for i in range(steps):
            f=i/(steps-1);m=p.lerp(q,f);loc=Vector(start).lerp(Vector(end),f)
            loc=loc+offset if kind=='GRAB' else hit_at(loc)
            path.append(dict(name='',location=loc,mouse=m,mouse_event=m,pressure=1,size=size,pen_flip=False,x_tilt=0,y_tilt=0,time=i*.08,is_start=i==0))
        with bpy.context.temp_override(area=area,region=region):
            result=bpy.ops.sculpt.brush_stroke(stroke=path,mode='INVERT' if invert else 'NORMAL')
        delta=max((v.co-v0).length for v,v0 in zip(obj.data.vertices,before))
        LOG.append(dict(brush=kind,view=view,start=start,end=end,radius=radius,max_displacement=delta,invert=invert))
        print('STROKE',len(LOG),kind,round(delta,5),flush=True)
    # Proporciones: bóveda amplia, cara más larga y estrecha, base posterior elevada.
    # Bóveda redondeada de la esfera inicial; evitar una frente alargada.
    stroke('GRAB','side',(.35,-.63,-.73),(.35,-.83,-1.40),1.05)
    stroke('GRAB','front',(.72,-.4,-.65),(.57,-.4,-.65),.78)
    stroke('GRAB','front',(.32,-.3,-1.30),(.52,-.3,-1.27),.55)
    stroke('GRAB','front',(0,-.3,-1.52),(0,-.3,-1.43),.4)
    stroke('GRAB','side',(.35,.64,-.63),(.35,.63,-.34),.85)
    stroke('GRAB','side',(.5,.65,.35),(.5,.85,.35),1.0)
    stroke('GRAB','side',(.4,-.84,.45),(.4,-.99,.45),.8)
    stroke('GRAB','front',(.7,-.5,-.38),(.86,-.5,-.38),.38)
    stroke('SMOOTH','front',(.4,-.8,-.5),(.35,-.6,-1.2),.6,.6,15)
    stroke('GRAB','side',(.45,.05,-.94),(.45,.12,-1.22),.56)
    stroke('GRAB','side',(.45,-.30,-1.01),(.45,-.30,-1.18),.50)
    # Redistribuir arcilla estirada: remallado voxel propio del flujo de escultura.
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.data.remesh_voxel_size=.028
    bpy.ops.object.voxel_remesh()
    for face in obj.data.polygons:face.use_smooth=True
    bpy.ops.object.mode_set(mode='SCULPT')
    # Órbitas amplias y sencillas, talladas con Draw invertido.
    stroke('DRAW','front',(.35,-.9,.00),(.53,-.9,-.04),.29,.48,16,True)
    stroke('DRAW','front',(.39,-.8,-.04),(.51,-.8,-.05),.27,.35,10,True)
    stroke('SMOOTH','front',(.4,-.8,-.0),(.46,-.8,-.07),.34,.25,5)
    # Cavidad nasal simple, aún sin tabiques ni borde fino.
    stroke('DRAW','front',(0,-.92,-.30),(0,-.9,-.52),.115,.48,12,True)
    stroke('DRAW','front',(.01,-.9,-.43),(.075,-.9,-.60),.125,.35,10,True)
    # Pómulos y arco supraorbitario, bloques sin detalle.
    stroke('DRAW','front',(.69,-.72,-.31),(.72,-.68,-.39),.28,.18,6)
    stroke('DRAW','front',(.25,-.9,.28),(.66,-.77,.23),.16,.15,9)
    # Depresión temporal y hueco bajo el pómulo, simplificados.
    stroke('DRAW','side',(.85,-.12,.18),(.9,.22,.25),.60,.045,7,True)
    stroke('DRAW','side',(.75,-.25,-.57),(.7,-.18,-.79),.34,.17,9,True)
    # Franja oral continua y mandíbula: nada de dientes individuales.
    stroke('DRAW','front',(0,-.8,-1.02),(.45,-.72,-.98),.12,.38,12,True)
    stroke('DRAW','front',(.1,-.82,-1.31),(.3,-.76,-1.29),.27,.15,6)
    stroke('SMOOTH','front',(.48,-.75,-.65),(.4,-.7,-.86),.3,.3,7)
    # Remallado final para evitar pliegues internos en las cavidades.
    bpy.ops.object.mode_set(mode='OBJECT');obj.data.remesh_voxel_size=.024
    bpy.ops.object.voxel_remesh()
    for face in obj.data.polygons:face.use_smooth=True
    bpy.ops.object.mode_set(mode='SCULPT')
    stroke('SMOOTH','front',(.36,-.6,.0),(.5,-.6,-.08),.34,.55,12)
    stroke('SMOOTH','side',(.7,-.22,-.6),(.65,-.10,-.8),.4,.4,8)
    stroke('SMOOTH','side',(.55,-.5,-1.08),(.55,-.05,-1.03),.5,.55,12)
    # Corrección amplia de anchura con Grab y simetrización de escultura.
    stroke('GRAB','front',(.85,-.4,.15),(.62,-.4,.15),1.8)
    bpy.context.tool_settings.sculpt.symmetrize_direction='NEGATIVE_X'
    with bpy.context.temp_override(area=area,region=region):
        bpy.ops.sculpt.symmetrize(merge_tolerance=.0001)
    # Material and saved sculpt workspace.
    mat=bpy.data.materials.new('Arcilla gris');mat.diffuse_color=(.48,.45,.41,1);mat.use_nodes=True
    shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=mat.diffuse_color;shader.inputs['Roughness'].default_value=.85
    obj.data.materials.append(mat)
    obj['proceso']='Esfera inicial, pinceladas nativas Grab, Draw invertido y Smooth, remallado voxel. Simetría X.'
    obj['alcance']='Base humana inicial: órbitas, nariz, pómulos y mandíbula sugeridos. Sin dientes ni detalle fino.'
    bpy.ops.object.mode_set(mode='OBJECT')
    # No modifiers, booleans, extrusions, direct vertex edits or assembled volumes.
    scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1000;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO';scene.display.shading.studio_light='paint.sl';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='BOTH';scene.display.shading.curvature_ridge_factor=1.2;scene.display.shading.curvature_valley_factor=1.0;scene.display.shading.background_type='WORLD';scene.world.color=(.065,.065,.065)
    bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Vista previa';scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=3.6
    for name,pos in [('tres_cuartos',(3.4,-6,1.3)),('frente',(0,-6,0)),('perfil',(6,0,0))]:
        cam.location=pos;cam.rotation_euler=(Vector((0,0,-.18))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=ROOT+'/'+name+'.png';bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam,do_unlink=True);scene.camera=None
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    # Escala de intercambio: 22 cm de altura; ajuste uniforme, sin alterar proporciones.
    factor=.22/obj.dimensions.z;obj.scale=(factor,)*3
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1.0
    bpy.ops.object.mode_set(mode='SCULPT');sculpt.brush=brushes['GRAB'];brushes['GRAB'].size=100
    rv.view_rotation=Quaternion((.88,.4,.1,.22)).normalized();rv.view_distance=4.7*factor;rv.view_location=(0,0,-.18*factor)
    space.overlay.show_floor=False;space.overlay.show_axis_x=False;space.overlay.show_axis_y=False;space.shading.color_type='MATERIAL'
    text=bpy.data.texts.new('LEEME');text.write('BASE INICIAL DE CRÁNEO\n\nUna sola esfera esculpida con pinceles nativos de Blender, automatizados mediante Python.\nSimetría X activa. No es una escultura manual de una persona.\nBase humana inicial: órbitas y nariz sencillas, pómulos y mandíbula. Sin dientes ni suturas.\nPasadas amplias y transiciones poco refinadas, como un ejercicio inicial.\n')
    bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/Craneo_Base.blend',compress=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.export_scene.gltf(filepath=ROOT+'/Craneo_Base.glb',export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_cameras=False,export_lights=False,export_texcoords=False)
    with open(ROOT+'/pinceladas.json','w') as f:json.dump(LOG,f,indent=2)
    bpy.ops.wm.quit_blender()
bpy.app.timers.register(run,first_interval=2)
