import React from 'react';
import { LogEntry } from '../types';

export const LogTable: React.FC<{ logs: LogEntry[] }> = ({ logs }) => {
    return (
        <div className="bg-black font-mono text-sm border border-zinc-800">
            {logs.map((log, i) => (
                <div key={i} className="grid grid-cols-12 p-2 border-b border-zinc-900">
                    <span className="col-span-2 text-zinc-500">{log.time}</span>
                    <span className={`col-span-1 font-bold ${getLevelColor(log.level)}`}>{log.level}</span>
                    <span className="col-span-9 text-zinc-300">{log.msg}</span>
                </div>
            ))}
        </div>
    );
};

const getLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
        case 'ERROR': return 'text-red-500';
        case 'WARNING': return 'text-yellow-500';
        case 'DEBUG': return 'text-blue-400';
        default: return 'text-green-400'; // INFO
    }
};