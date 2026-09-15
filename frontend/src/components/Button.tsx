import type { ReactNode } from "react";

type Props = {
  children: ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  disabled?: boolean;
};

export default function Button({ children, onClick, type = "button", disabled }: Props) {
  return (
    <button className="btn-primary" type={type} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}
