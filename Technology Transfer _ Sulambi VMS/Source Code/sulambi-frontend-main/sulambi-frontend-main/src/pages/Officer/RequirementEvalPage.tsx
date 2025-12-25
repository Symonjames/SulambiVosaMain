import { useContext, useEffect, useState } from "react";
import TextHeader from "../../components/Headers/TextHeader";
import TextSubHeader from "../../components/Headers/TextSubHeader";
import DataTable from "../../components/Tables/DataTable";
import PageLayout from "../PageLayout";
import {
  acceptRequirement,
  getAllRequirements,
  rejectRequirement,
} from "../../api/requirements";
import { RequirementsDataType } from "../../interface/types";
import Chip from "../../components/Chips/Chip";
import MenuButtonTemplate from "../../components/Menu/MenuButtonTemplate";

import RemoveRedEyeIcon from "@mui/icons-material/RemoveRedEye";
import ThumbDownIcon from "@mui/icons-material/ThumbDown";
import ThumbUpIcon from "@mui/icons-material/ThumbUp";
import { SnackbarContext } from "../../contexts/SnackbarProvider";
// import { IconButton } from "@mui/material";
import InsertDriveFileIcon from "@mui/icons-material/InsertDriveFile";
import RequirementForm from "../../components/Forms/RequirementForm";
import { FormDataContext } from "../../contexts/FormDataProvider";
import CustomDropdown from "../../components/Inputs/CustomDropdown";
import { useNavigate } from "react-router-dom";

