import { Check, X } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

/**
 * Renders an agent approval request (Backend agent/validator_agent.py /
 * AgentState.approval_message). Wire `onApprove`/`onReject` up to the
 * agent's approval endpoint once it exists on the backend — today the
 * chat endpoint has no way to resume a paused workflow, so this is the
 * UI contract to build that endpoint against.
 */
export function ApprovalCard({
  summary,
  onApprove,
  onReject
}: {
  summary: string;
  onApprove: () => void;
  onReject: () => void;
}) {
  return (
    <Card tone="yellow" className="max-w-[75ch]">
      <p className="font-display text-sm font-bold uppercase tracking-wide text-ink/70">
        Approval needed
      </p>
      <p className="mt-2 text-base">{summary}</p>
      <div className="mt-4 flex gap-2">
        <Button variant="primary" size="sm" onClick={onApprove}>
          <Check size={16} /> Approve
        </Button>
        <Button variant="secondary" size="sm" onClick={onReject}>
          <X size={16} /> Reject
        </Button>
      </div>
    </Card>
  );
}
