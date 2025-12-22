import React, { useState, useEffect } from 'react';
import { WebhookConfig } from '../types';

interface Torrent {
    name: string;
    hash: string;
    size: number;
    state: string;
    progress: number;
}

interface Props {
    webhook: WebhookConfig | null;
    isOpen: boolean;
    onClose: () => void;
}

export const DryRunModal: React.FC<Props> = ({ webhook, isOpen, onClose }) => {
    const [torrents, setTorrents] = useState<Torrent[]>([]);
    const [loading, setLoading] = useState(false);
    const [selectedTorrent, setSelectedTorrent] = useState<string | null>(null);
    const [filter, setFilter] = useState('');
    const [result, setResult] = useState<string | null>(null);
    const [running, setRunning] = useState(false);

    useEffect(() => {
        if (isOpen && webhook) {
            fetchTorrents();
            setResult(null);
            setSelectedTorrent(null);
            setFilter('');
        }
    }, [isOpen, webhook]);

    const fetchTorrents = async () => {
        setLoading(true);
        try {
            const res = await fetch(`api/torrents`);
            const json = await res.json();
            if (json.status === 'success') {
                setTorrents(json.data);
            } else {
                console.error("Failed to fetch torrents", json);
            }
        } catch (error) {
            console.error("Error fetching torrents:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleRun = async () => {
        if (!webhook || !selectedTorrent) return;
        setRunning(true);
        setResult(null);

        try {
            // Because our backend expects POST to /webhook/add_watched_tag (which is webhook.endpoint)
            // But usually endpoints are relative like "/webhook/add_watched_tag", so we prepend base url if needed
            // However, the existing logic in App.tsx or useWebhooks might handle this differently.
            // Let's assume webhook.endpoint is the full relative path e.g. /webhook/add_watched_tag

            const url = `webhook${webhook.endpoint}`;

            const res = await fetch(`${url}?dry_run=true`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    dry_run: true,
                    Name: selectedTorrent,
                    NotificationType: 'PlaybackStop', // Simulate playback stop
                    PlayedPercentage: 100 // Simulate fully watched
                })
            });

            const text = await res.text();
            try {
                const json = JSON.parse(text);
                setResult(JSON.stringify(json, null, 2));
            } catch {
                setResult(text);
            }

        } catch (error) {
            setResult(`Error: ${error}`);
        } finally {
            setRunning(false);
        }
    };

    if (!isOpen || !webhook) return null;

    const filteredTorrents = torrents.filter(t =>
        t.name.toLowerCase().includes(filter.toLowerCase())
    );

    return (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
            <div className="bg-zinc-900 border border-zinc-700 rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col font-mono">

                {/* Header */}
                <div className="p-4 border-b border-zinc-800 flex justify-between items-center bg-zinc-950 rounded-t-lg">
                    <h2 className="text-xl font-bold text-white">Dry Run: {webhook.name}</h2>
                    <button onClick={onClose} className="text-zinc-400 hover:text-white text-2xl">&times;</button>
                </div>

                {/* Content */}
                <div className="p-4 flex-1 overflow-hidden flex flex-col gap-4">
                    <p className="text-zinc-400 text-sm">
                        Select a torrent to simulate a "PlaybackStop" event for. This will check if the torrent exists and (in a real run) tag it.
                    </p>

                    {/* Search */}
                    <input
                        type="text"
                        placeholder="Search torrents..."
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        className="w-full bg-zinc-950 border border-zinc-700 text-white px-3 py-2 rounded focus:outline-none focus:border-blue-500"
                    />

                    {/* Torrent List */}
                    <div className="flex-1 overflow-y-auto border border-zinc-800 rounded bg-black/50 p-2">
                        {loading ? (
                            <div className="text-zinc-500 text-center py-4">Loading torrents...</div>
                        ) : (
                            <div className="space-y-1">
                                {filteredTorrents.map((t) => (
                                    <label key={t.hash} className={`flex items-center p-2 rounded cursor-pointer hover:bg-zinc-800 ${selectedTorrent === t.name ? 'bg-blue-900/30 border border-blue-900' : ''}`}>
                                        <input
                                            type="radio"
                                            name="torrent"
                                            value={t.name}
                                            checked={selectedTorrent === t.name}
                                            onChange={() => setSelectedTorrent(t.name)}
                                            className="mr-3"
                                        />
                                        <div className="flex-1 min-w-0">
                                            <div className="text-white truncate">{t.name}</div>
                                            <div className="text-zinc-500 text-xs">
                                                {(t.size / 1024 / 1024 / 1024).toFixed(2)} GB • {t.state} • {(t.progress * 100).toFixed(1)}%
                                            </div>
                                        </div>
                                    </label>
                                ))}
                                {filteredTorrents.length === 0 && (
                                    <div className="text-zinc-500 text-center py-2">No torrents found.</div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Result Area */}
                    {result && (
                        <div className="bg-black border border-zinc-800 p-2 rounded text-xs text-green-400 font-mono h-32 overflow-auto">
                            <pre>{result}</pre>
                        </div>
                    )}

                </div>

                {/* Footer */}
                <div className="p-4 border-t border-zinc-800 bg-zinc-950 rounded-b-lg flex justify-end gap-2">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded text-sm"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleRun}
                        disabled={!selectedTorrent || running}
                        className={`px-4 py-2 rounded text-sm font-bold text-white ${!selectedTorrent || running ? 'bg-zinc-700 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500'}`}
                    >
                        {running ? 'Running...' : 'Run Test'}
                    </button>
                </div>
            </div>
        </div>
    );
};
