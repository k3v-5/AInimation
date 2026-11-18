import bpy, math
from mathutils import Vector, Euler, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

bpy.ops.import_scene.fbx(filepath=r'E:\Darx_Proyect\Art\FBX\SK_Player.fbx')
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.name = 'ARM_Player'
for pb in arm.pose.bones: pb.rotation_mode = 'XYZ'

# Torso bladed stance
arm.pose.bones['spine'].rotation_euler = (math.radians(-4), math.radians(12), 0)
arm.pose.bones['chest'].rotation_euler = (math.radians(-2), math.radians(10), 0)
arm.pose.bones['head'].rotation_euler  = (math.radians(2),  math.radians(-20), 0)
arm.pose.bones['clavicle_L'].rotation_euler = (0, 0, math.radians(-16)) # left shoulder extended forward
arm.pose.bones['clavicle_R'].rotation_euler = (0, 0, math.radians(-4))

# Legs
arm.pose.bones['thigh_R'].rotation_euler = (math.radians(14), 0, math.radians(-4))
arm.pose.bones['calf_R'].rotation_euler  = (math.radians(-12), 0, 0)
arm.pose.bones['thigh_L'].rotation_euler = (math.radians(-14), 0, math.radians(6))
arm.pose.bones['calf_L'].rotation_euler  = (math.radians(8), 0, 0)

bpy.context.view_layer.update()

# Load SMG
with bpy.data.libraries.load(r'E:\Darx_Proyect\Art\Blender\SM_Wep_PhaseSMG_Workspace.blend', link=False) as (df, dt):
    dt.objects = [n for n in df.objects if n not in ('StudioTable', 'Cam', 'KeyLight', 'FillLight', 'RimLight', 'Light_ReactorSMG')]
for o in dt.objects: scene.collection.objects.link(o)
bpy.ops.object.select_all(action='DESELECT')
for o in dt.objects: o.select_set(True)
bpy.context.view_layer.objects.active = dt.objects[0]
bpy.ops.object.join()
smg = bpy.context.active_object
smg.name = 'SMG'

# Weapon orientation:
# Stock at right shoulder (X=0.18, Y=-0.10, Z=1.38)
# Angled 6 deg inward toward X=0.08, pitched down 3 deg
smg.rotation_euler = (math.radians(-3), math.radians(-2), math.radians(174))
# Position SMG so Stock_Buttpad local (0, -0.282, 0.065) is at (0.18, -0.10, 1.38)
# With rot_z ~ 174 deg:
smg.location = (0.16, -0.37, 1.33)
bpy.context.view_layer.update()

rgrip_world = smg.matrix_world @ Vector((0, -0.0465, -0.0225))
fgrip_world = smg.matrix_world @ Vector((0, 0.2318, -0.0220))
butt_world  = smg.matrix_world @ Vector((0, -0.282, 0.065))
muzzle_world = smg.matrix_world @ Vector((0, 0.565, 0.085))

print('Stock Butt world:', butt_world)
print('Rear grip world:', rgrip_world)
print('Foregrip world:', fgrip_world)
print('Muzzle world:', muzzle_world)

# Nelder-Mead optimizer
def nelder_mead(func, x0, step=5.0, max_iter=250, tol=1e-5):
    n = len(x0)
    sim = [list(x0)]
    for i in range(n):
        y = list(x0); y[i] += step; sim.append(y)
    f_sim = [func(x) for x in sim]
    for _ in range(max_iter):
        order = sorted(range(n + 1), key=lambda idx: f_sim[idx])
        sim = [sim[i] for i in order]
        f_sim = [f_sim[i] for i in order]
        if f_sim[-1] - f_sim[0] < tol: break
        x_bar = [sum(sim[i][j] for i in range(n))/n for j in range(n)]
        xr = [2*x_bar[j] - sim[-1][j] for j in range(n)]
        fxr = func(xr)
        if f_sim[0] <= fxr < f_sim[-2]: sim[-1] = xr; f_sim[-1] = fxr
        elif fxr < f_sim[0]:
            xe = [x_bar[j] + 2*(xr[j] - x_bar[j]) for j in range(n)]
            fxe = func(xe)
            if fxe < fxr: sim[-1] = xe; f_sim[-1] = fxe
            else: sim[-1] = xr; f_sim[-1] = fxr
        else:
            xc = [x_bar[j] + 0.5*(sim[-1][j] - x_bar[j]) for j in range(n)]
            fxc = func(xc)
            if fxc < f_sim[-1]: sim[-1] = xc; f_sim[-1] = fxc
            else:
                for i in range(1, n + 1):
                    sim[i] = [0.5*(sim[i][j] + sim[0][j]) for j in range(n)]
                    f_sim[i] = func(sim[i])
    return sim[0], f_sim[0]

