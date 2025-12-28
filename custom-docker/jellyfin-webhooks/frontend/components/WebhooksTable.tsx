import React from 'react';
import { WebhookConfig } from '../types';

interface InternalProps {
    webhooks: WebhookConfig[];
    onDryRun: (hook: WebhookConfig) => void;
    onNetwork: (hook: WebhookConfig) => void;
}

export const WebhooksTable: React.FC<InternalProps> = ({ webhooks, onDryRun, onNetwork }: InternalProps) => {
    return (
        <div className="bg-black font-mono text-sm border border-zinc-800 mb-8 w-full">
            <div className="grid grid-cols-12 p-2 border-b border-zinc-900 bg-zinc-900 font-bold text-zinc-400">
                <span className="col-span-2">Name</span>
                <span className="col-span-1 text-center">Enabled</span>
                <span className="col-span-4">Description</span>
                <span className="col-span-3">Action Buttons</span>
                <span className="col-span-2 text-right">Endpoint</span>
            </div>
            {webhooks.length === 0 && (
                <div className="p-4 text-center text-zinc-500">No webhooks configured.</div>
            )}
            {webhooks.map((hook, i) => (
                <div key={i} className="grid grid-cols-12 p-2 border-b border-zinc-900 items-center">
                    <span className="col-span-2 font-bold text-blue-400">{hook.name}</span>
                    <span className="col-span-1 text-center">
                        <span className={`px-2 py-0.5 rounded text-xs ${hook.enabled ? 'bg-green-900 text-green-400' : 'bg-red-900 text-red-400'}`}>
                            {hook.enabled ? 'ON' : 'OFF'}
                        </span>
                    </span>
                    <span className="col-span-4 text-zinc-400 text-xs">{hook.description}</span>
                    <div className="col-span-3 flex gap-2">
                        <button
                            onClick={() => onDryRun(hook)}
                            className="px-2 py-1 bg-zinc-800 hover:bg-zinc-700 text-xs rounded border border-zinc-700 text-zinc-300"
                        >
                            Dry Run
                        </button>

                        <button
                            onClick={() => onNetwork(hook)}
                            className="px-2 py-1 bg-zinc-800 hover:bg-zinc-700 text-xs rounded border border-zinc-700 text-blue-300"
                        >
                            Requests
                        </button>
                    </div>

                    <span className="col-span-2 text-zinc-500 font-mono text-xs overflow-x-auto whitespace-nowrap bg-zinc-900/50 p-1 rounded text-right">
                        {hook.endpoint}
                    </span>
                </div>
            ))
            }
        </div >
    );
};
