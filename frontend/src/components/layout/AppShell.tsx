"use client";

import React from "react";
import Sidebar from "./Sidebar";
import Header from "./Header";

export default function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-navy-950">
      <Sidebar />
      {/* Main content — offset by sidebar width. Uses ml-[68px] for collapsed,
          but sidebar starts expanded at w-[260px]. We use a responsive default. */}
      <div className="ml-[260px] flex min-h-screen flex-1 flex-col transition-all duration-300">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
