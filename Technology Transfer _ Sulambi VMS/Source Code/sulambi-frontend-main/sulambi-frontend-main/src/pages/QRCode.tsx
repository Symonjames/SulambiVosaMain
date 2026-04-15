import { Typography, Card, CardContent, CardActions, Box, Chip } from "@mui/material";
import FlexBox from "../components/FlexBox";
import PopupModal from "../components/Modal/PopupModal";
import CustomInput from "../components/Inputs/CustomInput";
import PrimaryButton from "../components/Buttons/PrimaryButton";
import SendIcon from "@mui/icons-material/Send";
import { checkReqIdValidity } from "../api/evaluation";
import { useNavigate } from "react-router-dom";
import { useContext, useState } from "react";
import { SnackbarContext } from "../contexts/SnackbarProvider";
import BeneficiariesEvaluationForm from "../components/Forms/BeneficiariesEvaluationForm";
import { VolunteerActivism, People, Star, Assignment } from "@mui/icons-material";

const QRCode = () => {
  const { showSnackbarMessage } = useContext(SnackbarContext);
  const navigate = useNavigate();
  const [id, setId] = useState("");
  const [showEvaluationOptions, setShowEvaluationOptions] = useState(false);
  const [openBeneficiaryForm, setOpenBeneficiaryForm] = useState(false);
  const [eventData] = useState<{ id?: number; title?: string } | null>(null);

  const checkvalidity = async () => {
    const normalizedToken = (id || "").trim();
    if (!normalizedToken) {
      showSnackbarMessage("Please enter your evaluation token", "warning");
      return;
    }
    try {
      await checkReqIdValidity(normalizedToken);
      setId(normalizedToken);
      // Token-based flow is for volunteer evaluation links.
      // Navigate directly to the public evaluation form.
      navigate(`/evaluation/${encodeURIComponent(normalizedToken)}`);
    } catch (_err) {
      showSnackbarMessage("Cannot evaluate on the token provided", "warning");
    }
  };

  const handleVolunteerStart = () => {
    if (id && id.trim()) {
      navigate(`/evaluation/${id.trim()}`);
    }
  };

  const handleBeneficiarySubmit = (data: any) => {
    console.log('Beneficiary Evaluation Submitted:', data);
    showSnackbarMessage("Beneficiary evaluation submitted successfully!", "success");
    setOpenBeneficiaryForm(false);
    // You can add API call here to submit beneficiary evaluation
  };

  return (
    <FlexBox
      width="100%"
      height="100%"
      justifyContent="center"
      alignItems="center"
      position="absolute"
    >
      <FlexBox
        flex="15"
        height="calc(100% - 40px)"
        alignItems="center"
        padding="20px 10px"
        flexDirection="column"
        rowGap="15px"
        sx={{
          background: "linear-gradient(180deg, #C07F00 0%, #FFD95A 100%)",
          boxShadow: "2px 0px 15px 0px #b3b3b3",
        }}
      >
        {!showEvaluationOptions ? (
          <PopupModal
            open
            hideCloseButton
            disableBGShadow
            header="Welcome to Evaluation Automatic Tracker"
          >
            <Typography gutterBottom>
              Kindly enter your evaluation token received from your email to start
              attendance/evaluation
            </Typography>
            <FlexBox alignItems="center" gap="10px">
              <CustomInput
                flex={1}
                label="Evaluation token"
                size="small"
                value={id}
                onChange={(event) => setId(event.target.value)}
                onKeyDown={(event: any) => {
                  if (event.key === "Enter") {
                    event.preventDefault();
                    checkvalidity();
                  }
                }}
              />
              <PrimaryButton
                label="Evaluate Now"
                icon={<SendIcon />}
                onClick={checkvalidity}
              />
            </FlexBox>
          </PopupModal>
        ) : (
          <PopupModal
            open
            hideCloseButton
            disableBGShadow
            header="Choose Your Evaluation Type"
            width="80vw"
            maxWidth="800px"
          >
            <Typography gutterBottom textAlign="center" mb={3}>
              Please select the type of evaluation that applies to you:
            </Typography>
            
            <FlexBox gap={3} justifyContent="center" flexWrap="wrap">
              {/* Volunteer Evaluation Card */}
              <Card 
                sx={{ 
                  minWidth: 300, 
                  maxWidth: 350,
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                  }
                }}
                onClick={handleVolunteerStart}
              >
                <CardContent>
                  <FlexBox alignItems="center" gap={2} mb={2}>
                    <VolunteerActivism sx={{ fontSize: 40, color: '#4caf50' }} />
                    <Box>
                      <Typography variant="h6" component="h2">
                        Volunteer Evaluation
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        I participated as a volunteer
                      </Typography>
                    </Box>
                  </FlexBox>
                  
                  <Typography variant="body2" paragraph>
                    Evaluate your volunteer experience including:
                  </Typography>
                  
                  <Box component="ul" sx={{ pl: 2, m: 0, fontSize: '0.875rem' }}>
                    <li>Event organization & planning</li>
                    <li>Learning & skill development</li>
                    <li>Team collaboration</li>
                    <li>Support & resources provided</li>
                  </Box>

                  <FlexBox gap={1} flexWrap="wrap" mt={2}>
                    <Chip label="Rating System" size="small" color="primary" />
                    <Chip label="Skill Development" size="small" color="primary" />
                    <Chip label="Team Work" size="small" color="primary" />
                  </FlexBox>
                </CardContent>
                
                <CardActions sx={{ p: 2, pt: 0 }}>
                  <PrimaryButton
                    label="Start Volunteer Evaluation"
                    icon={<Star />}
                    fullWidth
                    onClick={handleVolunteerStart}
                  />
                </CardActions>
              </Card>

              {/* Beneficiary Evaluation Card */}
              <Card 
                sx={{ 
                  minWidth: 300, 
                  maxWidth: 350,
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
                  }
                }}
                onClick={() => setOpenBeneficiaryForm(true)}
              >
                <CardContent>
                  <FlexBox alignItems="center" gap={2} mb={2}>
                    <People sx={{ fontSize: 40, color: '#9c27b0' }} />
                    <Box>
                      <Typography variant="h6" component="h2">
                        Beneficiary Evaluation
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        I received services/benefits
                      </Typography>
                    </Box>
                  </FlexBox>
                  
                  <Typography variant="body2" paragraph>
                    Evaluate the service you received including:
                  </Typography>
                  
                  <Box component="ul" sx={{ pl: 2, m: 0, fontSize: '0.875rem' }}>
                    <li>Service quality & impact</li>
                    <li>Volunteer helpfulness</li>
                    <li>Accessibility & participation</li>
                    <li>Cultural sensitivity</li>
                  </Box>

                  <FlexBox gap={1} flexWrap="wrap" mt={2}>
                    <Chip label="Impact Assessment" size="small" color="secondary" />
                    <Chip label="Demographics" size="small" color="secondary" />
                    <Chip label="Accessibility" size="small" color="secondary" />
                  </FlexBox>
                </CardContent>
                
                <CardActions sx={{ p: 2, pt: 0 }}>
                  <PrimaryButton
                    label="Start Beneficiary Evaluation"
                    icon={<Assignment />}
                    fullWidth
                    color="secondary"
                    onClick={() => setOpenBeneficiaryForm(true)}
                  />
                </CardActions>
              </Card>
            </FlexBox>

            <FlexBox justifyContent="center" mt={3} gap="15px" flexWrap="wrap">
              <PrimaryButton
                label="Back to Token Entry"
                variant="outlined"
                onClick={() => {
                  setShowEvaluationOptions(false);
                  setId("");
                }}
              />
              <PrimaryButton
                label="Direct Volunteer Form"
                variant="outlined"
                onClick={() => navigate('/volunteer-evaluation')}
                sx={{ borderColor: '#4caf50', color: '#4caf50' }}
              />
              <PrimaryButton
                label="Direct Beneficiary Form"
                variant="outlined"
                onClick={() => navigate('/beneficiary-evaluation')}
                sx={{ borderColor: '#9c27b0', color: '#9c27b0' }}
              />
            </FlexBox>
          </PopupModal>
        )}
      </FlexBox>

      {/* Beneficiary evaluation (PIN-based) stays as modal; volunteer uses same form as email link via /evaluation/:id */}
      <BeneficiariesEvaluationForm
        open={openBeneficiaryForm}
        setOpen={setOpenBeneficiaryForm}
        eventId={eventData?.id != null ? String(eventData.id) : "1"}
        eventTitle={eventData?.title || "Event Evaluation"}
        onSubmit={handleBeneficiarySubmit}
      />
    </FlexBox>
  );
};

export default QRCode;
