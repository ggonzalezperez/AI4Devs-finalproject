import type { ReactNode } from "react";

export default function ScreenCard({ children }: { children: ReactNode }) {
  return <div className="screen-card">{children}</div>;
}
