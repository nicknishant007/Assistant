import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

export function ClarificationCard({
  question,
  options,
  onSelect
}: {
  question: string;
  options?: { label: string; value: string }[];
  onSelect: (value: string) => void;
}) {
  return (
    <Card tone="mint" className="max-w-[75ch]">
      <p className="font-display text-sm font-bold uppercase tracking-wide text-ink/70">
        Quick question
      </p>
      <p className="mt-2 text-base">{question}</p>
      {options && options.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {options.map((opt) => (
            <Button
              key={opt.value}
              variant="secondary"
              size="sm"
              onClick={() => onSelect(opt.value)}
            >
              {opt.label}
            </Button>
          ))}
        </div>
      )}
    </Card>
  );
}
