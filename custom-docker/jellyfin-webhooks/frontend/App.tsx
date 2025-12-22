// frontend/App.tsx
import { useEffect, useState } from 'react';
import { LogTable } from './components/LogTable';
import { WebhooksTable } from './components/WebhooksTable';
import { DryRunModal } from './components/DryRunModal';
import { ApiResponse, LogEntry, WebhookConfig } from './types';

const App = () => {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [webhooks, setWebhooks] = useState<WebhookConfig[]>([]);

    // Logs Pagination & Filtering
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [minLevel, setMinLevel] = useState('INFO');

    // Modals & Action State
    const [selectedDryRunWebhook, setSelectedDryRunWebhook] = useState<WebhookConfig | null>(null);
    const [webhookLogs, setWebhookLogs] = useState<LogEntry[] | null>(null); // Null means not showing modal
    const [selectedWebhook, setSelectedWebhook] = useState<string | null>(null); // For Logs Modal Title

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

    // --- Action Handlers ---

    const handleDryRun = (hook: WebhookConfig) => {
        setSelectedDryRunWebhook(hook);
    };

    const handleLogs = async (hook: WebhookConfig) => {
        // Filter main logs for this webhook (client-side filtering for simplicity for now)
        // Ideally backend would support filtering by source, but we don't store source structured yet.
        // We will filter by checking if the log message contains the webhook ID/Name or related keywords.
        // Since we only have 'app.log', we might just show ALL logs in the modal for now, or fetch fresh.
        // Let's reuse the existing logs but filter them.

        // Better approach: Since user wants to see logs *for that webhook*, let's just show the main log table
        // filtered by a search term, OR just open a modal with *all* logs if specific filtering isn't implemented.
        // Given the prompt "Logs for that webhook", let's try to filter by Webhook Name.
        setSelectedWebhook(hook.name);
        const relevantLogs = logs.filter((l: LogEntry) => l.msg.toLowerCase().includes(hook.name.toLowerCase()));
        setWebhookLogs(relevantLogs);
    };


    useEffect(() => {
        fetchLogs(page, minLevel);
    }, [page, minLevel]);

    useEffect(() => {
        fetchWebhooks();
    }, []);

    return (
        <div className="min-h-screen bg-zinc-950 text-white p-8 w-full">
            <header className="mb-8 border-b border-zinc-800 pb-4">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">Jellyfin Webhooks</h1>
                <p className="text-zinc-500 mt-2">Manage your media automation integrations</p>
            </header>

            <section className="mb-12 w-full">
                <h2 className="text-xl font-semibold mb-4 text-zinc-300 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-green-500"></span>
                    Configured Webhooks
                </h2>
                <WebhooksTable webhooks={webhooks} onDryRun={handleDryRun} onLogs={handleLogs} />
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

            {/* Logs Modal */}
            {webhookLogs && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
                    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6 max-w-4xl w-full shadow-2xl flex flex-col max-h-[90vh]">
                        <h3 className="text-xl font-bold mb-4 text-green-400">Logs for: {selectedWebhook}</h3>
                        <div className="overflow-auto flex-1">
                            {webhookLogs.length > 0 ? (
                                <LogTable logs={webhookLogs} />
                            ) : (
                                <p className="text-zinc-500 text-center py-8">No logs found matching this webhook name.</p>
                            )}
                        </div>
                        <div className="mt-6 flex justify-end">
                            <button
                                onClick={() => { setWebhookLogs(null); setSelectedWebhook(null); }}
                                className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded"
                            >Close</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default App;