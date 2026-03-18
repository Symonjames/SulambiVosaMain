import { useContext, useEffect, useState } from "react";
import { getPersonalEvaluation } from "../../api/evaluation";
import { ParticipationHistoryType } from "../../interface/types";

import TextHeader from "../../components/Headers/TextHeader";
import TextSubHeader from "../../components/Headers/TextSubHeader";
import DataTable from "../../components/Tables/DataTable";
import PageLayout from "../PageLayout";

import MenuButtonTemplate from "../../components/Menu/MenuButtonTemplate";
import Chip from "../../components/Chips/Chip";

import ArticleIcon from "@mui/icons-material/Article";
import EventAvailableIcon from "@mui/icons-material/EventAvailable";
import RequirementForm from "../../components/Forms/RequirementForm";
import { FormDataContext } from "../../contexts/FormDataProvider";
import CustomDropdown from "../../components/Inputs/CustomDropdown";
import FormPreviewDetails from "../../components/Forms/FormPreviewDetails";

const ParticipationHistory = () => {
  const { formData, setFormData } = useContext(FormDataContext);

  const [data, setData] = useState<any[]>([]);
  const [searchStatus, setSearchStatus] = useState("");

  const [openReqForm, setOpenReqForm] = useState(false);
  const [openEventForm, setOpenEventForm] = useState(false);
  const [currentEventType, setCurrentEventType] = useState<any>();

  const ModComponents = [
    <CustomDropdown
      label="Attendance Status"
      width="200px"
      onChange={(event) => setSearchStatus(event.target.value)}
      menu={[
        { key: "All", value: "" },
        { key: "Not Attended", value: "not-attended" },
        { key: "Registered", value: "registered" },
        { key: "Attended", value: "attended" },
      ]}
    />,
  ];

  const chipMap = {
    "not-attended": (
      <Chip bgcolor="#c10303" label="not-attended" color="white" />
    ),
    registered: <Chip bgcolor="#a3a300" label="registered" color="white" />,
    attended: <Chip bgcolor="#2f7a00" label="attended" color="white" />,
  };

  useEffect(() => {
    getPersonalEvaluation().then((response) => {
      const responseData: ParticipationHistoryType[] = response.data.data;
      setData(
        responseData
          .filter((personal) => {
            if (searchStatus === "") return true;
            return personal.attendanceStatus === searchStatus;
          })
          .map((personal) => {
            return [
              personal.event.title,
              personal.eventType,
              chipMap[personal.attendanceStatus],
              <MenuButtonTemplate
                items={[
                  {
                    label: "View Event Details",
                    icon: <EventAvailableIcon />,
                    onClick: () => {
                      setFormData(personal.event);
                      setCurrentEventType(personal.eventType);
                      setOpenEventForm(true);
                    },
                  },
                  {
                    label: "View Requirements",
                    icon: <ArticleIcon />,
                    onClick: () => {
                      setFormData(personal.requirement);
                      setCurrentEventType(personal.eventType);
                      setOpenReqForm(true);
                    },
                  },
                ]}
              />,
            ];
          })
      );
    });
  }, [searchStatus]);

  return (
    <>
      <RequirementForm
        preventLoadingCache
        viewOnly
        eventId={0}
        open={openReqForm}
        eventType={currentEventType}
        setOpen={setOpenReqForm}
      />
      {/* <FormDataLoaderModal
        data={formData}
        open={openEventForm}
        setOpen={setOpenEventForm}
        formType={
          currentEventType === "external" ? "externalEvent" : "internalEvent"
        }
      /> */}
      <FormPreviewDetails
        open={openEventForm}
        eventData={formData}
        setOpen={setOpenEventForm}
      />
      <PageLayout page="participation">
        <TextHeader>Participation History</TextHeader>
        <TextSubHeader>Check your participation status here</TextSubHeader>
        <DataTable
          title="Participation History"
          fields={["Event Title", "Event Type", "Attendance Status", "Actions"]}
          data={data}
          componentBeforeSearch={ModComponents}
        />
      </PageLayout>
    </>
  );
};

export default ParticipationHistory;
