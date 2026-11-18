import { Intent } from '../../core/abstractions.js';

export class RiggingAgent {
    public async handleRiggingTask(prompt: string): Promise<Intent> {
        console.log(`[RiggingAgent] Planning rigging/orchestration for: "${prompt}"`);

        return {
            id: `intent_rig_${Date.now()}`,
            type: 'ae.comp.create',
            parameters: {
                composition_name: prompt
            }
        };
    }

    public generateCorrectionScript(xOffset: number, yOffset: number, targetLayerName: string = "TargetLayer"): string {
        console.log(`[RiggingAgent] Generating dynamic JSX to correct ${targetLayerName} by x:${xOffset}, y:${yOffset}`);

        return `
        app.beginUndoGroup("Swarm Correction");
        try {
            var comp = app.project.activeItem;
            if (comp && comp instanceof CompItem) {
                var layer = comp.layer("${targetLayerName}");
                if (layer) {
                    var currentPos = layer.property("Position").value;
                    layer.property("Position").setValue([currentPos[0] + (${xOffset}), currentPos[1] + (${yOffset})]);
                    $.writeln(JSON.stringify({ success: true, new_x: currentPos[0] + (${xOffset}), new_y: currentPos[1] + (${yOffset}) }));
                } else {
                    $.writeln(JSON.stringify({ success: false, error: "Layer not found" }));
                }
            } else {
                $.writeln(JSON.stringify({ success: false, error: "No active comp" }));
            }
        } catch(e) {
            $.writeln(JSON.stringify({ success: false, error: e.toString() }));
        }
        app.endUndoGroup();
        `;
    }
}
