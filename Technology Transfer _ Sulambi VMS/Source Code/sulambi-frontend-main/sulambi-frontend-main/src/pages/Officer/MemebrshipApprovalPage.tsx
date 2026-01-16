import { useContext, useEffect, useState } from "react";
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
          if (!searchVal) return true; // If no search term, show all
          const searchLower = searchVal.toLowerCase();
          return (
            (member.srcode?.toLowerCase() || "").includes(searchLower) ||
            (member.fullname?.toLowerCase() || "").includes(searchLower) ||
            (member.collegeDept?.toLowerCase() || "").includes(searchLower)
          );
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
            member.accepted === null ? (
              <MenuButtonTemplate
                items={[
                  {
                    label: "View Requirements",
                    icon: <RemoveRedEyeIcon />,
                    onClick: () => {
                      setFormData(member);
                      setOpenViewer(true);
                    },
                  },
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
            ) : member.accepted === 0 ? (
              <></>
            ) : member.accepted === 1 && member.active === 1 ? (
              <MenuButtonTemplate
                items={[
                  {
                    label: "View Requirements",
                    icon: <RemoveRedEyeIcon />,
                    onClick: () => {
                      setFormData(member);
                      setOpenViewer(true);
                    },
                  },
                  {
                    label: "Deactivate",
                    icon: <ToggleOffIcon />,
                    onClick: deactivateCallback(member.id),
                  },
                ]}
              />
            ) : member.accepted === 1 && member.active === 0 ? (
              <MenuButtonTemplate
                items={[
                  {
                    label: "View Requirements",
                    icon: <RemoveRedEyeIcon />,
                    onClick: () => {
                      setFormData(member);
                      setOpenViewer(true);
                    },
                  },
                  {
                    label: "Reactivate",
                    icon: <ToggleOnIcon />,
                    onClick: activateCallback(member.id),
                  },
                ]}
              />
            ) : (
              <></>
            ),
          ])
      );
      setLoading(false);
    }).catch((error) => {
      console.error("Error fetching membership data:", error);
      setMembershipData([]);
      setLoading(false);
    });
  }, [refreshTable, searchVal, searchStatus, searchAccStatus]);

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
            setSearchVal(key.toLowerCase());
          }}
          componentBeforeSearch={ModRightComponents}
          // componentOnLeft={ModLeftComponents}
        />
      </PageLayout>
    </>
  );
};

export default MemebrshipApprovalPage;
