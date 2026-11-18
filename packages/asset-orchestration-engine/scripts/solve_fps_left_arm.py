import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r'E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx')
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
for o in [o for o in bpy.data.objects if o.type == 'MESH']: bpy.data.objects.remove(o)
for pb in arm.pose.bones: pb.rotation_mode = 'XYZ'

# SMG foregrip target in SK_FPS_Arms space
# In rest, weapon bone is at (0.0980, -0.2260, -0.0880)
# SMG attached to weapon with loc=(0.01, 0.08, 0.0):
# Foregrip is at: (0.0880, -0.5633, -0.1100)
# But note: hand_L origin is the WRIST.
# The fingers extend to tail which is at (0, length, 0).
# The palm/fingers hold the grip around (0.088, -0.50, -0.12)
tg = Vector((0.04, -0.44, -0.14))

pb_u = arm.pose.bones['upperarm_L']
pb_f = arm.pose.bones['forearm_L']
pb_h = arm.pose.bones['hand_L']

def nelder_mead(func, x0, step=5.0, max_iter=300, tol=1e-5):
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

def cost(x):
    pb_u.rotation_euler = (math.radians(x[0]), math.radians(x[1]), math.radians(x[2]))
    pb_f.rotation_euler = (math.radians(x[3]), math.radians(x[4]), math.radians(x[5]))
    bpy.context.view_layer.update()
    pos = (arm.matrix_world @ pb_h.matrix).to_translation()
    return (pos - tg).length

sol, loss = nelder_mead(cost, [-35, 0, 35, -45, 0, 35], step=10.0, max_iter=400)
cost(sol)
pos = (arm.matrix_world @ pb_h.matrix).to_translation()
print(f'Solved FPS Left Arm: dist={loss*100:.2f}cm, hand_L={pos}')
print(f'Angles upperarm_L: {[round(a, 1) for a in sol[:3]]}, forearm_L: {[round(a, 1) for a in sol[3:]]}')
