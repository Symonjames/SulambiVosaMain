import { Box, Typography, CircularProgress } from "@mui/material";
import { useEffect, useState, useContext } from "react";
import TextHeader from "../../components/Headers/TextHeader";
import TextSubHeader from "../../components/Headers/TextSubHeader";
import PageLayout from "../PageLayout";
import FlexBox from "../../components/FlexBox";
import { getAllEvents } from "../../api/events";
import MediaCard from "../../components/Cards/MediaCard";
import HorizontalCarousel from "../../components/Carousel/HorizontalCarousel";
import { useMediaQuery } from "react-responsive";
import { ExternalEventProposalType, InternalEventProposalType } from "../../interface/types";
import FormPreviewDetails from "../../components/Forms/FormPreviewDetails";
import RequirementForm from "../../components/Forms/RequirementForm";
import { FormDataContext } from "../../contexts/FormDataProvider";
import { useCachedFetch } from "../../hooks/useCachedFetch";
import { CACHE_TIMES } from "../../utils/apiCache";

const EventsPage = () => {
  const { setFormData } = useContext(FormDataContext);
  const [openPreview, setOpenPreview] = useState(false);
  const [previewData, setPreviewData] = useState<any>({});
  const [openRequirementForm, setOpenRequirementForm] = useState(false);
  const [selectedEventId, setSelectedEventId] = useState<number | undefined>(undefined);
  const [selectedEventType, setSelectedEventType] = useState<"external" | "internal">("external");
  
  const isMobile = useMediaQuery({
    query: "(max-width: 600px)",
  });

  // Use cached fetch - data persists when navigating away and coming back!
  const { data: eventsResponse, loading } = useCachedFetch({
    cacheKey: 'events_all',
    fetchFn: () => getAllEvents(),
    cacheTime: CACHE_TIMES.MEDIUM, // Cache for 5 minutes
    useMemoryCache: true, // Fast memory cache for navigation
  });

  // Process events data
  const events = eventsResponse
    ? [
        ...(eventsResponse.external || []),
        ...(eventsResponse.internal || []),
      ]
    : [];

  const viewDataCallback = (eventData: any) => {
    return () => {
      setPreviewData(eventData);
      setOpenPreview(true);
    };
  };

  const volunteerCallback = (eventData: any) => {
    return () => {
      // Determine event type
      const eventType = (eventData as ExternalEventProposalType).location ? "external" : "internal";
      setSelectedEventType(eventType);
      setSelectedEventId(eventData.id);
      setFormData({});
      setOpenRequirementForm(true);
    };
  };

  return (
    <PageLayout page="events">
      <FormPreviewDetails
        open={openPreview}
        eventData={previewData}
        setOpen={setOpenPreview}
      />
      {selectedEventId && (
        <RequirementForm
          preventLoadingCache
          eventId={selectedEventId}
          open={openRequirementForm}
          eventType={selectedEventType}
          setOpen={setOpenRequirementForm}
          afterOpen={() => {
            setFormData({});
          }}
        />
      )}
      
      <TextHeader>Events</TextHeader>
      <TextSubHeader gutterBottom>
        View and participate in exclusive member events.
      </TextSubHeader>

      {loading ? (
        <FlexBox
          width="100%"
          minHeight="60vh"
          justifyContent="center"
          alignItems="center"
        >
          <CircularProgress />
        </FlexBox>
      ) : events.length === 0 ? (
        <FlexBox
          width="100%"
          minHeight="60vh"
          justifyContent="center"
          alignItems="center"
        >
          <Box textAlign="center">
            <Typography variant="h6" color="text.secondary">
              No events are available at the moment.
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              Please check back soon for upcoming activities.
            </Typography>
          </Box>
        </FlexBox>
      ) : (
        <FlexBox
          width="100%"
          gap="20px"
          flexWrap="wrap"
          justifyContent="flex-start"
          marginTop="20px"
        >
          {events.length > 0 &&
          ((isMobile && events.length >= 2) || events.length > 4) ? (
            <HorizontalCarousel>
              {events.map((event, id) => (
                <MediaCard
                  key={id}
                  width={isMobile ? "73vw" : "20vw"}
                  cardTitle={event.title}
                  location={(event as ExternalEventProposalType).location ?? (event as InternalEventProposalType).venue ?? ""}
                  onViewDetails={viewDataCallback(event)}
                  onVolunteer={volunteerCallback(event)}
                />
              ))}
            </HorizontalCarousel>
          ) : (
            events.map((event, id) => (
              <MediaCard
                key={id}
                width={isMobile ? "auto" : "20vw"}
                cardTitle={event.title}
                location={(event as ExternalEventProposalType).location ?? (event as InternalEventProposalType).venue ?? ""}
                onViewDetails={viewDataCallback(event)}
                onVolunteer={volunteerCallback(event)}
              />
            ))
          )}
        </FlexBox>
      )}
    </PageLayout>
  );
};

export default EventsPage;
