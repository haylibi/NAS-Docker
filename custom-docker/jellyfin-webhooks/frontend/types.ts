export interface LogEntry {
    time: string;
    level: string;
    msg: string;
}

export interface WebhookConfig {
    id: string;
    name: string;
    description: string;
    enabled: boolean;
    endpoint: string;
}

export interface ApiResponse {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    data: any[];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    metadata?: any;
}