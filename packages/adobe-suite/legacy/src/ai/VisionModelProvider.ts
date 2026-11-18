export interface VLMResponse {
    isValid: boolean;
    feedback: string;
}

export interface SpatialVLMResponse {
    found: boolean;
    x?: number;
    y?: number;
    width?: number;
    height?: number;
    feedback: string;
}

export interface IVisionModelProvider {
    inspectImage(filePath: string, criteria: string): Promise<VLMResponse>;
    inspectImageSpatial(filePath: string, element: string): Promise<SpatialVLMResponse>;
}

export class MockVisionModelProvider implements IVisionModelProvider {
    public async inspectImage(filePath: string, criteria: string): Promise<VLMResponse> {
        // In a real scenario, this would encode the file to base64 and call GPT-4V/Claude 3.5 Sonnet
        console.log(`[VLM] Inspecting physical file: ${filePath}`);
        console.log(`[VLM] Against criteria: "${criteria}"`);

        // Mocking a successful validation for tests
        return {
            isValid: true,
            feedback: "The image perfectly matches the criteria."
        };
    }

    public async inspectImageSpatial(filePath: string, element: string): Promise<SpatialVLMResponse> {
        console.log(`[VLM Spatial] Locating '${element}' in file: ${filePath}`);

        // Mocking a spatial coordinate response
        if (element.toLowerCase().includes('error') || element.toLowerCase().includes('misaligned')) {
            return {
                found: true,
                x: 100,
                y: 200,
                width: 50,
                height: 50,
                feedback: "Element found but needs adjustment."
            };
        }

        // Default perfectly aligned response (0,0 offset needed)
        return {
            found: true,
            x: 0,
            y: 0,
            feedback: "Element is aligned."
        };
    }
}
