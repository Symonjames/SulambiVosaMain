import React, { useEffect, useMemo, useState } from "react";
import { Box, Typography, styled } from "@mui/material";
import { getAllReports } from "../api/reports";
import { InternalReportType, ExternalReportType } from "../interface/types";

const getBaseUrl = (): string => {
  const apiUri = (import.meta as any).env.VITE_API_URI as string | undefined;
  if (apiUri) return apiUri.replace("/api", "");
  if ((import.meta as any).env.DEV) return "http://localhost:8000";
  return window.location.origin;
};
const BASE_URL = getBaseUrl();

const Section = styled(Box)({ width: "100%" });
const Header = styled(Box)({ marginBottom: "16px" });
const Title = styled(Typography)({ 
  fontSize: "28px", 
  fontWeight: 700, 
  color: "#1e40af",
  marginBottom: "8px",
  letterSpacing: "-0.025em"
});
const Grid = styled(Box)({
  display: "grid",
  gridTemplateColumns: "repeat(4, 1fr)",
  gap: "24px",
  "@media (max-width: 1024px)": { gridTemplateColumns: "repeat(2, 1fr)" },
  "@media (max-width: 600px)": { gridTemplateColumns: "repeat(1, 1fr)" },
});
const Card = styled(Box)({
  display: "flex",
  flexDirection: "column",
  border: "1px solid #e5e7eb",
  borderRadius: "12px",
  overflow: "hidden",
  backgroundColor: "#fff",
  cursor: "pointer",
  transition: "all 0.2s ease",
  boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
  ':hover': { 
    boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
    transform: "translateY(-2px)"
  }
});
const Thumb = styled("img")({ width: "100%", aspectRatio: "16/9", objectFit: "cover", background: "#f3f4f6" });
const Body = styled(Box)({ padding: "16px" });
const Headline = styled(Typography)({ 
  fontSize: "16px", 
  fontWeight: 700, 
  color: "#111827",
  lineHeight: 1.3,
  marginBottom: "8px"
});
const Excerpt = styled(Typography)({ 
  fontSize: "13px", 
  color: "#6b7280", 
  lineHeight: 1.4,
  display: "-webkit-box",
  WebkitLineClamp: 3,
  WebkitBoxOrient: "vertical",
  overflow: "hidden"
});

type CombinedReport = (InternalReportType | ExternalReportType) & {
  photos?: string[];
  narrative?: string;
  eventId?: any;
};

const buildImageUrl = (filename?: string) => {
  if (!filename) return "";
  let clean = filename.trim();
  try { clean = decodeURIComponent(clean); } catch {}
  clean = clean.replace(/\\\\/g, "/");
  if (clean.startsWith("uploads/")) clean = clean.replace(/^uploads[\\/\\\\]/, "");
  return `${BASE_URL}/uploads/${clean}?t=${Date.now()}`;
};
const truncate = (t?: string, n = 110) => {
  if (!t) return "";
  const s = t.trim();
  return s.length > n ? `${s.slice(0, n - 1)}…` : s;
};


interface Props { limit?: number; title?: string; onOpenReport?: (report: CombinedReport) => void; }

const PhotoThumbnailGrid: React.FC<Props> = ({ limit = 8, title = "Latest News", onOpenReport }) => {
  const [reports, setReports] = useState<CombinedReport[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    getAllReports()
      .then((res) => {
        if (!mounted) return;
        const external = (res.data?.external || []) as CombinedReport[];
        const internal = (res.data?.internal || []) as CombinedReport[];
        setReports([...external, ...internal]);
      })
      .catch(() => mounted && setReports([]))
      .finally(() => mounted && setLoading(false));
    return () => { mounted = false; };
  }, []);

  const items = useMemo(() => {
    return reports
      .map((r, idx) => ({
        raw: r,
        id: `${idx}`,
        img: buildImageUrl(Array.isArray(r.photos) && r.photos.length > 0 ? r.photos[0] : undefined),
        title: r?.eventId?.title || `Report ${idx + 1}`,
        desc: truncate(r?.narrative, 120),
      }))
      .filter((x) => x.img)
      .slice(0, limit);
  }, [reports, limit]);

  return (
    <Section>
      <Header>
        <Title>{title}</Title>
      </Header>
      {loading ? (
        <Typography color="text.secondary">Loading…</Typography>
      ) : items.length === 0 ? (
        <Typography color="text.secondary">No reports with photos yet.</Typography>
      ) : (
        <Grid>
          {items.map((it) => (
            <Card key={it.id} onClick={() => onOpenReport && onOpenReport(it.raw)}>
              <Thumb src={it.img} alt="report" loading="lazy" crossOrigin="anonymous" />
              <Body>
                <Headline>{it.title}</Headline>
                {it.desc && <Excerpt>{it.desc}</Excerpt>}
              </Body>
            </Card>
          ))}
        </Grid>
      )}
    </Section>
  );
};

export default PhotoThumbnailGrid;

















































