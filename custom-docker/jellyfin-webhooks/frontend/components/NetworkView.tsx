
import React, { useState } from 'react';
import { RequestLogEntry } from '../types';

interface Props {
    logs: RequestLogEntry[];
    pagination: {
        page: number;
        totalPages: number;
        totalItems: number;
        onNext: () => void;
        onPrev: () => void;
    };
    onClose: () => void;
    title: string;
}

export const NetworkView: React.FC<Props> = ({ logs, pagination, onClose, title }) => {
    const [selectedId, setSelectedId] = useState<number | null>(null);

    // Selected log logic
    // We don't have a unique ID in the log entry itself (unless we add UUID). 
    // Using index in the current page list for now.
    const selectedLog = selectedId !== null ? logs[selectedId] : null;

    const getStatusColor = (status?: number) => {
        if (!status) return 'text-zinc-500';
        if (status >= 200 && status < 300) return 'text-green-400';
        if (status >= 400 && status < 500) return 'text-yellow-400';
        if (status >= 500) return 'text-red-400';
        return 'text-zinc-400';
    };

    return (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center p-4 z-50">
            <div className="bg-zinc-950 border border-zinc-800 rounded-lg w-full max-w-7xl h-[90vh] flex flex-col shadow-2xl overflow-hidden font-mono text-sm">
                {/* Header */}
                <div className="bg-zinc-900 p-4 border-b border-zinc-800 flex justify-between items-center">
                    <h2 className="text-xl font-bold text-zinc-200 flex items-center gap-2">
                        <span className="text-blue-400">Network Activity:</span> {title}
                        <span className="text-zinc-600 text-sm ml-2">({pagination.totalItems} requests)</span>
                    </h2>
                    <button onClick={onClose} className="px-3 py-1 bg-zinc-800 hover:bg-zinc-700 text-white rounded">Close</button>
                </div>

                {/* Content - Split View */}
                <div className="flex-1 flex overflow-hidden">

                    {/* LEFT PANE: List */}
                    <div className={`${selectedLog ? 'w-1/3' : 'w-full'} border-r border-zinc-800 flex flex-col transition-all duration-300`}>
                        {/* Table Header */}
                        <div className="grid grid-cols-12 bg-zinc-900/50 p-2 border-b border-zinc-800 font-bold text-zinc-500 text-xs uppercase tracking-wider">
                            <div className="col-span-2">Status</div>
                            <div className="col-span-2">Method</div>
                            <div className="col-span-3">Time</div>
                            <div className="col-span-3">Duration</div>
                            <div className="col-span-2">Dry-Run</div>
                        </div>

                        {/* List Items */}
                        <div className="overflow-y-auto flex-1">
                            {logs.map((log, idx) => (
                                <div
                                    key={idx}
                                    onClick={() => setSelectedId(idx)}
                                    className={`grid grid-cols-12 p-3 border-b border-zinc-900 cursor-pointer hover:bg-zinc-900 transition-colors ${selectedId === idx ? 'bg-blue-900/20 border-l-2 border-l-blue-500' : ''}`}
                                >
                                    <div className={`col-span-2 font-bold ${getStatusColor(log.response?.status)}`}>
                                        {log.response?.status || 'N/A'}
                                    </div>
                                    <div className="col-span-2 text-zinc-300">{log.method}</div>
                                    <div className="col-span-3 text-zinc-500 text-xs">
                                        {new Date(Number(log.timestamp) * 1000).toLocaleString()}
                                    </div>
                                    <div className="col-span-3 text-zinc-400 text-xs">{log.duration_ms.toFixed(0)} ms</div>

                                    <div className="col-span-2 text-xs">
                                        <span className={`px-2 py-0.5 rounded border border-opacity-50 ${log.url.includes('dry_run=true')
                                            ? 'text-purple-400 border-purple-400 bg-purple-400/10'
                                            : 'text-zinc-400 border-zinc-700 bg-zinc-800'
                                            }`}>
                                            {log.url.includes('dry_run=true') ? 'Yes' : 'No'}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Pagination Footer */}
                        <div className="p-3 border-t border-zinc-800 bg-zinc-900 flex justify-between items-center text-xs text-zinc-400">
                            <button
                                disabled={pagination.page === 1}
                                onClick={pagination.onPrev}
                                className="px-2 py-1 bg-zinc-800 rounded disabled:opacity-50 hover:bg-zinc-700"
                            >
                                ← Prev
                            </button>
                            <span>Page {pagination.page} of {pagination.totalPages}</span>
                            <button
                                disabled={pagination.page === pagination.totalPages}
                                onClick={pagination.onNext}
                                className="px-2 py-1 bg-zinc-800 rounded disabled:opacity-50 hover:bg-zinc-700"
                            >
                                Next →
                            </button>
                        </div>
                    </div>

                    {/* RIGHT PANE: Detail View */}
                    {selectedLog && (
                        <div className="flex-1 flex flex-col overflow-hidden bg-zinc-925">
                            {/* Detail Header */}
                            <div className="p-3 border-b border-zinc-800 bg-zinc-900 flex gap-4 text-xs font-bold text-zinc-400">
                                <div className="text-zinc-200">Request Details</div>
                            </div>

                            <div className="flex-1 overflow-y-auto p-4 space-y-6">
                                {/* General Info */}
                                <div>
                                    <h4 className="text-blue-400 text-xs uppercase font-bold mb-2">General</h4>
                                    <div className="bg-zinc-900 p-3 rounded text-zinc-300 text-xs space-y-1">
                                        <div className="flex"><span className="w-24 text-zinc-500">Request URL:</span> <span className="text-white break-all">{selectedLog.url}</span></div>
                                        <div className="flex"><span className="w-24 text-zinc-500">Method:</span> <span className="text-yellow-400">{selectedLog.method}</span></div>
                                        <div className="flex"><span className="w-24 text-zinc-500">Remote Addr:</span> <span>{selectedLog.remote_addr}</span></div>
                                        <div className="flex"><span className="w-24 text-zinc-500">Timestamp:</span> <span>{selectedLog.timestamp}</span></div>
                                        <div className="flex"><span className="w-24 text-zinc-500">Date-ISO:</span> <span>{selectedLog.date_iso}</span></div>
                                    </div>
                                </div>

                                {/* Request Headers */}
                                <div>
                                    <h4 className="text-blue-400 text-xs uppercase font-bold mb-2">Request Headers</h4>
                                    <pre className="bg-zinc-900 p-3 rounded text-zinc-400 text-xs overflow-x-auto">
                                        {JSON.stringify(selectedLog.headers, null, 2)}
                                    </pre>
                                </div>

                                {/* Request Body */}
                                <div>
                                    <h4 className="text-blue-400 text-xs uppercase font-bold mb-2">Request Payload</h4>
                                    <pre className="bg-zinc-900 p-3 rounded text-green-300 text-xs overflow-x-auto whitespace-pre-wrap">
                                        {typeof selectedLog.body === 'object' ? JSON.stringify(selectedLog.body, null, 2) : selectedLog.body}
                                    </pre>
                                </div>

                                {/* Response */}
                                <div>
                                    <h4 className="text-purple-400 text-xs uppercase font-bold mb-2">Response ({selectedLog.response?.status})</h4>
                                    <pre className="bg-zinc-900 p-3 rounded text-purple-200 text-xs overflow-x-auto whitespace-pre-wrap">
                                        {typeof selectedLog.response?.body === 'object'
                                            ? JSON.stringify(selectedLog.response?.body, null, 2)
                                            : selectedLog.response?.body}
                                    </pre>
                                </div>

                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
