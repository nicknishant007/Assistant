import { format, isToday, isYesterday, parseISO } from "date-fns";

export function formatMessageTime(iso: string): string {
  return format(parseISO(iso), "h:mm a");
}

export function formatConversationDate(iso: string): string {
  const date = parseISO(iso);
  if (isToday(date)) return "Today";
  if (isYesterday(date)) return "Yesterday";
  return format(date, "MMM d");
}

export function formatEventRange(startIso: string, endIso: string): string {
  const start = parseISO(startIso);
  const end = parseISO(endIso);
  return `${format(start, "h:mm a")} – ${format(end, "h:mm a")}`;
}
