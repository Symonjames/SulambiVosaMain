import React, { useEffect, useState, useRef } from "react";
import { Box, Typography, styled, IconButton } from "@mui/material";
import ArrowBackIosIcon from "@mui/icons-material/ArrowBackIos";
import ArrowForwardIosIcon from "@mui/icons-material/ArrowForwardIos";
import { getAllReports } from "../api/reports";
import { InternalReportType, ExternalReportType } from "../interface/types";
import FormDataLoaderModal from "./Modal/FormDataLoaderModal";
import NewsFeedEventModal from "./Popups/NewsFeedEventModal";

const getBaseUrl = (): string => {
  const apiUri = (import.meta as any).env.VITE_API_URI as string | undefined;
  if (apiUri) return apiUri.replace("/api", "");
  if ((import.meta as any).env.DEV) return "http://localhost:8000";
  return window.location.origin;
};
const BASE_URL = getBaseUrl();

// Nation-style news grid container
const Section = styled(Box)({ 
  width: "100%", 
  marginTop: "24px" 
});

const Header = styled(Box)({ 
  marginBottom: "20px" 
});

const Subtitle = styled(Typography)({ 
  fontSize: "14px", 
  fontWeight: 400, 
  color: "#7A8C7A",
  marginBottom: "16px",
  textTransform: "none"
});

const Title = styled(Typography)({ 
  fontSize: "28px", 
  fontWeight: 700, 
  color: "#4F624F",
  marginBottom: "8px",
  letterSpacing: "-0.025em"
});

// Carousel Container with sliding animation
const CarouselContainer = styled(Box)({
  position: "relative",
  width: "100%",
  overflow: "hidden",
  borderRadius: "12px",
});

const CarouselTrack = styled(Box)({
  display: "flex",
  transition: "transform 0.6s cubic-bezier(0.4, 0, 0.2, 1)",
  willChange: "transform",
});

const CarouselItem = styled(Box)({
  width: "calc(33.333% - 12px)",
  minWidth: "calc(33.333% - 12px)",
  maxWidth: "calc(33.333% - 12px)",
  flexShrink: 0,
  padding: "0 6px",
  "@media (max-width: 1024px)": {
    width: "calc(50% - 8px)",
    minWidth: "calc(50% - 8px)",
    maxWidth: "calc(50% - 8px)",
  },
  "@media (max-width: 600px)": {
    width: "calc(100% - 8px)",
    minWidth: "calc(100% - 8px)",
    maxWidth: "calc(100% - 8px)",
  },
});

// Calculate card width for smooth sliding (one card at a time)
const getCardWidth = () => {
  if (typeof window !== 'undefined') {
    if (window.innerWidth <= 600) return 100;
    if (window.innerWidth <= 1024) return 50;
    return 33.333; // 3 cards = 33.333% each
  }
  return 33.333;
};

const NavigationButton = styled(IconButton)({
  position: "absolute",
  top: "50%",
  transform: "translateY(-50%)",
  zIndex: 10,
  backgroundColor: "rgba(255, 255, 255, 0.9)",
  boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
  "&:hover": {
    backgroundColor: "rgba(255, 255, 255, 1)",
    boxShadow: "0 4px 12px rgba(0,0,0,0.25)",
  },
  "&:disabled": {
    backgroundColor: "rgba(255, 255, 255, 0.5)",
    opacity: 0.5,
  },
});

const LeftButton = styled(NavigationButton)({
  left: "16px",
  "@media (max-width: 768px)": {
    left: "8px",
  },
});

const RightButton = styled(NavigationButton)({
  right: "16px",
  "@media (max-width: 768px)": {
    right: "8px",
  },
});

const IndicatorContainer = styled(Box)({
  display: "flex",
  justifyContent: "center",
  gap: "8px",
  marginTop: "20px",
});

const Indicator = styled(Box)<{ $active: boolean }>(({ $active }) => ({
  width: $active ? "24px" : "8px",
  height: "8px",
  borderRadius: "4px",
  backgroundColor: $active ? "#4F624F" : "#d0d0d0",
  transition: "all 0.3s ease",
  cursor: "pointer",
  "&:hover": {
    backgroundColor: $active ? "#4F624F" : "#a0a0a0",
  },
}));

