# 🔌 API Integration Guide for V0 Dashboard

## API Base Configuration

```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export const api = {
  // Health check
  health: async () => {
    const res = await fetch(`${API_BASE_URL}/health`);
    return res.json();
  },

  // Get all calls
  getCalls: async () => {
    const res = await fetch(`${API_BASE_URL}/api/calls`);
    return res.json();
  },

  // Get call transcripts
  getCallTranscripts: async (callSid: string) => {
    const res = await fetch(`${API_BASE_URL}/api/calls/${callSid}/transcripts`);
    return res.json();
  },

  // Process audio (for testing)
  processAudio: async (file: File, callSid?: string) => {
    const formData = new FormData();
    formData.append('audio', file);
    if (callSid) formData.append('call_sid', callSid);
    
    const res = await fetch(`${API_BASE_URL}/api/process-audio`, {
      method: 'POST',
      body: formData,
    });
    return res.json();
  },
};
```

## TypeScript Types

```typescript
// types/index.ts
export interface Call {
  id: number;
  call_sid: string;
  from_number: string;
  to_number: string;
  status: 'ringing' | 'in-progress' | 'completed' | 'failed';
  start_time: string;
  end_time: string | null;
  duration: number | null;
}

export interface Transcript {
  text: string;
  is_final: string;
  timestamp: string;
  speaker?: 'user' | 'agent';
}

export interface CallWithTranscripts extends Call {
  transcripts: Transcript[];
}

export interface HealthStatus {
  status: string;
  timestamp: string;
  services: {
    assemblyai: boolean;
    groq: boolean;
    gemini: boolean;
    openai: boolean;
    tts: boolean;
    ai_provider: string;
  };
}
```

## Example React Components

### CallCard Component
```typescript
import { Call } from '@/types';
import { Badge } from '@/components/ui/badge';
import { formatDistanceToNow } from 'date-fns';

export function CallCard({ call }: { call: Call }) {
  const statusColors = {
    ringing: 'bg-yellow-100 text-yellow-800',
    'in-progress': 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
  };

  return (
    <div className="border rounded-lg p-4 hover:shadow-md transition">
      <div className="flex justify-between items-start">
        <div>
          <p className="font-mono text-sm text-gray-500">{call.call_sid}</p>
          <p className="font-semibold mt-1">{call.from_number}</p>
          <p className="text-sm text-gray-600">→ {call.to_number}</p>
        </div>
        <Badge className={statusColors[call.status]}>
          {call.status}
        </Badge>
      </div>
      <div className="mt-3 text-sm text-gray-500">
        {formatDistanceToNow(new Date(call.start_time))} ago
        {call.duration && ` • ${Math.floor(call.duration / 60)}m ${call.duration % 60}s`}
      </div>
    </div>
  );
}
```

### Transcript Viewer Component
```typescript
import { Transcript } from '@/types';
import { format } from 'date-fns';

export function TranscriptViewer({ transcripts }: { transcripts: Transcript[] }) {
  return (
    <div className="space-y-4">
      {transcripts.map((t, i) => (
        <div
          key={i}
          className={`flex ${t.speaker === 'user' ? 'justify-start' : 'justify-end'}`}
        >
          <div
            className={`max-w-[70%] rounded-lg p-3 ${
              t.speaker === 'user'
                ? 'bg-blue-100 text-blue-900'
                : 'bg-green-100 text-green-900'
            }`}
          >
            <p className="text-sm font-medium mb-1">
              {t.speaker === 'user' ? 'User' : 'AI Agent'}
            </p>
            <p>{t.text}</p>
            <p className="text-xs mt-1 opacity-70">
              {format(new Date(t.timestamp), 'HH:mm:ss')}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
```

## Environment Variables

Create `.env.local` in your Next.js project:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

For production:
```env
NEXT_PUBLIC_API_URL=https://your-deployed-backend.com
```

## CORS Configuration

The Flask backend already has CORS enabled, but if you need to adjust:

```python
# In app.py
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "https://your-domain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

## Real-time Updates

For real-time call updates, use polling:

```typescript
// hooks/useCalls.ts
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export function useCalls() {
  const [calls, setCalls] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCalls = async () => {
      try {
        const data = await api.getCalls();
        setCalls(data.calls);
      } catch (error) {
        console.error('Failed to fetch calls:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCalls();
    
    // Poll every 5 seconds
    const interval = setInterval(fetchCalls, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return { calls, loading };
}
```

## Error Handling

```typescript
// lib/error-handler.ts
export async function handleApiError(response: Response) {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.error || `HTTP ${response.status}`);
  }
  return response.json();
}
```
