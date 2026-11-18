import express, { Express, Request, Response } from 'express';
import cors from 'cors';

export interface CEPCommand {
    id: string;
    command: string;
    payload: any;
}

export class AdobeCEPAdapter {
    private app: Express;
    private server: any;
    private isListening: boolean = false;
    private port: number = 3001;

    // Commands waiting to be picked up by the CEP polling mechanism
    private pendingCommands: CEPCommand[] = [];

    // Maps command ID to its Promise resolver
    private responsePromises: Map<string, { resolve: (val: any) => void, reject: (err: any) => void }> = new Map();

    constructor() {
        this.app = express();
        this.app.use(cors({ origin: 'http://localhost:3001' }));
        this.app.use(express.json());

        // Endpoint for CEP extension to poll pending commands
        this.app.get('/api/commands', (req: Request, res: Response) => {
            const commands = [...this.pendingCommands];
            this.pendingCommands = []; // Clear queue once fetched
            res.json(commands);
        });

        // Endpoint for CEP extension to post results back
        this.app.post('/api/results', (req: Request, res: Response) => {
            const { id, success, data, error } = req.body;

            if (this.responsePromises.has(id)) {
                const { resolve, reject } = this.responsePromises.get(id)!;
                if (success) {
                    resolve(data);
                } else {
                    reject(new Error(error || 'CEP Command execution failed'));
                }
                this.responsePromises.delete(id);
            }
            res.sendStatus(200);
        });
    }

    public async startServer(): Promise<void> {
        if (this.isListening) return;
        return new Promise((resolve) => {
            this.server = this.app.listen(this.port, '127.0.0.1', () => {
                console.log(`[AdobeCEPAdapter] Server listening on port ${this.port}`);
                this.isListening = true;
                resolve();
            });
            this.server.on('error', (e: any) => {
                if (e.code === 'EADDRINUSE') {
                    console.log(`[AdobeCEPAdapter] Port ${this.port} is already in use. Assuming server is running.`);
                    this.isListening = true;
                    resolve();
                }
            });
        });
    }

    public async stopServer(): Promise<void> {
        if (!this.isListening || !this.server) return;
        return new Promise((resolve) => {
            this.server.close(() => {
                console.log('[AdobeCEPAdapter] Server stopped.');
                this.isListening = false;
                resolve();
            });
        });
    }

    public isExtensionConnected(): boolean {
        // In a real WebSocket implementation, we'd check active connections.
        // For polling, we might track the last time '/api/commands' was hit.
        // Currently stubbed to false so the provider falls back to macros natively unless overridden in tests.
        return process.env.CEP_MOCK_CONNECTED === 'true';
    }

    public async sendCommand(command: string, payload: any, timeoutMs: number = 30000): Promise<any> {
        if (!this.isExtensionConnected()) {
            throw new Error("CEP Extension is not connected.");
        }

        const commandId = `cmd_${Date.now()}_${Math.floor(Math.random() * 1000)}`;

        const cmd: CEPCommand = {
            id: commandId,
            command,
            payload
        };

        this.pendingCommands.push(cmd);

        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                if (this.responsePromises.has(commandId)) {
                    this.responsePromises.delete(commandId);
                    reject(new Error(`Command ${commandId} timed out after ${timeoutMs}ms`));
                }
            }, timeoutMs);

            this.responsePromises.set(commandId, {
                resolve: (val) => {
                    clearTimeout(timeout);
                    resolve(val);
                },
                reject: (err) => {
                    clearTimeout(timeout);
                    reject(err);
                }
            });
        });
    }
}
