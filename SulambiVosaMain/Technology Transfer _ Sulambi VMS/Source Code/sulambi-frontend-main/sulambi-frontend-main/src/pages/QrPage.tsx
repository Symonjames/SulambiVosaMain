import FlexBox from "../components/FlexBox";

const QrPage = () => {
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
      ></FlexBox>
    </FlexBox>
  );
};

export default QrPage;
