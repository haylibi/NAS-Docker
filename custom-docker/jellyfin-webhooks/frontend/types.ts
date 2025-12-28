export interface LogEntry {
    time: string;
    level: string;
    msg: string;
}

export interface RequestLogEntry {
    timestamp: string;
    date_iso: string;
    method: string;
    url: string;
    headers: Record<string, string>;
    remote_addr?: string;
    body?: any;
    duration_ms: number;
    response?: {
        status: number;
        body: any;
    };
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

export interface EndpointLog {
    id: string;
    category: string;
    name: string;
    endpoint: string;
}