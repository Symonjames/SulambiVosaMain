import TextHeader from "../../components/Headers/TextHeader";
import TextSubHeader from "../../components/Headers/TextSubHeader";
import DataTable from "../../components/Tables/DataTable";
import PageLayout from "../PageLayout";

const HelpdeskMemberPage = () => {
  return (
    <PageLayout page="helpdesk">
      <TextHeader>HelpDesk</TextHeader>
      <TextSubHeader>Submit or propose your helpdesk here</TextSubHeader>
      <DataTable
        title="Proposed Helpdesk"
        data={[]}
        fields={["Title", "Location", "Participants", "Actions"]}
      />
    </PageLayout>
  );
};

export default HelpdeskMemberPage;
