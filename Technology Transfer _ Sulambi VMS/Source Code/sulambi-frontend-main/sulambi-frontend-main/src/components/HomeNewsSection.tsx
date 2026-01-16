import React, { useEffect, useMemo, useState } from "react";
import { Box, Typography, styled } from "@mui/material";
import { getAllReports } from "../api/reports";
import { InternalReportType, ExternalReportType } from "../interface/types";

// Build base URL like PhotoThumbnailCarousel
const getBaseUrl = (): string => {
  const apiUri = (import.meta as any).env.VITE_API_URI as string | undefined;
  if (apiUri) return apiUri.replace("/api", "");
  if ((import.meta as any).env.DEV) return "http://localhost:8000";
  return window.location.origin;
};

const BASE_URL = getBaseUrl();

const Section = styled(Box)({
  width: "100%",
  marginTop: "56px",
});

const SectionHeader = styled(Box)({
  width: "100%",
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
  marginBottom: "16px",
});

const SectionTitle = styled(Typography)({
  fontSize: "26px",
  fontWeight: 800,
  color: "#111827",
});

const Grid = styled(Box)({
  display: "grid",
  gridTemplateColumns: "repeat(4, 1fr)",
  gap: "24px",
  "@media (max-width: 1024px)": {
    gridTemplateColumns: "repeat(2, 1fr)",
  },
  "@media (max-width: 600px)": {
    gridTemplateColumns: "repeat(1, 1fr)",
  },
});

const Card = styled(Box)({
  display: "flex",
  flexDirection: "column",
  border: "1px solid rgba(0,0,0,0.08)",
  borderRadius: "8px",
  overflow: "hidden",
  backgroundColor: "#fff",
  transition: "box-shadow .15s ease",
  boxShadow: "0 0 0 0 rgba(0,0,0,0)",
  ':hover': {
    boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
  }
});

const Thumbnail = styled("img")({
  width: "100%",
  aspectRatio: "16/9",
  objectFit: "cover",
  display: "block",
  backgroundColor: "#f3f4f6",
});

const CardBody = styled(Box)({
  padding: "12px",
});

const Headline = styled(Typography)({
  fontSize: "15px",
  fontWeight: 800,
  lineHeight: 1.35,
  color: "#111827",
  marginBottom: "6px",
});

const Excerpt = styled(Typography)({
  fontSize: "12px",
  color: "#6b7280",
  lineHeight: 1.5,
});

type CombinedReport = (InternalReportType | ExternalReportType) & {
  photos?: string[];
  narrative?: string;
  eventId?: any;
};

const buildImageUrl = (filename: string): string => {
  if (!filename) return "";
  let clean = filename.trim();
  try { clean = decodeURIComponent(clean); } catch {}
  
  // Check if it's already a Cloudinary URL or other full URL
  if (clean.startsWith("http://") || clean.startsWith("https://")) {
    // Use Cloudinary URL or other full URL directly
    return clean;
  }
  
  clean = clean.replace(/\\\\/g, "/");
  if (clean.startsWith("uploads/")) clean = clean.replace(/^uploads[\\/\\\\]/, "");
  return `${BASE_URL}/uploads/${clean}?t=${Date.now()}`;
};

const truncate = (text: string | undefined, max = 120): string => {
  if (!text) return "";
  const t = text.trim();
  return t.length > max ? `${t.slice(0, max - 1)}…` : t;
};

const HomeNewsSection: React.FC = () => {
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
    return () => {
      mounted = false;
    };
  }, []);

  const items = useMemo(() => {
    return reports
      .map((r, idx) => {
        const firstPhoto = Array.isArray(r.photos) && r.photos.length > 0 ? r.photos[0] : undefined;
        const imageUrl = firstPhoto ? buildImageUrl(firstPhoto) : "";
        const title = r?.eventId?.title || `Report ${idx + 1}`;
        const desc = truncate(r?.narrative || "", 110);
        return { id: `${idx}`, imageUrl, title, desc };
      })
      .filter((x) => x.imageUrl)
      .slice(0, 8);
  }, [reports]);

  if (loading) {
    return (
      <Section>
        <SectionHeader>
          <SectionTitle>Latest Reports</SectionTitle>
        </SectionHeader>
        <Typography color="text.secondary">Loading news…</Typography>
      </Section>
    );
  }

  if (items.length === 0) {
    return (
      <Section>
        <SectionHeader>
          <SectionTitle>Latest Reports</SectionTitle>
        </SectionHeader>
        <Typography color="text.secondary">No recent reports with photos.</Typography>
      </Section>
    );
  }

  return (
    <Section>
      <SectionHeader>
        <SectionTitle>Latest Reports</SectionTitle>
      </SectionHeader>
      <Grid>
        {items.map((item) => (
          <Card key={item.id}>
            {item.imageUrl && <Thumbnail src={item.imageUrl} alt="report" loading="lazy" crossOrigin="anonymous" />}
            <CardBody>
              <Headline>{item.title}</Headline>
              {item.desc && <Excerpt>{item.desc}</Excerpt>}
            </CardBody>
          </Card>
        ))}
      </Grid>
    </Section>
  );
};

export default HomeNewsSection;


