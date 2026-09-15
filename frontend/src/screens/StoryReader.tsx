import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getMyStory, type Story } from "../api/stories";
import { useI18n } from "../i18n/I18nContext";
import ScreenCard from "../components/ScreenCard";
import ChildHeader from "../components/ChildHeader";

export default function StoryReader() {
  const { id } = useParams();
  const [story, setStory] = useState<Story | null>(null);
  const [loaded, setLoaded] = useState(false);
  const { t } = useI18n();

  useEffect(() => {
    if (!id) return;
    getMyStory(Number(id))
      .then(setStory)
      .catch(() => undefined)
      .finally(() => setLoaded(true));
  }, [id]);

  return (
    <ScreenCard>
      <ChildHeader />
      {story ? (
        <>
          <h1>{story.title}</h1>
          <div style={{ background: "#fff", borderRadius: 16, padding: 16, lineHeight: 1.7, fontSize: 16, color: "var(--teal-dark)" }}>
            {story.body}
          </div>
        </>
      ) : (
        loaded && <p style={{ color: "#0a5a53" }}>{t("stories.notFound")}</p>
      )}
      <Link to="/jugar/cuentos" style={{ textAlign: "center", marginTop: 8 }}>
        {t("stories.back")}
      </Link>
    </ScreenCard>
  );
}
