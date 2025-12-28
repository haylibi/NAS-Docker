// frontend/App.tsx
import { useEffect, useState } from 'react';
import { LogTable } from './components/LogTable';
import { WebhooksTable } from './components/WebhooksTable';
import { DevLogTable } from './components/DevLogTable';
import { DryRunModal } from './components/DryRunModal';
import { NetworkView } from './components/NetworkView';
import { ApiResponse, LogEntry, RequestLogEntry, WebhookConfig, EndpointLog } from './types';

interface NetworkTarget {
    category: string;
    endpoint: string;
    name: string;
}

const App = () => {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [webhooks, setWebhooks] = useState<WebhookConfig[]>([]);
    const [endpoints, setEndpoints] = useState<EndpointLog[]>([]);

    // View Mode
    const [activeTab, setActiveTab] = useState<'webhooks' | 'devlogs'>('webhooks');

    // Logs Pagination & Filtering
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [minLevel, setMinLevel] = useState('INFO');

    // Modals & Action State
    const [selectedDryRunWebhook, setSelectedDryRunWebhook] = useState<WebhookConfig | null>(null);
    const [networkLogs, setNetworkLogs] = useState<RequestLogEntry[] | null>(null);

    // Generic Network View Target
    const [selectedNetworkTarget, setSelectedNetworkTarget] = useState<NetworkTarget | null>(null);

    const [networkPage, setNetworkPage] = useState(1);
    const [networkTotalPages, setNetworkTotalPages] = useState(1);
    const [networkTotalItems, setNetworkTotalItems] = useState(1);

    const fetchLogs = async (p: number, level: string) => {
        try {
            const res = await fetch(`api/logs?page=${p}&min_level=${level}`);
            const json: ApiResponse = await res.json();
            setLogs(json.data);
            setTotalPages(json.metadata.total_pages);
        } catch (err) {
            console.error("Failed to fetch logs", err);
        }
    };

    const fetchWebhooks = async () => {
        try {
            const res = await fetch(`api/webhooks`);
            const json: ApiResponse = await res.json();
            setWebhooks(json.data);
        } catch (err) {
            console.error("Failed to fetch webhooks", err);
        }
    };

    const fetchEndpoints = async () => {
        try {
            const res = await fetch(`api/requests/endpoints`);
            const json: ApiResponse = await res.json();
            setEndpoints(json.data);
        } catch (err) {
            console.error("Failed to fetch endpoints", err);
        }
    };

    const fetchRequestLogs = async (category: string, endpoint: string, p: number) => {
        try {
            const res = await fetch(`api/requests/${category}/${endpoint}?page=${p}&per_page=50`);
            const json: ApiResponse = await res.json();
            setNetworkLogs(json.data);
            setNetworkTotalPages(json.metadata?.total_pages || 1);
            setNetworkTotalItems(json.metadata.total_items || 0);
        } catch (err) {
            console.error("Failed to fetch request logs", err);
        }
    };

    // --- Action Handlers ---

    const handleDryRun = (hook: WebhookConfig) => {
        setSelectedDryRunWebhook(hook);
    };

    const handleNetworkWebhook = (hook: WebhookConfig) => {
        setSelectedNetworkTarget({
            category: 'webhook', // Current assumption for webhooks
            endpoint: hook.id,
            name: hook.name
        });
        setNetworkPage(1);
        fetchRequestLogs('webhook', hook.id, 1);
    };

    const handleNetworkEndpoint = (ep: EndpointLog) => {
        setSelectedNetworkTarget({
            category: ep.category,
            endpoint: ep.name, // The backend uses the 'name' as the filename/endpoint ID usually
            name: `${ep.category}/${ep.name}`
        });
        setNetworkPage(1);
        fetchRequestLogs(ep.category, ep.name, 1);
    };

    useEffect(() => {
        if (selectedNetworkTarget) {
            fetchRequestLogs(selectedNetworkTarget.category, selectedNetworkTarget.endpoint, networkPage);
        }
    }, [networkPage, selectedNetworkTarget]);

    useEffect(() => {
        fetchLogs(page, minLevel);
    }, [page, minLevel]);

    useEffect(() => {
        fetchWebhooks();
        fetchEndpoints();
    }, []);

    // Refresh endpoints when switching to devlogs
    useEffect(() => {
        if (activeTab === 'devlogs') {
            fetchEndpoints();
        }
    }, [activeTab]);

    return (
        <div className="min-h-screen bg-zinc-950 text-white p-8 w-full">
            <header className="mb-8 border-b border-zinc-800 pb-4">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">Jellyfin Webhooks</h1>
                <p className="text-zinc-500 mt-2">Manage your media automation integrations</p>
            </header>

            <section className="mb-12 w-full">
                <div className="flex gap-6 mb-4 border-b border-zinc-800">
                    <button
                        onClick={() => setActiveTab('webhooks')}
                        className={`pb-2 text-sm font-bold uppercase tracking-wide transition-colors ${activeTab === 'webhooks' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-zinc-500 hover:text-zinc-300'}`}
                    >
                        Configured Webhooks
                    </button>
                    <button
                        onClick={() => setActiveTab('devlogs')}
                        className={`pb-2 text-sm font-bold uppercase tracking-wide transition-colors ${activeTab === 'devlogs' ? 'text-purple-400 border-b-2 border-purple-400' : 'text-zinc-500 hover:text-zinc-300'}`}
                    >
                        Dev Logs / Admin
                    </button>
                </div>

                {activeTab === 'webhooks' ? (
                    <>
                        <h2 className="text-xl font-semibold mb-4 text-zinc-300 flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-green-500"></span>
                            Webhooks
                        </h2>
                        <WebhooksTable webhooks={webhooks} onDryRun={handleDryRun} onNetwork={handleNetworkWebhook} />
                    </>
                ) : (
                    <>
                        <h2 className="text-xl font-semibold mb-4 text-zinc-300 flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-purple-500"></span>
                            System Endpoints
                        </h2>
                        <DevLogTable endpoints={endpoints} onNetwork={handleNetworkEndpoint} />
                    </>
                )}
            </section>

            <section>
                <div className="flex justify-between items-end mb-4">
                    <h2 className="text-xl font-semibold text-zinc-300 flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                        System Logs
                    </h2>

                    <div className="flex gap-4 items-center">
                        <label className="text-zinc-400 text-sm">Min Level:</label>
                        <select
                            value={minLevel}
                            onChange={(e) => { setMinLevel(e.target.value); setPage(1); }}
                            className="bg-zinc-900 text-white px-3 py-1 text-sm rounded border border-zinc-700 focus:outline-none focus:border-zinc-500"
                        >
                            <option value="DEBUG">DEBUG</option>
                            <option value="INFO">INFO</option>
                            <option value="WARNING">WARNING</option>
                            <option value="ERROR">ERROR</option>
                        </select>
                    </div>
                </div>

                <LogTable logs={logs} />

                <div className="mt-4 flex gap-4 items-center justify-between text-sm text-zinc-400">
                    <span>Page {page} of {totalPages}</span>
                    <div className="flex gap-2">
                        <button
                            onClick={() => setPage(p => Math.max(1, p - 1))}
                            className="px-4 py-1.5 bg-zinc-900 border border-zinc-800 rounded hover:bg-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                            disabled={page === 1}
                        >Previous</button>
                        <button
                            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                            className="px-4 py-1.5 bg-zinc-900 border border-zinc-800 rounded hover:bg-zinc-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                            disabled={page === totalPages}
                        >Next</button>
                    </div>
                </div>
            </section>

            {/* Dry Run Modal */}
            <DryRunModal
                webhook={selectedDryRunWebhook}
                isOpen={!!selectedDryRunWebhook}
                onClose={() => setSelectedDryRunWebhook(null)}
            />

            {/* Network View Modal */}
            {selectedNetworkTarget && networkLogs && (
                <NetworkView
                    logs={networkLogs}
                    pagination={{
                        page: networkPage,
                        totalPages: networkTotalPages,
                        totalItems: networkTotalItems,
                        onNext: () => setNetworkPage(p => Math.min(networkTotalPages, p + 1)),
                        onPrev: () => setNetworkPage(p => Math.max(1, p - 1))
                    }}
                    onClose={() => { setSelectedNetworkTarget(null); setNetworkLogs(null); }}
                    title={selectedNetworkTarget.name}
                />
            )}
        </div>
    );
};

export default App;