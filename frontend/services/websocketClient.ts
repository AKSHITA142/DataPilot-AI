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
          const event = JSON.parse(ev.data as string) as WSEvent;
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