const Card = styled(Box)({
  display: "flex",
  flexDirection: "column",
  border: "1px solid #e0e0e0",
  borderRadius: "6px",
  overflow: "hidden",
  backgroundColor: "#fffbf3",
  cursor: "pointer",
  transition: "all 0.3s ease",
  boxShadow: "0 1px 2px rgba(0,0,0,0.05)",
  position: "relative",
  zIndex: 1,
  width: "100%",
  height: "250px",
  minHeight: "250px",
  maxHeight: "250px",
  ':hover': { 
    boxShadow: "0 2px 4px rgba(0,0,0,0.08)",
    transform: "translateY(-1px)",
    borderColor: "#d0d0d0",
    backgroundColor: "#fff8e1"
  },
  ':active': {
    transform: "translateY(0px)",
    boxShadow: "0 1px 2px rgba(0,0,0,0.06)"
  }
});

const Thumb = styled("img")({ 
  width: "calc(100% - 8px)", 
  height: "140px",
  minHeight: "140px",
  maxHeight: "140px",
  objectFit: "cover", 
  background: "#f3f4f6",
  border: "1px solid #f0f0f0",
  borderRadius: "4px",
  margin: "4px",
  boxShadow: "0 1px 2px rgba(0,0,0,0.06)",
  flexShrink: 0,
  display: "block"
});

const Body = styled(Box)({ 
  padding: "4px 8px",
  flex: 1,
  display: "flex",
  flexDirection: "column",
  justifyContent: "flex-start",
  overflow: "hidden",
  minHeight: 0
});

const Headline = styled(Typography)({ 
  fontSize: "12px", 
  fontWeight: 700, 
  color: "#111827",
  lineHeight: 1.2,
  marginBottom: "4px",
  overflow: "hidden",
  textOverflow: "ellipsis",
  display: "-webkit-box",
  WebkitLineClamp: 2,
  WebkitBoxOrient: "vertical",
  wordBreak: "break-word"
});

const Divider = styled(Box)({
  height: "1px",
  backgroundColor: "#e5e7eb",
  margin: "3px 0"
});

const Excerpt = styled(Typography)({ 
  fontSize: "10px", 
  color: "#6b7280", 
  lineHeight: 1.2,
  display: "-webkit-box",
  WebkitLineClamp: 2,
  WebkitBoxOrient: "vertical",
  overflow: "hidden"
});

type CombinedReport = (InternalReportType | ExternalReportType) & Record<string, any>;

const buildImageUrl = (filename?: string) => {
  if (!filename) {
    console.log('[NewsThumbnailCarousel] No filename provided');
    return "";
  }
  let clean = filename.trim();
  try { clean = decodeURIComponent(clean); } catch {}
  
  // Check if it's already a Cloudinary URL or other full URL
  if (clean.startsWith("http://") || clean.startsWith("https://")) {
    // Use Cloudinary URL or other full URL directly
    return clean;
  }
  
  // Convert Windows backslashes to forward slashes
  clean = clean.replace(/\\/g, "/");
  // Remove any leading "uploads/" or "uploads\" to avoid double uploads
  clean = clean.replace(/^uploads[\/\\]/, "");
  const finalUrl = `${BASE_URL}/uploads/${clean}?t=${Date.now()}`;
  console.log('[NewsThumbnailCarousel] Built image URL:', { original: filename, cleaned: clean, final: finalUrl });
  return finalUrl;
};

const truncate = (t?: string, n = 120) => {
  if (!t) return "";
  const s = t.trim();
  return s.length > n ? `${s.slice(0, n - 1)}…` : s;
};

const truncateWords = (text?: string, maxWords = 6) => {
  if (!text) return "";
  const words = text.trim().split(/\s+/);
  if (words.length <= maxWords) return text;
  return words.slice(0, maxWords).join(" ") + "...";
};

interface Props { title?: string; limit?: number; }