# Optimize Right Arm
pb_ur = arm.pose.bones['upperarm_R']
pb_fr = arm.pose.bones['forearm_R']
pb_hr = arm.pose.bones['hand_R']

def cost_r(x):
    pb_ur.rotation_euler = (math.radians(x[0]), math.radians(x[1]), math.radians(x[2]))
    pb_fr.rotation_euler = (math.radians(x[3]), math.radians(x[4]), math.radians(x[5]))
    bpy.context.view_layer.update()
    pos = (arm.matrix_world @ pb_hr.matrix).to_translation()
    elbow = (arm.matrix_world @ pb_fr.matrix).to_translation()
    elbow_penalty = max(0, elbow.x - 0.32) * 2.0
    return (pos - rgrip_world).length + elbow_penalty

sol_r, loss_r = nelder_mead(cost_r, [-25, 0, 30, -50, 0, 0], step=8.0, max_iter=300)
cost_r(sol_r)
h_r = (arm.matrix_world @ pb_hr.matrix).to_translation()
print(f'Right Arm solved: dist={loss_r*100:.2f}cm, hand_pos={h_r}')
print(f'Angles upperarm_R: {[round(a, 1) for a in sol_r[:3]]}, forearm_R: {[round(a, 1) for a in sol_r[3:]]}')

# Optimize Left Arm
pb_ul = arm.pose.bones['upperarm_L']
pb_fl = arm.pose.bones['forearm_L']
pb_hl = arm.pose.bones['hand_L']

def cost_l(x):
    pb_ul.rotation_euler = (math.radians(x[0]), math.radians(x[1]), math.radians(x[2]))
    pb_fl.rotation_euler = (math.radians(x[3]), math.radians(x[4]), math.radians(x[5]))
    bpy.context.view_layer.update()
    pos = (arm.matrix_world @ pb_hl.matrix).to_translation()
    elbow = (arm.matrix_world @ pb_fl.matrix).to_translation()
    elbow_penalty = max(0, -0.32 - elbow.x) * 2.0
    return (pos - fgrip_world).length + elbow_penalty

sol_l, loss_l = nelder_mead(cost_l, [-50, 0, -40, -40, 0, 0], step=8.0, max_iter=300)
cost_l(sol_l)
h_l = (arm.matrix_world @ pb_hl.matrix).to_translation()
print(f'Left Arm solved: dist={loss_l*100:.2f}cm, hand_pos={h_l}')
print(f'Angles upperarm_L: {[round(a, 1) for a in sol_l[:3]]}, forearm_L: {[round(a, 1) for a in sol_l[3:]]}')

# Orient hands to wrap grips
# hand_R: palm wraps rear grip
pb_hr.rotation_euler = (math.radians(12), math.radians(-10), math.radians(5))
# hand_L: fingers wrap vertical foregrip
pb_hl.rotation_euler = (math.radians(-10), math.radians(15), math.radians(-15))
bpy.context.view_layer.update()

# Render test view
cam = bpy.data.cameras.new('TestCam')
cam.lens = 42
cam_obj = bpy.data.objects.new('TestCam', cam)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (1.4, -2.4, 1.35)
target = bpy.data.objects.new('CamTarget', None)
target.location = (0.05, -0.2, 1.25)
scene.collection.objects.link(target)
tt = cam_obj.constraints.new('TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

# Light
l = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN'))
l.data.energy = 3.5
l.rotation_euler = (0.8, 0.3, -0.6)
scene.collection.objects.link(l)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_path = r'C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_solved_player_smg.png'
scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print('Rendered to:', out_path)
