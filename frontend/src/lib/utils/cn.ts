import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Standard class-merge helper used by every component — avoids duplicated
 *  conditional-class logic scattered across the codebase. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
