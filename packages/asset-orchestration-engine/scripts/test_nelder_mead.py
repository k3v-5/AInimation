import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

bpy.ops.import_scene.fbx(filepath=r'E:\Darx_Proyect\Art\FBX\SK_Player.fbx')
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.name = 'ARM_Player'
for pb in arm.pose.bones: pb.rotation_mode = 'XYZ'

# Torso bladed stance
arm.pose.bones['spine'].rotation_euler = (math.radians(-6), math.radians(14), 0)
arm.pose.bones['chest'].rotation_euler = (math.radians(-4), math.radians(12), 0)
arm.pose.bones['head'].rotation_euler  = (math.radians(4),  math.radians(-24), 0)
arm.pose.bones['thigh_R'].rotation_euler = (math.radians(14), 0, math.radians(-4))
arm.pose.bones['calf_R'].rotation_euler  = (math.radians(-12), 0, 0)
arm.pose.bones['thigh_L'].rotation_euler = (math.radians(-14), 0, math.radians(6))
arm.pose.bones['calf_L'].rotation_euler  = (math.radians(8), 0, 0)
arm.pose.bones['clavicle_L'].rotation_euler = (0, 0, math.radians(-14))
arm.pose.bones['clavicle_R'].rotation_euler = (0, 0, math.radians(-4))

bpy.context.view_layer.update()

# Target grips:
# Rear grip target: (0.17, -0.37, 1.32)
# Foregrip target: (0.17, -0.65, 1.30)
tg_r = Vector((0.17, -0.37, 1.32))
tg_l = Vector((0.17, -0.65, 1.30))

def nelder_mead(func, x0, step=5.0, max_iter=200, tol=1e-5):
    n = len(x0)
    sim = [list(x0)]
    for i in range(n):
        y = list(x0)
        y[i] += step
        sim.append(y)
    f_sim = [func(x) for x in sim]
    for _ in range(max_iter):
        order = sorted(range(n + 1), key=lambda idx: f_sim[idx])
        sim = [sim[i] for i in order]
        f_sim = [f_sim[i] for i in order]
        if f_sim[-1] - f_sim[0] < tol: break
        x_bar = [sum(sim[i][j] for i in range(n))/n for j in range(n)]
        xr = [2*x_bar[j] - sim[-1][j] for j in range(n)]
        fxr = func(xr)
        if f_sim[0] <= fxr < f_sim[-2]:
            sim[-1] = xr; f_sim[-1] = fxr
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

# Optimize Right Arm: u_rx, u_ry, u_rz, f_rx, f_ry, f_rz
pb_ur = arm.pose.bones['upperarm_R']
pb_fr = arm.pose.bones['forearm_R']
pb_hr = arm.pose.bones['hand_R']

def cost_r(x):
    pb_ur.rotation_euler = (math.radians(x[0]), math.radians(x[1]), math.radians(x[2]))
    pb_fr.rotation_euler = (math.radians(x[3]), math.radians(x[4]), math.radians(x[5]))
    bpy.context.view_layer.update()
    pos = (arm.matrix_world @ pb_hr.matrix).to_translation()
    # Also discourage flaring elbow outward
    elbow = (arm.matrix_world @ pb_fr.matrix).to_translation()
    elbow_penalty = max(0, elbow.x - 0.35) * 2.0
    return (pos - tg_r).length + elbow_penalty

sol_r, loss_r = nelder_mead(cost_r, [-30, 0, 30, -70, 0, 0], step=10.0, max_iter=250)
cost_r(sol_r)
h_r_eval = (arm.matrix_world @ pb_hr.matrix).to_translation()
print(f'Right Arm solved: dist={loss_r*100:.2f}cm, hand_pos={h_r_eval}')
print(f'Angles upperarm_R: {[round(a, 1) for a in sol_r[:3]]}, forearm_R: {[round(a, 1) for a in sol_r[3:]]}')

# Optimize Left Arm: u_rx, u_ry, u_rz, f_rx, f_ry, f_rz
pb_ul = arm.pose.bones['upperarm_L']
pb_fl = arm.pose.bones['forearm_L']
pb_hl = arm.pose.bones['hand_L']

def cost_l(x):
    pb_ul.rotation_euler = (math.radians(x[0]), math.radians(x[1]), math.radians(x[2]))
    pb_fl.rotation_euler = (math.radians(x[3]), math.radians(x[4]), math.radians(x[5]))
    bpy.context.view_layer.update()
    pos = (arm.matrix_world @ pb_hl.matrix).to_translation()
    elbow = (arm.matrix_world @ pb_fl.matrix).to_translation()
    elbow_penalty = max(0, -0.35 - elbow.x) * 2.0
    return (pos - tg_l).length + elbow_penalty

sol_l, loss_l = nelder_mead(cost_l, [-45, 0, -45, -30, 0, 0], step=10.0, max_iter=250)
cost_l(sol_l)
h_l_eval = (arm.matrix_world @ pb_hl.matrix).to_translation()
print(f'Left Arm solved: dist={loss_l*100:.2f}cm, hand_pos={h_l_eval}')
print(f'Angles upperarm_L: {[round(a, 1) for a in sol_l[:3]]}, forearm_L: {[round(a, 1) for a in sol_l[3:]]}')
