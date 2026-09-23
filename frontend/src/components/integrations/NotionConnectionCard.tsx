"use client";

import { useEffect } from "react";
import { CheckCircle2, XCircle } from "lucide-react";
import { useNotionStore } from "@/store/notionStore";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";

/**
 * Notion connect/disconnect card. Self-contained: fetches its own
 * status on mount via notionStore, so it can be dropped into Settings
 * or Home without extra wiring.
 */
export function NotionConnectionCard() {
  const { connected, checked, loading, error, fetchStatus, connect, disconnect } =
    useNotionStore();

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  return (
    <Card className="bg-white">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="font-display text-lg font-bold">Notion</h2>
          <p className="mt-1 text-sm text-ink/70">
            Let NuroFlow search, read, and update pages in your Notion workspace.
          </p>
        </div>

        {checked && (
          <Badge tone={connected ? "mint" : "surface"} className="shrink-0">
            {connected ? (
              <>
                <CheckCircle2 size={12} /> Connected
              </>
            ) : (
              <>
                <XCircle size={12} /> Not connected
              </>
            )}
          </Badge>
        )}
      </div>

      {error && <p className="mt-3 text-sm text-danger">{error}</p>}

      <div className="mt-4">
        {connected ? (
          <Button variant="secondary" size="sm" className="bg-cobalt text-white hover:bg-mint" onClick={disconnect} disabled={loading}>
            {loading ? "Disconnecting…" : "Disconnect"}
          </Button>
        ) : (
          <Button variant="primary" size="sm" className="bg-cobalt text-white hover:bg-mint" onClick={connect} disabled={loading}>
            {loading ? "Checking…" : "Connect Notion"}
          </Button>
        )}
      </div>
    </Card>
  );
}