const RequirementEvalPage = () => {
  const { showSnackbarMessage } = useContext(SnackbarContext);
  const { setFormData } = useContext(FormDataContext);
  const navigate = useNavigate();

  const [searchStatus, setSearchStatus] = useState(3);
  const [searchVal, setSearchVal] = useState("");
  const [tableData, setTableData] = useState<any[]>([]);
  const [forceRefresh, setForceRefresh] = useState(0);

  const [selectedFormData, setSelectedFormData] = useState<any>({});
  const [viewFormData, setViewFormData] = useState(false);

  useEffect(() => {
    getAllRequirements()
      .then((response) => {
        // Ensure response has the expected structure
        if (!response?.data?.data) {
          console.warn("Invalid response structure:", response);
          setTableData([]);
          return;
        }

        const requirementsData: RequirementsDataType[] = response.data.data;

        // Check if requirementsData is an array
        if (!Array.isArray(requirementsData)) {
          console.warn("Requirements data is not an array:", requirementsData);
          setTableData([]);
          return;
        }

        console.log("Fetched requirements:", requirementsData.length, "items");
        console.log("Raw requirements data:", requirementsData);
        console.log("Current search filter:", { searchVal, searchStatus });

      const chipMap = {
        notEvaluated: (
          <Chip bgcolor="blue" label="not-evaluated" color="white" />
        ),
        approved: <Chip bgcolor="#2f7a00" label="approved" color="white" />,
        rejected: <Chip bgcolor="#c10303" label="rejected" color="white" />,
      };

      // Log each requirement before filtering
      requirementsData.forEach((req, index) => {
        console.log(`Requirement ${index}:`, {
          id: req.id,
          eventId: req.eventId,
          eventTitle: req.eventId?.title,
          fullname: req.fullname,
          email: req.email,
          type: req.type,
          accepted: req.accepted,
        });
      });

      const afterSearchFilter = requirementsData
          .filter((req) => {
            // If searchVal is empty, show all items
            if (!searchVal || searchVal.trim() === "") return true;
            
            // Handle cases where eventId might be null or undefined
            const eventTitle = req.eventId?.title || "Unknown Event";
            const fullname = req.fullname || "";
            const srcode = req.srcode || "";
            const collegeDept = req.collegeDept || "";
            const searchLower = searchVal.toLowerCase();
            return (
              eventTitle.toLowerCase().includes(searchLower) ||
              fullname.toLowerCase().includes(searchLower) ||
              srcode.toLowerCase().includes(searchLower) ||
              collegeDept.toLowerCase().includes(searchLower)
            );
          });
      
      console.log("After search filter:", afterSearchFilter.length, "requirements");
      
      const afterStatusFilter = afterSearchFilter
          .filter((req) => {
            if (searchStatus === 3) return true; // Show all
            if (searchStatus === 2) {
              // Show not evaluated (null or undefined)
              return req.accepted === null || req.accepted === undefined;
            }
            // Show specific status (0 = rejected, 1 = approved)
            return req.accepted === searchStatus;
          });
      
      console.log("After status filter:", afterStatusFilter.length, "requirements");

      const filteredAndMappedData = afterStatusFilter
          .map((req) => [
            req.eventId?.title || "Unknown Event",
            req.fullname || "N/A",
            req.accepted === 0
              ? chipMap.rejected
              : req.accepted === 1
              ? chipMap.approved
              : chipMap.notEvaluated,
            typeof req.accepted !== "number" ? (
              <MenuButtonTemplate
                items={[
                  {
                    label: "View Requirement",
                    icon: <RemoveRedEyeIcon />,
                    onClick: () => {
                      setSelectedFormData(req);
                      setFormData(req);
                      setViewFormData(true);
                    },
                  },
                  {
                    label: "Accept",
                    icon: <ThumbUpIcon />,
                    onClick: () => {
                      acceptRequirement(req.id)
                        .then(() => {
                          showSnackbarMessage(
                            "Successfully accepted requirement",
                            "success"
                          );
                        })
                        .catch(() => {
                          showSnackbarMessage(
                            "An error occured in accepting requirement",
                            "error"
                          );
                        })
                        .finally(() => {
                          setForceRefresh(forceRefresh + 1);
                        });
                    },
                  },
                  {
                    label: "Reject",
                    icon: <ThumbDownIcon />,
                    onClick: () => {
                      rejectRequirement(req.id)
                        .then(() => {
                          showSnackbarMessage(
                            "Successfully rejected requirement"
                          );
                        })
                        .catch(() => {
                          showSnackbarMessage(
                            "An error occured in rejecting requirement"
                          );
                        })
                        .finally(() => {
                          setForceRefresh(forceRefresh + 1);
                        });
                    },
                  },
                ]}
              />
            ) : (
              <MenuButtonTemplate
                items={[
                  {
                    label: "View Requirement",
                    icon: <RemoveRedEyeIcon />,
                    onClick: () => {
                      setSelectedFormData(req);
                      setFormData(req);
                      setViewFormData(true);
                    },
                  },
                  {
                    label: "Show Evaluation Form",
                    icon: <InsertDriveFileIcon />,
                    onClick: () => {
                      navigate(`/evaluation/${req.id}`);
                    },
                  },
                ]}
              />
              // <IconButton
              //   onClick={() => {
              //     setSelectedFormData(req);
              //     setFormData(req);
              //     setViewFormData(true);
              //   }}
              // >
              //   <RemoveRedEyeIcon />
              // </IconButton>
            ),
          ]);

      console.log("Final processed table data:", filteredAndMappedData.length, "rows");
      setTableData(filteredAndMappedData);
      })
      .catch((err) => {
        console.error("Error fetching requirements:", err);
        console.error("Error details:", err.response?.data || err.message);
        setTableData([]);
        showSnackbarMessage(
          "An error occurred while fetching requirements",
          "error"
        );
      });
  }, [forceRefresh, searchVal, searchStatus, showSnackbarMessage]);

  const ModRightComponents = [
    <CustomDropdown
      key="filter-status-dropdown"
      label="Filter Status"
      width="200px"
      menu={[
        { key: "All", value: 3 },
        { key: "Not Evaluated", value: 2 },
        { key: "Approved", value: 1 },
        { key: "Rejected", value: 0 },
      ]}
      onChange={(event) => {
        setSearchStatus(parseInt(event.target.value));
      }}
    />,
  ];

  return (
    <>
      <RequirementForm
        preventLoadingCache
        viewOnly
        eventId={selectedFormData.eventId?.id || selectedFormData.eventId || 0}
        eventType={selectedFormData.type || "external"}
        open={viewFormData}
        setOpen={setViewFormData}
      />
      <PageLayout page="requirement-evaluation">
        <TextHeader>REQUIREMENT EVALUATION</TextHeader>
        <TextSubHeader>Evaluate participant requirements here</TextSubHeader>
        <DataTable
          title="Participant Requirements"
          fields={["Event Title", "Participant Name", "Status", "Actions"]}
          data={tableData}
          onSearch={(key) => setSearchVal(key.toLowerCase())}
          componentBeforeSearch={ModRightComponents}
          // componentOnLeft={ModLeftComponents}
        />
      </PageLayout>
    </>
  );
};

export default RequirementEvalPage;
