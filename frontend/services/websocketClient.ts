import type { WSEvent, WSEventType } from "@/types/api";

type WSListener = (event: WSEvent) => void;

class WebSocketClient {
  private socket: WebSocket | null = null;
  private jobId: string | null = null;
  private listeners: Map<WSEventType | "all", Set<WSListener>> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private isManualClose = false;

  connect(jobId: string): void {
    if (this.socket?.readyState === WebSocket.OPEN && this.jobId === jobId) {
      return; // already connected to same job
    }
    this.disconnect();
    this.jobId = jobId;
    this.isManualClose = false;
    this.reconnectAttempts = 0;
    this._connect();
  }

  private _connect(): void {
    if (!this.jobId) return;

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const url = `${protocol}//localhost:8000/api/v1/ws/jobs/${this.jobId}`;

    try {
      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        this.reconnectAttempts = 0;
      };

      this.socket.onmessage = (ev: MessageEvent) => {
        try {
          const raw = JSON.parse(ev.data as string);

          // Normalize the incoming payload into the WSEvent shape the frontend expects.
          // Backend now sends: { event, job_id, timestamp, data: { status, stage, ... } }
          // But older payloads may have fields at top level without a nested `data` object.
          const event: WSEvent = {
            event: raw.event,
            job_id: raw.job_id ?? this.jobId ?? "",
            timestamp: raw.timestamp ?? new Date().toISOString(),
            data: {
              // Prefer nested data, fall back to top-level fields
              status: raw.data?.status ?? raw.status,
              stage: raw.data?.stage ?? raw.stage,
              progress_percent: raw.data?.progress_percent ?? raw.progress_percent ?? raw.progress,
              message: raw.data?.message ?? raw.message,
              level: raw.data?.level ?? raw.level,
              experiment_id: raw.data?.experiment_id ?? raw.experiment_id,
              finding: raw.data?.finding,
              report: raw.data?.report,
            },
          };

          this._dispatch(event);
        } catch {
          // ignore malformed messages
        }
      };

      this.socket.onclose = () => {
        if (!this.isManualClose) {
          this._scheduleReconnect();
        }
      };

      this.socket.onerror = () => {
        this.socket?.close();
      };
    } catch {
      this._scheduleReconnect();
    }
  }

  private _scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) return;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
    this.reconnectAttempts++;
    this.reconnectTimer = setTimeout(() => this._connect(), delay);
  }

  private _dispatch(event: WSEvent): void {
    // fire specific event listeners
    const specific = this.listeners.get(event.event);
    if (specific) specific.forEach((fn) => fn(event));

    // fire catch-all listeners
    const all = this.listeners.get("all");
    if (all) all.forEach((fn) => fn(event));
  }

  on(eventType: WSEventType | "all", listener: WSListener): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(listener);

    // Return unsubscribe function
    return () => {
      this.listeners.get(eventType)?.delete(listener);
    };
  }

  disconnect(): void {
    this.isManualClose = true;
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.socket) {
      this.socket.onclose = null;
      this.socket.close();
      this.socket = null;
    }
    this.jobId = null;
  }

  get isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }
}

// Singleton instance
export const wsClient = new WebSocketClient();
