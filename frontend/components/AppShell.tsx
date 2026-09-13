"use client";

import { createContext, useContext, useState } from "react";
import Sidebar from "@/components/Sidebar";

export const MobileMenuContext = createContext<() => void>(() => {});
export function useMobileMenu() {
  return useContext(MobileMenuContext);
}

export default function AppShell({ children }: { children: React.ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex min-h-screen">
      <Sidebar mobileOpen={mobileOpen} onClose={() => setMobileOpen(false)} />
      <div className="flex-1 min-w-0">
        <MobileMenuContext.Provider value={() => setMobileOpen(true)}>
          {children}
        </MobileMenuContext.Provider>
      </div>
    </div>
  );
}
