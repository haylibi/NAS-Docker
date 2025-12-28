import React from 'react';
import { EndpointLog } from '../types';

interface InternalProps {
    endpoints: EndpointLog[];
    onNetwork: (endpoint: EndpointLog) => void;
}

export const DevLogTable: React.FC<InternalProps> = ({ endpoints, onNetwork }: InternalProps) => {
    return (
        <div className="bg-black font-mono text-sm border border-zinc-800 mb-8 w-full">
            <div className="grid grid-cols-12 p-2 border-b border-zinc-900 bg-zinc-900 font-bold text-zinc-400">
                <span className="col-span-2">Category</span>
                <span className="col-span-4">Name</span>
                <span className="col-span-4">ID/Endpoint</span>
                <span className="col-span-2 text-right">Actions</span>
            </div>
            {endpoints.length === 0 && (
                <div className="p-4 text-center text-zinc-500">No logs found.</div>
            )}
            {endpoints.map((ep, i) => (
                <div key={i} className="grid grid-cols-12 p-2 border-b border-zinc-900 items-center">
                    <span className="col-span-2">
                        <span className={`px-2 py-0.5 rounded text-xs uppercase ${ep.category === 'webhook' ? 'bg-green-900 text-green-400' : 'bg-blue-900 text-blue-400'}`}>
                            {ep.category}
                        </span>
                    </span>
                    <span className="col-span-4 font-bold text-zinc-300">{ep.name}</span>
                    <span className="col-span-4 text-zinc-500 text-xs font-mono">{ep.endpoint}</span>
                    <div className="col-span-2 flex justify-end gap-2">
                        <button
                            onClick={() => onNetwork(ep)}
                            className="px-2 py-1 bg-zinc-800 hover:bg-zinc-700 text-xs rounded border border-zinc-700 text-blue-300"
                        >
                            Requests
                        </button>
                    </div>
                </div>
            ))
            }
        </div >
    );
};
