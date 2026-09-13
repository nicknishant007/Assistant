import { create } from "zustand";

/** Cross-cutting UI state: panel visibility, responsive drawers, modals.
 *  Nothing feature-specific lives here — that belongs in its own store. */
interface UiState {
  sidebarOpen: boolean; // mobile drawer
  contextPanelCollapsed: boolean;
  activeModal: string | null;

  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  toggleContextPanel: () => void;
  openModal: (id: string) => void;
  closeModal: () => void;
}

export const useUiStore = create<UiState>((set) => ({
  sidebarOpen: false,
  contextPanelCollapsed: false,
  activeModal: null,

  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleContextPanel: () =>
    set((s) => ({ contextPanelCollapsed: !s.contextPanelCollapsed })),
  openModal: (id) => set({ activeModal: id }),
  closeModal: () => set({ activeModal: null })
}));
