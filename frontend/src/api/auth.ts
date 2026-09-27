import { apiFetch } from "./client";

export type TokenResponse = { access_token: string; token_type: string };
export type RegisterResult = TokenResponse & { recovery_code: string };

export function registerFamily(
  name: string,
  email: string,
  password: string,
  inviteCode?: string,
) {
  return apiFetch<RegisterResult>("/auth/register", {
    method: "POST",
    // El campo solo viaja si tiene valor: en un despliegue casero el servidor
    // no exige invitación y el cuerpo debe seguir siendo el de siempre.
    body: { name, email, password, ...(inviteCode ? { invite_code: inviteCode } : {}) },
  });
}

export function loginFamily(email: string, password: string) {
  return apiFetch<TokenResponse>("/auth/login", {
    method: "POST",
    body: { email, password },
  });
}

export function changePassword(currentPassword: string, newPassword: string) {
  return apiFetch<{ status: string }>("/auth/change-password", {
    method: "POST",
    auth: true,
    body: { current_password: currentPassword, new_password: newPassword },
  });
}

export function resetPassword(email: string, recoveryCode: string, newPassword: string) {
  return apiFetch<{ recovery_code: string }>("/auth/reset-password", {
    method: "POST",
    body: { email, recovery_code: recoveryCode, new_password: newPassword },
  });
}

/** Confirma que quien está al teclado es el adulto. El token de familia sigue
 *  en el dispositivo mientras juega el niño, así que tenerlo no prueba nada. */
export function verifyFamilyPassword(password: string) {
  return apiFetch<{ status: string }>("/auth/verify-password", {
    method: "POST",
    auth: true,
    body: { password },
  });
}
