import React, { useEffect, useMemo, useState } from "react";
import { Box, Typography, Chip, Stack } from "@mui/material";
import { getAllReports } from "../../api/reports";

const BASE_URL = (import.meta as any).env.VITE_API_URI
  ? (import.meta as any).env.VITE_API_URI.replace("/api", "")
  : "http://localhost:8000";

type Check = { label: string; ok: boolean; details?: string };

const NewsThumbnailValidator: React.FC = () => {
  const [checks, setChecks] = useState<Check[]>([]);
  const [sampleImage, setSampleImage] = useState<string>("");

  useEffect(() => {
    const run = async () => {
      const results: Check[] = [];

      // 1) Env and export
      results.push({ label: `BASE_URL resolved: ${BASE_URL}`, ok: !!BASE_URL });

      // 2) API reachable and data shape
      try {
        const res = await getAllReports();
        const data = res?.data || {};
        const combined = [...(data.external || []), ...(data.internal || [])];
        results.push({ label: `GET /reports responded`, ok: true });
        results.push({ label: `Reports count: ${combined.length}`, ok: combined.length >= 0 });

        const first = combined[0];
        if (first) {
          const hasPhotos = Array.isArray(first.photos) && first.photos.length > 0;
          const eventName = first.event_name || first?.eventId?.title;
          const narrative = first.narrative_report || first.narrative;
          results.push({ label: `First report has photos[]`, ok: hasPhotos });
          results.push({ label: `Has event name`, ok: !!eventName, details: String(eventName || "") });
          results.push({ label: `Has narrative`, ok: typeof narrative === 'string', details: narrative ? narrative.slice(0, 60) : "" });

          if (hasPhotos) {
            const filename = String(first.photos[0]).trim().replace(/^uploads[\\/]/, "");
            const url = `${BASE_URL}/uploads/${filename}?t=${Date.now()}`;
            setSampleImage(url);
            results.push({ label: `Image URL constructed`, ok: true, details: url });
          }
        } else {
          results.push({ label: `No reports returned`, ok: false });
        }
      } catch (e: any) {
        results.push({ label: `GET /reports failed`, ok: false, details: e?.message || String(e) });
      }

      setChecks(results);
      // eslint-disable-next-line no-console
      console.log("[NewsThumbnailValidator] Checks:", results);
    };
    run();
  }, []);

  const allOk = useMemo(() => checks.every((c) => c.ok), [checks]);

  return (
    <Box sx={{ border: "1px dashed #cbd5e1", padding: "12px", borderRadius: "8px", background: "#f8fafc" }}>
      <Typography variant="subtitle1" fontWeight={700} gutterBottom>
        NewsThumbnail Validator
      </Typography>
      <Stack direction="column" spacing={1}>
        {checks.map((c, i) => (
          <Stack key={i} direction="row" spacing={1} alignItems="center">
            <Chip size="small" label={c.ok ? "PASS" : "FAIL"} color={c.ok ? "success" : "error"} />
            <Typography variant="body2">
              {c.label} {c.details ? `— ${c.details}` : ""}
            </Typography>
          </Stack>
        ))}
      </Stack>
      {sampleImage && (
        <Box sx={{ marginTop: "8px" }}>
          <Typography variant="caption" color="text.secondary">Sample image preview:</Typography>
          <Box component="img" src={sampleImage} alt="sample" sx={{ width: 240, height: 135, objectFit: "cover", display: "block", borderRadius: "6px", border: "1px solid #e5e7eb", marginTop: "6px" }} />
        </Box>
      )}
      <Typography variant="body2" sx={{ marginTop: "8px" }} color={allOk ? "success.main" : "error.main"}>
        {allOk ? "All checks passed." : "Some checks failed. See details above and console for logs."}
      </Typography>
    </Box>
  );
};

export default NewsThumbnailValidator;

















