const NewsThumbnailCarousel: React.FC<Props> = ({ title = "Latest News", limit = 5 }) => {
  const [items, setItems] = useState<Array<{ id: string; img: string; title: string; desc: string; rawHtml: string; reportData: any; reportType: "external" | "internal" }>>([]);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [selectedReportType, setSelectedReportType] = useState<"external" | "internal">("external");
  const [formPreviewOpen, setFormPreviewOpen] = useState(false);
  const [newsFeedModalOpen, setNewsFeedModalOpen] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const autoPlayIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  


  const handleCardClick = (item: { id: string; img: string; title: string; desc: string; rawHtml: string; reportData: any; reportType: "external" | "internal" }) => {
    if (!item.reportData) return;
    
    setSelectedReport(item.reportData);
    setSelectedReportType(item.reportType);
    setNewsFeedModalOpen(true);
  };

  // Calculate how many items to show at once (always 3 on desktop, responsive on smaller screens)
  const getItemsPerView = () => {
    if (typeof window !== 'undefined') {
      if (window.innerWidth <= 600) return 1;
      if (window.innerWidth <= 1024) return 2;
      return 3;
    }
    return 3;
  };

  const [itemsPerView] = useState(getItemsPerView());
  
  // Create extended array for seamless infinite scrolling
  // Duplicate items to create: [1,2,3,4,5,1,2,3,4,5] for smooth looping
  const extendedItems = items.length > 0 ? [...items, ...items] : [];

  const nextSlide = () => {
    if (items.length === 0) return;
    setCurrentIndex((prevIndex) => {
      // When we reach the end of original items, reset to 0 seamlessly
      if (prevIndex >= items.length - 1) {
        return 0;
      }
      return prevIndex + 1;
    });
  };

  const prevSlide = () => {
    if (items.length === 0) return;
    setCurrentIndex((prevIndex) => {
      if (prevIndex <= 0) {
        return items.length - 1;
      }
      return prevIndex - 1;
    });
  };

  const goToSlide = (index: number) => {
    setCurrentIndex(index);
  };

  // Auto-cycle: slide by one card every 1 second
  // Start after 1 second delay to show initial 3 events first
  useEffect(() => {
    if (items.length === 0 || items.length <= itemsPerView) return;

    // Clear existing interval and timeout
    if (autoPlayIntervalRef.current) {
      clearInterval(autoPlayIntervalRef.current);
    }

    // Initial delay: wait 1 second before starting auto-slide
    const initialDelay = setTimeout(() => {
      // Set up auto-play: slide one card every 5 seconds
      autoPlayIntervalRef.current = setInterval(() => {
        setCurrentIndex((prevIndex) => {
          // Loop back to 0 when we've shown all events
          if (prevIndex >= items.length - 1) {
            return 0;
          }
          return prevIndex + 1;
        });
      }, 5000); // 5 second interval between slides
    }, 1000); // Wait 1 second before starting

    // Cleanup on unmount or when items change
    return () => {
      clearTimeout(initialDelay);
      if (autoPlayIntervalRef.current) {
        clearInterval(autoPlayIntervalRef.current);
      }
    };
  }, [items.length, itemsPerView]);

  // Reset to first slide when items change
  useEffect(() => {
    setCurrentIndex(0);
  }, [items.length]);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    
    getAllReports()
      .then((res) => {
        if (!mounted) return;
        
        const ext = (res.data?.external || []) as CombinedReport[];
        const intr = (res.data?.internal || []) as CombinedReport[];
        
        // Map external reports
        const extMapped = ext.map((r, i) => {
          const firstPhoto = Array.isArray(r.photos) && r.photos.length > 0 ? r.photos[0] : undefined;
          const img = buildImageUrl(firstPhoto);
          const eventName = r?.eventId?.title || r.event_name || `External Report ${i + 1}`;
          const narrative = r.narrative || r.narrative_report || "";
          
          return { 
            id: `ext-${i}`, 
            img, 
            title: eventName, 
            desc: truncate(narrative, 120),
            rawHtml: narrative,
            reportData: r,
            reportType: "external" as const
          };
        });
        
        // Map internal reports
        const intrMapped = intr.map((r, i) => {
          const firstPhoto = Array.isArray(r.photos) && r.photos.length > 0 ? r.photos[0] : undefined;
          const img = buildImageUrl(firstPhoto);
          const eventName = r?.eventId?.title || r.event_name || `Internal Report ${i + 1}`;
          const narrative = r.narrative || r.narrative_report || "";
          
          return { 
            id: `int-${i}`, 
            img, 
            title: eventName, 
            desc: truncate(narrative, 120),
            rawHtml: narrative,
            reportData: r,
            reportType: "internal" as const
          };
        });
        
        const combined = [...extMapped, ...intrMapped];
        
        // Sort by event creation date (most recent first)
        // Only show events that have reports with photos
        const sorted = combined
          .filter((x) => x.img && x.img.length > 0 && x.reportData?.eventId) // Ensure event exists
          .sort((a, b) => {
            // Get creation date from event (preferred) or use report id as fallback
            const getDateValue = (item: typeof a) => {
              const eventDate = item.reportData?.eventId?.createdAt;
              if (eventDate) {
                // Handle both number (timestamp) and string dates
                return typeof eventDate === 'number' ? eventDate : new Date(eventDate).getTime();
              }
              // Fallback to report id (higher id = newer)
              return item.reportData?.id || 0;
            };
            
            const dateA = getDateValue(a);
            const dateB = getDateValue(b);
            // Sort descending (newest first)
            return dateB - dateA;
          });
        
        // Take only the 5 most recent events with reports
        // This automatically "archives" older events when new ones are added
        const mapped = sorted.slice(0, limit);
        
        setItems(mapped);
      })
      .catch((error) => {
        console.error('[NewsThumbnailCarousel] Error fetching reports:', error);
        setItems([]);
      })
      .finally(() => mounted && setLoading(false));
    return () => { mounted = false; };
  }, [limit]);

  return (
    <Section>
      <Header>
        <Title>{title}</Title>
        <Subtitle>View latest reports and updates</Subtitle>
      </Header>
      {loading ? (
        <Typography color="text.secondary">Loading…</Typography>
      ) : items.length === 0 ? (
        <Box>
          <Typography color="text.secondary" gutterBottom>
            No reports with photos yet.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Debug: Check console for API response details.
          </Typography>
        </Box>
      ) : (
        <CarouselContainer>
          <CarouselTrack
            sx={{
              transform: `translateX(-${currentIndex * (getCardWidth())}%)`,
            }}
          >
            {extendedItems.map((item, index) => (
              <CarouselItem key={`${item.id}-${index}`}>
                <Card 
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    handleCardClick(item);
                  }}
                  sx={{
                    cursor: 'pointer',
                    ':hover': {
                      boxShadow: "0 4px 8px rgba(0,0,0,0.12)",
                      transform: "translateY(-2px)",
                      borderColor: "#d0d0d0",
                      backgroundColor: "#fff8e1"
                    }
                  }}
                >
                  <Thumb 
                    src={item.img} 
                    alt={item.title} 
                    loading="lazy" 
                    crossOrigin="anonymous"
                    onError={(e) => {
                      // Fallback for broken images - show placeholder
                      const target = e.target as HTMLImageElement;
                      target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5YTNhZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPk5vIEltYWdlPC90ZXh0Pjwvc3ZnPg==';
                    }}
                  />
                  <Body>
                    <Headline>{truncateWords(item.title, 6)}</Headline>
                    <Divider />
                    {item.rawHtml && (
                      <Excerpt 
                        dangerouslySetInnerHTML={{ __html: item.rawHtml }}
                      />
                    )}
                  </Body>
                </Card>
              </CarouselItem>
            ))}
          </CarouselTrack>

          {/* Navigation Arrows */}
          {items.length > itemsPerView && (
            <>
              <LeftButton
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  prevSlide();
                }}
                aria-label="Previous event"
              >
                <ArrowBackIosIcon />
              </LeftButton>
              <RightButton
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  nextSlide();
                }}
                aria-label="Next event"
              >
                <ArrowForwardIosIcon />
              </RightButton>
            </>
          )}

          {/* Indicator Dots - Show one dot per event */}
          {items.length > itemsPerView && (
            <IndicatorContainer>
              {items.map((_, index) => (
                <Indicator
                  key={index}
                  $active={index === currentIndex}
                  onClick={() => goToSlide(index)}
                  aria-label={`Go to event ${index + 1}`}
                />
              ))}
            </IndicatorContainer>
          )}
        </CarouselContainer>
      )}
      
      {/* News Feed Event Modal - Calendar Event Style */}
      {selectedReport && (
        <NewsFeedEventModal
          reportData={selectedReport}
          reportType={selectedReportType}
          open={newsFeedModalOpen}
          setOpen={setNewsFeedModalOpen}
        />
      )}
      
      {/* Form Preview Modal for print view (kept for backwards compatibility) */}
      {selectedReport && formPreviewOpen && (
        <FormDataLoaderModal
          formType={selectedReportType === "external" ? "externalReport" : "internalReport"}
          data={selectedReport}
          open={formPreviewOpen}
          setOpen={setFormPreviewOpen}
          hidePrintButton={false}
        />
      )}
    </Section>
  );
};

export default NewsThumbnailCarousel;


