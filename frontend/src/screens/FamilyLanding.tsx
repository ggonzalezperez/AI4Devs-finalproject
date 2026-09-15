import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { listChildren } from "../api/children";
import ScreenCard from "../components/ScreenCard";

/**
 * Aterrizaje de la familia ya logueada:
 * - Si hay EXACTAMENTE un explorador → directo a su acceso con PIN.
 * - Si hay 0 o varios → al hub "¿Quién va a explorar?" (para elegir/añadir).
 * (Desde el acceso del niño hay un enlace "Ajustes de familia" para el padre.)
 */
export default function FamilyLanding() {
  const [target, setTarget] = useState<string | null>(null);
  const [navState, setNavState] = useState<{ name: string; avatar: string } | undefined>(undefined);

  useEffect(() => {
    listChildren()
      .then((cs) => {
        if (cs.length === 1) {
          setNavState({ name: cs[0].name, avatar: cs[0].avatar });
          setTarget(`/explorar/${cs[0].id}`);
        } else {
          setTarget("/familia/explorar");
        }
      })
      .catch(() => setTarget("/familia/explorar"));
  }, []);

  if (!target) {
    return (
      <ScreenCard>
        <p>…</p>
      </ScreenCard>
    );
  }
  return <Navigate to={target} replace state={navState} />;
}
