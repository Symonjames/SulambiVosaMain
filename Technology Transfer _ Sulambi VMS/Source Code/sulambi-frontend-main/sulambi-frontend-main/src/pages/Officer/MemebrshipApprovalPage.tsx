import { useContext, useEffect, useState } from "react";
import { Box, Typography } from "@mui/material";
import TextHeader from "../../components/Headers/TextHeader";
import TextSubHeader from "../../components/Headers/TextSubHeader";
import DataTable from "../../components/Tables/DataTable";
import PageLayout from "../PageLayout";
import {
  activateMember,
  approveMembership,
  deactivateMember,
  getAllMembers,
  rejectMembership,
} from "../../api/membership";
import { MembershipType } from "../../interface/types";
import MenuButtonTemplate from "../../components/Menu/MenuButtonTemplate";
import RemoveRedEyeIcon from "@mui/icons-material/RemoveRedEye";
import ThumbDownIcon from "@mui/icons-material/ThumbDown";
import ThumbUpIcon from "@mui/icons-material/ThumbUp";
import ToggleOnIcon from "@mui/icons-material/ToggleOn";
import ToggleOffIcon from "@mui/icons-material/ToggleOff";
import MembershipAppForm from "../../components/Forms/MembershipAppForm";
import { FormDataContext } from "../../contexts/FormDataProvider";
import Chip from "../../components/Chips/Chip";
import CustomDropdown from "../../components/Inputs/CustomDropdown";
import { useSearchParams } from "react-router-dom";
import LoadingSpinner from "../../components/Loading/LoadingSpinner";

