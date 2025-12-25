import { ReactNode } from "react";

export interface CheckBoxDataType {
  label: string;
  initialValue: boolean;
  callback?: (event: any) => void;
}

export interface RadioListDataType {
  label: string;
  callback?: (event: any) => void;
}

export interface SessionResponse {
  accountType: "admin" | "member" | "officer";
  id: number;
  token: string | null;
  userid: number;
}

export interface MembershipType {
  id: number;
  applyingAs: string;
  volunterismExperience: boolean;
  weekdaysTimeDevotion: string;
  weekendsTimeDevotion: string;
  areasOfInterest: string;
  fullname: string;
  email: string;
  srcode: string;
  age: number;
  birthday: string;
  sex: string;
  campus: string;
  collegeDept: string;
  yrlevelprogram: string;
  address: string;
  contactNum: string;
  fblink: string;
  bloodType: string;
  bloodDonation: string;
  medicalCondition: string;
  paymentOption: string;
  username: string;
  password: string;
  accepted?: number | boolean;
  volunteerExpQ1?: string;
  volunteerExpQ2?: string;
  reasonQ1?: string;
  reasonQ2?: string;
  active: number;
}

export interface SignatoriesType {
  preparedBy: string;
  reviewedBy: string;
  recommendingApproval1: string;
  recommendingApproval2: string;
  approvedBy: string;
  preparedTitle: string;
  reviewedTitle: string;
  approvedTitle: string;
  recommendingSignatory1: string;
  recommendingSignatory2: string;
}

export interface ExternalEventProposalType {
  id: number;
  extensionServiceType: string;
  eventProposalType: string;
  externalServiceType: string;
  title: string;
  location: string;
  durationStart: number;
  durationEnd: number;
  sdg: string;
  orgInvolved: string;
  programInvolved: string;
  projectLeader: string;
  partners: string;
  beneficiaries: string;
  totalCost: string;
  sourceOfFund: string;
  rationale: string;
  objectives: string;
  expectedOutput: string;
  description: string;
  financialPlan: string;
  dutiesOfPartner: string;
  evaluationMechanicsPlan: string;
  sustainabilityPlan: string;
  createdBy: any;
  status: "editing" | "submitted" | "accepted" | "rejected";
  toPublic: boolean;
  hasReport?: boolean;
  createdAt?: number;
  signatoriesId: SignatoriesType;
}

export interface InternalEventProposalType {
  id: number;
  title: string;
  venue: string;
  durationStart: number;
  durationEnd: number;
  modeOfDelivery: string;
  projectTeam: string;
  partner: string;
  participant: string;
  maleTotal: string;
  femaleTotal: string;
  rationale: string;
  objectives: string;
  description: string;
  workPlan: any;
  financialRequirement: any;
  evaluationMechanicsPlan: any;
  sustainabilityPlan: string;
  createdBy: any;
  status: "editing" | "submitted" | "accepted" | "rejected";
  toPublic: boolean;
  hasReport?: boolean;
  createdAt?: number;
  signatoriesId: SignatoriesType;
  eventProposalType?: string;
  activities?: Array<{ activity_name: string; months: number[] }>;
}

export interface MenuButtomTemplateItemType {
  label: string;
  icon?: ReactNode;
  onClick?: () => void;
}

export interface EvaluationDataType {
  criteria: any;
  comment: string;
  q13: string;
  q14: string;
}

export interface RequirementsDataType {
  id: number;
  eventId: any;
  medCert: string;
  waiver: string;

  fullname: string;
  email: string;
  srcode: string;
  age: string;
  birthday: string;
  sex: string;
  campus: string;
  collegeDept: string;
  yrlevelprogram: string;
  address: string;
  contactNum: string;
  fblink: string;

  curriculum?: string;
  destination?: string;
  firstAid?: string;
  fees?: string;
  personnelInCharge?: string;
  personnelRole?: string;
  accepted?: number;
}

export interface AccountsDataType {
  id: number;
  accountType: "admin" | "officer" | "member";
  username: string;
  password: string;
}

export interface ParticipationHistoryType {
  evaluationId: number;
  event: ExternalEventProposalType | InternalEventProposalType;
  requirement: RequirementsDataType;
  eventType: "external" | "internal";
  attendanceStatus: "registered" | "attended" | "not-attended";
}

export interface EventEvalListType {
  requirements: RequirementsDataType;
  evaluation: EvaluationDataType;
}

export interface AnalysisResultType {
  "Animal Welfare": number;
  Community: number;
  "Cultural Preservation": number;
  "Disaster Response": number;
  Education: number;
  Environmental: number;
  "Food Distribution": number;
  Fundraising: number;
  Health: number;
  "Homeless Outreach": number;
  "Mental Health Support": number;
  "Public Safety": number;
  "Senior Assistance": number;
  Sports: number;
  "Youth Mentorship": number;
}

export interface DashboardDataType {
  implementedEvent: number;
  pendingEvents: number;
  rejectedEvents: number;
  totalAccounts: number;
  totalActiveMembers: number;
  totalApprovedEvents: number;
  totalMembers: number;
  totalPendingMembers: number;
  totalAllMembers: number; // Total members uploaded (all statuses)
}

export interface ExternalReportType {
  eventId?: ExternalEventProposalType;
  narrative: string;
  photos: string[];
  photoCaptions?: string[];
  signatoriesId?: any;
}

export interface InternalReportType {
  eventId?: InternalEventProposalType;
  narrative: string;
  photos: string[];
  photoCaptions?: string[];
  signatoriesId?: any;
  finance: {
    budgetUtilized: number;
    psAttribution: number;
    budgetUtilizedSource: string;
    psAttributionSource: string;
  };
}

export interface ReportAnalytics {
  outsider: {
    sex: {
      male: number;
      female: number;
    };
    evaluation: {
      overall: {
        excellent: number;
        verySatisfactory: number;
        satisfactory: number;
        fair: number;
        poor: number;
      };
      timeline: {
        excellent: number;
        verySatisfactory: number;
        satisfactory: number;
        fair: number;
        poor: number;
      };
    };
  };
  insider: {
    sex: {
      male: number;
      female: number;
    };
    evaluation: {
      overall: {
        excellent: number;
        verySatisfactory: number;
        satisfactory: number;
        fair: number;
        poor: number;
      };
      timeline: {
        excellent: number;
        verySatisfactory: number;
        satisfactory: number;
        fair: number;
        poor: number;
      };
    };
  };
}

export interface InternalReportAnalytics {
  sex: {
    male: number;
    female: number;
  };
  evalResult: {
    male: {
      excellent: number;
      verySatisfactory: number;
      satisfactory: number;
      fair: number;
      poor: number;
    };
    female: {
      excellent: number;
      verySatisfactory: number;
      satisfactory: number;
      fair: number;
      poor: number;
    };
  };
}
