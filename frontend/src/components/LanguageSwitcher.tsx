import { LANGS, type Lang } from "../i18n/translations";
import { useI18n } from "../i18n/I18nContext";

export default function LanguageSwitcher() {
  const { lang, setLang } = useI18n();
  return (
    <label
      style={{ display: "flex", gap: 6, alignItems: "center", fontSize: 13, alignSelf: "flex-end" }}
    >
      🌐
      <select
        aria-label="Idioma / Language"
        value={lang}
        onChange={(e) => setLang(e.target.value as Lang)}
        style={{ borderRadius: 10, padding: "4px 8px", fontFamily: "var(--font-body)" }}
      >
        {LANGS.map((l) => (
          <option key={l.code} value={l.code}>
            {l.label}
          </option>
        ))}
      </select>
    </label>
  );
}