const MemebrshipApprovalPage = () => {
  const { setFormData } = useContext(FormDataContext);
  const [searchParams] = useSearchParams();

  const [searchAccStatus, setSearchAccStatus] = useState(
    parseInt(searchParams.get("account_status") ?? "") || 3
  );
  const [searchStatus, setSearchstatus] = useState<number | undefined | null>(
    parseInt(searchParams.get("status") ?? "") || 3
  );
  const [searchVal, setSearchVal] = useState("");
  const [debouncedSearchVal, setDebouncedSearchVal] = useState("");

  const [membershipData, setMembershipData] = useState<any[]>([]);
  const [openViewer, setOpenViewer] = useState(false);
  const [refreshTable, setRefreshTable] = useState(0);
  const [loading, setLoading] = useState(true);

  const approveCallback = (memberId: number) => {
    return () => {
      approveMembership(memberId).finally(() => {
        setRefreshTable(refreshTable + 1);
      });
    };
  };

  const rejectCallback = (memberId: number) => {
    return () => {
      rejectMembership(memberId).finally(() => {
        setRefreshTable(refreshTable + 1);
      });
    };
  };

  const activateCallback = (memberId: number) => {
    return () => {
      activateMember(memberId).finally(() => {
        setRefreshTable(refreshTable + 1);
      });
    };
  };

  const deactivateCallback = (memberId: number) => {
    return () => {
      deactivateMember(memberId).finally(() => {
        setRefreshTable(refreshTable + 1);
      });
    };
  };

  const ModRightComponents = [
    <CustomDropdown
      label="Filter Status"
      width="230px"
      menu={[
        { key: "All", value: 3 },
        { key: "Not Evaluated", value: 2 },
        { key: "Approved", value: 1 },
        { key: "Rejected", value: 0 },
      ]}
      onChange={(event) => {
        setSearchstatus(event.target.value as unknown as number);
      }}
    />,
    <CustomDropdown
      label="Filter Account Status"
      width="230px"
      menu={[
        { key: "All", value: 3 },
        { key: "Active", value: 1 },
        { key: "Not Active", value: 0 },
      ]}
      onChange={(event) => {
        setSearchAccStatus(event.target.value as unknown as number);
      }}
    />,
  ];

  const chipMap = {
    notEvaluated: <Chip bgcolor="blue" label="not-evaluated" color="white" />,
    noStatus: <Chip bgcolor="black" label="inactive" color="white" />,
    approved: <Chip bgcolor="#2f7a00" label="approved" color="white" />,
    rejected: <Chip bgcolor="#c10303" label="rejected" color="white" />,
    notActive: <Chip bgcolor="black" label="inactive" color="white" />,
    active: <Chip bgcolor="#2f7a00" label="active" color="white" />,
  };

  // Debounce search input to improve performance
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchVal(searchVal);
    }, 300); // 300ms delay

    return () => clearTimeout(timer);
  }, [searchVal]);

  useEffect(() => {
    setLoading(true);
    console.log("Fetching membership data...");
    console.log("Current filters - Status:", searchStatus, "Account Status:", searchAccStatus, "Search:", searchVal);
    getAllMembers().then((response) => {
      console.log("API Response:", response.data);
      const membershipResponseData: MembershipType[] = response.data.data || [];
      console.log("Raw membership data count:", membershipResponseData.length);
      console.log("Sample member:", membershipResponseData[0]);
      
      // Debug: Check pending members specifically
      const pendingMembers = membershipResponseData.filter(m => m.accepted === null || m.accepted === undefined);
      console.log(`[MEMBERSHIP_FILTER] Found ${pendingMembers.length} members with accepted=null/undefined`);
      if (pendingMembers.length > 0) {
        console.log(`[MEMBERSHIP_FILTER] Sample pending member:`, pendingMembers[0]);
        console.log(`[MEMBERSHIP_FILTER] accepted value:`, pendingMembers[0].accepted, `type:`, typeof pendingMembers[0].accepted);
      }
      
      const filteredData = membershipResponseData
        .filter((member) => {
          if (searchStatus === 3) return true;
          // Check for both null and undefined (JSON null might be either)
          if (searchStatus === 2) {
            const isPending = member.accepted === null || member.accepted === undefined;
            if (isPending) {
              console.log(`[MEMBERSHIP_FILTER] Including pending member: ID ${member.id}, accepted=${member.accepted}`);
            }
            return isPending;
          }
          if (searchStatus === 0) return member.accepted === 0;
          return member.accepted === searchStatus;
        })
        .filter((member) => {
          if (searchAccStatus === 3) return true; // Show all
          if (searchAccStatus === 1) {
            // Active: must be accepted AND active
            return member.accepted === 1 && member.active === 1;
          }
          if (searchAccStatus === 0) {
            // Not Active: either not accepted, or accepted but inactive
            return member.accepted !== 1 || member.active === 0;
          }
          return true;
        })
        .filter((member) => {
          // Use debounced search value
          if (!debouncedSearchVal || debouncedSearchVal.trim() === "") return true;
          
          const searchLower = debouncedSearchVal.toLowerCase().trim();
          const searchTerms = searchLower.split(/\s+/).filter(term => term.length > 0);
          
          // If multiple search terms, all must match (AND logic)
          if (searchTerms.length === 0) return true;
          
          // Build searchable text from all relevant fields
          const fullname = (member.fullname || "").toLowerCase();
          const srcode = (member.srcode || "").toLowerCase();
          const collegeDept = (member.collegeDept || "").toLowerCase();
          const email = (member.email || "").toLowerCase();
          const campus = (member.campus || "").toLowerCase();
          const yrlevelprogram = (member.yrlevelprogram || "").toLowerCase();
          const address = (member.address || "").toLowerCase();
          const contactNum = (member.contactNum || "").toLowerCase();
          const affiliation = (member.affiliation || "").toLowerCase();
          
          // Combine all searchable fields
          const searchableText = `${fullname} ${srcode} ${collegeDept} ${email} ${campus} ${yrlevelprogram} ${address} ${contactNum} ${affiliation}`;
          
          // Check if all search terms are found in the searchable text
          return searchTerms.every(term => searchableText.includes(term));
        });
      
      console.log("Filtered data:", filteredData);
      console.log("Filter settings - Status:", searchStatus, "Account Status:", searchAccStatus);
      
      setMembershipData(filteredData
          .map((member) => [
            member.fullname,
            member.collegeDept,
            member.accepted === 1
              ? chipMap.approved
              : member.accepted === 0
              ? chipMap.rejected
              : chipMap.notEvaluated,
            member.accepted === null
              ? chipMap.notEvaluated
              : member.accepted === 0
              ? chipMap.noStatus
              : member.active === 1
              ? chipMap.active
              : chipMap.notActive,
            // Always show action buttons - at minimum "View Requirements"
            (() => {
              const baseActions = [
                {
                  label: "View Requirements",
                  icon: <RemoveRedEyeIcon />,
                  onClick: () => {
                    setFormData(member);
                    setOpenViewer(true);
                  },
                },
              ];

              // Add status-specific actions
              if (member.accepted === null || member.accepted === undefined) {
                // Not evaluated - show approve/reject
                return (
                  <MenuButtonTemplate
                    items={[
                      ...baseActions,
                      {
                        label: "Approve Membership",
                        icon: <ThumbUpIcon />,
                        onClick: approveCallback(member.id),
                      },
                      {
                        label: "Reject/Disable",
                        icon: <ThumbDownIcon />,
                        onClick: rejectCallback(member.id),
                      },
                    ]}
                  />
                );
              } else if (member.accepted === 1 && member.active === 1) {
                // Approved and active - show deactivate
                return (
                  <MenuButtonTemplate
                    items={[
                      ...baseActions,
                      {
                        label: "Deactivate",
                        icon: <ToggleOffIcon />,
                        onClick: deactivateCallback(member.id),
                      },
                    ]}
                  />
                );
              } else if (member.accepted === 1 && member.active === 0) {
                // Approved but inactive - show reactivate
                return (
                  <MenuButtonTemplate
                    items={[
                      ...baseActions,
                      {
                        label: "Reactivate",
                        icon: <ToggleOnIcon />,
                        onClick: activateCallback(member.id),
                      },
                    ]}
                  />
                );
              } else {
                // Rejected (accepted === 0) or other status - show view only
                return <MenuButtonTemplate items={baseActions} />;
              }
            })(),
          ])
      );
      setLoading(false);
    }).catch((error) => {
      console.error("Error fetching membership data:", error);
      setMembershipData([]);
      setLoading(false);
    });
  }, [refreshTable, debouncedSearchVal, searchStatus, searchAccStatus]);

  if (loading) {
    return (
      <PageLayout page="membership-approval">
        <TextHeader>MEMBERSHIP APPROVAL</TextHeader>
        <TextSubHeader>Evaluate membership requirements here</TextSubHeader>
        <LoadingSpinner message="Loading membership data..." />
      </PageLayout>
    );
  }

  return (
    <>
      <MembershipAppForm
        hideSubmit
        dataLoader
        viewOnly={true}
        open={openViewer}
        setOpen={setOpenViewer}
      />
      <PageLayout page="membership-approval">
        <TextHeader>MEMBERSHIP APPROVAL</TextHeader>
        <TextSubHeader>Evaluate membership requirements here</TextSubHeader>
        {(debouncedSearchVal || searchStatus !== 3 || searchAccStatus !== 3) && (
          <Box sx={{ 
            padding: "10px 20px", 
            backgroundColor: "#f5f5f5", 
            borderRadius: "8px",
            marginBottom: "10px",
            display: "flex",
            alignItems: "center",
            gap: 1
          }}>
            <Typography variant="body2" color="text.secondary">
              Showing {membershipData.length} result{membershipData.length !== 1 ? 's' : ''}
              {debouncedSearchVal && ` for "${debouncedSearchVal}"`}
              {searchStatus !== 3 && ` (${searchStatus === 2 ? 'Not Evaluated' : searchStatus === 1 ? 'Approved' : 'Rejected'})`}
              {searchAccStatus !== 3 && ` (${searchAccStatus === 1 ? 'Active' : 'Not Active'})`}
            </Typography>
          </Box>
        )}
        <DataTable
          title="Membership requirements"
          fields={[
            "Full Name",
            "College/Department",
            "Status",
            "Account Status",
            "Actions",
          ]}
          data={membershipData}
          onSearch={(key) => {
            setSearchVal(key);
          }}
          componentBeforeSearch={ModRightComponents}
          // componentOnLeft={ModLeftComponents}
        />
      </PageLayout>
    </>
  );
};

export default MemebrshipApprovalPage;
